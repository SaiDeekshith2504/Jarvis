"""
core/voice.py
-------------
Voice I/O module for Jarvis — Day 2.

Provides:
  speak(text)   → text-to-speech output (pyttsx3, offline)
  listen()      → microphone input → returns text string

If dependencies are missing the module degrades gracefully: speak() just
prints, and listen() falls back to keyboard input. This keeps the rest of
Jarvis completely independent of audio hardware.
"""

from __future__ import annotations
import sys

# ── Try to import TTS ────────────────────────────────────────────────────────
try:
    import pyttsx3
    _tts_engine = pyttsx3.init()
    _tts_engine.setProperty("rate", 165)      # words-per-minute (default ~200)
    _tts_engine.setProperty("volume", 0.95)   # 0.0–1.0
    _TTS_AVAILABLE = True
except Exception:
    _TTS_AVAILABLE = False

# ── Try to import Speech Recognition ────────────────────────────────────────
try:
    import speech_recognition as sr
    _recogniser = sr.Recognizer()
    _recogniser.pause_threshold = 0.8   # seconds of silence = end of phrase
    _SR_AVAILABLE = True
except Exception:
    _SR_AVAILABLE = False


# ─── Public API ──────────────────────────────────────────────────────────────

def speak(text: str) -> None:
    """
    Speaks *text* aloud. Falls back to a plain print if TTS is unavailable.
    Always also prints the response so text-only users see it.
    """
    print(f"\n  [Jarvis] {text}\n")
    if _TTS_AVAILABLE:
        try:
            _tts_engine.say(text)
            _tts_engine.runAndWait()
        except Exception as exc:
            # TTS can occasionally fail mid-session — never crash the loop.
            print(f"  [voice] TTS error: {exc}")


def listen(timeout: int = 5, phrase_limit: int = 8) -> str | None:
    """
    Listens via the default microphone and returns recognised text (lowercase).

    Args:
        timeout:      Seconds to wait for speech to start.
        phrase_limit: Maximum seconds of audio to capture.

    Returns:
        Recognised text string, or None if nothing was understood / error.
    """
    if not _SR_AVAILABLE:
        return None   # Caller should fall back to text input.

    try:
        with sr.Microphone() as source:
            print("  [Jarvis] Listening… (speak now)")
            _recogniser.adjust_for_ambient_noise(source, duration=0.5)
            audio = _recogniser.listen(source, timeout=timeout,
                                       phrase_time_limit=phrase_limit)

        text = _recogniser.recognize_google(audio)
        print(f"  [You said] {text}")
        return text.lower().strip()

    except sr.WaitTimeoutError:
        speak("I didn't hear anything. Try again.")
    except sr.UnknownValueError:
        speak("Sorry, I couldn't understand that.")
    except sr.RequestError as exc:
        speak(f"Speech service error: {exc}")
    except Exception as exc:
        speak(f"Unexpected voice error: {exc}")

    return None


def is_voice_available() -> bool:
    """Returns True only when both TTS and SR are working."""
    return _TTS_AVAILABLE and _SR_AVAILABLE
