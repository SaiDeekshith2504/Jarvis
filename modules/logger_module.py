"""
modules/logger_module.py
--------------------------
Command-level structured logger for Jarvis — Day 7.

Stores every executed command with full metadata in data/command_logs.json.
This is the foundation for future weekly productivity analytics.

Log schema (each entry):
    {
        "timestamp":  "2026-06-21 11:00:00",
        "command":    "weather",
        "full_input": "open google python tutorials",
        "response":   "Opening Google search...",
        "status":     "success" | "error" | "unknown",
        "source":     "text" | "voice" | "gui" | "startup",
        "duration_ms": 42
    }

Public API:
    log_command(command, full_input, response, status, source, duration_ms)
    get_recent_logs(n)      -> last n log entries as a list of dicts
    get_stats()             -> dict with counts, top commands, etc.
    format_stats()          -> human-readable stats string
    clear_logs()            -> wipes command_logs.json
"""

from __future__ import annotations

import datetime
import json
import os
from pathlib import Path

import config

# Day 7 command log file (separate from Day 6's jarvis_log.json)
COMMAND_LOG_FILE = os.path.join(config._BASE, "data", "command_logs.json")


# ─── File I/O ─────────────────────────────────────────────────────────────────

def _load() -> list[dict]:
    if not os.path.exists(COMMAND_LOG_FILE):
        return []
    try:
        with open(COMMAND_LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save(entries: list[dict]) -> None:
    os.makedirs(os.path.dirname(COMMAND_LOG_FILE), exist_ok=True)
    with open(COMMAND_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


# ─── Public API ───────────────────────────────────────────────────────────────

def log_command(
    command:     str,
    full_input:  str  = "",
    response:    str  = "",
    status:      str  = "success",
    source:      str  = "text",
    duration_ms: int  = 0,
) -> None:
    """
    Appends one command entry to command_logs.json.

    Args:
        command:     The primary keyword (e.g. 'weather', 'time').
        full_input:  The raw user input string.
        response:    Jarvis's reply (truncated to 300 chars for storage).
        status:      'success' | 'error' | 'unknown'.
        source:      'text' | 'voice' | 'gui' | 'startup'.
        duration_ms: How many ms the command took to process.
    """
    entry = {
        "timestamp":   datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "command":     command,
        "full_input":  full_input.strip(),
        "response":    response.strip()[:300],
        "status":      status,
        "source":      source,
        "duration_ms": duration_ms,
    }
    try:
        entries = _load()
        entries.append(entry)
        _save(entries)
    except Exception:
        pass  # Never crash Jarvis over logging


def get_recent_logs(n: int = 20) -> list[dict]:
    """Returns the last *n* command log entries."""
    return _load()[-n:]


def get_stats() -> dict:
    """
    Returns a summary dict with:
        total_commands, today_count, top_commands, source_breakdown,
        error_count, first_logged, last_logged
    """
    entries = _load()
    if not entries:
        return {"total_commands": 0}

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    today_count = sum(1 for e in entries if e.get("timestamp", "").startswith(today_str))

    # Top 5 commands by usage count
    from collections import Counter
    cmd_counts = Counter(e.get("command", "unknown") for e in entries)
    top_commands = cmd_counts.most_common(5)

    # Source breakdown
    sources = Counter(e.get("source", "text") for e in entries)

    error_count = sum(1 for e in entries if e.get("status") == "error")

    return {
        "total_commands": len(entries),
        "today_count":    today_count,
        "top_commands":   top_commands,
        "source_breakdown": dict(sources),
        "error_count":    error_count,
        "first_logged":   entries[0].get("timestamp", "?"),
        "last_logged":    entries[-1].get("timestamp", "?"),
    }


def format_stats() -> str:
    """Returns a human-readable stats report."""
    s = get_stats()
    if not s.get("total_commands"):
        return "No command history yet. Start using Jarvis to build your stats!"

    top = "\n".join(
        f"    {i+1}. {cmd:<20} ({cnt} uses)"
        for i, (cmd, cnt) in enumerate(s["top_commands"])
    )

    sources_str = "  |  ".join(
        f"{src}: {cnt}" for src, cnt in s["source_breakdown"].items()
    )

    lines = [
        "-- Jarvis Command Analytics ---------------------------------",
        f"  Total commands  : {s['total_commands']}",
        f"  Today           : {s['today_count']} commands",
        f"  Errors          : {s['error_count']}",
        f"  Sources         : {sources_str}",
        f"  Active since    : {s['first_logged']}",
        f"  Last command    : {s['last_logged']}",
        "",
        "  Top Commands:",
        top,
        "-------------------------------------------------------------",
    ]
    return "\n".join(lines)


def clear_logs() -> str:
    """Clears all command logs."""
    if not os.path.exists(COMMAND_LOG_FILE):
        return "Command log is already empty."
    try:
        _save([])
        return "Command logs cleared."
    except Exception as exc:
        return f"Could not clear logs: {exc}"
