"""
core/commands.py
----------------
All supported commands live here as individual functions.
To add a new command: write a function and register it in COMMAND_MAP.

Day 1: time, date, hello, help, about
Day 2: search, open, note, notes, status, joke  (+ Day 1 preserved)
Day 3: create note, write note, list notes, open file,
       create todo, list todos, done todo,
       sysinfo, quote, ask, clear notes          (+ Day 1+2 preserved)
Day 4: remind me, list reminders, check reminders, clear reminder,
       morning summary, night summary, routine,
       status (enhanced with todos + reminders)  (+ Day 1-3 preserved)
Day 5: ask (upgraded to ai.py), chat mode,
       set name, get name, set preference, get preference,
       my profile, ai status, run <shell command>  (+ Day 1-4 preserved)
Day 6: open url/google/youtube/github/maps/wikipedia/reddit (browser automation),
       show history, clear history, tips           (+ Day 1-5 preserved)
Day 7: weather, calendar, morning briefing, desktop notifications,
       VS Code / GitHub / Flask automation, command stats  (+ Day 1-6 preserved)
"""

from __future__ import annotations
import datetime
import json
import os
import random
import subprocess
import webbrowser

import config
from config import (
    APP_MAP, JOKES, NOTES_FILE, NOTES_DIR, TODOS_FILE, QUOTES,
    DAILY_ROUTINE, MORNING_MESSAGES, NIGHT_MESSAGES, BLOCKED_COMMANDS,
    TIPS,
)
from core import reminders as rem_engine
from core import ai as ai_engine
from core import user_profile as profile_engine
from core import browser as browser_engine
from core import logger as log_engine

# Day 7 modules (graceful if not yet installed)
try:
    from modules import weather_module
    from modules import calendar_module
    from modules import notification_module
    from modules import automation_module
    from modules import logger_module as cmd_logger
    from modules import morning_briefing as briefing_module
    _DAY7_OK = True
except Exception as _day7_err:
    _DAY7_OK = False
    _day7_err_msg = str(_day7_err)


# ═══════════════════════════════════════════════════════════════════════════════
#  DAY 1 — ORIGINAL COMMANDS (unchanged)
# ═══════════════════════════════════════════════════════════════════════════════

def cmd_time(_args: str) -> str:
    """Returns the current local time with timezone note."""
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    tz_name  = datetime.datetime.now().astimezone().strftime("%Z")
    return f"The current time is {time_str} ({tz_name})."


def cmd_date(_args: str) -> str:
    """Returns today's full date."""
    today = datetime.datetime.now().strftime("%A, %B %d, %Y")
    return f"Today is {today}."


def cmd_hello(_args: str) -> str:
    """Responds to a greeting."""
    return "Hello! Great to hear from you. What can I do for you today?"


