"""
core/commands.py
----------------
All supported commands live here as individual functions.
To add a new command: write a function and register it in COMMAND_MAP.

Day 2+: Add web search, system automation, AI responses here.
"""

import datetime


# ─── Individual Command Handlers ─────────────────────────────────────────────

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
    """Lists all available commands."""
    commands = "\n".join(f"    • {cmd}" for cmd in sorted(COMMAND_MAP.keys()))
    return f"Here's what I can do:\n{commands}\n    • exit / quit / bye"


def cmd_about(_args: str) -> str:
    """Returns information about Jarvis."""
    return (
        "I'm Jarvis — a personal assistant built with Python.\n"
        "  Day 1 prototype. More features coming soon."
    )


# ─── Command Registry ────────────────────────────────────────────────────────

# Maps command keywords → handler functions.
# To add a new command: define a function above and add it here.
COMMAND_MAP: dict = {
    "time":    cmd_time,
    "date":    cmd_date,
    "hello":   cmd_hello,
    "hi":      cmd_hello,
    "hey":     cmd_hello,
    "help":    cmd_help,
    "about":   cmd_about,
}


# ─── Command Router ───────────────────────────────────────────────────────────

def handle_command(user_input: str):
    """
    Parses user input, routes it to the correct handler, and prints
    the response. Handles unknown commands gracefully.
    """
    parts = user_input.strip().lower().split(maxsplit=1)
    keyword = parts[0]
    args = parts[1] if len(parts) > 1 else ""

    handler = COMMAND_MAP.get(keyword)

    if handler:
        response = handler(args)
        print(f"\n  [Jarvis] {response}\n")
    else:
        print(
            f"\n  [Jarvis] I don't understand '{user_input}' yet. "
            f"Type 'help' to see what I can do.\n"
        )
