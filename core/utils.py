"""
core/utils.py
-------------
Shared helpers used across Jarvis modules.

Day 2: Banner updated to v0.2; get_input() supports voice fallback.
Day 3: Banner updated to v0.3; startup_capabilities() added.
Day 4: Banner updated to v0.4; startup_capabilities() shows Day 4 features.
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

                     [ Day 5 -- v0.5 ]
  ══════════════════════════════════════════════════════
"""


def display_banner() -> None:
    """Prints the Jarvis ASCII banner to the console."""
    print(JARVIS_BANNER)


def startup_capabilities() -> None:
    """Prints a concise 'what can I do?' teaser on startup."""
    print("  +- What can I do? -----------------------------------------------+")
    print("  |  set name <name>    my profile    set preference <key> <value>  |")
    print("  |  ask <question>     chat          ai status                     |")
    print("  |  run <command>      remind me <time> <task>                     |")
    print("  |  morning summary    night summary   routine    status           |")
    print("  |  create note/todo   list notes/todos   search   open <app>     |")
    print("  |  joke   quote   sysinfo   help (full list)                     |")
    print("  +----------------------------------------------------------------+")
    print()


def get_text_input() -> str:
    """
    Reads a line of text from the user via the CLI.
    Handles keyboard interrupt (Ctrl+C) cleanly.
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
    """
    if voice_mode and listen_fn:
        result = listen_fn()
        if result:
            return result
    return get_text_input()
