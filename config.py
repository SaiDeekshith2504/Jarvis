"""
config.py
---------
Central configuration for Jarvis.
Edit this file to customise behaviour without touching core logic.
"""

import os

# ─── Version ─────────────────────────────────────────────────────────────────
VERSION = "0.5"
DAY     = "Day 5"

# ─── Voice Mode ──────────────────────────────────────────────────────────────
# Set to True to enable microphone input + TTS output.
# Set to False for pure text mode (no audio dependencies needed).
VOICE_ENABLED = True

# ─── Paths ───────────────────────────────────────────────────────────────────
_BASE = os.path.dirname(__file__)

# Day 2 legacy: flat notes file (kept for backwards compatibility)
NOTES_FILE = os.path.join(_BASE, "data", "notes.txt")

# Day 3: individual note files live here (one .txt per note title)
NOTES_DIR = os.path.join(_BASE, "data", "notes")

# Day 3: structured todos stored as JSON
TODOS_FILE = os.path.join(_BASE, "data", "todos.json")

# Day 4: reminders stored as JSON
REMINDERS_FILE = os.path.join(_BASE, "data", "reminders.json")

# Day 5: personalization profile stored as JSON
USER_FILE = os.path.join(_BASE, "data", "user.json")

# ─── Apps ────────────────────────────────────────────────────────────────────
# Maps short names → executable / command used to launch apps.
APP_MAP: dict[str, str] = {
    "notepad":    "notepad",
    "calculator": "calc",
    "browser":    "start chrome",
    "vscode":     "code .",
    "terminal":   "start cmd",
    "explorer":   "explorer .",
    "paint":      "mspaint",
}

# ─── Daily Routine ───────────────────────────────────────────────────────────
# A simple static daily routine shown with the 'routine' command.
DAILY_ROUTINE: list[str] = [
    "06:30  Wake up & morning stretch",
    "07:00  Breakfast + review goals for the day",
    "08:00  Deep work session #1 (most important task)",
    "10:00  Short break — walk / hydrate",
    "10:15  Deep work session #2 (study / code)",
    "12:30  Lunch break",
    "13:30  Light tasks — emails, notes, planning",
    "15:00  Deep work session #3 (projects / assignments)",
    "17:00  Review todos & mark completed items",
    "18:00  Exercise / outdoor time",
    "19:30  Personal learning (reading / courses)",
    "21:00  Wind down — no screens, light journaling",
    "22:30  Sleep",
]

# ─── Motivational Morning Message ────────────────────────────────────────────
MORNING_MESSAGES: list[str] = [
    "Today is a fresh start. Make it count! 💪",
    "Every expert was once a beginner. Keep going! 🚀",
    "Your future self will thank you for the work you do today. 🌟",
    "Small steps every day lead to big results. 🎯",
    "Focus on progress, not perfection. You've got this! ✨",
]

# ─── Night Messages ───────────────────────────────────────────────────────────
NIGHT_MESSAGES: list[str] = [
    "Rest well — you've earned it. Tomorrow is another opportunity. 🌙",
    "Great work today. Recharge and come back stronger! 😴",
    "Consistency beats intensity. See you tomorrow! 🌃",
    "Sleep is productivity for your brain. Good night! 💤",
    "Today's effort is tomorrow's progress. Sleep well! ⭐",
]

# ─── AI Integration (Optional) ───────────────────────────────────────────────
# Set your API key here OR create a .env file with the key (recommended).
# Jarvis will load .env automatically if python-dotenv is installed.
#
# Supported providers: "gemini" | "openai" | "" (rule-based fallback only)
AI_PROVIDER = ""          # e.g. "gemini" or "openai"

# Optional: override the default model for the chosen provider.
# Leave empty to use the built-in default (gemini-1.5-flash / gpt-4o-mini).
AI_MODEL = ""             # e.g. "gemini-1.5-pro" or "gpt-4o"

GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY",  "")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY",  "")

# ─── Shell Command Safety (Day 5) ────────────────────────────────────────────
# Commands that start with any of these tokens are blocked by 'run <cmd>'.
BLOCKED_COMMANDS: list[str] = [
    "rm", "del", "rmdir", "rd", "format", "mkfs",
    "shutdown", "reboot", "poweroff", "halt",
    "dd", "fdisk", "diskpart",
    "curl", "wget",           # no silent downloads
    "reg", "regedit",         # no registry edits
    "net user", "net localgroup",
]

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

# ─── Quotes ──────────────────────────────────────────────────────────────────
QUOTES: list[str] = [
    "The secret of getting ahead is getting started. — Mark Twain",
    "It always seems impossible until it's done. — Nelson Mandela",
    "Don't watch the clock; do what it does. Keep going. — Sam Levenson",
    "The only way to do great work is to love what you do. — Steve Jobs",
    "Code is like humor. When you have to explain it, it's bad. — Cory House",
    "First, solve the problem. Then, write the code. — John Johnson",
    "Programs must be written for people to read. — Abelson & Sussman",
    "Simplicity is the soul of efficiency. — Austin Freeman",
    "Make it work, make it right, make it fast. — Kent Beck",
    "Talk is cheap. Show me the code. — Linus Torvalds",
]
