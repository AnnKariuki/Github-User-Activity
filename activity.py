#!/usr/local/bin/python3
from dotenv_loader import API_KEY
import argparse
from urllib.request import urlopen, Request
import json 
from urllib.error import HTTPError, URLError
from typing import Any

def get_github_activity(args: argparse.Namespace) -> None:
    username = args.username
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
            print(f"Unauthorized to carry out this action ")
        else:
            print(error.status, error.reason)
        return
    except URLError as error:
        print(error.reason)
        return
    except TimeoutError:
        print('Request Timed out')
        return
    else:
        decoded_body = body.decode("utf-8")
        events = json.loads(decoded_body)
        display_events(events)

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
