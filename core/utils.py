"""
core/utils.py
-------------
Shared helpers used across Jarvis modules.
Keeps presentation and input logic separate from business logic.

Day 2: Banner updated to v0.2; get_input() now supports voice fallback.
"""

import sys


JARVIS_BANNER = r"""
  ══════════════════════════════════════════════════════
    ░░░░░░  ░░░░░░  ░░░░░  ░░   ░░  ░░░░░░  ░░░░░░
         ░░ ░░  ░░ ░░  ░░  ░░  ░░   ░░      ░░
     ░░░░░  ░░░░░  ░░░░░░  ░░░░░░   ░░░░░   ░░░░░░
         ░░ ░░  ░░ ░░  ░░  ░░  ░░   ░░           ░░
    ░░░░░░  ░░  ░░ ░░  ░░  ░░   ░░  ░░░░░░  ░░░░░░

                J U S T   A   R A T H E R
               V E R Y   I N T E L L I G E N T
                      S Y S T E M

                     [ Day 2 — v0.2 ]
  ══════════════════════════════════════════════════════
"""


def display_banner() -> None:
    """Prints the Jarvis ASCII banner to the console."""
    print(JARVIS_BANNER)


def get_text_input() -> str:
    """
    Reads a line of text from the user via the CLI.
    Handles keyboard interrupt (Ctrl+C) cleanly.

    Returns:
        str: The user's input, stripped of whitespace.
             Returns empty string if nothing was typed.
    """
    try:
        raw = input("  You → ").strip()
        return raw
    except KeyboardInterrupt:
        print("\n\n  [Jarvis] Keyboard interrupt detected. Goodbye!\n")
        sys.exit(0)
    except EOFError:
        return ""


def get_input(voice_mode: bool, listen_fn=None) -> str:
    """
    Unified input function for Day 2+.

    In voice mode: calls listen_fn() (from core.voice); if that returns
    nothing, falls back to text input automatically.
    In text mode:  calls get_text_input() directly.

    Args:
        voice_mode: True → try mic first.
        listen_fn:  Callable() → str | None  (core.voice.listen).

    Returns:
        str: Non-empty user input string (may be from mic or keyboard).
    """
    if voice_mode and listen_fn:
        result = listen_fn()
        if result:
            return result
        # Mic failed — silently fall back to keyboard this round
    return get_text_input()
