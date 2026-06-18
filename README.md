# Jarvis — Personal AI Assistant

> A modular Python personal assistant, built to grow. Day 4: Scheduling, Reminders & Daily Routine.

---

## Project Structure

```
Jarvis/
├── main.py                  # Entry point — run this to start Jarvis
├── config.py                # All settings: paths, apps, routine, messages
├── requirements.txt         # All dependencies
│
├── core/
│   ├── __init__.py
│   ├── assistant.py         # Main loop: startup, input, routing, shutdown
│   ├── commands.py          # All command handlers + command registry
│   ├── reminders.py         # ★ Day 4 — Reminder engine (add/list/check/clear)
│   ├── greeting.py          # Time-aware greeting logic
│   ├── voice.py             # TTS + microphone input
│   └── utils.py             # Shared helpers: banner, input reader
│
├── data/
│   ├── notes.txt            # Day 2 quick notes (append-only)
│   ├── todos.json           # Day 3 structured todo list
│   ├── reminders.json       # ★ Day 4 scheduled reminders
│   └── notes/               # Day 3 per-title note files
│
└── tests/
    ├── __init__.py
    └── test_commands.py     # Unit tests for command handlers
```

---

## How to Run

```bash
# 1. Navigate to the project folder
cd path/to/Jarvis

# 2. Install dependencies (Day 2–3 features)
pip install -r requirements.txt

# 3. Start Jarvis
python main.py
```

---

## Day 4 — New Commands

| Command | What it does |
|---|---|
| `remind me 08:30 Attend class` | Set a reminder for today at 08:30 |
| `remind me tomorrow 09:00 Submit assignment` | Reminder for tomorrow |
| `remind me in 30 minutes Take a break` | Relative time reminder |
| `remind me 2026-06-20 14:00 Team meeting` | Absolute date+time reminder |
| `list reminders` | Show all pending reminders |
| `check reminders` | Check if any are overdue right now |
| `clear reminder <#>` | Dismiss a reminder by number |
| `morning summary` | Date + pending todos + upcoming reminders + motivation |
| `night summary` | Completed todos + done reminders + good night |
| `routine` | Print your daily schedule (edit in config.py) |
| `status` | Full snapshot: time, todos, reminders, OS info |

---

## All Supported Commands

### Core (Day 1)
| Command | What it does |
|---|---|
| `time` | Current time (with timezone) |
| `date` | Today's date |
| `hello` / `hi` / `hey` | Greeting |
| `about` | About Jarvis |
| `help` | Full command list |
| `exit` / `quit` / `bye` / `stop` | Shut down Jarvis |

### Voice & Notes (Day 2)
| Command | What it does |
|---|---|
| `note <text>` | Save a timestamped quick note |
| `notes` | View all quick notes |
| `search <query>` | Google search in browser |
| `open <app>` | Launch an app (browser, vscode, notepad…) |
| `joke` | Random programmer joke |
| `voice` | Toggle voice/text mode |

### Automation (Day 3)
| Command | What it does |
|---|---|
| `create note <title>` | Create a new note file |
| `write note <title> <content>` | Append to a note |
| `list notes` | List all note files |
| `open file <name>` | Open a file in the default app |
| `clear notes` | Delete all notes |
| `create todo <task>` | Add a task |
| `list todos` | Show todos |
| `done todo <#>` | Mark a todo complete |
| `sysinfo` | CPU / RAM / disk usage |
| `quote` | Motivational quote |
| `ask <question>` | Ask the AI (Gemini / OpenAI) |

---

## Configuration (config.py)

```python
VOICE_ENABLED = True          # Set False for text-only mode

REMINDERS_FILE = "data/reminders.json"
TODOS_FILE     = "data/todos.json"
NOTES_DIR      = "data/notes/"

APP_MAP = {                   # Add your own apps here
    "vscode": "code .",
    "browser": "start chrome",
    ...
}

DAILY_ROUTINE = [             # Edit your personal schedule
    "06:30  Wake up",
    "08:00  Deep work #1",
    ...
]

AI_PROVIDER = "gemini"        # or "openai" or "" (disabled)
```

---

## Run Tests

```bash
python -m pytest tests/ -v
```

---

## How to Add a New Command

1. Open `core/commands.py`
2. Write a new function:

```python
def cmd_mycommand(args: str) -> str:
    return "Your response here."
```

3. Register it in `COMMAND_MAP`:

```python
COMMAND_MAP["mycommand"] = cmd_mycommand
```

That's it. Jarvis will automatically route to it.

---

## Day 5 Ideas

| Feature | Description |
|---|---|
| 🤖 **AI Chat Mode** | Persistent conversation memory with Gemini/OpenAI |
| 💻 **Terminal Commands** | Run shell commands directly from Jarvis |
| 🎭 **Personality Modes** | Switch between formal, casual, and motivator tones |
| 🌐 **VS Code Integration** | Open files, run tasks, git status from Jarvis |
| 📊 **Habit Tracker** | Track daily habits with streaks |
| 🌤️ **Weather** | Show local weather on morning summary |
| 📆 **Calendar Integration** | Sync with Google Calendar |
| 🔔 **System Tray Notifications** | Pop-up desktop alerts for reminders |
| 📈 **Productivity Stats** | Weekly report: todos completed, reminders hit |
| 🔌 **Plugin System** | Load new commands from external files |

---

## Milestone History

| Day | Focus | Key Additions |
|---|---|---|
| Day 1 | Foundation | Greeting, time, date, help, about |
| Day 2 | Voice & I/O | TTS, microphone, search, notes, open apps |
| Day 3 | Automation | File notes, todos, sysinfo, AI (ask), quotes |
| **Day 4** | **Productivity** | **Reminders, morning/night summary, routine, enhanced status** |
