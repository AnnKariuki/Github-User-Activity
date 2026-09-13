#!/usr/bin/env python3
from dotenv_loader import API_KEY
import argparse
from urllib.request import urlopen, Request
import json 
from urllib.error import HTTPError, URLError
from typing import Any
import redis

r = redis.Redis(
    host='localhost',
    port=6379,
    db=0 # The default Redis database index,
)

def get_user_data(username: str) -> bytes | None:
    cache_key = f"user_activity:{username.lower()}"
    # Always make sure there is connectivity with Redis before performing any redis operations
    try:
        # github usernames are case-insensitive so octat and Octat should be the same key. avoid data duplication
        cached_data = r.get(cache_key)
        if cached_data is not None:
            print("Cache hit!")
            return cached_data
    except redis.ConnectionError as e:
        print(f"❌ Connection error: Could not connect to Redis at {e}.")
        print("Fall through to api call")

    print("Cache miss")
    url = f"https://api.github.com/users/{username}/events"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    request = Request(url, headers=headers)
    try: 
        with urlopen(request, timeout=10) as response:
            body = response.read()
    except HTTPError as error:
        if error.code == 404:
            print(f"Github username {username} was not found")
        elif error.code == 401:
            print("Unauthorized to carry out this action")
        else:
            print(error.status, error.reason)
        return None
    except URLError as error:
        print(error.reason)
        return None
    except TimeoutError:
        print('Request Timed out')
        return None
    else:
        try: 
            r.set(cache_key, body, ex=300)
        except redis.ConnectionError as e:
            print(f"❌ Connection error: Could not connect to Redis at {e}.")
        return body
  
def get_github_activity(args: argparse.Namespace) -> None:
    username = args.username
    user_data = get_user_data(username)
    if user_data is not None:
        decoded_body = user_data.decode("utf-8")
        events = json.loads(decoded_body)
        display_events(events)
    else:
        return None

def format_event(event: dict[str,Any]) -> str:
    event_type = event["type"]
    actor = event["actor"]["login"]
    repo = event["repo"]["name"]

    if event_type == "CommitCommentEvent":
        return f"{actor} created commit comment"

    elif event_type == "CreateEvent":
        ref = event["payload"]["ref"]
        return f"{actor} created {ref} in {repo}"

    elif event_type == "DeleteEvent":
        ref = event["payload"]["ref"]
        return f"{actor} deleted {ref} in {repo}"

    elif event_type == "PushEvent":
        return f"{actor} pushed to {repo}"

    elif event_type == "IssueCommentEvent":
        issue_number = event["payload"]["issue"]["number"]
        return f"{actor} commented on issue {issue_number}"

    elif event_type == "IssuesEvent":
        issue_number = event["payload"]["issue"]["number"]
        return f"{actor} created issue {issue_number}"

    elif event_type == "WatchEvent":
        return f"{actor} starred {repo}"

    elif event_type == "PullRequestEvent":
        pull_request_number = event["payload"]["pull_request"]["number"]
        return f"{actor} created pull request {pull_request_number}"

    elif event_type == "PullRequestReviewEvent":
        pull_request_number = event["payload"]["pull_request"]["number"]
        return f"{actor} reviewed pull request {pull_request_number}"

    elif event_type == "PullRequestReviewCommentEvent":
        pull_request_number = event["payload"]["pull_request"]["number"]
        return f"{actor} commented on pull request {pull_request_number}"
    else:
        return event_type

def display_events(events: list[dict[str,Any]]) -> None:
    if not events:
        print('No events to print')
        return

    for event in events:
        print(format_event(event))


def main() -> None:
    argument_parser = argparse.ArgumentParser(prog="Github Events", description="Fetch and see recent activity of a github user in a moment's notice")
    argument_parser.add_argument("username", help="to see the github activity of a particular user run: program_name <username>")
    argument_parser.set_defaults(func=get_github_activity)
    args = argument_parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
