"""
modules/calendar_module.py
---------------------------
Google Calendar integration for Jarvis — Day 7.

Reads today's events using the Google Calendar API (read-only).

Setup (one-time):
    1. Go to https://console.cloud.google.com/
    2. Create a project → Enable "Google Calendar API"
    3. Create OAuth 2.0 credentials (Desktop app) → Download as credentials.json
    4. Place credentials.json in the project root (same folder as main.py)
    5. Run Jarvis — first run opens a browser for Google sign-in
    6. token.json is auto-saved for future runs (no re-auth needed)

Requirements:
    pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

Public API:
    get_todays_events()     -> list[dict] (title, start, end, location, link)
    format_events(events)   -> human-readable multi-line string
    events_due_soon(events, minutes) -> events starting within N minutes
"""

from __future__ import annotations

import datetime
import os
from pathlib import Path

import config

# ── Paths ─────────────────────────────────────────────────────────────────────
_BASE             = Path(__file__).parent.parent   # project root
CREDENTIALS_FILE  = _BASE / "credentials.json"
TOKEN_FILE        = _BASE / "token.json"

# OAuth scopes: read-only calendar access
_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

_SETUP_MSG = (
    "\n  [Calendar] Google Calendar is not configured yet.\n"
    "  To enable it:\n"
    "    1. Go to https://console.cloud.google.com/\n"
    "    2. Create a project → Enable 'Google Calendar API'\n"
    "    3. Create OAuth 2.0 credentials (Desktop app)\n"
    "    4. Download as 'credentials.json' → place in your project root\n"
    "    5. Restart Jarvis — a browser tab will open for sign-in\n"
    "    6. token.json will be saved automatically for future runs.\n"
)


def _build_service():
    """Authenticates and returns a Google Calendar API service object."""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        return None, (
            "Google Calendar libraries not installed.\n"
            "  Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
        )

    if not CREDENTIALS_FILE.exists():
        return None, _SETUP_MSG

    creds = None

    # Load existing token
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), _SCOPES)
        except Exception:
            creds = None

    # Refresh or re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE), _SCOPES
                )
                creds = flow.run_local_server(port=0)
            except Exception as exc:
                return None, f"Google Calendar auth failed: {exc}"

        # Save token for next run
        try:
            TOKEN_FILE.write_text(creds.to_json())
        except Exception:
            pass

    try:
        service = build("calendar", "v3", credentials=creds)
        return service, None
    except Exception as exc:
        return None, f"Calendar service build failed: {exc}"


def get_todays_events(calendar_id: str = "primary") -> tuple[list[dict], str | None]:
    """
    Fetches all events for today from the given Google Calendar.

    Returns:
        (events_list, error_message)
        On success: (list of event dicts, None)
        On failure: ([], error_string)
    """
    service, err = _build_service()
    if err:
        return [], err

    now   = datetime.datetime.now().astimezone()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end   = now.replace(hour=23, minute=59, second=59, microsecond=0)

    try:
        result = service.events().list(
            calendarId=calendar_id,
            timeMin=today_start.isoformat(),
            timeMax=today_end.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        ).execute()
    except Exception as exc:
        return [], f"Failed to fetch calendar events: {exc}"

    raw_events = result.get("items", [])
    events = []
    for e in raw_events:
        start_raw = e.get("start", {})
        end_raw   = e.get("end",   {})

        # All-day events have "date"; timed events have "dateTime"
        if "dateTime" in start_raw:
            start_dt = datetime.datetime.fromisoformat(start_raw["dateTime"])
            end_dt   = datetime.datetime.fromisoformat(end_raw["dateTime"])
            start_str = start_dt.strftime("%I:%M %p")
            end_str   = end_dt.strftime("%I:%M %p")
        else:
            start_str = "All day"
            end_str   = ""
            start_dt  = today_start

        events.append({
            "title":    e.get("summary", "(No title)"),
            "start":    start_str,
            "end":      end_str,
            "start_dt": start_dt,
            "location": e.get("location", ""),
            "link":     e.get("htmlLink", ""),
        })

    return events, None


def format_events(events: list[dict]) -> str:
    """Returns a readable multi-line string of today's events."""
    if not events:
        return "No events on your calendar today. Enjoy the free time!"

    lines = [f"-- Today's Calendar Events ({len(events)}) --------------------"]
    for i, e in enumerate(events, 1):
        time_part = e["start"]
        if e["end"]:
            time_part += f" - {e['end']}"
        loc_part = f"  @ {e['location']}" if e["location"] else ""
        lines.append(f"  [{i}] {time_part}  |  {e['title']}{loc_part}")
    lines.append("------------------------------------------------------")
    return "\n".join(lines)


def events_due_soon(events: list[dict], within_minutes: int = 15) -> list[dict]:
    """Returns events that start within the next *within_minutes* minutes."""
    now = datetime.datetime.now().astimezone()
    due = []
    for e in events:
        start = e.get("start_dt")
        if start is None:
            continue
        # Make start timezone-aware if naive
        if start.tzinfo is None:
            start = start.replace(tzinfo=now.tzinfo)
        delta = (start - now).total_seconds() / 60
        if 0 <= delta <= within_minutes:
            due.append(e)
    return due
