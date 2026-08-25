import os
# Minimal dotenv loader cause I can't use external packages like python-dotenv as per the project requirements
with open(".env") as f:
    for line in f:
        key, value = line.strip().split("=", 1)
        os.environ[key] = value
API_KEY = os.environ["GITHUB_PAT"]