import base64
import os
import re

import requests
from github import Github

JOKE_API = "https://v2.jokeapi.dev/joke/Programming?format=json"
JOKE_PATTERN = re.compile(
    r"(⚡ AI Joke of the Day: 🤖 ).*?( 🤖)", re.DOTALL,
)
MAX_JOKE_ATTEMPTS = 40
REQUEST_TIMEOUT = 15


def fetch_clean_joke():
    for _ in range(MAX_JOKE_ATTEMPTS):
        response = requests.get(JOKE_API, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        joke_data = response.json()

        if joke_data.get("error"):
            continue

        flags = joke_data.get("flags") or {}
        if any(
            flags.get(k)
            for k in (
                "nsfw", "religious", "political", "racist", "sexist", "explicit",
            )
        ):
            continue

        if joke_data.get("type") == "single":
            return joke_data["joke"].strip()
        return f"{joke_data['setup'].strip()} {joke_data['delivery'].strip()}"

    raise RuntimeError(
        f"Could not obtain a clean programming joke after {MAX_JOKE_ATTEMPTS} tries",
    )


def replace_joke_in_readme(readme_data: str, joke: str) -> str:
    new_readme, count = JOKE_PATTERN.subn(
        lambda m: f"{m.group(1)}{joke}{m.group(2)}",
        readme_data,
        count=1,
    )
    if count != 1:
        raise RuntimeError("Joke marker not found or not unique in README.md")
    return new_readme


def main():
    my_secret_key = os.environ["MY_SECRET_KEY"]
    joke = fetch_clean_joke()

    g = Github(my_secret_key)
    repo = g.get_repo("tsmith4014/tsmith4014")
    contents = repo.get_contents("README.md")
    readme_data = base64.b64decode(contents.content).decode("utf-8")
    new_readme_data = replace_joke_in_readme(readme_data, joke)
    repo.update_file(
        contents.path,
        "Updated Joke of the Day",
        new_readme_data,
        contents.sha,
    )


if __name__ == "__main__":
    main()
