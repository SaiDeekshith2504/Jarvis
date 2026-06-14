# Jarvis

> Day 1 Prototype — A modular Python personal assistant, built to grow.

---

## Project Structure

```
Jarvis/
├── main.py               # Entry point — run this to start Jarvis
├── requirements.txt      # Current and future dependencies
│
├── core/
│   ├── __init__.py
│   ├── assistant.py      # Main loop: startup, input, routing, shutdown
│   ├── commands.py       # All command handlers + command registry
│   ├── greeting.py       # Time-aware greeting logic
│   └── utils.py          # Shared helpers: banner, input reader
│
└── tests/
    ├── __init__.py
    └── test_commands.py  # Unit tests for command handlers
```

---

## How to Run

```bash
# 1. Navigate to the project folder
cd path/to/Jarvis

# 2. No dependencies needed for Day 1 (pure Python standard library)

# 3. Start Jarvis
python main.py
```

---

## Supported Commands (Day 1)

| Command       | What it does                      |
|---------------|-----------------------------------|
| `time`        | Tells you the current local time  |
| `date`        | Tells you today's full date       |
| `hello` / `hi`| Responds to a greeting            |
| `help`        | Lists all available commands      |
| `about`       | Information about Jarvis          |
| `exit` / `quit` / `bye` | Exits the assistant   |

---

## Run Tests

```bash
python -m pytest tests/ -v
```

---

## Day 2 Roadmap

- [ ] Add text-to-speech with `pyttsx3`
- [ ] Add voice input with `SpeechRecognition`
- [ ] Add `weather` command via a free API
- [ ] Add `note` command to save text to a file
- [ ] Add `search` command to open browser results
- [ ] Add `config.py` for user preferences (name, voice, etc.)

---

## How to Add a New Command

1. Open `core/commands.py`
2. Write a new function following this pattern:

```python
def cmd_mycommand(args: str) -> str:
    return "Your response here."
```

3. Register it in `COMMAND_MAP`:

```python
COMMAND_MAP = {
    ...
    "mycommand": cmd_mycommand,
}
```

That's it. Jarvis will automatically route to it.
