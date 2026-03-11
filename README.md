# Daily Dev Log Automation System

[![Daily Log Automation](https://img.shields.io/badge/Daily%20Log-Automated-brightgreen)](https://github.com/yourusername/daily-dev-log/actions)
[![Weekly Summary](https://img.shields.io/badge/Weekly%20Summary-Automated-blue)](https://github.com/yourusername/daily-dev-log/actions)
[![Tests](https://github.com/yourusername/daily-dev-log/actions/workflows/tests.yml/badge.svg)](https://github.com/yourusername/daily-dev-log/actions/workflows/tests.yml)
[![Active Development](https://img.shields.io/github/commit-activity/m/yourusername/daily-dev-log)](https://github.com/yourusername/daily-dev-log/graphs/commit-activity)

A production-ready automation system designed to maintain a developer's daily learning and coding activity while automatically updating logs and committing them to GitHub.

## Project Overview

The Daily Dev Log Automation System helps developers maintain consistency by:
- Automatically generating structured daily logs.
- Capturing learning topics, code written, and problems solved.
- Summarizing weekly progress every Sunday.
- Keeping GitHub contributions consistent and meaningful.

## Project Structure

```text
Daily-Dev-Log
|
|-- logs/
|   |-- YYYY-MM-DD.md
|
|-- summaries/
|   |-- weekly-summary.md
|
|-- scripts/
|   |-- generate_daily_log.py
|   |-- weekly_summary.py
|
|-- .github/
|   |-- workflows/
|       |-- auto-daily-log.yml
|       |-- weekly-summary.yml
|
|-- README.md
|-- requirements.txt
```

## How Daily Automation Works

The `auto-daily-log.yml` workflow runs every day at 18:00 UTC and triggers `scripts/generate_daily_log.py`:
- Creates `logs/YYYY-MM-DD.md` if it does not exist.
- Appends a timestamped update if the file already exists.
- Ensures the log always contains the five required sections.
- Commits changes with `chore: update daily dev log`.

## How Weekly Summaries Work

The `weekly-summary.yml` workflow runs every Sunday at 20:00 UTC and triggers `scripts/weekly_summary.py`:
- Reads logs from the last 7 days.
- Extracts highlights for each section.
- Counts learning topics from bullet items.
- Calculates commit statistics for the week.
- Produces a weekly productivity score.
- Writes `summaries/weekly-summary.md` and commits it.

## Configuration

Optional environment variables:
- `DAILY_LOG_TIMEZONE`: IANA timezone for timestamps (example: `Asia/Kolkata`, `UTC`). Use `LOCAL` or leave unset to use system local time.
- `DAILY_LOG_DIR`: Override the log directory (default: `logs`).
- `DAILY_SUMMARY_DIR`: Override the summary directory (default: `summaries`).

Note: On Windows, IANA timezones may require Python 3.9+ with timezone data available. If the timezone is invalid or not available, the scripts fall back to local time.

## Running Scripts Locally

```bash
# Generate or update today's log
python scripts/generate_daily_log.py "Learning topic" "Code update" "Problem" "Solution" "Plan"

# Generate weekly summary
python scripts/weekly_summary.py
```

## Running Tests

```bash
python -m unittest discover -s tests
```

## GitHub Actions Automation

1. Clone the repository and push it to your GitHub account.
2. Update the badge links in this README to match your `owner/repo`.
3. Enable GitHub Actions in the repository settings if required.
4. The workflows will run on schedule and commit updates automatically.

## Contributor Guide

Contributions are welcome.
- Keep code style clean and documented.
- Prefer small, focused changes.
- Add tests if you introduce complex logic.

## Notes

- This project uses only Python standard library modules.
- Replace `yourusername/daily-dev-log` in badges with your GitHub repo.
