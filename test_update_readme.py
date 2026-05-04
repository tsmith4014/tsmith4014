import unittest

from update_readme import (
    JOKE_PATTERN,
    SUGGESTION_PATTERN,
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
        )
        updated = update_readme_text(readme, "new joke", "new suggestion")
        self.assertIn("⚡ AI Joke of the Day: 🤖 new joke 🤖", updated)
        self.assertIn("⚡ AI Suggestion of the Day: 🤖 new suggestion 🤖", updated)

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
