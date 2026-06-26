import json
from pathlib import Path

from django.test import TestCase

from .analytics import analyze

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "whatsapp_sample.txt"

EXPECTED_KEYS = {
    "summary",
    "per_user",
    "peak_hours",
    "frequency",
    "sentiment",
    "top_influencers",
    "spam_flags",
}


class AnalyzeTests(TestCase):
    def setUp(self):
        with open(FIXTURE_PATH, encoding="utf-8") as f:
            self.results = analyze(f)

    def test_all_top_level_keys_present(self):
        self.assertEqual(set(self.results.keys()), EXPECTED_KEYS)

    def test_summary_shape(self):
        summary = self.results["summary"]
        self.assertIn("date_range", summary)
        self.assertIn("first", summary["date_range"])
        self.assertIn("last", summary["date_range"])
        self.assertGreater(summary["total_messages"], 0)

    def test_peak_hours_has_24_entries(self):
        self.assertEqual(len(self.results["peak_hours"]), 24)
        self.assertEqual({"hour", "count"}, set(self.results["peak_hours"][0].keys()))

    def test_per_user_is_list_of_dicts(self):
        per_user = self.results["per_user"]
        self.assertIsInstance(per_user, list)
        self.assertTrue(per_user)
        self.assertEqual({"name", "messages", "media", "avg_sentiment"}, set(per_user[0].keys()))

    def test_top_influencers_is_flat_name_list(self):
        names = self.results["top_influencers"]
        self.assertIsInstance(names, list)
        self.assertTrue(all(isinstance(n, str) for n in names))
        self.assertLessEqual(len(names), 5)

    def test_sentiment_fractions_sum_to_one(self):
        sentiment = self.results["sentiment"]
        self.assertAlmostEqual(sum(sentiment.values()), 1.0, places=4)

    def test_frequency_lists_have_expected_keys(self):
        freq = self.results["frequency"]
        self.assertEqual({"date", "count"}, set(freq["daily"][0].keys()))
        self.assertEqual({"iso_week", "count"}, set(freq["weekly"][0].keys()))

    def test_spam_flags_is_list_of_dicts_with_reason(self):
        for flag in self.results["spam_flags"]:
            self.assertEqual({"sender", "reason", "examples"}, set(flag.keys()))
            self.assertEqual(flag["reason"], "high_volume_burst")

    def test_results_are_json_serializable(self):
        json.dumps(self.results)
