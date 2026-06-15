"""
core/assistant.py
-----------------
The main loop of Jarvis. Handles startup, input, routing, and shutdown.

Day 2 changes:
  • Imports voice module and wires speak() / listen() into the loop.
  • Supports VOICE_ENABLED flag from config.py.
  • 'voice' command toggles voice mode at runtime.
  • handle_command() now receives speak_fn so responses are spoken.
"""

from __future__ import annotations

import config
from config import VOICE_ENABLED

from core.greeting import greet_user
from core.commands import handle_command
from core.utils    import display_banner, get_input

# ── Import voice module (graceful if unavailable) ───────────────────────────
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
    print("  Type a command below. Type 'help' to see what I can do.")
    if voice_mode:
        print("  Voice mode is ACTIVE — just speak, or type normally.\n")
    else:
        print("  Voice mode is OFF — type 'voice' to enable it.\n")


# ─── Main Loop ───────────────────────────────────────────────────────────────

def run_jarvis() -> None:
    """Entry point. Starts Jarvis and runs the main command loop."""

    # Decide initial voice state from config
    voice_mode: bool = VOICE_ENABLED and is_voice_available()

    # If config wanted voice but it's unavailable, warn the user
    if VOICE_ENABLED and not is_voice_available():
        print(
            "\n  [Jarvis] ⚠️  Voice mode requested but audio libraries are "
            "missing.\n"
            "           Running in text-only mode.\n"
            "           Install pyttsx3 + SpeechRecognition + pyaudio to enable voice.\n"
        )

    # Choose speak function based on current voice_mode
    speak_fn = speak if voice_mode else None

    # ── Startup ──────────────────────────────────────────────────────────────
    display_banner()
    greet_user(speak_fn=speak_fn)
    _startup_hints(voice_mode)

    # ── Command Loop ─────────────────────────────────────────────────────────
    while True:
        user_input = get_input(voice_mode=voice_mode, listen_fn=listen)

        if not user_input:
            continue  # Ignore empty input

        lower = user_input.lower().strip()

        # ── Exit ─────────────────────────────────────────────────────────────
        if lower in ("exit", "quit", "bye", "goodbye"):
            msg = "Goodbye! See you next time."
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
