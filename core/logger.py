"""
core/logger.py
--------------
Interaction logging for Jarvis — Day 6.

Every command and response is logged to LOG_FILE (default: data/jarvis_log.json).

Public API:
  log_interaction(user_input, response, command_type)
  show_history(n)         -> formatted string of last n entries
  clear_history(confirm)  -> wipes the log file
  get_log_entries(n)      -> raw list of the last n dicts
"""

from __future__ import annotations

import json
import os
import datetime

import config


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _load_log() -> list[dict]:
    """Reads the log file and returns a list of entry dicts."""
    if not os.path.exists(config.LOG_FILE):
        return []
    try:
        with open(config.LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_log(entries: list[dict]) -> None:
    """Persists the log list back to disk."""
    os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
    with open(config.LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


# ─── Public API ───────────────────────────────────────────────────────────────

def log_interaction(
    user_input: str,
    response: str,
    command_type: str = "unknown",
) -> None:
    """
    Appends one interaction entry to the log.

    Args:
        user_input:   What the user typed / spoke.
        response:     Jarvis's reply.
        command_type: Short category label (e.g. 'time', 'todo', 'ai', 'unknown').
    """
    entry = {
        "timestamp":    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_input":   user_input.strip(),
        "response":     response.strip(),
        "command_type": command_type,
    }
    try:
        entries = _load_log()
        entries.append(entry)
        _save_log(entries)
    except Exception:
        pass  # Logging must never crash the assistant


def show_history(n: int = 15) -> str:
    """
    Returns the last *n* log entries formatted for display.
    Usage (command): show history
    """
    entries = _load_log()
    if not entries:
        return "No history yet. Start chatting and I'll remember everything! 📋"

    recent = entries[-n:]
    lines  = [f"── Last {len(recent)} Interactions ─────────────────────────────"]
    for i, e in enumerate(recent, 1):
        ts  = e.get("timestamp", "?")
        inp = e.get("user_input", "")
        cmd = e.get("command_type", "")
        lines.append(f"\n  [{i:02d}]  {ts}  ({cmd})")
        lines.append(f"        You  : {inp}")
        # Truncate long responses for readability
        resp = e.get("response", "")
        resp_short = resp[:120].replace("\n", " ")
        if len(resp) > 120:
            resp_short += "…"
        lines.append(f"        Jarvis: {resp_short}")
    lines.append("\n─────────────────────────────────────────────────────────────")
    lines.append(f"  Total logged interactions: {len(entries)}")
    return "\n".join(lines)


def clear_history() -> str:
    """
    Clears all logged interactions.
    Usage (command): clear history
    """
    if not os.path.exists(config.LOG_FILE):
        return "History is already empty. Nothing to clear."

    try:
        _save_log([])
        return "History cleared. Starting fresh! 🗑️"
    except Exception as exc:
        return f"Couldn't clear history: {exc}"


def get_log_entries(n: int = 20) -> list[dict]:
    """Returns the raw last *n* log entries (used by the GUI)."""
    entries = _load_log()
    return entries[-n:]