def cmd_about(_args: str) -> str:
    """Returns information about Jarvis."""
    return (
        f"I'm Jarvis — a personal assistant built with Python.\n"
        f"  Version {config.VERSION} · {config.DAY} milestone.\n"
        f"  Commands keep growing — type 'help' to see them all."
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  DAY 2 — COMMANDS (unchanged)
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
    Saves a timestamped note to data/notes.txt (Day 2 legacy).
    Usage: note Buy more coffee
    """
    if not args:
        return "What should I note down? Try: note <your text>"

    os.makedirs(os.path.dirname(NOTES_FILE), exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"[{timestamp}]  {args.strip()}\n"

    try:
        with open(NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
        return "Got it! Note saved. 📝"
    except Exception as exc:
        return f"Couldn't save note: {exc}"


def cmd_notes(_args: str) -> str:
    """
    Displays all saved notes from data/notes.txt (Day 2 legacy).
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
        body   = "".join(f"  {line}" for line in lines[-20:])
        return f"{header}\n{body}"
    except Exception as exc:
        return f"Couldn't read notes: {exc}"


def cmd_joke(_args: str) -> str:
    """Tells a random programming joke. Usage: joke"""
    return random.choice(JOKES)


def cmd_voice(_args: str) -> str:
    """Placeholder — actual toggle lives in assistant.py."""
    return "Voice mode toggled. (See the assistant loop for live state.)"


# ═══════════════════════════════════════════════════════════════════════════════
#  DAY 3 — COMMANDS (unchanged)
# ═══════════════════════════════════════════════════════════════════════════════

# ── Helpers ───────────────────────────────────────────────────────────────────

def _note_path(title: str) -> str:
    """Returns the full path for a note file, sanitising the title."""
    safe = "".join(c if c.isalnum() or c in "._- " else "_" for c in title)
    safe = safe.strip().replace(" ", "_").lower()
    if not safe:
        safe = "untitled"
    return os.path.join(NOTES_DIR, f"{safe}.txt")


def _load_todos() -> list[dict]:
    """Reads todos.json; returns an empty list if missing or corrupt."""
    if not os.path.exists(TODOS_FILE):
        return []
    try:
        with open(TODOS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_todos(todos: list[dict]) -> None:
    """Writes todos list back to todos.json."""
    os.makedirs(os.path.dirname(TODOS_FILE), exist_ok=True)
    with open(TODOS_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2, ensure_ascii=False)


# ── Notes (file-per-note) ────────────────────────────────────────────────────

def cmd_create_note(args: str) -> str:
    """
    Creates a new note file in data/notes/.
    Usage: create note <title>
    """
    title = args.strip()
    if not title:
        return "Please provide a title. Usage: create note <title>"

    os.makedirs(NOTES_DIR, exist_ok=True)
    path = _note_path(title)

    if os.path.exists(path):
        return (
            f"Note '{title}' already exists. "
            f"Use 'write note {title} <content>' to add to it."
        )

    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n")
            f.write(f"Created: {timestamp}\n")
            f.write("─" * 40 + "\n\n")
        return f"Note created: {os.path.basename(path)} 📄"
    except Exception as exc:
        return f"Couldn't create note: {exc}"


def cmd_write_note(args: str) -> str:
    """
    Appends content to a note file. Auto-creates the note if it doesn't exist.
    Usage: write note <title> <content>
    """
    if not args:
        return "Usage: write note <title> <content>"

    parts = args.split(maxsplit=1)
    if len(parts) < 2:
        return "I need both a title and content. Usage: write note <title> <content>"

    title, content = parts[0], parts[1]
    os.makedirs(NOTES_DIR, exist_ok=True)
    path = _note_path(title)

    if not os.path.exists(path):
        cmd_create_note(title)

    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {content.strip()}\n")
        return f"Written to '{title}' ✏️"
    except Exception as exc:
        return f"Couldn't write to note: {exc}"


def cmd_list_notes(_args: str) -> str:
    """
    Lists all note files in data/notes/.
    Usage: list notes
    """
    if not os.path.isdir(NOTES_DIR):
        return "No notes folder yet. Use 'create note <title>' to get started."

    files = sorted(f for f in os.listdir(NOTES_DIR) if f.endswith(".txt"))

    if not files:
        return "No notes found. Use 'create note <title>' to make one."

    header = f"── Your Notes ({len(files)} files) ─────────────────────"
    body   = "\n".join(f"  [{i+1}] {f}" for i, f in enumerate(files))
    return f"{header}\n{body}"


def cmd_open_file(args: str) -> str:
    """
    Opens a file with the OS default application.
    Usage: open file <path or note title>
    """
    if not args:
        return "Which file? Usage: open file <path>"

    path = args.strip()

    # Look in notes dir if a bare name is given
    if not os.path.isabs(path) and not os.path.exists(path):
        candidate = _note_path(path)
        if os.path.exists(candidate):
            path = candidate

    if not os.path.exists(path):
        return f"File not found: '{path}'"

    try:
        os.startfile(path)
        return f"Opening '{os.path.basename(path)}'…"
    except AttributeError:
        subprocess.Popen(["xdg-open", path])
        return f"Opening '{os.path.basename(path)}'…"
    except Exception as exc:
        return f"Couldn't open file: {exc}"


def cmd_clear_notes(_args: str) -> str:
    """
    Deletes all note files in data/notes/.
    Usage: clear notes
    """
    if not os.path.isdir(NOTES_DIR):
        return "No notes folder to clear."

    files = [f for f in os.listdir(NOTES_DIR) if f.endswith(".txt")]
    if not files:
        return "Notes folder is already empty."

    deleted = 0
    for f in files:
        try:
            os.remove(os.path.join(NOTES_DIR, f))
            deleted += 1
        except Exception:
            pass

    return f"Cleared {deleted} note(s) from the notes folder."


# ── Todos ────────────────────────────────────────────────────────────────────

def cmd_create_todo(args: str) -> str:
    """
    Adds a new task to the todo list.
    Usage: create todo <task description>
    """
    task = args.strip()
    if not task:
        return "What's the task? Usage: create todo <task>"

    todos = _load_todos()
    entry = {
        "id":      len(todos) + 1,
        "task":    task,
        "done":    False,
        "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    try:
        todos.append(entry)
        _save_todos(todos)
        return f"Todo added: {task} ✅"
    except Exception as exc:
        return f"Couldn't save todo: {exc}"


def cmd_list_todos(_args: str) -> str:
    """
    Shows all todos with their status.
    Usage: list todos
    """
    todos = _load_todos()

    if not todos:
        return "No todos yet. Use 'create todo <task>' to add one."

    pending = [t for t in todos if not t["done"]]
    done    = [t for t in todos if t["done"]]

    lines = [f"── Todos ({len(pending)} pending, {len(done)} done) ────────"]
    for t in pending:
        lines.append(f"  [ ] #{t['id']}  {t['task']}")
    for t in done:
        lines.append(f"  [✓] #{t['id']}  {t['task']}")
    lines.append("  Use 'done todo <#>' to mark a task complete.")
    return "\n".join(lines)


def cmd_done_todo(args: str) -> str:
    """
    Marks a todo as complete by its number.
    Usage: done todo <#>
    """
    if not args.strip().isdigit():
        return "Please give a todo number. Usage: done todo <#>"

    num   = int(args.strip())
    todos = _load_todos()

    for todo in todos:
        if todo["id"] == num:
            if todo["done"]:
                return f"Todo #{num} is already done!"
            todo["done"] = True
            _save_todos(todos)
            return f"Done! Marked #{num} '{todo['task']}' as complete ✓"

    return f"No todo with #{num} found. Use 'list todos' to see all."


# ── System Info ──────────────────────────────────────────────────────────────

def cmd_sysinfo(_args: str) -> str:
    """
    Shows CPU, RAM, and disk usage via psutil.
    Usage: sysinfo
    """
    try:
        import psutil

        cpu  = psutil.cpu_percent(interval=0.5)
        ram  = psutil.virtual_memory()
        disk = (
            psutil.disk_usage("C:\\") if os.name == "nt"
            else psutil.disk_usage("/")
        )

        ram_used   = ram.used   / (1024 ** 3)
        ram_total  = ram.total  / (1024 ** 3)
        disk_used  = disk.used  / (1024 ** 3)
        disk_total = disk.total / (1024 ** 3)

        lines = [
            "── System Info ─────────────────────────────────",
            f"  CPU usage  : {cpu:.1f}%",
            f"  RAM        : {ram_used:.1f} GB / {ram_total:.1f} GB  ({ram.percent:.0f}%)",
            f"  Disk       : {disk_used:.1f} GB / {disk_total:.1f} GB  ({disk.percent:.0f}%)",
            "────────────────────────────────────────────────",
        ]
        return "\n".join(lines)

    except ImportError:
        return (
            "psutil is not installed. Run:\n"
            "  pip install psutil\n"
            "then restart Jarvis."
        )
    except Exception as exc:
        return f"Couldn't get system info: {exc}"


# ── Quote ────────────────────────────────────────────────────────────────────

def cmd_quote(_args: str) -> str:
    """Returns a random motivational quote. Usage: quote"""
    return f"💡 {random.choice(QUOTES)}"


# ── AI Ask ───────────────────────────────────────────────────────────────────

def cmd_ask(args: str) -> str:
    """
    Sends a question to the configured AI provider (Gemini or OpenAI).
    Usage: ask <your question>
    """
    if not args.strip():
        return "What would you like to ask? Usage: ask <your question>"
    return ai_engine.ask_ai(args)


# ═══════════════════════════════════════════════════════════════════════════════
#  DAY 4 — NEW COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

# ── Reminders ────────────────────────────────────────────────────────────────

def cmd_remind(args: str) -> str:
    """
    Sets a reminder at a specified time.
    Usage: remind me <time> <task>

    Time formats:
      remind me 08:30 Attend class
      remind me 2026-06-20 09:00 Submit assignment
      remind me tomorrow 10:00 Team meeting
      remind me in 30 minutes Take a break
      remind me in 2 hours Review notes
    """
    args = args.strip()
    if not args:
        return (
            "Usage: remind me <time> <task>\n"
            "  Examples:\n"
            "    remind me 08:30 Attend class\n"
            "    remind me tomorrow 09:00 Submit assignment\n"
            "    remind me in 30 minutes Take a break"
        )

    # Strip leading "me " if user typed "remind me ..."
    if args.lower().startswith("me "):
        args = args[3:]

    # Try to extract time from common patterns
    # Pattern: "in X minutes/hours <task>"
    import re
    m = re.match(r"(in\s+\d+\s+(?:minute|minutes|hour|hours))\s+(.*)", args, re.IGNORECASE)
    if m:
        return rem_engine.add_reminder(m.group(2), m.group(1))

    # Pattern: "tomorrow HH:MM <task>"
    m = re.match(r"(tomorrow\s+\d{1,2}:\d{2})\s+(.*)", args, re.IGNORECASE)
    if m:
        return rem_engine.add_reminder(m.group(2), m.group(1))

    # Pattern: "YYYY-MM-DD HH:MM <task>"
    m = re.match(r"(\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2})\s+(.*)", args)
    if m:
        return rem_engine.add_reminder(m.group(2), m.group(1))

    # Pattern: "HH:MM <task>"
    m = re.match(r"(\d{1,2}:\d{2})\s+(.*)", args)
    if m:
        return rem_engine.add_reminder(m.group(2), m.group(1))

    return (
        f"I couldn't parse a time from '{args}'.\n"
        "  Try: remind me 08:30 <task>  |  remind me in 20 minutes <task>"
    )


def cmd_list_reminders(_args: str) -> str:
    """Shows all pending reminders. Usage: list reminders"""
    return rem_engine.list_reminders()


def cmd_check_reminders(_args: str) -> str:
    """Checks for due reminders and marks them done. Usage: check reminders"""
    result = rem_engine.check_reminders()
    if result:
        return result
    return "No reminders are due right now. ✅"


def cmd_clear_reminder(args: str) -> str:
    """
    Marks a reminder as done by index.
    Usage: clear reminder <#>
    """
    return rem_engine.clear_reminder(args.strip())


# ── Status (enhanced for Day 4) ───────────────────────────────────────────────

def cmd_status(_args: str) -> str:
    """
    Shows a full productivity snapshot: date/time, user, OS, todos, reminders.
    Usage: status
    """
    import platform
    import getpass

    now     = datetime.datetime.now().strftime("%A, %B %d %Y  %I:%M %p")
    tz_name = datetime.datetime.now().astimezone().strftime("%Z")
    user    = getpass.getuser()
    system  = platform.system()
    release = platform.release()
    py_ver  = platform.python_version()

    # Count pending todos
    todos   = _load_todos()
    pending_todos = sum(1 for t in todos if not t["done"])
    done_todos    = sum(1 for t in todos if t["done"])

    # Count pending reminders
    all_reminders     = rem_engine._load_reminders()
    pending_reminders = sum(1 for r in all_reminders if r["status"] == "pending")

    lines = [
        "── Jarvis Status ───────────────────────────────────────",
        f"  User         : {user}",
        f"  Date/Time    : {now} ({tz_name})",
        f"  OS           : {system} {release}",
        f"  Python       : {py_ver}",
        f"  Jarvis       : v{config.VERSION} · {config.DAY}",
        "  ─────────────────────────────────────────────────────",
        f"  Todos        : {pending_todos} pending  |  {done_todos} done",
        f"  Reminders    : {pending_reminders} pending",
        "─────────────────────────────────────────────────────────",
    ]
    return "\n".join(lines)


# ── Morning Summary ──────────────────────────────────────────────────────────

def cmd_morning_summary(_args: str) -> str:
    """
    Displays a morning briefing: date, todos, reminders, + motivation.
    Usage: morning summary
    """
    now  = datetime.datetime.now()
    date = now.strftime("%A, %B %d, %Y")
    time = now.strftime("%I:%M %p")

    todos         = _load_todos()
    pending_todos = [t for t in todos if not t["done"]]

    all_reminders     = rem_engine._load_reminders()
    pending_reminders = [r for r in all_reminders if r["status"] == "pending"]

    lines = [
        "=" * 56,
        "       GOOD MORNING -- DAILY BRIEFING",
        "=" * 56,
        f"\n  Date : {date}",
        f"  Time : {time}\n",
    ]

    # Todos section
    if pending_todos:
        lines.append(f"  ✅  Pending Todos ({len(pending_todos)})")
        for t in pending_todos[:5]:   # show up to 5
            lines.append(f"       [ ] {t['task']}")
        if len(pending_todos) > 5:
            lines.append(f"       … and {len(pending_todos) - 5} more. Use 'list todos'.")
    else:
        lines.append("  ✅  No pending todos — clean slate! 🎉")

    lines.append("")

    # Reminders section
    if pending_reminders:
        lines.append(f"  ⏰  Upcoming Reminders ({len(pending_reminders)})")
        for r in pending_reminders[:5]:
            lines.append(f"       [{r['time']}]  {r['task']}")
        if len(pending_reminders) > 5:
            lines.append(f"       … and {len(pending_reminders) - 5} more. Use 'list reminders'.")
    else:
        lines.append("  ⏰  No reminders scheduled.")

    lines.append("")
    lines.append(f"  💬  {random.choice(MORNING_MESSAGES)}")
    lines.append("\n  Type 'routine' to see your daily schedule.")
    lines.append("──────────────────────────────────────────────────────")

    return "\n".join(lines)


# ── Night Summary ─────────────────────────────────────────────────────────────

def cmd_night_summary(_args: str) -> str:
    """
    Displays an evening wrap-up: completed todos, done reminders, night message.
    Usage: night summary
    """
    now  = datetime.datetime.now()
    date = now.strftime("%A, %B %d, %Y")

    todos      = _load_todos()
    done_todos = [t for t in todos if t["done"]]

    all_reminders  = rem_engine._load_reminders()
    done_reminders = [r for r in all_reminders if r["status"] == "done"]

    lines = [
        "=" * 56,
        "           EVENING WRAP-UP SUMMARY",
        "=" * 56,
        f"\n  Date : {date}\n",
    ]

    # Completed todos
    if done_todos:
        lines.append(f"  ✅  Completed Todos Today ({len(done_todos)})")
        for t in done_todos[-5:]:    # show last 5
            lines.append(f"       [✓] {t['task']}")
    else:
        lines.append("  ✅  No todos marked done yet.")

    lines.append("")

    # Done reminders
    if done_reminders:
        lines.append(f"  ⏰  Completed Reminders ({len(done_reminders)})")
        for r in done_reminders[-5:]:
            lines.append(f"       [✓] {r['task']}")
    else:
        lines.append("  ⏰  No reminders completed today.")

    lines.append("")
    lines.append(f"  💬  {random.choice(NIGHT_MESSAGES)}")
    lines.append("\n  Sweet dreams. Jarvis will be here when you wake up. 🌟")
    lines.append("──────────────────────────────────────────────────────")

    return "\n".join(lines)


# ── Daily Routine ─────────────────────────────────────────────────────────────

def cmd_routine(_args: str) -> str:
    """
    Displays the configured daily routine from config.py.
    Usage: routine
    """
    now  = datetime.datetime.now()
    hour = now.hour

    lines = ["── 📋  Your Daily Routine ──────────────────────────────"]
    for item in DAILY_ROUTINE:
        # Highlight the current time block
        try:
            slot_hour = int(item.split(":")[0])
            marker = " ◀ NOW" if slot_hour == hour else ""
        except (ValueError, IndexError):
            marker = ""
        lines.append(f"  {item}{marker}")
    lines.append("────────────────────────────────────────────────────────")
    lines.append("  (Edit your routine in config.py → DAILY_ROUTINE)")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
#  DAY 6 — NEW COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

# ── Browser Automation ───────────────────────────────────────────────────────

def cmd_open_url(args: str) -> str:
    """Opens a URL in the default browser. Usage: open url <url>"""
    return browser_engine.open_url(args)


def cmd_open_google(args: str) -> str:
    """Opens a Google search. Usage: open google <query>"""
    return browser_engine.open_google(args)


def cmd_open_youtube(args: str) -> str:
    """Opens a YouTube search. Usage: open youtube <query>"""
    return browser_engine.open_youtube(args)


def cmd_open_github(args: str) -> str:
    """Opens a GitHub code search. Usage: open github <query>"""
    return browser_engine.open_github(args)


def cmd_open_maps(args: str) -> str:
    """Opens a Google Maps search. Usage: open maps <location>"""
    return browser_engine.open_maps(args)


def cmd_open_wikipedia(args: str) -> str:
    """Opens Wikipedia search. Usage: open wikipedia <query>"""
    return browser_engine.open_wikipedia(args)


def cmd_open_reddit(args: str) -> str:
    """Opens a Reddit search. Usage: open reddit <query>"""
    return browser_engine.open_reddit(args)


# ── History / Logging ────────────────────────────────────────────────────────

def cmd_show_history(args: str) -> str:
    """
    Shows the last 15 (or N) logged interactions.
    Usage: show history        (last 15)
           show history 25     (last 25)
    """
    n = 15
    if args.strip().isdigit():
        n = int(args.strip())
    return log_engine.show_history(n)


def cmd_clear_history_cmd(_args: str) -> str:
    """Clears all interaction history. Usage: clear history"""
    return log_engine.clear_history()


# ── Tips ─────────────────────────────────────────────────────────────────────

def cmd_tips(_args: str) -> str:
    """Shows helpful tips for using Jarvis. Usage: tips"""
    lines = ["-- Jarvis Tips -----------------------------------------------"]
    for i, tip in enumerate(TIPS, 1):
        lines.append(f"  [{i}]  {tip}")
    lines.append("--------------------------------------------------------------")
    lines.append("  More commands: type 'help' for the full list.")
    return "\n".join(lines)


# ===============================================================================
#  DAY 7 -- NEW COMMANDS
# ===============================================================================

def _day7_guard() -> str | None:
    """Returns an error string if Day 7 modules failed to load, else None."""
    if not _DAY7_OK:
        return f"Day 7 modules not loaded: {_day7_err_msg}\n  Run: pip install requests win10toast-reborn"
    return None


# -- Weather -------------------------------------------------------------------

def cmd_weather(args: str) -> str:
    """
    Shows live weather for a city (default: WEATHER_CITY in config.py).
    Usage: weather            -> weather for default city
           weather London     -> weather for London
    """
    if (err := _day7_guard()): return err
    data = weather_module.get_weather(args.strip())
    return weather_module.format_weather(data)


# -- Calendar ------------------------------------------------------------------

def cmd_calendar(_args: str) -> str:
    """Shows today's Google Calendar events. Usage: calendar"""
    if (err := _day7_guard()): return err
    events, err = calendar_module.get_todays_events()
    if err:
        return err
    return calendar_module.format_events(events)


# -- Morning Briefing ----------------------------------------------------------

def cmd_briefing(_args: str) -> str:
    """
    Generates the full morning briefing (weather + calendar + todos + motivation).
    Usage: briefing   |   morning briefing
    """
    if (err := _day7_guard()): return err
    return briefing_module.generate_briefing()


# -- Notification test ---------------------------------------------------------

def cmd_notify(args: str) -> str:
    """
    Sends a test desktop notification.
    Usage: notify <message>
    """
    if (err := _day7_guard()): return err
    msg = args.strip() or "Jarvis notification test!"
    notification_module.notify("Jarvis", msg)
    return f"Notification sent: {msg}"


# -- VS Code / Developer Automation -------------------------------------------

def cmd_open_vscode(args: str) -> str:
    """Opens VS Code. Usage: open vscode [path]"""
    if (err := _day7_guard()): return err
    return automation_module.open_vscode(args)


def cmd_open_project(args: str) -> str:
    """Opens a known project in VS Code. Usage: open project <name>"""
    if (err := _day7_guard()): return err
    return automation_module.open_project(args)


def cmd_open_flask(args: str) -> str:
    """Starts the Flask dev server. Usage: run flask [path/to/app.py]"""
    if (err := _day7_guard()): return err
    return automation_module.run_flask_app(args)


def cmd_open_terminal_cmd(args: str) -> str:
    """Opens Windows Terminal or CMD. Usage: open terminal [path]"""
    if (err := _day7_guard()): return err
    return automation_module.open_terminal(args)


def cmd_kill_process(args: str) -> str:
    """Kills a running process. Usage: kill <process name>"""
    if (err := _day7_guard()): return err
    return automation_module.kill_process(args)


# -- Command Analytics ---------------------------------------------------------

def cmd_stats(_args: str) -> str:
    """Shows command usage analytics. Usage: stats"""
    if (err := _day7_guard()): return err
    return cmd_logger.format_stats()


def cmd_clear_cmd_logs(_args: str) -> str:
    """Clears the structured command log. Usage: clear cmdlogs"""
    if (err := _day7_guard()): return err
    return cmd_logger.clear_logs()


# ─── Context-aware responses ─────────────────────────────────────────────────


def _handle_busy(user_input: str) -> str | None:
    """
    Detects phrases like "a lot to do", "busy", "overwhelmed" and gives
    context-aware suggestions.
    """
    triggers = ["a lot to do", "so much to do", "busy", "overwhelmed",
                "too many tasks", "stressed", "behind on"]
    text = user_input.lower()
    if any(t in text for t in triggers):
        todos   = _load_todos()
        pending = sum(1 for t in todos if not t["done"])
        if pending:
            return (
                f"Sounds like you've got a lot on your plate!\n"
                f"  You have {pending} pending todo(s).\n"
                f"  Try: 'list todos' to review them, or 'morning summary' for a full briefing."
            )
        else:
            return (
                "Feeling busy? Your todo list is actually clear! 🎉\n"
                "  Try 'morning summary' for a full briefing, or 'routine' to plan your day."
            )
    return None


# ═══════════════════════════════════════════════════════════════════════════════
#  DAY 5 — NEW COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

# ── Personalization ───────────────────────────────────────────────────────────

def cmd_set_name(args: str) -> str:
    """
    Stores the user's preferred name in data/user.json.
    Usage: set name <your name>
    """
    return profile_engine.set_name(args)


def cmd_get_name(_args: str) -> str:
    """
    Reads and returns the stored user name.
    Usage: get name
    """
    name = profile_engine.get_name()
    if name:
        return f"Your name is set to: {name}"
    return "No name stored yet. Use: set name <your name>"


def cmd_set_preference(args: str) -> str:
    """
    Stores a user preference as key=value.
    Usage: set preference <key> <value>
    Example: set preference theme light
    """
    parts = args.strip().split(maxsplit=1)
    if len(parts) < 2:
        return "Usage: set preference <key> <value>  (e.g. set preference theme dark)"
    return profile_engine.set_preference(parts[0], parts[1])


def cmd_get_preference(args: str) -> str:
    """
    Reads a stored preference value.
    Usage: get preference <key>
    """
    return profile_engine.get_preference(args.strip())


def cmd_my_profile(_args: str) -> str:
    """
    Shows the full user profile: name + all preferences.
    Usage: my profile
    """
    name  = profile_engine.get_name() or "(not set)"
    prefs = profile_engine.list_preferences()
    lines = [
        "-- Your Profile --------------------------------",
        f"  Name         : {name}",
        "",
        prefs,
        "  Use 'set name <name>' or 'set preference <key> <value>' to update.",
    ]
    return "\n".join(lines)


# ── AI status ─────────────────────────────────────────────────────────────────

def cmd_ai_status(_args: str) -> str:
    """
    Shows the current AI configuration.
    Usage: ai status
    """
    return ai_engine.ai_status()


# ── Chat mode ─────────────────────────────────────────────────────────────────

def cmd_chat(_args: str) -> str:
    """
    Enters interactive chat mode — every message is sent to ask_ai().
    Usage: chat
    Type 'exit', 'back', or 'stop' to leave chat mode.
    """
    # chat_session() is a blocking loop; call it directly.
    # speak_fn is not wired here because cmd_* functions only return strings.
    # The actual blocking session is invoked from handle_command() below.
    return "__CHAT_MODE__"   # sentinel — caught by handle_command


# ── Shell run ─────────────────────────────────────────────────────────────────

def cmd_run(args: str) -> str:
    """
    Runs a simple shell command and returns its stdout/stderr output.
    Usage: run echo hello  |  run dir  |  run python --version
           run flask [path]  -> starts Flask dev server (Day 7)

    Safety: commands starting with a blocked token are refused.
    Edit BLOCKED_COMMANDS in config.py to adjust the list.
    """
    cmd = args.strip()
    if not cmd:
        return "What should I run? Usage: run <shell command>  (e.g. run echo hello)"

    # Day 7: intercept 'run flask'
    if cmd.lower().startswith("flask"):
        flask_args = cmd[5:].strip()
        if _DAY7_OK:
            return automation_module.run_flask_app(flask_args)
        return "Day 7 modules not loaded. Run: pip install requests"

    # Safety check: reject blocked command prefixes
    cmd_lower = cmd.lower()
    for blocked in BLOCKED_COMMANDS:
        if cmd_lower.startswith(blocked.lower()):
            return (
                f"Sorry, '{blocked}' is on the blocked-commands list for safety.\n"
                "  Edit BLOCKED_COMMANDS in config.py to adjust."
            )

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,          # never hang longer than 10 s
        )
        output = (result.stdout or "").strip()
        errors = (result.stderr or "").strip()

        parts = []
        if output:
            parts.append(output)
        if errors:
            parts.append(f"[stderr] {errors}")
        if not parts:
            parts.append("(Command ran successfully with no output.)")

        return "\n".join(parts)

    except subprocess.TimeoutExpired:
        return "Command timed out after 10 seconds."
    except Exception as exc:
        return f"Failed to run command: {exc}"


# ═══════════════════════════════════════════════════════════════════════════════
#  HELP — updated for Day 5
# ═══════════════════════════════════════════════════════════════════════════════

def cmd_help(_args: str) -> str:
    """Lists all available commands with a short description."""
    lines = [
        "Here's everything I can do:\n",
        "  -- Core -----------------------------------------------",
        "  time                             -> current time (with timezone)",
        "  date                             -> today's date",
        "  hello / hi / hey                 -> say hello",
        "  about                            -> about Jarvis",
        "  status                           -> full snapshot (OS + todos + reminders)",
        "  sysinfo                          -> CPU / RAM / disk usage",
        "",
        "  -- Personalization (Day 5) ----------------------------",
        "  set name <name>                  -> save your name",
        "  get name                         -> read your stored name",
        "  set preference <key> <value>     -> save a preference",
        "  get preference <key>             -> read a preference",
        "  my profile                       -> show name + all preferences",
        "",
        "  -- AI (Day 5 upgraded) --------------------------------",
        "  ask <question>                   -> smart AI answer (API or rule-based)",
        "  chat                             -> enter interactive AI chat mode",
        "  ai status                        -> show current AI configuration",
        "",
        "  -- Shell (Day 5) --------------------------------------",
        "  run <command>                    -> execute a shell command safely",
        "",
        "  -- Browser Automation (Day 6) -------------------------",
        "  open url <url>                   -> open any URL in the browser",
        "  open google <query>              -> Google search",
        "  open youtube <query>             -> YouTube search",
        "  open github <query>              -> GitHub code search",
        "  open maps <location>             -> Google Maps",
        "  open wikipedia <query>           -> Wikipedia search",
        "  open reddit <query>              -> Reddit search",
        "",
        "  -- History & Logging (Day 6) --------------------------",
        "  show history [n]                 -> last 15 (or n) interactions",
        "  clear history                    -> wipe the log",
        "",
        "  -- Tips & Help (Day 6) --------------------------------",
        "  tips                             -> helpful usage tips",
        "",
        "  -- Daily Routine (Day 4) ------------------------------",
        "  morning summary                  -> today's date, todos & reminders",
        "  night summary                    -> completed tasks + good night",
        "  routine                          -> your daily schedule",
        "",
        "  -- Reminders (Day 4) ----------------------------------",
        "  remind me <time> <task>          -> set a reminder",
        "  list reminders                   -> show pending reminders",
        "  check reminders                  -> alert if any are due",
        "  clear reminder <#>               -> dismiss a reminder",
        "",
        "  -- Quick Note (Day 2) ---------------------------------",
        "  note <text>                      -> timestamped quick note",
        "  notes                            -> show quick notes",
        "",
        "  -- Notes (Day 3 - file per note) ----------------------",
        "  create note <title>              -> create notes/<title>.txt",
        "  write note <title> <content>     -> append content to note",
        "  list notes                       -> list all note files",
        "  open file <name>                 -> open file in default app",
        "  clear notes                      -> delete all note files",
        "",
        "  -- Todos ----------------------------------------------",
        "  create todo <task>               -> add a task",
        "  list todos                       -> show all todos",
        "  done todo <#>                    -> mark a todo complete",
        "",
        "  -- Web & Apps ----------------------------------------",
        "  search <query>                   -> Google search in browser",
        "  open <app>                       -> launch an app",
        "",
        "  -- Fun -----------------------------------------------",
        "  joke                             -> random programmer joke",
        "  quote                            -> random motivational quote",
        "",
        "  -- Control -------------------------------------------",
        "  voice                            -> toggle voice / text mode",
        "  help                             -> show this list",
        "  exit / quit / bye / stop         -> shut down Jarvis",
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
#  SMART DISPATCHERS
# ═══════════════════════════════════════════════════════════════════════════════

def _dispatch_open(args: str) -> str:
    """Routes 'open <sub> ...' to the correct specialist handler."""
    parts = args.strip().split(maxsplit=1)
    sub   = parts[0].lower() if parts else ""
    rest  = parts[1] if len(parts) > 1 else ""

    # -- Day 6 browser targets ------------------------------------------------
    if sub == "file":      return cmd_open_file(rest)
    if sub == "url":       return cmd_open_url(rest)
    if sub == "google":    return cmd_open_google(rest)
    if sub == "youtube":   return cmd_open_youtube(rest)
    if sub == "github":    return cmd_open_github(rest)
    if sub == "maps":      return cmd_open_maps(rest)
    if sub == "wikipedia": return cmd_open_wikipedia(rest)
    if sub == "reddit":    return cmd_open_reddit(rest)

    # -- Day 7 developer targets ----------------------------------------------
    if sub in ("vscode", "vs", "code"): return cmd_open_vscode(rest)
    if sub == "project":               return cmd_open_project(rest)
    if sub in ("terminal", "cmd"):     return cmd_open_terminal_cmd(rest)

    return cmd_open(args)



def _dispatch_create(args: str) -> str:
    """Routes 'create note …' or 'create todo …'."""
    parts = args.strip().split(maxsplit=1)
    sub   = parts[0].lower() if parts else ""
    rest  = parts[1] if len(parts) > 1 else ""

    if sub == "note":
        return cmd_create_note(rest)
    if sub == "todo":
        return cmd_create_todo(rest)
    return "I can create 'note' or 'todo'. Try: create note <title> | create todo <task>"


def _dispatch_write(args: str) -> str:
    """Routes 'write note <title> <content>'."""
    parts = args.strip().split(maxsplit=1)
    sub   = parts[0].lower() if parts else ""
    rest  = parts[1] if len(parts) > 1 else ""

    if sub == "note":
        return cmd_write_note(rest)
    return "Did you mean 'write note <title> <content>'?"


def _dispatch_list(args: str) -> str:
    """Routes 'list notes', 'list todos', or 'list reminders'."""
    first = args.strip().lower().split()[0] if args.strip() else ""

    if first == "notes":
        return cmd_list_notes("")
    if first in ("todos", "todo"):
        return cmd_list_todos("")
    if first in ("reminders", "reminder"):
        return cmd_list_reminders("")
    return "I can list 'notes', 'todos', or 'reminders'."


def _dispatch_done(args: str) -> str:
    """Routes 'done todo <#>'."""
    parts = args.strip().split(maxsplit=1)
    sub   = parts[0].lower() if parts else ""
    rest  = parts[1] if len(parts) > 1 else ""

    if sub == "todo":
        return cmd_done_todo(rest)
    return "Did you mean 'done todo <#>'?"


def _dispatch_clear(args: str) -> str:
    """Routes 'clear notes', 'clear reminder <#>', or 'clear history'."""
    parts = args.strip().lower().split(maxsplit=1)
    first = parts[0] if parts else ""
    rest  = parts[1] if len(parts) > 1 else ""

    if first == "notes":             return cmd_clear_notes("")
    if first in ("reminder",
                 "reminders"):       return cmd_clear_reminder(rest)
    if first == "history":           return cmd_clear_history_cmd("")
    return "Did you mean 'clear notes', 'clear reminder <#>', or 'clear history'?"


def _dispatch_check(args: str) -> str:
    """Routes 'check reminders'."""
    first = args.strip().lower().split()[0] if args.strip() else ""
    if first in ("reminders", "reminder"):
        return cmd_check_reminders("")
    return "Did you mean 'check reminders'?"


def _dispatch_morning(args: str) -> str:
    """Routes 'morning summary'."""
    first = args.strip().lower().split()[0] if args.strip() else ""
    if first == "summary":
        return cmd_morning_summary("")
    return cmd_morning_summary("")   # "morning" alone also works


def _dispatch_night(args: str) -> str:
    """Routes 'night summary'."""
    first = args.strip().lower().split()[0] if args.strip() else ""
    if first == "summary":
        return cmd_night_summary("")
    return cmd_night_summary("")     # "night" alone also works


def _dispatch_set(args: str) -> str:
    """Routes 'set name …' or 'set preference <key> <value>'."""
    parts = args.strip().split(maxsplit=1)
    sub   = parts[0].lower() if parts else ""
    rest  = parts[1] if len(parts) > 1 else ""

    if sub == "name":
        return cmd_set_name(rest)
    if sub in ("preference", "pref"):
        return cmd_set_preference(rest)
    return "Did you mean 'set name <name>' or 'set preference <key> <value>'?"


def _dispatch_get(args: str) -> str:
    """Routes 'get name' or 'get preference <key>'."""
    parts = args.strip().split(maxsplit=1)
    sub   = parts[0].lower() if parts else ""
    rest  = parts[1] if len(parts) > 1 else ""

    if sub == "name":
        return cmd_get_name(rest)
    if sub in ("preference", "pref"):
        return cmd_get_preference(rest)
    return "Did you mean 'get name' or 'get preference <key>'?"


def _dispatch_my(args: str) -> str:
    """Routes 'my profile'."""
    first = args.strip().lower().split()[0] if args.strip() else ""
    if first == "profile":
        return cmd_my_profile("")
    return cmd_my_profile("")  # 'my' alone also shows profile


def _dispatch_ai(args: str) -> str:
    """Routes 'ai status'."""
    first = args.strip().lower().split()[0] if args.strip() else ""
    if first == "status":
        return cmd_ai_status("")
    # 'ai' alone: show AI status
    return cmd_ai_status("")


def _dispatch_remind(args: str) -> str:
    """Routes 'remind me <time> <task>'."""
    return cmd_remind(args)


def _dispatch_show(args: str) -> str:
    """Routes 'show history [n]'."""
    parts = args.strip().split(maxsplit=1)
    first = parts[0].lower() if parts else ""
    n_str = parts[1] if len(parts) > 1 else ""
    if first == "history":
        return cmd_show_history(n_str)
    return f"Did you mean 'show history'? (Unknown: show {args})"


# ═══════════════════════════════════════════════════════════════════════════════
#  SMART FALLBACK — auto-search natural-language input
# ═══════════════════════════════════════════════════════════════════════════════

_QUESTION_STARTERS = {
    "what", "who", "where", "when", "why", "how", "is", "are",
    "can", "does", "do", "tell", "explain", "define",
}


def _looks_like_search(text: str) -> bool:
    """Returns True when text reads like a natural-language question."""
    t          = text.strip().lower()
    first_word = t.split()[0] if t.split() else ""
    return t.endswith("?") or first_word in _QUESTION_STARTERS


# ═══════════════════════════════════════════════════════════════════════════════
#  COMMAND REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

COMMAND_MAP: dict[str, callable] = {
    # -- Day 1 ----------------------------------------------------------------
    "time":    cmd_time,
    "date":    cmd_date,
    "hello":   cmd_hello,
    "hi":      cmd_hello,
    "hey":     cmd_hello,
    "help":    cmd_help,
    "about":   cmd_about,

    # -- Day 2 ----------------------------------------------------------------
    "search":  cmd_search,
    "open":    _dispatch_open,
    "note":    cmd_note,
    "notes":   cmd_notes,
    "joke":    cmd_joke,
    "voice":   cmd_voice,

    # -- Day 3 ----------------------------------------------------------------
    "create":  _dispatch_create,
    "write":   _dispatch_write,
    "done":    _dispatch_done,
    "sysinfo": cmd_sysinfo,
    "quote":   cmd_quote,
    "ask":     cmd_ask,

    # -- Day 4 ----------------------------------------------------------------
    "remind":    _dispatch_remind,
    "reminder":  _dispatch_remind,
    "reminders": cmd_list_reminders,
    "routine":   cmd_routine,
    "morning":   _dispatch_morning,
    "night":     _dispatch_night,
    "evening":   _dispatch_night,

    # -- Day 5 ----------------------------------------------------------------
    "chat":      cmd_chat,
    "run":       cmd_run,         # shell run (Day 5) — 'run flask' handled in _dispatch_run below
    "set":       _dispatch_set,
    "get":       _dispatch_get,
    "my":        _dispatch_my,
    "profile":   cmd_my_profile,
    "ai":        _dispatch_ai,

    # -- Day 6 ----------------------------------------------------------------
    "tips":      cmd_tips,
    "show":      _dispatch_show,
    "history":   cmd_show_history,

    # -- Day 7 ----------------------------------------------------------------
    "weather":   cmd_weather,
    "calendar":  cmd_calendar,
    "briefing":  cmd_briefing,
    "notify":    cmd_notify,
    "kill":      cmd_kill_process,
    "stats":     cmd_stats,

    # -- Unified dispatchers (updated for Day 7) ------------------------------
    "list":    _dispatch_list,
    "clear":   _dispatch_clear,
    "check":   _dispatch_check,
    "status":  cmd_status,
}


# ═══════════════════════════════════════════════════════════════════════════════
#  COMMAND ROUTER
# ═══════════════════════════════════════════════════════════════════════════════

def handle_command(user_input: str, speak_fn=None) -> str:
    """
    Parses user input, routes it to the correct handler, and returns the
    response string. Optionally calls speak_fn(response) for TTS output.
    Also runs context-aware checks (e.g., 'I'm busy' -> show todos).
    Day 5: handles the __CHAT_MODE__ sentinel from cmd_chat().
    Day 6: logs every interaction via logger.py.
    """
    # Context-aware check first
    ctx = _handle_busy(user_input)
    if ctx:
        if speak_fn:
            speak_fn(ctx)
        else:
            print(f"\n  [Jarvis] {ctx}\n")
        log_engine.log_interaction(user_input, ctx, "context")
        return ctx

    parts   = user_input.strip().split(maxsplit=1)
    keyword = parts[0].lower()
    args    = parts[1] if len(parts) > 1 else ""

    handler = COMMAND_MAP.get(keyword)

    if handler:
        response = handler(args)
        # Handle chat mode sentinel
        if response == "__CHAT_MODE__":
            ai_engine.chat_session(speak_fn)
            response = "Chat session ended."
    elif _looks_like_search(user_input):
        # Unknown input that looks like a question -> try AI first
        response = ai_engine.ask_ai(user_input)
    else:
        response = (
            f"I don't understand '{user_input}' yet.\n"
            f"  -> Try: ask {user_input}\n"
            f"  -> Or type 'help' to see all commands.\n"
            f"  -> Tip: type 'tips' for quick usage hints."
        )

    # ── Log every interaction ────────────────────────────────────────────────
    cmd_type = keyword if handler else ("ai" if _looks_like_search(user_input) else "unknown")
    log_engine.log_interaction(user_input, response, cmd_type)

    if speak_fn:
        speak_fn(response)
    else:
        print(f"\n  [Jarvis] {response}\n")

    return response
