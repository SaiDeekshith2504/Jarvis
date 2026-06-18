"""
core/user_profile.py
--------------------
Personalization & memory engine for Jarvis — Day 5.

Provides:
  load_profile()                     -> dict with all user data
  get_name()                         -> user's stored name (str)
  set_name(name)                     -> persist name, return confirmation
  get_preference(key)                -> read a preference value
  set_preference(key, value)         -> persist a preference, return confirmation
  list_preferences()                 -> formatted string of all preferences
  get_greeting_name()                -> name for use in greetings (or fallback)

Data is stored in data/user.json.  The file is created automatically with
sane defaults the first time Jarvis runs, so no manual setup is needed.
"""

from __future__ import annotations

import json
import os

import config


# ─── Defaults ────────────────────────────────────────────────────────────────
# These are written to user.json on first run if the file doesn't exist.

_DEFAULTS: dict = {
    "name": "",                 # User's preferred name (empty = not set)
    "preferences": {
        "theme":              "dark",
        "language":           "English",
        "preferred_browser":  "chrome",
        "preferred_editor":   "vscode",
        "ai_tone":            "friendly",   # friendly | formal | concise
    },
}


# ─── File helpers ─────────────────────────────────────────────────────────────

def _ensure_file() -> None:
    """Creates user.json with defaults if it doesn't exist yet."""
    os.makedirs(os.path.dirname(config.USER_FILE), exist_ok=True)
    if not os.path.exists(config.USER_FILE):
        _write(_DEFAULTS.copy())


def _read() -> dict:
    """Reads and returns the user profile dict."""
    _ensure_file()
    try:
        with open(config.USER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Merge with defaults so new fields are never missing
        merged = _DEFAULTS.copy()
        merged.update(data)
        if "preferences" not in merged:
            merged["preferences"] = {}
        for k, v in _DEFAULTS["preferences"].items():
            merged["preferences"].setdefault(k, v)
        return merged
    except Exception:
        return _DEFAULTS.copy()


def _write(profile: dict) -> None:
    """Writes the profile dict back to disk."""
    os.makedirs(os.path.dirname(config.USER_FILE), exist_ok=True)
    with open(config.USER_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)


# ─── Public API ───────────────────────────────────────────────────────────────

def load_profile() -> dict:
    """Returns the full user profile dictionary."""
    return _read()


def get_name() -> str:
    """Returns the stored user name, or an empty string if not set."""
    return _read().get("name", "").strip()


def set_name(name: str) -> str:
    """Stores the user's preferred name. Returns a confirmation string."""
    name = name.strip()
    if not name:
        return "Please provide a name. Usage: set name <your name>"

    profile = _read()
    profile["name"] = name
    _write(profile)
    return f"Got it! I'll call you {name} from now on."


def get_preference(key: str) -> str:
    """Returns the value for a preference key, or a 'not set' message."""
    key = key.strip().lower()
    if not key:
        return "Which preference? Usage: get preference <key>"

    prefs = _read().get("preferences", {})
    if key in prefs:
        return f"{key}: {prefs[key]}"
    return (
        f"No preference named '{key}'.\n"
        f"  Known preferences: {', '.join(prefs.keys())}\n"
        f"  Set one with: set preference {key} <value>"
    )


def set_preference(key: str, value: str) -> str:
    """Stores a key-value preference. Returns a confirmation string."""
    key   = key.strip().lower()
    value = value.strip()
    if not key:
        return "Usage: set preference <key> <value>"
    if not value:
        return f"What value should I set for '{key}'? Usage: set preference {key} <value>"

    profile = _read()
    profile.setdefault("preferences", {})[key] = value
    _write(profile)
    return f"Preference saved: {key} = {value}"


def list_preferences() -> str:
    """Returns a formatted string of all stored preferences."""
    prefs = _read().get("preferences", {})
    if not prefs:
        return "No preferences set yet. Use: set preference <key> <value>"

    lines = ["-- Your Preferences ---------------------------"]
    for k, v in prefs.items():
        lines.append(f"  {k:<22} : {v}")
    lines.append("-----------------------------------------------")
    return "\n".join(lines)


def get_greeting_name() -> str:
    """
    Returns the name to use in greetings.
    Falls back to the OS username if no name is stored.
    """
    name = get_name()
    if name:
        return name
    try:
        import getpass
        return getpass.getuser().capitalize()
    except Exception:
        return "there"
