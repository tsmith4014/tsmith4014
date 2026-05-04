import base64
import os

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


def _participants_label(participants: int) -> str:
    if participants <= 0:
        return "solo"
    if participants == 1:
        return "pair-friendly"
    if participants == 2:
        return "small group"
    return "group-sized"


def _price_label(price: float) -> str:
    if price == 0:
        return "free"
    if price < 0.2:
        return "pocket change"
    if price < 0.5:
        return "modest spend"
    return "splurge territory"


def fetch_suggestion():
    """One-line suggestion for README (plain text between the robot markers)."""
    d = fetch_activity_data()
    activity = str(d["activity"]).strip()
    activity_type = str(d["type"]).strip().lower().replace("_", " ")
    participants = int(d["participants"])
    price = float(d["price"])
    people = _participants_label(participants)
    cost = _price_label(price)
    return f"{activity} - {activity_type} - {people} - {cost}"


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
