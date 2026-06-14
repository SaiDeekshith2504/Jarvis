"""
core/greeting.py
----------------
Handles all greeting logic for Jarvis.
Detects the current time-of-day and greets accordingly.

Day 2+: Hook in text-to-speech here.
"""

import datetime


def get_time_of_day() -> str:
    """Returns 'morning', 'afternoon', or 'evening' based on current hour."""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    else:
        return "evening"


def greet_user():
    """Prints a personalized greeting to the console."""
    period = get_time_of_day()
    now = datetime.datetime.now().strftime("%A, %B %d %Y")

    print(f"  [Jarvis] Good {period}! Today is {now}.")
    print(f"  [Jarvis] I'm Jarvis, your personal assistant. How can I help?")
