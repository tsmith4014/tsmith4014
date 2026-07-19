from __future__ import annotations

import re
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path

README_PATH = Path(__file__).with_name("README.md")
REQUEST_TIMEOUT = 15
MAX_TITLE_LENGTH = 110
REQUEST_HEADERS = {
    "User-Agent": "tsmith4014-profile-readme/1.0 (+https://github.com/tsmith4014/tsmith4014)",
}

TRACK_SOURCES = (
    {
        "track": "AI practice",
        "sources": (
            {
                "source": "Simon Willison",
                "feed_url": "https://simonwillison.net/atom/everything/",
                "home_url": "https://simonwillison.net/",
            },
            {
                "source": "OpenAI Developers",
                "feed_url": "https://developers.openai.com/rss.xml",
                "home_url": "https://developers.openai.com/",
            },
        ),
    },
    {
        "track": "AI research",
        "sources": (
            {
                "source": "arXiv cs.AI",
                "feed_url": "https://rss.arxiv.org/rss/cs.AI",
                "home_url": "https://arxiv.org/list/cs.AI/recent",
            },
            {
                "source": "arXiv cs.LG",
                "feed_url": "https://rss.arxiv.org/rss/cs.LG",
                "home_url": "https://arxiv.org/list/cs.LG/recent",
            },
        ),
    },
    {
        "track": "Systems",
        "sources": (
            {
                "source": "LWN.net",
                "feed_url": "https://lwn.net/headlines/rss",
                "home_url": "https://lwn.net/",
            },
            {
                "source": "Brendan Gregg",
                "feed_url": "https://www.brendangregg.com/blog/rss.xml",
                "home_url": "https://www.brendangregg.com/blog/",
            },
        ),
    },
    {
        "track": "Architecture",
        "sources": (
            {
                "source": "Martin Fowler",
                "feed_url": "https://martinfowler.com/feed.atom",
                "home_url": "https://martinfowler.com/",
            },
            {
                "source": "InfoQ",
                "feed_url": "https://feed.infoq.com",
                "home_url": "https://www.infoq.com/",
            },
        ),
    },
    {
        "track": "Edge & cloud",
        "sources": (
            {
                "source": "Cloudflare Blog",
                "feed_url": "https://blog.cloudflare.com/rss/",
                "home_url": "https://blog.cloudflare.com/",
            },
            {
                "source": "AWS What's New",
                "feed_url": "https://aws.amazon.com/about-aws/whats-new/recent/feed/",
                "home_url": "https://aws.amazon.com/about-aws/whats-new/",
            },
        ),
    },
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


def fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers=REQUEST_HEADERS)
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
        return response.read().decode("utf-8", errors="replace")


def clean_inline(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(str(value))).strip()


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


def parse_feed_items(track: str, source_name: str, feed_text: str) -> list[SignalItem]:
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
                track=track,
                source=source_name,
                title=title,
                url=url,
                published=published,
            ),
        )

    return items


def fetch_signal_item(track: str, source: dict[str, str]) -> SignalItem:
    try:
        items = parse_feed_items(track, source["source"], fetch_text(source["feed_url"]))
    except (ET.ParseError, OSError, ValueError):
        return SignalItem(
            track=track,
            source=source["source"],
            title=f"{source['source']} feed temporarily unavailable",
            url=source["home_url"],
        )

    if items:
        return items[0]

    return SignalItem(
        track=track,
        source=source["source"],
        title=f"Visit {source['source']}",
        url=source["home_url"],
    )


def normalize_timestamp(value: datetime | None) -> datetime:
    if value is None:
        return datetime.min.replace(tzinfo=timezone.utc)
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def select_track_item(items: list[SignalItem]) -> SignalItem:
    with_dates = [item for item in items if item.published is not None]
    if with_dates:
        return max(with_dates, key=lambda item: normalize_timestamp(item.published))
    return items[0]


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
    selected_items: list[SignalItem] = []
    for track_spec in TRACK_SOURCES:
        track = track_spec["track"]
        candidates = [
            fetch_signal_item(track, source_spec) for source_spec in track_spec["sources"]
        ]
        selected_items.append(select_track_item(candidates))
    return build_signal_board(selected_items)


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
    signal_board: str,
) -> str:
    return replace_marker(readme_text, SIGNALS_PATTERN, signal_board)


def main() -> None:
    signal_board = fetch_signal_board()
    readme_text = README_PATH.read_text(encoding="utf-8")
    updated_text = update_readme_text(readme_text, signal_board)

    if updated_text != readme_text:
        README_PATH.write_text(updated_text, encoding="utf-8")


if __name__ == "__main__":
    main()
