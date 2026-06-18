"""
core/ai.py
----------
AI integration layer for Jarvis — Day 5.

Provides:
  ask_ai(question)       -> call Gemini/OpenAI API, or fall back to rule-based answers
  chat_session(speak_fn) -> interactive multi-turn chat loop
  ai_status()            -> human-readable config summary

The module is completely optional: if no API key is set Jarvis continues
to work with a friendly rule-based fallback so the experience never breaks.
"""

from __future__ import annotations

import os
import re

import config


# ─── Rule-based fallback answers ─────────────────────────────────────────────
# Ordered list of (pattern, answer) tuples.
# Patterns are compiled case-insensitively at import time.

_RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b(your name|who are you|what are you|what is your name)\b", re.I),
     "I'm Jarvis — your personal Python assistant. I get smarter every day!"),

    (re.compile(r"\b(who (made|built|created|programmed) you|who is your (creator|developer|author))\b", re.I),
     "I was built by a developer learning Python, growing one day at a time. "
     "Each day adds new features — you're on Day 5!"),

    (re.compile(r"\bwhat (can|do) you do\b", re.I),
     "I can manage notes, todos, reminders, run a morning/night summary, "
     "search the web, launch apps, run shell commands, and even chat using AI. "
     "Type 'help' for the full list."),

    (re.compile(r"\b(how are you|how do you do|how's it going|are you ok)\b", re.I),
     "Running smoothly, thanks for asking! All systems are operational. How can I help?"),

    (re.compile(r"\b(what time is it|current time|tell me the time)\b", re.I),
     "Use the 'time' command and I'll give you the exact local time with timezone."),

    (re.compile(r"\b(what('s| is) (today|the date)|today'?s date)\b", re.I),
     "Use the 'date' command for today's full date."),

    (re.compile(r"\b(hello|hi|hey|greetings|good (morning|afternoon|evening))\b", re.I),
     "Hey! Great to hear from you. What can I do for you today?"),

    (re.compile(r"\b(thank(s| you)|cheers|appreciate)\b", re.I),
     "You're very welcome! Happy to help anytime."),

    (re.compile(r"\b(joke|funny|make me laugh)\b", re.I),
     "Use the 'joke' command and I'll tell you a programmer joke!"),

    (re.compile(r"\b(motivat|inspir|quote)\b", re.I),
     "Use the 'quote' command for a motivational quote to keep you going!"),

    (re.compile(r"\b(python|programming|coding|developer|software)\b", re.I),
     "Python is a fantastic choice! Clean syntax, huge ecosystem, and it's what "
     "powers me. Keep coding — consistency beats talent every time."),

    (re.compile(r"\b(weather|temperature|forecast)\b", re.I),
     "I don't have live weather data yet — that's a great Day 6 feature! "
     "For now, try: search weather <your city>"),

    (re.compile(r"\b(todo|task|remind|schedule|plan)\b", re.I),
     "I can help you manage tasks and reminders! "
     "Try: 'create todo <task>', 'remind me 09:00 <task>', or 'morning summary'."),
]


def _rule_based_answer(question: str) -> str | None:
    """Checks the question against known patterns. Returns an answer or None."""
    for pattern, answer in _RULES:
        if pattern.search(question):
            return answer
    return None


# ─── API call helpers ─────────────────────────────────────────────────────────

def _call_gemini(question: str, api_key: str) -> str:
    """Sends question to Google Gemini and returns the text response."""
    try:
        import google.generativeai as genai  # type: ignore
        genai.configure(api_key=api_key)
        model    = genai.GenerativeModel(config.AI_MODEL or "gemini-1.5-flash")
        response = model.generate_content(question)
        return response.text.strip()
    except ImportError:
        return (
            "The 'google-generativeai' package is not installed.\n"
            "  Run: pip install google-generativeai"
        )
    except Exception as exc:
        return f"Gemini error: {exc}"


def _call_openai(question: str, api_key: str) -> str:
    """Sends question to OpenAI Chat Completions and returns the reply."""
    try:
        import openai  # type: ignore
        client = openai.OpenAI(api_key=api_key)
        resp   = client.chat.completions.create(
            model=config.AI_MODEL or "gpt-4o-mini",
            messages=[{"role": "user", "content": question}],
            max_tokens=400,
        )
        return resp.choices[0].message.content.strip()
    except ImportError:
        return (
            "The 'openai' package is not installed.\n"
            "  Run: pip install openai"
        )
    except Exception as exc:
        return f"OpenAI error: {exc}"


# ─── Public API ───────────────────────────────────────────────────────────────

def ask_ai(question: str) -> str:
    """
    Main entry point for AI questions.

    Priority:
      1. If an API key is set → call the configured provider.
      2. Otherwise → try rule-based fallback.
      3. If no rule matches → politely say AI is not configured.
    """
    if not question.strip():
        return "What would you like to ask? Usage: ask <your question>"

    # Load .env if available (silently skip if python-dotenv is missing)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    provider = (config.AI_PROVIDER or "").strip().lower()

    # ── Gemini ────────────────────────────────────────────────────────────────
    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY") or config.GEMINI_API_KEY
        if api_key:
            return _call_gemini(question, api_key)
        return (
            "Gemini API key not set.\n"
            "  -> Add GEMINI_API_KEY=your_key to a .env file\n"
            "  -> Or set it in config.py"
        )

    # ── OpenAI ────────────────────────────────────────────────────────────────
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY") or config.OPENAI_API_KEY
        if api_key:
            return _call_openai(question, api_key)
        return (
            "OpenAI API key not set.\n"
            "  -> Add OPENAI_API_KEY=your_key to a .env file\n"
            "  -> Or set it in config.py"
        )

    # ── No provider configured — use rule-based fallback ──────────────────────
    answer = _rule_based_answer(question)
    if answer:
        return answer

    # Final fallback
    return (
        "I don't have an AI provider configured to answer that.\n"
        "  -> Set AI_PROVIDER = \"gemini\" or \"openai\" in config.py\n"
        "  -> Add your API key to a .env file\n"
        "  -> Or try: search " + question.replace(" ", "+")
    )


def ai_status() -> str:
    """Returns a human-readable summary of the current AI configuration."""
    provider = (config.AI_PROVIDER or "none").strip().lower()

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    if provider == "gemini":
        key = os.getenv("GEMINI_API_KEY") or config.GEMINI_API_KEY
        model = config.AI_MODEL or "gemini-1.5-flash"
        status = "configured" if key else "NO KEY SET"
        return f"AI: Gemini ({model}) -- {status}"

    if provider == "openai":
        key = os.getenv("OPENAI_API_KEY") or config.OPENAI_API_KEY
        model = config.AI_MODEL or "gpt-4o-mini"
        status = "configured" if key else "NO KEY SET"
        return f"AI: OpenAI ({model}) -- {status}"

    return "AI: rule-based fallback only (no provider configured)"


def chat_session(speak_fn=None) -> None:
    """
    Enters an interactive chat loop where every message is treated as ask_ai().
    Type 'exit', 'stop', or 'back' to return to the main Jarvis loop.
    """
    _print = speak_fn or (lambda t: print(f"\n  [Jarvis] {t}\n"))

    _print(
        "Chat mode activated! Every message goes straight to AI.\n"
        "  Type 'exit', 'stop', or 'back' to return to normal mode."
    )

    while True:
        try:
            user_input = input("  Chat -> ").strip()
        except (KeyboardInterrupt, EOFError):
            _print("Leaving chat mode.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "stop", "quit", "back", "bye"):
            _print("Leaving chat mode. Back to command mode!")
            break

        answer = ask_ai(user_input)
        _print(answer)
