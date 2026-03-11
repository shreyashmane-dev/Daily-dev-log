import os
import sys
from datetime import datetime
from typing import List, Optional

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - fallback for older Python
    ZoneInfo = None

LOG_DIR = "logs"
DATE_FORMAT = "%Y-%m-%d"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

DEFAULT_ENTRY = "No entry"


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


def _render_sections(learning: str, code: str, problems: str, solutions: str, plan: str, heading_level: int) -> str:
    h = "#" * heading_level
    return (
        f"{h} Learning Today\n"
        f"- {learning}\n\n"
        f"{h} Code Written\n"
        f"- {code}\n\n"
        f"{h} Problems Faced\n"
        f"- {problems}\n\n"
        f"{h} Solutions Discovered\n"
        f"- {solutions}\n\n"
        f"{h} Plan for Tomorrow\n"
        f"- {plan}\n"
    )


def _render_new_log(date_str: str, timestamp: str, entries: List[str]) -> str:
    learning, code, problems, solutions, plan = entries
    return (
        f"# Daily Development Log - {date_str}\n\n"
        + _render_sections(learning, code, problems, solutions, plan, 2)
        + "\n---\n"
        + f"*Last update: {timestamp}*\n"
    )


def _render_update(timestamp: str, entries: List[str]) -> str:
    learning, code, problems, solutions, plan = entries
    return (
        f"### Update - {timestamp}\n\n"
        + _render_sections(learning, code, problems, solutions, plan, 4)
        + "\n---\n"
        + f"*Last update: {timestamp}*\n"
    )


def _normalize_args(args: List[str]) -> List[str]:
    normalized = [a.strip() for a in args]
    while len(normalized) < 5:
        normalized.append(DEFAULT_ENTRY)
    return normalized[:5]


def generate_daily_log(entries: List[str], now: Optional[datetime] = None, log_dir: Optional[str] = None) -> str:
    log_dir = log_dir or _get_log_dir()
    _ensure_dir(log_dir)

    tz = _get_timezone()
    now = now or _now(tz)
    date_str = now.strftime(DATE_FORMAT)
    timestamp = now.strftime(TIMESTAMP_FORMAT)
    filename = os.path.join(log_dir, f"{date_str}.md")

    try:
        if not os.path.exists(filename):
            content = _render_new_log(date_str, timestamp, entries)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Daily log created: {filename}"

        update = _render_update(timestamp, entries)
        with open(filename, "a", encoding="utf-8") as f:
            f.write("\n\n" + update)
        return f"Daily log updated: {filename}"
    except OSError as exc:
        return f"Error writing daily log: {exc}"


def main() -> int:
    # Usage: python scripts/generate_daily_log.py "Learning" "Code" "Problems" "Solutions" "Plan"
    args = _normalize_args(sys.argv[1:])
    result = generate_daily_log(args)
    print(result)
    return 0 if not result.startswith("Error") else 1


if __name__ == "__main__":
    raise SystemExit(main())
