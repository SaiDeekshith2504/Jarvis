"""
core/assistant.py
-----------------
The main loop of Jarvis. Handles startup, input, routing, and shutdown.

Day 2: Imports voice module, wires speak()/listen(), supports VOICE_ENABLED flag.
Day 3: Adds startup_capabilities() teaser; improved exit message.
Day 4: Adds background reminder check on every loop iteration;
       'What can I do for you today?' prompt on startup;
       cleaner goodbye message; stop/exit aliases.
Day 5: Loads user profile on startup; greets by stored name;
       goodbye mentions the user by name.
Day 7: Auto morning briefing on startup (if AUTO_MORNING_BRIEFING=True in config).
"""

from __future__ import annotations

import config
from config import VOICE_ENABLED

from core.greeting  import greet_user
from core.commands  import handle_command
from core.utils     import display_banner, get_input, startup_capabilities
from core           import reminders as rem_engine
from core           import user_profile as profile_engine

# Day 7 morning briefing (graceful if modules not installed yet)
try:
    from modules.morning_briefing import run_morning_briefing
    _BRIEFING_OK = True
except Exception:
    _BRIEFING_OK = False

# ── Import voice module (graceful if unavailable) ────────────────────────────
try:
    from core.voice import speak, listen, is_voice_available
    _voice_module_ok = True
except ImportError:
    _voice_module_ok = False

    def speak(text: str) -> None:           # type: ignore[misc]
        print(f"\n  [Jarvis] {text}\n")

    def listen():                           # type: ignore[misc]
        return None

    def is_voice_available() -> bool:       # type: ignore[misc]
        return False


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _print_voice_status(enabled: bool) -> None:
    mode = "ON  🎙️" if enabled else "OFF ⌨️"
    print(f"\n  [Jarvis] Voice mode: {mode}\n")


def _startup_hints(voice_mode: bool) -> None:
    name = profile_engine.get_name()
    if name:
        print(f"  Welcome back, {name}! What can I do for you today?")
    else:
        print("  What can I do for you today? (Tip: 'set name <name>' to personalise me)")
    print("  Type a command or ask a question naturally.")
    if voice_mode:
        print("  Voice mode is ACTIVE -- speak now, or type normally.\n")
    else:
        print("  Voice mode is OFF -- type 'voice' to enable it.\n")


def _check_and_notify_reminders(speak_fn) -> None:
    """
    Runs the reminder check and prints/speaks any due reminders.
    Called on every loop iteration so nothing is missed.
    """
    alert = rem_engine.check_reminders()
    if alert:
        if speak_fn:
            speak_fn(alert)
        else:
            print(f"\n  [Jarvis] {alert}\n")


# ─── Main Loop ───────────────────────────────────────────────────────────────

def run_jarvis() -> None:
    """Entry point. Starts Jarvis and runs the main command loop."""

    voice_mode: bool = VOICE_ENABLED and is_voice_available()

    if VOICE_ENABLED and not is_voice_available():
        print(
            "\n  [Jarvis] ⚠️  Voice mode requested but audio libraries are missing.\n"
            "           Running in text-only mode.\n"
            "           Install pyttsx3 + SpeechRecognition + pyaudio to enable voice.\n"
        )

    speak_fn = speak if voice_mode else None

    # ── Startup ──────────────────────────────────────────────────────────────
    display_banner()
    greet_user(speak_fn=speak_fn)
    startup_capabilities()
    _startup_hints(voice_mode)

    # Day 7: Auto morning briefing
    if _BRIEFING_OK and getattr(config, "AUTO_MORNING_BRIEFING", True):
        print("\n  [Jarvis] Generating morning briefing...\n")
        try:
            run_morning_briefing(speak_fn=speak_fn, source="startup")
        except Exception as _be:
            print(f"  [Jarvis] Morning briefing skipped: {_be}")

    # Check for any overdue reminders right on startup
    _check_and_notify_reminders(speak_fn)

    # ── Command Loop ─────────────────────────────────────────────────────────
    while True:
        # Passive reminder check on every loop (lightweight — just reads JSON)
        _check_and_notify_reminders(speak_fn)

        user_input = get_input(voice_mode=voice_mode, listen_fn=listen)

        if not user_input:
            continue

        lower = user_input.lower().strip()

        # ── Exit ─────────────────────────────────────────────────────────────
        if lower in ("exit", "quit", "bye", "goodbye", "stop", "close"):
            name = profile_engine.get_name()
            farewell = f", {name}" if name else ""
            msg = (
                f"Thanks for using Jarvis{farewell}. Goodbye!\n"
                "  Stay productive -- see you next time!"
            )
            if speak_fn:
                speak_fn(msg)
            else:
                print(f"\n  [Jarvis] {msg}\n")
            break

        # ── Voice toggle ─────────────────────────────────────────────────────
        if lower == "voice":
            if not is_voice_available():
                speak("Voice mode unavailable — audio libraries are not installed.")
                continue
            voice_mode = not voice_mode
            speak_fn   = speak if voice_mode else None
            _print_voice_status(voice_mode)
            continue

        # ── Route to command handler ──────────────────────────────────────────
        handle_command(user_input, speak_fn=speak_fn)
