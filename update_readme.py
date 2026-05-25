from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path

import requests

README_PATH = Path(__file__).with_name("README.md")
REQUEST_TIMEOUT = 15
MAX_JOKE_ATTEMPTS = 40
MAX_TITLE_LENGTH = 110
REQUEST_HEADERS = {
    "User-Agent": "tsmith4014-profile-readme/1.0 (+https://github.com/tsmith4014/tsmith4014)",
}

JOKE_API = "https://v2.jokeapi.dev/joke/Programming?format=json"
ACTIVITY_URLS = (
    "https://boredapi.com/api/activity",
    "https://bored.api.lewagon.com/api/activity/",
)
SIGNAL_SOURCES = (
    {
        "track": "AI practice",
        "source": "Simon Willison",
        "feed_url": "https://simonwillison.net/atom/everything/",
        "home_url": "https://simonwillison.net/",
    },
    {
        "track": "AI research",
        "source": "arXiv cs.AI",
        "feed_url": "https://rss.arxiv.org/rss/cs.AI",
        "home_url": "https://arxiv.org/list/cs.AI/recent",
    },
    {
        "track": "Systems",
        "source": "LWN.net",
        "feed_url": "https://lwn.net/headlines/rss",
        "home_url": "https://lwn.net/",
    },
    {
        "track": "Architecture",
        "source": "Martin Fowler",
        "feed_url": "https://martinfowler.com/feed.atom",
        "home_url": "https://martinfowler.com/",
    },
    {
        "track": "Edge & cloud",
        "source": "Cloudflare Blog",
        "feed_url": "https://blog.cloudflare.com/rss/",
        "home_url": "https://blog.cloudflare.com/",
    },
)

JOKE_PATTERN = re.compile(r"(⚡ AI Joke of the Day: 🤖 ).*?( 🤖)", re.DOTALL)
SUGGESTION_PATTERN = re.compile(
    r"(⚡ AI Suggestion of the Day: 🤖 ).*?( 🤖)",
    re.DOTALL,
)
SIGNALS_PATTERN = re.compile(
    r"(<!-- SIGNALS:START -->\n).*?(\n<!-- SIGNALS:END -->)",
    re.DOTALL,
)


@dataclass(frozen=True)
class SignalItem:
    track: str
    source: str
    title: str
    url: str
    published: datetime | None = None


def fetch_json(url: str) -> dict:
    response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def fetch_text(url: str) -> str:
    response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.text


def clean_inline(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(str(value))).strip()


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
            return clean_inline(str(joke_data["joke"]))

        setup = clean_inline(str(joke_data["setup"]))
        delivery = clean_inline(str(joke_data["delivery"]))
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
    activity = clean_inline(str(activity_data["activity"]))
    activity_type = clean_inline(str(activity_data["type"])).lower().replace("_", " ")
    participants = int(activity_data["participants"])
    price = float(activity_data["price"])
    people = participants_label(participants)
    cost = price_label(price)
    return f"{activity} | {activity_type} | {people} | {cost}"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def child_text(element: ET.Element, name: str) -> str:
    for child in element:
        if local_name(child.tag) == name and child.text:
            return clean_inline(child.text)
    return ""


def child_link(element: ET.Element) -> str:
    for child in element:
        if local_name(child.tag) != "link":
            continue
        href = child.attrib.get("href")
        rel = child.attrib.get("rel", "alternate")
        if href and rel == "alternate":
            return href
        if child.text:
            return clean_inline(child.text)
    return ""


def parse_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        pass
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed


def feed_entries(root: ET.Element) -> list[ET.Element]:
    root_kind = local_name(root.tag)
    if root_kind == "feed":
        return [child for child in root if local_name(child.tag) == "entry"]

    for child in root:
        if local_name(child.tag) == "channel":
            return [entry for entry in child if local_name(entry.tag) == "item"]

    return [child for child in root if local_name(child.tag) in {"entry", "item"}]


def parse_feed_items(source: dict[str, str], feed_text: str) -> list[SignalItem]:
    root = ET.fromstring(feed_text)
    items: list[SignalItem] = []

    for entry in feed_entries(root):
        title = child_text(entry, "title")
        url = child_link(entry)
        published = (
            parse_date(child_text(entry, "pubDate"))
            or parse_date(child_text(entry, "published"))
            or parse_date(child_text(entry, "updated"))
        )
        if not title or not url:
            continue
        items.append(
            SignalItem(
                track=source["track"],
                source=source["source"],
                title=title,
                url=url,
                published=published,
            ),
        )

    return items


def fetch_signal_item(source: dict[str, str]) -> SignalItem:
    try:
        items = parse_feed_items(source, fetch_text(source["feed_url"]))
    except (ET.ParseError, requests.RequestException, ValueError):
        return SignalItem(
            track=source["track"],
            source=source["source"],
            title=f"{source['source']} feed temporarily unavailable",
            url=source["home_url"],
        )

    if items:
        return items[0]

    return SignalItem(
        track=source["track"],
        source=source["source"],
        title=f"Visit {source['source']}",
        url=source["home_url"],
    )


def markdown_escape(value: str) -> str:
    return clean_inline(value).replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")


def trim_title(title: str) -> str:
    title = clean_inline(title)
    if len(title) <= MAX_TITLE_LENGTH:
        return title
    return title[: MAX_TITLE_LENGTH - 3].rstrip() + "..."


def date_label(value: datetime | None) -> str:
    if not value:
        return ""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%b %d").replace(" 0", " ")


def build_signal_board(items: list[SignalItem]) -> str:
    lines = [
        "| Track | Fresh signal | Source |",
        "|---|---|---|",
    ]
    for item in items:
        title = markdown_escape(trim_title(item.title))
        track = markdown_escape(item.track)
        source = markdown_escape(item.source)
        label = date_label(item.published)
        dated_source = f"{source} · {label}" if label else source
        lines.append(f"| {track} | [{title}]({item.url}) | {dated_source} |")
    return "\n".join(lines)


def fetch_signal_board() -> str:
    return build_signal_board([fetch_signal_item(source) for source in SIGNAL_SOURCES])


def replace_marker(readme_text: str, pattern: re.Pattern[str], replacement: str) -> str:
    updated, count = pattern.subn(
        lambda match: f"{match.group(1)}{replacement}{match.group(2)}",
        readme_text,
        count=1,
    )
    if count != 1:
        raise RuntimeError("README marker not found or not unique")
    return updated


def update_readme_text(
    readme_text: str,
    joke: str,
    suggestion: str,
    signal_board: str,
) -> str:
    updated = replace_marker(readme_text, JOKE_PATTERN, joke)
    updated = replace_marker(updated, SUGGESTION_PATTERN, suggestion)
    return replace_marker(updated, SIGNALS_PATTERN, signal_board)


def main() -> None:
    joke = fetch_clean_joke()
    suggestion = fetch_suggestion()
    signal_board = fetch_signal_board()
    readme_text = README_PATH.read_text(encoding="utf-8")
    updated_text = update_readme_text(readme_text, joke, suggestion, signal_board)

    if updated_text != readme_text:
        README_PATH.write_text(updated_text, encoding="utf-8")


if __name__ == "__main__":
    main()
