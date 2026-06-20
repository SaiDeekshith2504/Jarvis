"""
core/utils.py
-------------
Shared helpers used across Jarvis modules.

Day 2: Banner updated to v0.2; get_input() supports voice fallback.
Day 3: Banner updated to v0.3; startup_capabilities() added.
Day 4: Banner updated to v0.4; startup_capabilities() shows Day 4 features.
Day 6: Banner bumped to v0.6; startup_capabilities() shows Day 6 features.
"""

import sys


JARVIS_BANNER = r"""
  ======================================================
    JARVIS -- Just A Rather Very Intelligent System

                   [ Day 6 -- v0.6 ]
  ======================================================
"""


def display_banner() -> None:
    """Prints the Jarvis ASCII banner to the console."""
    print(JARVIS_BANNER)


def startup_capabilities() -> None:
    """Prints a concise 'what can I do?' teaser on startup."""
    print("  +- What can I do? (Day 6) ---------------------------------------+")
    print("  |  open google/youtube/github/maps <query>  (browser search)   |")
    print("  |  show history   clear history   tips                          |")
    print("  |  set name <name>   my profile   set preference <key> <value>  |")
    print("  |  ask <question>    chat          ai status                    |")
    print("  |  run <command>     remind me <time> <task>                    |")
    print("  |  morning summary   night summary   routine    status          |")
    print("  |  create note/todo  list notes/todos  search   open <app>      |")
    print("  |  joke   quote   sysinfo   help (full list)                    |")
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
