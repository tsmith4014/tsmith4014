import unittest

from update_readme import (
    JOKE_PATTERN,
    SUGGESTION_PATTERN,
    SIGNALS_PATTERN,
    SignalItem,
    build_signal_board,
    parse_feed_items,
    participants_label,
    price_label,
    replace_marker,
    update_readme_text,
)


class UpdateReadmeTests(unittest.TestCase):
    def test_replace_marker_updates_exactly_one_match(self) -> None:
        readme = "⚡ AI Joke of the Day: 🤖 old 🤖"
        updated = replace_marker(readme, JOKE_PATTERN, "new")
        self.assertEqual(updated, "⚡ AI Joke of the Day: 🤖 new 🤖")

    def test_replace_marker_requires_unique_marker(self) -> None:
        readme = "missing marker"
        with self.assertRaisesRegex(RuntimeError, "marker not found or not unique"):
            replace_marker(readme, JOKE_PATTERN, "new")

    def test_update_readme_text_updates_both_dynamic_sections(self) -> None:
        readme = (
            "⚡ AI Joke of the Day: 🤖 old joke 🤖\n"
            "⚡ AI Suggestion of the Day: 🤖 old suggestion 🤖\n"
            "<!-- SIGNALS:START -->\nold signals\n<!-- SIGNALS:END -->\n"
        )
        updated = update_readme_text(readme, "new joke", "new suggestion", "new signals")
        self.assertIn("⚡ AI Joke of the Day: 🤖 new joke 🤖", updated)
        self.assertIn("⚡ AI Suggestion of the Day: 🤖 new suggestion 🤖", updated)
        self.assertIn("<!-- SIGNALS:START -->\nnew signals\n<!-- SIGNALS:END -->", updated)

    def test_signal_board_renders_markdown_table(self) -> None:
        board = build_signal_board(
            [
                SignalItem(
                    track="AI practice",
                    source="Example Source",
                    title="Useful [signal] with | characters",
                    url="https://example.com/item",
                ),
            ],
        )
        self.assertIn("| Track | Fresh signal | Source |", board)
        self.assertIn(
            "[Useful \\[signal\\] with \\| characters](https://example.com/item)",
            board,
        )

    def test_signal_marker_updates_exactly_one_section(self) -> None:
        readme = "<!-- SIGNALS:START -->\nold\n<!-- SIGNALS:END -->"
        updated = replace_marker(readme, SIGNALS_PATTERN, "new")
        self.assertEqual(updated, "<!-- SIGNALS:START -->\nnew\n<!-- SIGNALS:END -->")

    def test_parse_feed_items_supports_rss(self) -> None:
        feed = """
        <rss version="2.0">
          <channel>
            <item>
              <title>Kernel prepatch</title>
              <link>https://example.com/kernel</link>
              <pubDate>Mon, 25 May 2026 05:05:04 +0000</pubDate>
            </item>
          </channel>
        </rss>
        """
        items = parse_feed_items(
            {"track": "Systems", "source": "Example", "home_url": "https://example.com"},
            feed,
        )
        self.assertEqual(items[0].title, "Kernel prepatch")
        self.assertEqual(items[0].url, "https://example.com/kernel")

    def test_parse_feed_items_supports_atom(self) -> None:
        feed = """
        <feed xmlns="http://www.w3.org/2005/Atom">
          <entry>
            <title>Agent release</title>
            <link href="https://example.com/agent" rel="alternate"/>
            <updated>2026-05-25T05:05:04+00:00</updated>
          </entry>
        </feed>
        """
        items = parse_feed_items(
            {"track": "AI practice", "source": "Example", "home_url": "https://example.com"},
            feed,
        )
        self.assertEqual(items[0].title, "Agent release")
        self.assertEqual(items[0].url, "https://example.com/agent")

    def test_participants_label_matches_activity_count(self) -> None:
        self.assertEqual(participants_label(0), "solo")
        self.assertEqual(participants_label(1), "solo")
        self.assertEqual(participants_label(2), "two-person")
        self.assertEqual(participants_label(4), "small group")
        self.assertEqual(participants_label(8), "group")

    def test_price_label_buckets_cost(self) -> None:
        self.assertEqual(price_label(0), "free")
        self.assertEqual(price_label(0.1), "low cost")
        self.assertEqual(price_label(0.3), "paid")
        self.assertEqual(price_label(0.8), "splurge")


if __name__ == "__main__":
    unittest.main()
