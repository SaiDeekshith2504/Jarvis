"""
modules/morning_briefing.py
-----------------------------
Intelligent morning briefing module for Jarvis — Day 7.

Assembles a rich summary from:
  - Current date & time
  - User's name (from user.json)
  - Live weather (OpenWeatherMap)
  - Today's calendar events (Google Calendar)
  - Pending todos & reminders
  - Focus task (today's top todo)
  - Motivational message

The briefing is:
  - Printed to the terminal in a formatted block
  - Spoken via TTS if voice mode is active
  - Sent as a desktop toast notification
  - Logged to command_logs.json

Public API:
    generate_briefing(speak_fn, source)  -> full briefing string
    run_morning_briefing(speak_fn)       -> generates + displays + notifies
"""

from __future__ import annotations

import datetime
import json
import os
import random

import config
from core import user_profile as profile_engine
from core import reminders as rem_engine
from modules import weather_module, calendar_module, notification_module, logger_module


def _load_todos() -> list[dict]:
    """Reads todos.json; returns [] if missing or corrupt."""
    try:
        with open(config.TODOS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [t for t in data if isinstance(data, list)] if isinstance(data, list) else []
    except Exception:
        return []


def generate_briefing(speak_fn=None, source: str = "text") -> str:
    """
    Builds and returns the full morning briefing as a formatted string.

    Also fires a desktop notification and speaks the TTS summary if requested.
    """
    now  = datetime.datetime.now()
    hour = now.hour

    # Greeting by time of day
    if hour < 12:
        tod = "Good morning"
    elif hour < 17:
        tod = "Good afternoon"
    elif hour < 21:
        tod = "Good evening"
    else:
        tod = "Good night"

    name      = profile_engine.get_name() or ""
    date_str  = now.strftime("%A, %B %d, %Y")
    time_str  = now.strftime("%I:%M %p")
    greeting  = f"{tod}, {name}!" if name else f"{tod}!"

    lines = [
        "=" * 60,
        f"  JARVIS MORNING BRIEFING — {config.VERSION}",
        "=" * 60,
        f"  {greeting}",
        f"  {date_str}  |  {time_str}",
        "",
    ]

    # ── Weather ───────────────────────────────────────────────────────────────
    weather_data   = weather_module.get_weather()
    weather_line   = weather_module.format_weather(weather_data)
    weather_spoken = ""

    if "error" not in weather_data:
        weather_spoken = (
            f"The weather in {weather_data['city']} is "
            f"{weather_data['temp']} degrees with {weather_data['description']}."
        )
        lines.append(f"  Weather    : {weather_line}")
    else:
        lines.append(f"  Weather    : {weather_data['error'].splitlines()[0]}")

    # ── Calendar events ───────────────────────────────────────────────────────
    events, cal_err = calendar_module.get_todays_events()
    cal_spoken      = ""

    if cal_err:
        lines.append(f"  Calendar   : {cal_err.strip().splitlines()[0]}")
        cal_spoken = "Google Calendar is not configured yet."
    elif events:
        lines.append(f"  Calendar   : {len(events)} event(s) today")
        for e in events[:3]:
            loc = f" @ {e['location']}" if e["location"] else ""
            lines.append(f"    [{e['start']}] {e['title']}{loc}")
        if len(events) > 3:
            lines.append(f"    ... and {len(events) - 3} more. Type 'calendar' to see all.")
        cal_spoken = (
            f"You have {len(events)} calendar event{'s' if len(events) > 1 else ''} today."
        )
    else:
        lines.append("  Calendar   : No events today.")
        cal_spoken = "You have no calendar events today."

    # ── Todos ─────────────────────────────────────────────────────────────────
    todos   = _load_todos()
    pending = [t for t in todos if not t.get("done")]
    done    = [t for t in todos if t.get("done")]

    lines.append("")
    if pending:
        lines.append(f"  Todos      : {len(pending)} pending  |  {len(done)} done")
        for t in pending[:3]:
            lines.append(f"    [ ] {t['task']}")
        if len(pending) > 3:
            lines.append(f"    ... and {len(pending) - 3} more. Type 'list todos'.")
    else:
        lines.append("  Todos      : All clear! No pending todos.")

    # ── Focus task (top pending todo) ─────────────────────────────────────────
    focus_spoken = ""
    if pending:
        focus_task = pending[0]["task"]
        lines.append(f"\n  Top Focus  : {focus_task}")
        focus_spoken = f"Your top focus task is: {focus_task}."

    # ── Reminders ─────────────────────────────────────────────────────────────
    all_reminders     = rem_engine._load_reminders()
    pending_reminders = [r for r in all_reminders if r.get("status") == "pending"]

    if pending_reminders:
        lines.append(f"\n  Reminders  : {len(pending_reminders)} pending")
        for r in pending_reminders[:3]:
            lines.append(f"    [{r['time']}]  {r['task']}")
    else:
        lines.append("\n  Reminders  : None scheduled.")

    # ── Motivational message ──────────────────────────────────────────────────
    motivation = random.choice(config.MORNING_MESSAGES)
    lines.append("")
    lines.append(f"  Tip        : {motivation}")
    lines.append("\n  Type 'help' to see all commands.")
    lines.append("=" * 60)

    briefing_text = "\n".join(lines)

    # ── TTS summary (short version for voice) ─────────────────────────────────
    tts_summary = " ".join(filter(None, [
        greeting,
        weather_spoken,
        cal_spoken,
        focus_spoken,
    ]))

    if speak_fn and tts_summary:
        speak_fn(tts_summary)

    # ── Desktop notification ──────────────────────────────────────────────────
    notif_body = f"{cal_spoken} {weather_spoken}".strip()
    notification_module.notify_morning_briefing(name, notif_body)

    # ── Check for calendar events due very soon ───────────────────────────────
    if events:
        due_soon = calendar_module.events_due_soon(events, within_minutes=15)
        for e in due_soon:
            notification_module.notify_calendar_event(e["title"], e["start"])
            if speak_fn:
                speak_fn(f"Heads up! Your event '{e['title']}' starts at {e['start']}.")

    # ── Log to command analytics ──────────────────────────────────────────────
    logger_module.log_command(
        command="morning_briefing",
        full_input="morning briefing",
        response=tts_summary or "Briefing generated.",
        status="success",
        source=source,
    )

    return briefing_text


def run_morning_briefing(speak_fn=None, source: str = "text") -> str:
    """Generates the briefing, prints it, and returns the text."""
    text = generate_briefing(speak_fn=speak_fn, source=source)
    print(text)
    return text
