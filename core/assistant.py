"""
core/assistant.py
-----------------
The main loop of Jarvis. Handles startup, input, routing, and shutdown.

Day 2: Imports voice module, wires speak()/listen(), supports VOICE_ENABLED flag.
Day 3: Adds startup_capabilities() teaser; improved exit message.
"""

from __future__ import annotations

import config
from config import VOICE_ENABLED

from core.greeting  import greet_user
from core.commands  import handle_command
from core.utils     import display_banner, get_input, startup_capabilities

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
    print("  Type a command below — or just ask a question naturally.")
    if voice_mode:
        print("  Voice mode is ACTIVE — speak now, or type normally.\n")
    else:
        print("  Voice mode is OFF — type 'voice' to enable it.\n")


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

    # ── Command Loop ─────────────────────────────────────────────────────────
    while True:
        user_input = get_input(voice_mode=voice_mode, listen_fn=listen)

        if not user_input:
            continue

        lower = user_input.lower().strip()

        # ── Exit ─────────────────────────────────────────────────────────────
        if lower in ("exit", "quit", "bye", "goodbye", "stop"):
            msg = "Thanks for using Jarvis. See you next time! 👋"
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
