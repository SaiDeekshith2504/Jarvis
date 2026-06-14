"""
core/assistant.py
-----------------
The main loop of Jarvis. Handles startup, input, routing,
and shutdown. This is the heart of the assistant.
"""

from core.greeting import greet_user
from core.commands import handle_command
from core.utils import display_banner, get_user_input


def run_jarvis():
    """Main entry point. Starts the assistant and runs the command loop."""

    display_banner()
    greet_user()

    print("\n  Type a command below. Type 'help' to see what I can do.\n")

    while True:
        user_input = get_user_input()

        if not user_input:
            continue  # Ignore empty input

        # Check for exit command
        if user_input.lower() in ("exit", "quit", "bye", "goodbye"):
            print("\n  [Jarvis] Goodbye! See you next time.\n")
            break

        # Route the input to the command handler
        handle_command(user_input)
