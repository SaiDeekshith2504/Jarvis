"""
core/reminders.py
-----------------
Reminder engine for Jarvis — Day 4.

Provides:
  add_reminder(task, time_str)  → parse & store a new reminder
  list_reminders()              → formatted string of pending reminders
  check_reminders()             → check for due/overdue; return alert string
  clear_reminder(index)         → mark a reminder done by 1-based index
  _load_reminders()             → read reminders.json
  _save_reminders(data)         → write reminders.json

Time formats accepted (flexible parsing):
  "08:30"               → today at 08:30
  "2026-06-19 08:30"    → absolute datetime
  "tomorrow 09:00"      → tomorrow at 09:00
  "in 10 minutes"       → relative offset
  "in 2 hours"          → relative offset
"""

from __future__ import annotations

import datetime
import json
import os
import re

import config


# ─── File helpers ─────────────────────────────────────────────────────────────

def _load_reminders() -> list[dict]:
    """Reads reminders.json; returns [] if missing or corrupt."""
    if not os.path.exists(config.REMINDERS_FILE):
        return []
    try:
        with open(config.REMINDERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_reminders(reminders: list[dict]) -> None:
    """Writes reminders list back to reminders.json."""
    os.makedirs(os.path.dirname(config.REMINDERS_FILE), exist_ok=True)
    with open(config.REMINDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(reminders, f, indent=2, ensure_ascii=False)


# ─── Time parser ──────────────────────────────────────────────────────────────

def _parse_time(time_str: str) -> datetime.datetime | None:
    """
    Attempts to parse a flexible time string into a datetime object.
    Returns None if parsing fails.
    """
    time_str = time_str.strip().lower()
    now = datetime.datetime.now()

    # "in X minutes" / "in X hours"
    m = re.match(r"in\s+(\d+)\s+(minute|minutes|hour|hours)", time_str)
    if m:
        amount = int(m.group(1))
        unit   = m.group(2)
        delta  = datetime.timedelta(minutes=amount) if "minute" in unit else datetime.timedelta(hours=amount)
        return now + delta

    # "tomorrow HH:MM"
    m = re.match(r"tomorrow\s+(\d{1,2}:\d{2}(?::\d{2})?)", time_str)
    if m:
        t = datetime.datetime.strptime(m.group(1)[:5], "%H:%M")
        target = now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
        return target + datetime.timedelta(days=1)

    # Absolute "YYYY-MM-DD HH:MM"
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.datetime.strptime(time_str, fmt)
        except ValueError:
            pass

    # Time-only "HH:MM" → assume today
    m = re.match(r"(\d{1,2}):(\d{2})", time_str)
    if m:
        hour, minute = int(m.group(1)), int(m.group(2))
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        # If that time has already passed today, schedule for tomorrow
        if target <= now:
            target += datetime.timedelta(days=1)
        return target

    return None


# ─── Public API ───────────────────────────────────────────────────────────────

def add_reminder(task: str, time_str: str) -> str:
    """
    Parses time_str and stores a new reminder.
    Returns a confirmation string or an error message.
    """
    if not task.strip():
        return "Please provide a task description."

    dt = _parse_time(time_str)
    if dt is None:
        return (
            f"I couldn't understand the time '{time_str}'.\n"
            "  Try: remind me 08:30 <task>  |  remind me 2026-06-20 09:00 <task>\n"
            "       remind me tomorrow 08:00 <task>  |  remind me in 30 minutes <task>"
        )

    reminders = _load_reminders()
    entry = {
        "id":      len(reminders) + 1,
        "task":    task.strip(),
        "time":    dt.strftime("%Y-%m-%d %H:%M"),
        "status":  "pending",
        "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    reminders.append(entry)
    _save_reminders(reminders)

    friendly = dt.strftime("%A, %B %d at %I:%M %p")
    return f"Reminder set for {friendly}: {task.strip()} ⏰"


def list_reminders() -> str:
    """Returns a formatted string of all pending reminders."""
    reminders = _load_reminders()
    pending = [r for r in reminders if r["status"] == "pending"]

    if not pending:
        return "No pending reminders. Use 'remind me <time> <task>' to add one."

    lines = [f"── Pending Reminders ({len(pending)}) ──────────────────────────"]
    for r in pending:
        dt_str = r["time"]
        lines.append(f"  [{r['id']}] {dt_str}  →  {r['task']}")
    lines.append("\n  Use 'clear reminder <#>' to dismiss one.")
    return "\n".join(lines)


def check_reminders() -> str | None:
    """
    Checks all pending reminders against the current time.
    Returns an alert string if any are due or overdue, else None.
    Marks due reminders as 'done'.
    """
    reminders = _load_reminders()
    now       = datetime.datetime.now()
    alerts    = []
    changed   = False

    for r in reminders:
        if r["status"] != "pending":
            continue
        try:
            due = datetime.datetime.strptime(r["time"], "%Y-%m-%d %H:%M")
        except ValueError:
            continue

        if due <= now:
            alerts.append(f"  🔔 REMINDER #{r['id']}: {r['task']}  (was due {r['time']})")
            r["status"] = "done"
            changed = True

    if changed:
        _save_reminders(reminders)

    if alerts:
        header = "── ⚠️  Due Reminders ─────────────────────────────────────"
        return header + "\n" + "\n".join(alerts)
    return None


def clear_reminder(index_str: str) -> str:
    """
    Marks a reminder as done by its ID (1-based).
    Usage: clear reminder <#>
    """
    if not index_str.strip().isdigit():
        return "Please provide a reminder number. Usage: clear reminder <#>"

    idx       = int(index_str.strip())
    reminders = _load_reminders()

    for r in reminders:
        if r["id"] == idx:
            if r["status"] == "done":
                return f"Reminder #{idx} is already cleared."
            r["status"] = "done"
            _save_reminders(reminders)
            return f"Reminder #{idx} cleared: '{r['task']}' ✓"

    return f"No reminder with #{idx}. Use 'list reminders' to see all."
