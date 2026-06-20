"""
main.py
-------
Jarvis -- Day 6  (v0.6)
Entry point. Run this file to start the assistant.

Usage:
    python main.py           # respects UI_MODE in config.py (cli / gui)
    python main.py --cli     # force CLI mode
    python main.py --gui     # force tkinter GUI mode
    python gui.py            # launch GUI directly
"""

import sys
import config


def _mode() -> str:
    """Resolves the UI mode from CLI args or config."""
    args = [a.lower() for a in sys.argv[1:]]
    if "--gui"  in args: return "gui"
    if "--cli"  in args: return "cli"
    return (config.UI_MODE or "cli").lower()


if __name__ == "__main__":
    mode = _mode()

    if mode == "gui":
        from gui import run_gui
        run_gui()
    else:
        from core.assistant import run_jarvis
        run_jarvis()
