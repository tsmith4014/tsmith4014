from __future__ import annotations

import re
from pathlib import Path

import requests

README_PATH = Path(__file__).with_name("README.md")
REQUEST_TIMEOUT = 15
MAX_JOKE_ATTEMPTS = 40

JOKE_API = "https://v2.jokeapi.dev/joke/Programming?format=json"
ACTIVITY_URLS = (
    "https://boredapi.com/api/activity",
    "https://bored.api.lewagon.com/api/activity/",
)

JOKE_PATTERN = re.compile(r"(⚡ AI Joke of the Day: 🤖 ).*?( 🤖)", re.DOTALL)
SUGGESTION_PATTERN = re.compile(
    r"(⚡ AI Suggestion of the Day: 🤖 ).*?( 🤖)",
    re.DOTALL,
)


def fetch_json(url: str) -> dict:
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def fetch_clean_joke() -> str:
    for _ in range(MAX_JOKE_ATTEMPTS):
        joke_data = fetch_json(JOKE_API)
        if joke_data.get("error"):
            continue

        flags = joke_data.get("flags") or {}
        if any(
            flags.get(key)
            for key in (
                "nsfw",
                "religious",
                "political",
                "racist",
                "sexist",
                "explicit",
            )
        ):
            continue

        if joke_data.get("type") == "single":
            return str(joke_data["joke"]).strip()

        setup = str(joke_data["setup"]).strip()
        delivery = str(joke_data["delivery"]).strip()
        return f"{setup} {delivery}"

    raise RuntimeError(
        f"Could not obtain a clean programming joke after {MAX_JOKE_ATTEMPTS} tries",
    )


def fetch_activity_data() -> dict:
    last_error = None
    for url in ACTIVITY_URLS:
        try:
            data = fetch_json(url)
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            continue

        if "activity" in data and "type" in data:
            return data

        last_error = ValueError(f"Activity response from {url} was missing fields")

    raise RuntimeError("Could not fetch activity from any provider") from last_error


def participants_label(participants: int) -> str:
    if participants <= 1:
        return "solo"
    if participants == 2:
        return "two-person"
    if participants <= 4:
        return "small group"
    return "group"


def price_label(price: float) -> str:
    if price <= 0:
        return "free"
    if price < 0.2:
        return "low cost"
    if price < 0.5:
        return "paid"
    return "splurge"


def fetch_suggestion() -> str:
    activity_data = fetch_activity_data()
    activity = str(activity_data["activity"]).strip()
    activity_type = str(activity_data["type"]).strip().lower().replace("_", " ")
    participants = int(activity_data["participants"])
    price = float(activity_data["price"])
    people = participants_label(participants)
    cost = price_label(price)
    return f"{activity} | {activity_type} | {people} | {cost}"


def replace_marker(readme_text: str, pattern: re.Pattern[str], replacement: str) -> str:
    updated, count = pattern.subn(
        lambda match: f"{match.group(1)}{replacement}{match.group(2)}",
        readme_text,
        count=1,
    )
    if count != 1:
        raise RuntimeError("README marker not found or not unique")
    return updated


def update_readme_text(readme_text: str, joke: str, suggestion: str) -> str:
    updated = replace_marker(readme_text, JOKE_PATTERN, joke)
    return replace_marker(updated, SUGGESTION_PATTERN, suggestion)


def main() -> None:
    joke = fetch_clean_joke()
    suggestion = fetch_suggestion()
    readme_text = README_PATH.read_text(encoding="utf-8")
    updated_text = update_readme_text(readme_text, joke, suggestion)

    if updated_text != readme_text:
        README_PATH.write_text(updated_text, encoding="utf-8")


if __name__ == "__main__":
    main()
