# Jarvis -- Personal AI Assistant

> A modular Python personal assistant, built to grow.
> **Day 5: AI-Powered, Personalized, Shell-Integrated.**

---

## Project Structure

```
Jarvis/
├── main.py                  # Entry point -- run this to start Jarvis
├── config.py                # All settings: paths, apps, AI, routine, messages
├── requirements.txt         # All dependencies
├── .env.example             # Copy to .env and add your API keys
│
├── core/
│   ├── __init__.py
│   ├── assistant.py         # Main loop: startup, input, routing, shutdown
│   ├── commands.py          # All command handlers + command registry
│   ├── ai.py                # ★ Day 5 -- AI engine (Gemini/OpenAI + rule-based fallback)
│   ├── user_profile.py      # ★ Day 5 -- Personalization & memory (data/user.json)
│   ├── reminders.py         # Day 4 -- Reminder engine (add/list/check/clear)
│   ├── greeting.py          # Time-aware, name-aware greeting
│   ├── voice.py             # TTS + microphone input
│   └── utils.py             # Shared helpers: banner, input reader
│
├── data/
│   ├── notes.txt            # Day 2 quick notes (append-only)
│   ├── todos.json           # Day 3 structured todo list
│   ├── reminders.json       # Day 4 scheduled reminders
│   ├── user.json            # ★ Day 5 personalization profile (name + preferences)
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

# 4. Start Jarvis
python main.py
```

---

## Day 5 -- New Commands

### Personalization
| Command | What it does |
|---|---|
| `set name Pandu` | Save your preferred name (persisted in data/user.json) |
| `get name` | Read your stored name |
| `set preference theme dark` | Save any preference as key-value |
| `get preference theme` | Read a stored preference |
| `my profile` | Show your full profile (name + all preferences) |

### AI Integration
| Command | What it does |
|---|---|
| `ask <question>` | Smart AI answer: calls Gemini/OpenAI or rule-based fallback |
| `chat` | Enter interactive AI chat mode (type `back` to exit) |
| `ai status` | Show current AI provider configuration |

### Shell Execution
| Command | What it does |
|---|---|
| `run echo hello` | Run a shell command and show output |
| `run python --version` | Check Python version |
| `run dir` | List current directory |

> **Safety**: Dangerous commands (`del`, `rm`, `shutdown`, etc.) are blocked.
> Edit `BLOCKED_COMMANDS` in `config.py` to customize.

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

---

## AI Configuration (config.py + .env)

```python
# config.py
AI_PROVIDER = "gemini"        # "gemini" | "openai" | "" (rule-based fallback)
AI_MODEL    = ""              # optional override, e.g. "gemini-1.5-pro"
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
VOICE_ENABLED = True          # False for text-only mode
AI_PROVIDER   = "gemini"      # AI provider
AI_MODEL      = ""            # Override default model
BLOCKED_COMMANDS = [...]      # Shell commands to block for safety

APP_MAP = {                   # Apps for 'open <name>'
    "vscode": "code .",
    "browser": "start chrome",
    ...
}

DAILY_ROUTINE = [             # Your personal schedule for 'routine'
    "06:30  Wake up",
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
| **Day 5** | **AI + Personalization** | **AI engine (Gemini/OpenAI/rule-based), user profile, chat mode, shell run** |

---

## Day 6+ Ideas

| Feature | Description |
|---|---|
| 🌤️ **Weather** | Live weather in morning summary (OpenWeatherMap API) |
| 📆 **Calendar Integration** | Sync with Google Calendar events |
| 🌐 **Browser Automation** | Open URLs, fill forms via Playwright/Selenium |
| 💻 **VS Code Integration** | Open files, run tasks from Jarvis |
| 📊 **Productivity Stats** | Weekly report: todos done, reminders hit, commands used |
| 🔔 **Desktop Notifications** | System tray pop-ups for overdue reminders |
| 🎭 **Personality Modes** | Switch between formal, casual, and motivator tones |
| 🖥️ **GUI / Web Interface** | Tkinter or Flask-based visual dashboard |
| 🔌 **Plugin System** | Load new command sets from external Python files |
| 💾 **Conversation History** | Multi-turn AI chat with memory across sessions |
