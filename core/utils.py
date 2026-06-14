"""
core/utils.py
-------------
Shared helpers used across Jarvis modules.
Keeps presentation and input logic separate from business logic.

Day 2+: Replace get_user_input() with a voice input function here.
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

                     [ Day 1 — v0.1 ]
  ══════════════════════════════════════════════════════
"""


def display_banner():
    """Prints the Jarvis ASCII banner to the console."""
    print(JARVIS_BANNER)


def get_user_input() -> str:
    """
    Reads a line of text from the user via the CLI.
    Handles keyboard interrupt (Ctrl+C) cleanly.

    Returns:
        str: The user's input, stripped of leading/trailing whitespace.
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
