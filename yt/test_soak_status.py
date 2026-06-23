#!/usr/bin/env python3
"""Regression tests for soak health classification."""

import unittest
from datetime import datetime, timezone

from yt.soak_status import audit


def run(number: int, started_at: str, conclusion: str = "success") -> dict:
    return {
        "event": "schedule",
        "run_number": number,
        "status": "completed",
        "conclusion": conclusion,
        "run_started_at": started_at,
        "html_url": f"https://example.test/runs/{number}",
    }


class SoakStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.start = datetime(2026, 6, 23, 10, 45, 15, tzinfo=timezone.utc)
        self.end = datetime(2026, 6, 30, 10, 45, 15, tzinfo=timezone.utc)

    def test_delayed_successful_runs_are_warnings_not_failures(self) -> None:
        report = audit(
            [
                run(8, "2026-06-23T10:45:15Z"),
                run(9, "2026-06-23T13:48:06Z"),
            ],
            self.start,
            self.end,
            {},
            {},
        )
        self.assertEqual([], report["unhealthy_reasons"])
        self.assertTrue(report["warning_reasons"])

    def test_failed_scheduled_run_is_unhealthy(self) -> None:
        report = audit(
            [run(8, "2026-06-23T10:45:15Z", conclusion="failure")],
            self.start,
            self.end,
            {},
            {},
        )
        self.assertTrue(report["unhealthy_reasons"])


if __name__ == "__main__":
    unittest.main()
