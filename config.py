"""
config.py
---------
Central configuration for Jarvis.
Edit this file to customise behaviour without touching core logic.
"""

import os

# ─── Version ─────────────────────────────────────────────────────────────────
VERSION = "0.2"
DAY     = "Day 2"

# ─── Voice Mode ──────────────────────────────────────────────────────────────
# Set to True to enable microphone input + TTS output.
# Set to False for pure text mode (no audio dependencies needed).
VOICE_ENABLED = True

# ─── Notes ───────────────────────────────────────────────────────────────────
# File where 'note' command saves entries.
NOTES_FILE = os.path.join(os.path.dirname(__file__), "data", "notes.txt")

# ─── Apps ────────────────────────────────────────────────────────────────────
# Maps short names → executable / command used to launch apps.
# Add or change entries to match apps installed on your machine.
APP_MAP: dict[str, str] = {
    "notepad":   "notepad",
    "calculator": "calc",
    "browser":   "start chrome",           # or "start msedge" / "start firefox"
    "vscode":    "code .",
    "terminal":  "start cmd",
    "explorer":  "explorer .",
    "paint":     "mspaint",
}

# ─── Jokes ───────────────────────────────────────────────────────────────────
JOKES: list[str] = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
    "Why did the developer go broke? Because he used up all his cache.",
    "A SQL query walks into a bar, walks up to two tables and asks… 'Can I join you?'",
    "Why do Java developers wear glasses? Because they don't C#.",
    "There are only 10 kinds of people: those who understand binary, and those who don't.",
    "My code never has bugs. It just develops random features.",
    "Debugging: being the detective in a crime movie where you're also the murderer.",
    "How many programmers does it take to change a light bulb? None — that's a hardware problem.",
    "I would tell you a UDP joke, but you might not get it.",
]
