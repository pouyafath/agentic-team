"""Tests for scripts/metrics.py. Run: python3 -m unittest discover -s scripts/tests"""
import json
import os
import sys
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import metrics  # noqa: E402

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "sample.json")


class Metrics(unittest.TestCase):
    def setUp(self):
        with open(FIXTURE, encoding="utf-8") as f:
            self.m = metrics.compute(json.load(f), now=datetime(2026, 10, 15, tzinfo=timezone.utc))

    def test_productivity(self):
        p = self.m["productivity"]
        self.assertEqual(p["stories_started"], 3)
        self.assertEqual(p["stories_done"], 2)
        self.assertEqual(p["median_lead_time_h"], 48.0)       # 24h and 72h
        self.assertEqual(p["median_pr_cycle_time_h"], 28.0)   # 8h and 48h

    def test_quality(self):
        q = self.m["quality"]
        self.assertEqual(q["first_pass_yield"], 0.5)           # story 1 only
        self.assertEqual(q["defects_caught_before_merge"], 2)  # QA FAIL on #2 + review reject on #3
        self.assertEqual(q["escaped_defects"], 1)              # production bug, not the QA one
        self.assertEqual(q["change_failure_rate"], 1.0)        # 1 prod bug / 1 published release

    def test_coordination_and_cost(self):
        c = self.m["coordination"]
        self.assertEqual(c["mean_rework_cycles"], 1.5)
        self.assertEqual(c["max_rework_cycles"], 3)
        self.assertEqual(c["stories_escalated"], 1)
        self.assertEqual(self.m["cost"]["cost_per_done_story_usd"], 3.5)
        self.assertEqual(self.m["delivery"]["production_releases"], 1)

    def test_since_filter_and_render(self):
        with open(FIXTURE, encoding="utf-8") as f:
            m = metrics.compute(json.load(f), since="2026-10-06", now=datetime(2026, 10, 15, tzinfo=timezone.utc))
        self.assertEqual(m["productivity"]["stories_started"], 1)
        self.assertIn("| 1 | risk:1 | ✓ |", metrics.render(self.m))


if __name__ == "__main__":
    unittest.main()
