from dotenv_loader import API_KEY
import argparse
import urllib.request
import json 

def get_github_activity(args):
    print(f"here {args}")

def main():
    argument_parser = argparse.ArgumentParser(prog="Github Events", description="Fetch and see recent activity of a github user in a moment's notice")
    argument_parser.add_argument("username", help="to see the github activity of a particular user run: program_name <username>")
    argument_parser.set_defaults(func=get_github_activity)
    args = argument_parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
