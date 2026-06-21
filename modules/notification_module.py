"""
modules/notification_module.py
--------------------------------
Windows desktop toast notifications for Jarvis — Day 7.

Uses win10toast-reborn (lightweight, no dependency on toast SDK).
Falls back to a simple print banner if the library is missing or
if not running on Windows.

Requirements (Windows only):
    pip install win10toast-reborn

Public API:
    notify(title, message, duration, icon_path)
    notify_reminder(task, time_str)
    notify_calendar_event(title, time_str)
    notify_weather(summary)
    notify_morning_briefing(name, summary)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ── Try to import the toast library ──────────────────────────────────────────
try:
    from win10toast import ToastNotifier
    _TOAST_OK = True
    _toaster  = ToastNotifier()
except ImportError:
    _TOAST_OK = False

# Jarvis icon path (optional — use None if not present)
_ICON = str(Path(__file__).parent.parent / "assets" / "jarvis.ico")
_ICON = _ICON if os.path.exists(_ICON) else None

_IS_WINDOWS = sys.platform == "win32"


# ─── Core notification function ───────────────────────────────────────────────

def notify(
    title: str,
    message: str,
    duration: int = 6,
    icon_path: str | None = None,
) -> None:
    """
    Sends a Windows toast notification.

    Falls back to printing a terminal banner if win10toast-reborn is
    not installed or the OS is not Windows.

    Args:
        title:      Bold notification title.
        message:    Notification body text.
        duration:   Seconds the toast stays visible (default 6).
        icon_path:  Path to a .ico file (optional).
    """
    if _TOAST_OK and _IS_WINDOWS:
        try:
            _toaster.show_toast(
                title,
                message,
                icon_path=icon_path or _ICON,
                duration=duration,
                threaded=True,   # non-blocking — Jarvis keeps running
            )
            return
        except Exception:
            pass  # fall through to terminal banner

    # Terminal fallback banner
    width = max(len(title), len(message), 40)
    border = "=" * (width + 4)
    print(f"\n  {border}")
    print(f"  | NOTIFICATION: {title:<{width - 14}} |")
    print(f"  | {message:<{width}} |")
    print(f"  {border}\n")


# ─── Semantic helpers ─────────────────────────────────────────────────────────

def notify_reminder(task: str, time_str: str = "") -> None:
    """Toast for a due/upcoming reminder."""
    msg = f"Due now: {task}" if not time_str else f"{time_str} — {task}"
    notify("⏰  Jarvis Reminder", msg, duration=8)


def notify_calendar_event(title: str, time_str: str = "") -> None:
    """Toast for an upcoming calendar event."""
    msg = f"Starting soon: {title}" if not time_str else f"{time_str} — {title}"
    notify("📅  Calendar Event", msg, duration=8)


def notify_weather(summary: str) -> None:
    """Toast showing today's weather summary."""
    notify("🌤️  Today's Weather", summary, duration=5)


def notify_morning_briefing(name: str, summary: str) -> None:
    """Toast for the morning briefing."""
    greeting = f"Good morning, {name}!" if name else "Good morning!"
    notify(f"☀️  Jarvis — {greeting}", summary[:200], duration=10)
