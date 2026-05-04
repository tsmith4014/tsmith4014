import base64
import os
import random

import requests
from github import Github

# Primary follows boredapi.com; some networks redirect to www (unreliable).
# Mirror keeps the workflow working when the primary is unreachable.
ACTIVITY_URLS = (
    "https://boredapi.com/api/activity",
    "https://bored.api.lewagon.com/api/activity/",
)
REQUEST_TIMEOUT = 15


def fetch_activity_data():
    last_error = None
    for url in ACTIVITY_URLS:
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            if "activity" in data and "type" in data:
                return data
        except (requests.RequestException, ValueError, KeyError) as exc:
            last_error = exc
            continue
    raise RuntimeError("Could not fetch activity from any provider") from last_error


def fetch_suggestion():
    suggestion_data = fetch_activity_data()
    activity = suggestion_data["activity"]
    activity_type = suggestion_data["type"]
    participants = suggestion_data["participants"]
    price = suggestion_data["price"]

    suggestion_parts = []

    activity_type_phrases = {
        "education": [
            "🎓 Let's work on some brainpower",
            "📚 Time to hit the books",
            "🤓 Geek out",
        ],
        "recreational": [
            "🏖️ Time to relax",
            "🎉 Let's have some fun",
            "🎮 Game on",
        ],
        "social": ["👥 Be social", "🗨️ Let's mingle", "🤝 Time to network"],
        "charity": [
            "❤️ Make the world a better place",
            "🤲 Time to give back",
            "🌍 Be a hero",
        ],
        "cooking": [
            "👨‍🍳 Masterchef time",
            "🍳 Let's cook up a storm",
            "🍲 Soup's on",
        ],
        "music": [
            "🎵 Feel the rhythm",
            "🎶 Let's make some noise",
            "🎸 Rock on",
        ],
        "busywork": ["🧹 Knock out a chore", "✅ Productivity time", "📋 Check something off"],
    }

    if activity_type in activity_type_phrases:
        suggestion_parts.append(random.choice(activity_type_phrases[activity_type]))

    if participants == 0:
        suggestion_parts.append("🚶‍♂️ Solo activity")
    elif participants == 1:
        suggestion_parts.append("👤 Grab a friend")
    elif participants == 2:
        suggestion_parts.append("👫 Grab a couple friends")
    else:
        suggestion_parts.append("👨‍👩‍👦‍👦 Gather the squad")

    if price == 0:
        suggestion_parts.append("💰 It's free!")
    elif 0 < price < 0.2:
        suggestion_parts.append("💵 Pocket change needed")
    elif 0.2 <= price < 0.5:
        suggestion_parts.append("💸 Break open your piggy bank")
    else:
        suggestion_parts.append("💳 Time to splurge!")

    suggestion_parts.append(f"🎉 {activity}")
    return " | ".join(suggestion_parts)


def replace_suggestion_in_readme(readme_data: str, suggestion: str) -> str:
    readme_lines = readme_data.split("\n")
    for i, line in enumerate(readme_lines):
        if "⚡ AI Suggestion of the Day: 🤖" not in line:
            continue
        start = line.find("🤖") + len("🤖")
        end = line.rfind("🤖")
        if start != -1 and end != -1 and start != end:
            readme_lines[i] = line[:start] + " " + suggestion + " " + line[end:]
            return "\n".join(readme_lines)
    raise RuntimeError("Suggestion marker not found in README.md")


def main():
    my_secret_key = os.environ["MY_SECRET_KEY"]
    suggestion = fetch_suggestion()

    g = Github(my_secret_key)
    repo = g.get_repo("tsmith4014/tsmith4014")
    contents = repo.get_contents("README.md")
    readme_data = base64.b64decode(contents.content).decode("utf-8")
    new_readme_data = replace_suggestion_in_readme(readme_data, suggestion)
    repo.update_file(
        contents.path,
        "Updated Suggestion of the Day",
        new_readme_data,
        contents.sha,
    )


if __name__ == "__main__":
    main()
