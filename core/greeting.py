"""
core/greeting.py
----------------
Handles all greeting logic for Jarvis.
Detects the current time-of-day and greets accordingly.

Day 2: greet_user() now accepts an optional speak_fn for TTS output.
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


def greet_user(speak_fn=None) -> None:
    """
    Delivers a personalised greeting.

    Args:
        speak_fn: Optional callable(str) for TTS. If None, uses print().
    """
    period = get_time_of_day()
    now    = datetime.datetime.now().strftime("%A, %B %d %Y")

    line1 = f"Good {period}! Today is {now}."
    line2 = "I'm Jarvis, your personal assistant. How can I help?"

    if speak_fn:
        speak_fn(line1)
        speak_fn(line2)
    else:
        print(f"  [Jarvis] {line1}")
        print(f"  [Jarvis] {line2}")
