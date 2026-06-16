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
"""

from __future__ import annotations
import datetime
import json
import os
import random
import subprocess
import webbrowser

import config
from config import APP_MAP, JOKES, NOTES_FILE, NOTES_DIR, TODOS_FILE, QUOTES


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


def cmd_status(_args: str) -> str:
    """
    Shows a quick system snapshot: date/time, user, platform, Python version.
    Usage: status
    """
    import platform
    import getpass

    now     = datetime.datetime.now().strftime("%A, %B %d %Y  %I:%M %p")
    user    = getpass.getuser()
    system  = platform.system()
    release = platform.release()
    py_ver  = platform.python_version()
    machine = platform.machine()

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
    """Tells a random programming joke. Usage: joke"""
    return random.choice(JOKES)


def cmd_voice(_args: str) -> str:
    """Placeholder — actual toggle lives in assistant.py."""
    return "Voice mode toggled. (See the assistant loop for live state.)"


# ═══════════════════════════════════════════════════════════════════════════════
#  DAY 3 — NEW COMMANDS
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

    Configure in config.py:
        AI_PROVIDER    = "gemini"   (or "openai")
        GEMINI_API_KEY = "your_key"
    Or add a .env file with GEMINI_API_KEY=your_key
    """
    if not args.strip():
        return "What do you want to ask? Usage: ask <your question>"

    question = args.strip()
    provider = config.AI_PROVIDER.lower()

    # Load .env if python-dotenv is available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    # ── Gemini ────────────────────────────────────────────────────────────────
    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY") or config.GEMINI_API_KEY
        if not api_key:
            return (
                "Gemini API key not set.\n"
                "  → Add GEMINI_API_KEY=your_key to a .env file,\n"
                "    or set GEMINI_API_KEY directly in config.py."
            )
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model    = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(question)
            return response.text.strip()
        except ImportError:
            return (
                "google-generativeai is not installed.\n"
                "  → pip install google-generativeai"
            )
        except Exception as exc:
            return f"Gemini error: {exc}"

    # ── OpenAI ───────────────────────────────────────────────────────────────
    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY") or config.OPENAI_API_KEY
        if not api_key:
            return (
                "OpenAI API key not set.\n"
                "  → Add OPENAI_API_KEY=your_key to a .env file,\n"
                "    or set OPENAI_API_KEY directly in config.py."
            )
        try:
            import openai
            openai.api_key = api_key
            resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": question}],
                max_tokens=300,
            )
            return resp.choices[0].message.content.strip()
        except ImportError:
            return "openai package not installed. Run: pip install openai"
        except Exception as exc:
            return f"OpenAI error: {exc}"

    # ── Not configured ────────────────────────────────────────────────────────
    else:
        return (
            "AI mode is not configured.\n"
            "  → Set AI_PROVIDER = \"gemini\" (or \"openai\") in config.py\n"
            "  → Add your API key to a .env file or directly in config.py."
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  HELP — updated for Day 3
# ═══════════════════════════════════════════════════════════════════════════════

def cmd_help(_args: str) -> str:
    """Lists all available commands with a short description."""
    lines = [
        "Here's everything I can do:\n",
        "  ── Core ──────────────────────────────────────────────",
        "  time                          → current time",
        "  date                          → today's date",
        "  hello / hi / hey              → say hello",
        "  about                         → about Jarvis",
        "  status                        → OS + Python snapshot",
        "  sysinfo                       → CPU / RAM / disk usage",
        "",
        "  ── Quick Note (Day 2) ────────────────────────────────",
        "  note <text>                   → timestamped quick note",
        "  notes                         → show quick notes",
        "",
        "  ── Notes (Day 3 — file per note) ────────────────────",
        "  create note <title>           → create notes/<title>.txt",
        "  write note <title> <content>  → append content to note",
        "  list notes                    → list all note files",
        "  open file <name>              → open file in default app",
        "  clear notes                   → delete all note files",
        "",
        "  ── Todos ─────────────────────────────────────────────",
        "  create todo <task>            → add a task",
        "  list todos                    → show all todos",
        "  done todo <#>                 → mark a todo complete",
        "",
        "  ── Web & Apps ────────────────────────────────────────",
        "  search <query>                → Google search in browser",
        "  open <app>                    → launch an app",
        "",
        "  ── Fun ───────────────────────────────────────────────",
        "  joke                          → random programmer joke",
        "  quote                         → random motivational quote",
        "",
        "  ── AI (optional) ─────────────────────────────────────",
        "  ask <question>                → ask the AI anything",
        "",
        "  ── Control ───────────────────────────────────────────",
        "  voice                         → toggle voice / text mode",
        "  help                          → show this list",
        "  exit / quit / bye             → shut down Jarvis",
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
#  SMART DISPATCHERS
#  Multi-word commands like "create note <title>" need a dispatcher at the
#  first-word level so the registry stays clean.
# ═══════════════════════════════════════════════════════════════════════════════

def _dispatch_open(args: str) -> str:
    """Routes 'open file …' → cmd_open_file, else → cmd_open (app launcher)."""
    parts = args.strip().split(maxsplit=1)
    sub   = parts[0].lower() if parts else ""
    rest  = parts[1] if len(parts) > 1 else ""

    if sub == "file":
        return cmd_open_file(rest)
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
    """Routes 'list notes' or 'list todos'."""
    first = args.strip().lower().split()[0] if args.strip() else ""

    if first == "notes":
        return cmd_list_notes("")
    if first in ("todos", "todo"):
        return cmd_list_todos("")
    return "I can list 'notes' or 'todos'. Try: list notes | list todos"


def _dispatch_done(args: str) -> str:
    """Routes 'done todo <#>'."""
    parts = args.strip().split(maxsplit=1)
    sub   = parts[0].lower() if parts else ""
    rest  = parts[1] if len(parts) > 1 else ""

    if sub == "todo":
        return cmd_done_todo(rest)
    return "Did you mean 'done todo <#>'?"


def _dispatch_clear(args: str) -> str:
    """Routes 'clear notes'."""
    first = args.strip().lower().split()[0] if args.strip() else ""
    if first == "notes":
        return cmd_clear_notes("")
    return "Did you mean 'clear notes'?"


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
    # ── Day 1 ────────────────────────────────────────────────────────────────
    "time":    cmd_time,
    "date":    cmd_date,
    "hello":   cmd_hello,
    "hi":      cmd_hello,
    "hey":     cmd_hello,
    "help":    cmd_help,
    "about":   cmd_about,

    # ── Day 2 ────────────────────────────────────────────────────────────────
    "search":  cmd_search,
    "open":    _dispatch_open,
    "note":    cmd_note,
    "notes":   cmd_notes,
    "status":  cmd_status,
    "joke":    cmd_joke,
    "voice":   cmd_voice,

    # ── Day 3 ────────────────────────────────────────────────────────────────
    "create":  _dispatch_create,
    "write":   _dispatch_write,
    "list":    _dispatch_list,
    "done":    _dispatch_done,
    "clear":   _dispatch_clear,
    "sysinfo": cmd_sysinfo,
    "quote":   cmd_quote,
    "ask":     cmd_ask,
}


# ═══════════════════════════════════════════════════════════════════════════════
#  COMMAND ROUTER
# ═══════════════════════════════════════════════════════════════════════════════

def handle_command(user_input: str, speak_fn=None) -> str:
    """
    Parses user input, routes it to the correct handler, and returns the
    response string. Optionally calls speak_fn(response) for TTS output.
    """
    parts   = user_input.strip().split(maxsplit=1)
    keyword = parts[0].lower()
    args    = parts[1] if len(parts) > 1 else ""

    handler = COMMAND_MAP.get(keyword)

    if handler:
        response = handler(args)
    elif _looks_like_search(user_input):
        # Auto-search natural-language questions
        response = (
            f"I don't know that command, but it sounds like a question.\n"
            f"  Searching Google for '{user_input}'…"
        )
        try:
            webbrowser.open(
                f"https://www.google.com/search?q={user_input.replace(' ', '+')}"
            )
        except Exception:
            pass
    else:
        response = (
            f"I don't understand '{user_input}' yet.\n"
            f"  → Try: search {user_input}\n"
            f"  → Or type 'help' to see all commands."
        )

    if speak_fn:
        speak_fn(response)
    else:
        print(f"\n  [Jarvis] {response}\n")

    return response
