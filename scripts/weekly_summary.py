import glob
import os
import subprocess
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - fallback for older Python
    ZoneInfo = None

LOG_DIR = "logs"
SUMMARY_DIR = "summaries"
SUMMARY_FILENAME = "weekly-summary.md"
DATE_FORMAT = "%Y-%m-%d"

SECTION_TITLES = [
    "Learning Today",
    "Code Written",
    "Problems Faced",
    "Solutions Discovered",
    "Plan for Tomorrow",
]


def _ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def _get_timezone() -> Optional[datetime.tzinfo]:
    tz_name = os.environ.get("DAILY_LOG_TIMEZONE", "").strip()
    if not tz_name or tz_name.upper() == "LOCAL":
        return None
    if ZoneInfo is None:
        return None
    try:
        return ZoneInfo(tz_name)
    except Exception:
        return None


def _now(tz: Optional[datetime.tzinfo]) -> datetime:
    return datetime.now(tz) if tz else datetime.now()


def _get_log_dir() -> str:
    return os.environ.get("DAILY_LOG_DIR", LOG_DIR)


def _get_summary_dir() -> str:
    return os.environ.get("DAILY_SUMMARY_DIR", SUMMARY_DIR)


def _get_week_range(now: datetime) -> Tuple[date, date]:
    end_date = now.date()
    start_date = end_date - timedelta(days=7)
    return start_date, end_date


def _get_weekly_logs(log_dir: str, start_date: date, end_date: date) -> List[str]:
    logs = glob.glob(os.path.join(log_dir, "*.md"))
    weekly_logs = []

    for log_path in logs:
        filename = os.path.basename(log_path)
        try:
            log_date = datetime.strptime(filename.replace(".md", ""), DATE_FORMAT).date()
        except ValueError:
            continue

        if start_date <= log_date <= end_date:
            weekly_logs.append(log_path)

    return sorted(weekly_logs)


def _extract_sections(content: str) -> Dict[str, str]:
    sections: Dict[str, List[str]] = {title: [] for title in SECTION_TITLES}
    current_title = None

    for line in content.splitlines():
        if line.startswith("#"):
            title = line.lstrip("#").strip()
            current_title = title if title in SECTION_TITLES else None
            continue

        if current_title:
            sections[current_title].append(line)

    result: Dict[str, str] = {}
    for title in SECTION_TITLES:
        block = "\n".join(sections[title]).strip()
        result[title] = block if block else "Not recorded"

    return result


def _collect_items(block: str) -> List[str]:
    if block == "Not recorded":
        return []

    lines = [line.strip() for line in block.splitlines() if line.strip()]
    bullets = [line[1:].strip() for line in lines if line.startswith("-")]
    if bullets:
        return bullets

    joined = " ".join(lines).strip()
    return [joined] if joined else []


def _git_commit_stats(start_date: date, end_date: date) -> Tuple[int, str]:
    since = start_date.strftime(DATE_FORMAT)
    until = (end_date + timedelta(days=1)).strftime(DATE_FORMAT)

    try:
        result = subprocess.run(
            ["git", "log", f"--since={since}", f"--until={until}", "--pretty=oneline"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return 0, "Git history not available"

        commits = [line for line in result.stdout.splitlines() if line.strip()]
        return len(commits), "OK"
    except OSError:
        return 0, "Git not available"


def _format_items(items: List[str]) -> str:
    cleaned = [item.strip() for item in items if item.strip()]
    if not cleaned:
        return "- Not recorded"
    return "\n".join(f"- {item}" for item in cleaned)


def generate_weekly_summary(
    log_dir: Optional[str] = None,
    summary_dir: Optional[str] = None,
    now: Optional[datetime] = None,
) -> str:
    log_dir = log_dir or _get_log_dir()
    summary_dir = summary_dir or _get_summary_dir()
    _ensure_dir(summary_dir)

    tz = _get_timezone()
    now = now or _now(tz)
    start_date, end_date = _get_week_range(now)

    weekly_logs = _get_weekly_logs(log_dir, start_date, end_date)
    if not weekly_logs:
        return "No logs found for this week. Cannot generate summary."

    learning_items: List[str] = []
    code_items: List[str] = []
    problem_items: List[str] = []
    solution_items: List[str] = []
    plan_items: List[str] = []

    for log in weekly_logs:
        with open(log, "r", encoding="utf-8") as f:
            content = f.read()

        sections = _extract_sections(content)
        learning_items.extend(_collect_items(sections["Learning Today"]))
        code_items.extend(_collect_items(sections["Code Written"]))
        problem_items.extend(_collect_items(sections["Problems Faced"]))
        solution_items.extend(_collect_items(sections["Solutions Discovered"]))
        plan_items.extend(_collect_items(sections["Plan for Tomorrow"]))

    learning_topic_count = len(learning_items)
    commit_count, commit_status = _git_commit_stats(start_date, end_date)
    num_logs = len(weekly_logs)

    productivity_score = min(100, (num_logs * 12) + (learning_topic_count * 4) + (commit_count * 2))

    summary = (
        f"# Weekly Development Summary - {end_date.strftime(DATE_FORMAT)}\n\n"
        "## Overview\n"
        f"- **Week of**: {start_date.strftime(DATE_FORMAT)} to {end_date.strftime(DATE_FORMAT)}\n"
        f"- **Total days logged**: {num_logs}\n"
        f"- **Total learning topics**: {learning_topic_count}\n"
        f"- **Commit count**: {commit_count} ({commit_status})\n"
        f"- **Weekly productivity score**: {productivity_score}/100\n\n"
        "## Total Learning Topics\n"
        f"{_format_items(learning_items)}\n\n"
        "## Projects Worked On\n"
        f"{_format_items(code_items)}\n\n"
        "## Challenges Faced\n"
        f"{_format_items(problem_items)}\n\n"
        "## Improvements Made\n"
        f"{_format_items(solution_items)}\n\n"
        "## Plans for Next Week\n"
        f"{_format_items(plan_items)}\n\n"
        "---\n"
        "*Generated by Weekly Summary Automation*\n"
    )

    summary_path = os.path.join(summary_dir, SUMMARY_FILENAME)
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)

    return f"Weekly summary generated: {summary_path}"


def main() -> int:
    try:
        result = generate_weekly_summary()
        print(result)
        return 0 if not result.startswith("No logs") else 1
    except OSError as exc:
        print(f"Error generating summary: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
