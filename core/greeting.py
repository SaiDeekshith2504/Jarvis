"""
core/greeting.py
----------------
Handles all greeting logic for Jarvis.
Detects the current time-of-day and greets accordingly.

Day 2: greet_user() now accepts an optional speak_fn for TTS output.
Day 5: Uses the stored user name from user_profile for a personalised greeting.
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
    Delivers a personalised greeting, using the stored user name if available.

    Args:
        speak_fn: Optional callable(str) for TTS. If None, uses print().
    """
    # Import here to avoid circular imports at module load time
    try:
        from core.user_profile import get_greeting_name
        name = get_greeting_name()
    except Exception:
        name = "there"

    period = get_time_of_day()
    now    = datetime.datetime.now().strftime("%A, %B %d %Y")

    line1 = f"Good {period}, {name}! Today is {now}."
    line2 = "I'm Jarvis, your personal assistant. How can I help?"

    if speak_fn:
        speak_fn(line1)
        speak_fn(line2)
    else:
        print(f"  [Jarvis] {line1}")
        print(f"  [Jarvis] {line2}")
