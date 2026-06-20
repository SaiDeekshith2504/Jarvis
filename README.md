# Jarvis -- Personal AI Assistant

> A modular Python personal assistant, built to grow.
> **Day 6: GUI, Browser Automation, Logging, and Improved UX.**

---

## Project Structure

```
Jarvis/
├── main.py                  # Entry point (CLI or GUI via --gui flag / config)
├── gui.py                   # ★ Day 6 -- Tkinter desktop GUI
├── config.py                # All settings: paths, apps, AI, UI mode, routine
├── requirements.txt         # All dependencies
├── .env.example             # Copy to .env and add your API keys
│
├── core/
│   ├── __init__.py
│   ├── assistant.py         # Main CLI loop: startup, input, routing, shutdown
│   ├── commands.py          # All command handlers + command registry
│   ├── ai.py                # Day 5 -- AI engine (Gemini/OpenAI + rule-based)
│   ├── user_profile.py      # Day 5 -- Personalization & memory (data/user.json)
│   ├── browser.py           # ★ Day 6 -- Browser automation (webbrowser module)
│   ├── logger.py            # ★ Day 6 -- Interaction logger (data/jarvis_log.json)
│   ├── reminders.py         # Day 4 -- Reminder engine (add/list/check/clear)
│   ├── greeting.py          # Time-aware, name-aware greeting
│   ├── voice.py             # TTS + microphone input
│   └── utils.py             # Shared helpers: banner, input reader
│
├── data/
│   ├── notes.txt            # Day 2 quick notes (append-only)
│   ├── todos.json           # Day 3 structured todo list
│   ├── reminders.json       # Day 4 scheduled reminders
│   ├── user.json            # Day 5 personalization profile (name + preferences)
│   ├── jarvis_log.json      # ★ Day 6 interaction log
│   └── notes/               # Day 3 per-title note files
│
└── tests/
    ├── __init__.py
    └── test_commands.py     # Unit tests
```

---

## How to Run

```bash
# 1. Clone / navigate to the project folder
cd path/to/Jarvis

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Configure AI provider
cp .env.example .env
# Edit .env: add GEMINI_API_KEY=... or OPENAI_API_KEY=...
# Edit config.py: set AI_PROVIDER = "gemini"  (or "openai")

# 4a. Start Jarvis in CLI mode (default)
python main.py

# 4b. Start Jarvis in GUI mode
python main.py --gui
# or:
python gui.py
```

### Choosing UI Mode

| Method | Description |
|---|---|
| `python main.py` | CLI mode (respects `UI_MODE` in `config.py`) |
| `python main.py --gui` | Force tkinter GUI window |
| `python main.py --cli` | Force CLI mode |
| `python gui.py` | Launch GUI directly |

Set `UI_MODE = "gui"` in `config.py` to always open the GUI.

---

## Day 6 -- New Features

### 🖥️ Tkinter GUI (`gui.py`)
- Dark-themed chat-style window (electric violet + navy color scheme)
- Scrollable output with color-coded user/Jarvis messages + timestamps
- `↑`/`↓` arrow keys navigate your input history
- **Voice** button toggles microphone input (if audio libs are installed)
- **Clear** resets the chat view without closing Jarvis
- Background reminder ticker (checks every 30 seconds, alerts in the UI)
- Threaded command processing (UI never freezes during AI/file operations)

### 🌐 Browser Automation (`core/browser.py`)
| Command | What it does |
|---|---|
| `open url <url>` | Open any URL in the default browser |
| `open google <query>` | Google search |
| `open youtube <query>` | YouTube search |
| `open github <query>` | GitHub code search |
| `open maps <location>` | Google Maps |
| `open wikipedia <query>` | Wikipedia search |
| `open reddit <query>` | Reddit search |

### 📋 Interaction Logging (`core/logger.py`)
| Command | What it does |
|---|---|
| `show history` | Show last 15 interactions (timestamp, input, response) |
| `show history 25` | Show last 25 interactions |
| `clear history` | Wipe the log file |

Every command is automatically logged to `data/jarvis_log.json` with:
- Timestamp
- User input
- Jarvis response
- Command type

### 💡 Tips
| Command | What it does |
|---|---|
| `tips` | Show 10 helpful usage tips for Jarvis |

---

## All Supported Commands

### Core (Day 1)
| `time` | `date` | `hello`/`hi` | `about` | `help` | `exit`/`quit`/`bye`/`stop` |

### Voice & Notes (Day 2)
| `note <text>` | `notes` | `search <query>` | `open <app>` | `joke` | `voice` |

