import json
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from django.contrib.auth import get_user_model
from django.core.files import File
from django.test import TestCase
from django.urls import reverse

from .analytics import analyze, compute_top_influencers
from .models import ChatAnalysis, ChatExport

User = get_user_model()

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


class ComputeTopInfluencersTests(TestCase):
    def test_ranks_engagement_triggered_over_raw_message_count(self):
        base = datetime(2026, 1, 1, 9, 0, 0)
        rows = [
            {"timestamp": base, "sender": "Alice", "is_system": False},
            {"timestamp": base + timedelta(minutes=1), "sender": "Bob", "is_system": False},
            {"timestamp": base + timedelta(minutes=2), "sender": "Carol", "is_system": False},
            {"timestamp": base + timedelta(minutes=3), "sender": "Dave", "is_system": False},
        ]
        # Eve fires off 10 messages back-to-back an hour later; nobody replies.
        rows += [
            {"timestamp": base + timedelta(hours=1, seconds=i), "sender": "Eve", "is_system": False}
            for i in range(10)
        ]
        df = pd.DataFrame(rows)

        top = compute_top_influencers(df)

        self.assertEqual(top[0], "Alice")
        self.assertLess(top.index("Alice"), top.index("Eve"))


class DashboardChartsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        self.client.force_login(self.user)

    def test_dashboard_without_analysis_skips_charts(self):
        response = self.client.get(reverse("whatsapp:dashboard"))

        self.assertNotContains(response, "peakHoursChart")

    def test_dashboard_renders_chart_canvases_and_data(self):
        with open(FIXTURE_PATH, "rb") as f:
            chat_export = ChatExport.objects.create(
                file=File(f, name="whatsapp_sample.txt"), uploaded_by=self.user
            )
            f.seek(0)
            results = analyze(f)
        ChatAnalysis.objects.create(chat_export=chat_export, results=results)

        response = self.client.get(reverse("whatsapp:dashboard"))

        self.assertContains(response, '<canvas id="peakHoursChart">')
        self.assertContains(response, '<canvas id="dailyFrequencyChart">')
        self.assertContains(response, '<canvas id="sentimentChart">')
        self.assertContains(response, "chart.js")
        self.assertContains(response, '<script id="peak-hours-data" type="application/json">')
