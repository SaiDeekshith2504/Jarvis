"""
core/commands.py
----------------
All supported commands live here as individual functions.
To add a new command: write a function and register it in COMMAND_MAP.

Day 1: time, date, hello, help, about
Day 2: search, open, note, status, joke  (+  Day 1 commands preserved)
"""

from __future__ import annotations
import datetime
import os
import random
import subprocess
import webbrowser

import config
from config import APP_MAP, JOKES, NOTES_FILE


# ═══════════════════════════════════════════════════════════════════════════════
#  DAY 1 — ORIGINAL COMMANDS (unchanged)
# ═══════════════════════════════════════════════════════════════════════════════

def cmd_time(_args: str) -> str:
    """Returns the current local time."""
    now = datetime.datetime.now().strftime("%I:%M %p")
    return f"The current time is {now}."


def cmd_date(_args: str) -> str:
    """Returns today's full date."""
    today = datetime.datetime.now().strftime("%A, %B %d, %Y")
    return f"Today is {today}."


def cmd_hello(_args: str) -> str:
    """Responds to a greeting."""
    return "Hello! Great to hear from you. What do you need?"


def cmd_help(_args: str) -> str:
    """Lists all available commands with a short description."""
    lines = [
        "Here's everything I can do:\n",
        "  ── Core ──────────────────────────────────────",
        "  time              → current time",
        "  date              → today's date",
        "  hello / hi / hey  → say hello",
        "  about             → about Jarvis",
        "  status            → system snapshot",
        "",
        "  ── New (Day 2) ───────────────────────────────",
        "  search <topic>    → open browser search",
        "  open <app>        → launch an app",
        "  note <text>       → save a note",
        "  notes             → show all saved notes",
        "  joke              → tell a joke",
        "",
        "  ── Control ───────────────────────────────────",
        "  voice             → toggle voice / text mode",
        "  help              → show this list",
        "  exit / quit / bye → shut down Jarvis",
    ]
    return "\n".join(lines)


def cmd_about(_args: str) -> str:
    """Returns information about Jarvis."""
    return (
        f"I'm Jarvis — a personal assistant built with Python.\n"
        f"  Version {config.VERSION} · {config.DAY} milestone.\n"
        f"  Commands keep growing — type 'help' to see them all."
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  DAY 2 — NEW COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

def cmd_search(args: str) -> str:
    """
    Opens the default browser with a Google search for <args>.
    Usage: search python tutorials
    """
    if not args:
        return "What should I search for? Try: search <topic>"

    query = args.strip()
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

    try:
        webbrowser.open(url)
        return f"Searching Google for '{query}'…"
    except Exception as exc:
        return f"Couldn't open the browser: {exc}"


def cmd_open(args: str) -> str:
    """
    Launches a system application by short name.
    Usage: open browser | open vscode | open notepad
    Registered apps are in config.APP_MAP.
    """
    if not args:
        available = ", ".join(sorted(APP_MAP.keys()))
        return f"Which app? Try: open <name>\n  Available: {available}"

    key = args.strip().lower()
    command = APP_MAP.get(key)

    if not command:
        available = ", ".join(sorted(APP_MAP.keys()))
        return (
            f"I don't know how to open '{key}'.\n"
            f"  Available: {available}\n"
            f"  (Add more in config.py → APP_MAP)"
        )

    try:
        subprocess.Popen(command, shell=True)
        return f"Opening {key}…"
    except Exception as exc:
        return f"Failed to open '{key}': {exc}"


def cmd_note(args: str) -> str:
    """
    Saves a timestamped note to data/notes.txt.
    Usage: note Buy more coffee
    """
    if not args:
        return "What should I note down? Try: note <your text>"

    # Ensure the data/ directory exists
    os.makedirs(os.path.dirname(NOTES_FILE), exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"[{timestamp}]  {args.strip()}\n"

    try:
        with open(NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
        return f"Got it! Note saved. 📝"
    except Exception as exc:
        return f"Couldn't save note: {exc}"


def cmd_notes(_args: str) -> str:
    """
    Displays all saved notes from data/notes.txt.
    Usage: notes
    """
    if not os.path.exists(NOTES_FILE):
        return "No notes yet. Use 'note <text>' to save one."

    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            return "Your notes file is empty."

        header = f"── Your Notes ({len(lines)} entries) ──────────────────────"
        body   = "".join(f"  {line}" for line in lines[-20:])  # last 20
        return f"{header}\n{body}"
    except Exception as exc:
        return f"Couldn't read notes: {exc}"


def cmd_status(_args: str) -> str:
    """
    Shows a quick system snapshot: date/time, user, platform, Python version.
    Usage: status
    """
    import platform
    import getpass

    now      = datetime.datetime.now().strftime("%A, %B %d %Y  %I:%M %p")
    user     = getpass.getuser()
    system   = platform.system()
    release  = platform.release()
    py_ver   = platform.python_version()
    machine  = platform.machine()

    lines = [
        "── System Status ───────────────────────────────",
        f"  User       : {user}",
        f"  Date/Time  : {now}",
        f"  OS         : {system} {release} ({machine})",
        f"  Python     : {py_ver}",
        f"  Jarvis     : v{config.VERSION} · {config.DAY}",
        "────────────────────────────────────────────────",
    ]
    return "\n".join(lines)


def cmd_joke(_args: str) -> str:
    """
    Tells a random programming joke from config.JOKES.
    Usage: joke
    """
    return random.choice(JOKES)


def cmd_voice(_args: str) -> str:
    """
    Placeholder — the actual toggle lives in assistant.py.
    This function is only called when the user types 'voice' directly
    without going through the assistant loop (e.g., in tests).
    """
    return "Voice mode toggled. (See the assistant loop for live state.)"


# ═══════════════════════════════════════════════════════════════════════════════
#  COMMAND REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

# Maps command keywords → handler functions.
# Keys are what the user types as the first word of their input.
COMMAND_MAP: dict[str, callable] = {
    # Day 1
    "time":    cmd_time,
    "date":    cmd_date,
    "hello":   cmd_hello,
    "hi":      cmd_hello,
    "hey":     cmd_hello,
    "help":    cmd_help,
    "about":   cmd_about,

    # Day 2
    "search":  cmd_search,
    "open":    cmd_open,
    "note":    cmd_note,
    "notes":   cmd_notes,
    "status":  cmd_status,
    "joke":    cmd_joke,
    "voice":   cmd_voice,
}


# ═══════════════════════════════════════════════════════════════════════════════
#  COMMAND ROUTER
# ═══════════════════════════════════════════════════════════════════════════════

def handle_command(user_input: str, speak_fn=None) -> str:
    """
    Parses user input, routes it to the correct handler, and returns the
    response string. Optionally calls speak_fn(response) for TTS output.

    Args:
        user_input: Raw string from the user.
        speak_fn:   Callable(str) → None, or None to skip TTS.

    Returns:
        The response string (so callers / tests can inspect it).
    """
    parts   = user_input.strip().lower().split(maxsplit=1)
    keyword = parts[0]
    args    = parts[1] if len(parts) > 1 else ""

    handler = COMMAND_MAP.get(keyword)

    if handler:
        response = handler(args)
    else:
        response = (
            f"I don't understand '{user_input}' yet. "
            f"Type 'help' to see what I can do."
        )

    # Output: always print, optionally speak
    if speak_fn:
        speak_fn(response)   # speak() already prints
    else:
        print(f"\n  [Jarvis] {response}\n")

    return response