### Automation (Day 3)
| `create note <title>` | `write note <title> <content>` | `list notes` |
| `clear notes` | `create todo <task>` | `list todos` | `done todo <#>` |
| `sysinfo` | `quote` |

### Productivity (Day 4)
| `remind me <time> <task>` | `list reminders` | `check reminders` | `clear reminder <#>` |
| `morning summary` | `night summary` | `routine` | `status` |

### AI & Personalization (Day 5)
| `ask <question>` | `chat` | `ai status` |
| `set name <name>` | `get name` | `set preference <key> <value>` | `get preference <key>` | `my profile` |
| `run <command>` |

### GUI, Browser, Logging (Day 6)
| `open url <url>` | `open google <q>` | `open youtube <q>` | `open github <q>` |
| `open maps <loc>` | `open wikipedia <q>` | `open reddit <q>` |
| `show history [n]` | `clear history` | `tips` |

---

## AI Configuration (config.py + .env)

```python
# config.py
AI_PROVIDER = "gemini"        # "gemini" | "openai" | "" (rule-based fallback)
AI_MODEL    = ""              # optional override, e.g. "gemini-1.5-pro"
UI_MODE     = "cli"           # "cli" | "gui"
```

```bash
# .env
GEMINI_API_KEY=your_key_here
# or
OPENAI_API_KEY=your_key_here
```

**Without an API key**, Jarvis uses its built-in rule-based AI to answer:
- Questions about itself ("who are you?", "what can you do?")
- Common greetings, motivation, Python questions, and more.
- It gracefully suggests using `search` for anything else.

---

## Personalization (data/user.json)

Auto-created on first run with defaults. Edit manually or via commands:

```json
{
  "name": "Pandu",
  "preferences": {
    "theme": "dark",
    "language": "English",
    "preferred_browser": "chrome",
    "preferred_editor": "vscode",
    "ai_tone": "friendly"
  }
}
```

---

## Configuration (config.py)

```python
VOICE_ENABLED    = True          # False for text-only mode
AI_PROVIDER      = "gemini"      # AI provider
AI_MODEL         = ""            # Override default model
UI_MODE          = "cli"         # "cli" or "gui"
BLOCKED_COMMANDS = [...]         # Shell commands to block for safety

APP_MAP = {                      # Apps for 'open <name>'
    "vscode": "code .",
    "browser": "start chrome",
    ...
}

DAILY_ROUTINE = [                # Your personal schedule for 'routine'
    "06:30  Wake up",
    ...
]

TIPS = [                         # Tips shown by the 'tips' command
    "💡 Type 'morning summary' first thing...",
    ...
]
```

---

## Run Tests

```bash
python -m pytest tests/ -v
```

---

## How to Add a New Command

1. Write a function in `core/commands.py`:

```python
def cmd_mycommand(args: str) -> str:
    return "Your response here."
```

2. Register it in `COMMAND_MAP`:

```python
COMMAND_MAP["mycommand"] = cmd_mycommand
```

---

## Milestone History

| Day | Focus | Key Additions |
|---|---|---|
| Day 1 | Foundation | Greeting, time, date, help, about |
| Day 2 | Voice & I/O | TTS, microphone, search, notes, open apps |
| Day 3 | Automation | File notes, todos, sysinfo, AI (ask), quotes |
| Day 4 | Productivity | Reminders, morning/night summary, routine, enhanced status |
| Day 5 | AI + Personalization | AI engine (Gemini/OpenAI/rule-based), user profile, chat mode, shell run |
| **Day 6** | **GUI + Browser + Logging** | **tkinter GUI, browser automation (7 targets), interaction logger, tips, improved UX** |

---

## Day 7+ Ideas

| Feature | Description |
|---|---|
| 📆 **Calendar Integration** | Sync with Google Calendar / remind from calendar events |
| 💻 **VS Code Integration** | Open specific files, run tasks directly from Jarvis |
| 🌤️ **Live Weather** | OpenWeatherMap API in morning summary |
| 🤖 **Advanced AI Behaviors** | System prompt with persona, memory across sessions |
| 📊 **Productivity Stats** | Weekly report: todos done, reminders hit, commands used |
| 🔔 **Desktop Notifications** | System tray / Windows toast notifications for reminders |
| 🎭 **Personality Modes** | Switch between formal, casual, motivator, and tutor tones |
| 🔌 **Plugin System** | Load new command packs from external Python files |
| 📱 **Mobile Companion App** | Simple React Native / Flutter app talking to a local Jarvis server |
| 🌐 **Full Web UI (Flask)** | Full web dashboard with history chart, stats, and remote access |
