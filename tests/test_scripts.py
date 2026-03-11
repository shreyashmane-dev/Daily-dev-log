import os
import sys
import unittest
from datetime import datetime
from unittest.mock import patch

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_SANDBOX = os.path.join(ROOT, "tests", "_sandbox_logs")
SUMMARY_SANDBOX = os.path.join(ROOT, "tests", "_sandbox_summaries")

sys.path.insert(0, ROOT)

from scripts import generate_daily_log as daily
from scripts import weekly_summary as weekly


class DailyLogTests(unittest.TestCase):
    def setUp(self) -> None:
        _clean_dir(LOG_SANDBOX)

    def test_create_log(self) -> None:
        now = datetime(2026, 3, 11, 10, 0, 0)
        entries = ["Learned testing", "Wrote parser", "Bug in parser", "Fixed parsing", "Write docs"]

        result = daily.generate_daily_log(entries, now=now, log_dir=LOG_SANDBOX)
        self.assertIn("Daily log created", result)

        path = os.path.join(LOG_SANDBOX, "2026-03-11.md")
        self.assertTrue(os.path.exists(path))

        content = _read(path)
        self.assertIn("# Daily Development Log - 2026-03-11", content)
        self.assertIn("## Learning Today", content)
        self.assertIn("## Code Written", content)
        self.assertIn("## Problems Faced", content)
        self.assertIn("## Solutions Discovered", content)
        self.assertIn("## Plan for Tomorrow", content)

    def test_append_update(self) -> None:
        first = datetime(2026, 3, 11, 9, 0, 0)
        second = datetime(2026, 3, 11, 11, 30, 0)

        daily.generate_daily_log(["A", "B", "C", "D", "E"], now=first, log_dir=LOG_SANDBOX)
        daily.generate_daily_log(["F", "G", "H", "I", "J"], now=second, log_dir=LOG_SANDBOX)

        path = os.path.join(LOG_SANDBOX, "2026-03-11.md")
        content = _read(path)
        self.assertIn("### Update - 2026-03-11 11:30:00", content)


class WeeklySummaryTests(unittest.TestCase):
    def setUp(self) -> None:
        _clean_dir(LOG_SANDBOX)
        _clean_dir(SUMMARY_SANDBOX)

    def test_weekly_summary_counts_learning_topics(self) -> None:
        log_content = (
            "# Daily Development Log - 2026-03-10\n\n"
            "## Learning Today\n"
            "- Topic A\n"
            "- Topic B\n\n"
            "## Code Written\n"
            "- Project X\n\n"
            "## Problems Faced\n"
            "- Bug Y\n\n"
            "## Solutions Discovered\n"
            "- Fix Z\n\n"
            "## Plan for Tomorrow\n"
            "- Next step\n\n"
            "---\n"
            "*Last update: 2026-03-10 09:00:00*\n"
        )

        _write(os.path.join(LOG_SANDBOX, "2026-03-10.md"), log_content)
        now = datetime(2026, 3, 11, 12, 0, 0)

        with patch("scripts.weekly_summary.subprocess.run") as mocked:
            mocked.return_value.returncode = 1
            mocked.return_value.stdout = ""

            result = weekly.generate_weekly_summary(
                log_dir=LOG_SANDBOX,
                summary_dir=SUMMARY_SANDBOX,
                now=now,
            )

        self.assertIn("Weekly summary generated", result)

        summary_path = os.path.join(SUMMARY_SANDBOX, "weekly-summary.md")
        content = _read(summary_path)
        self.assertIn("**Total learning topics**: 2", content)
        self.assertIn("- Topic A", content)
        self.assertIn("- Topic B", content)


def _clean_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)
    for name in os.listdir(path):
        full = os.path.join(path, name)
        if os.path.isfile(full):
            os.remove(full)


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _write(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    unittest.main()
