"""
core/browser.py
---------------
Browser automation helpers for Jarvis — Day 6.

All functions use the standard-library `webbrowser` module (no Selenium
required) so they work everywhere Python runs without extra installs.

Public API:
  open_url(url)            -> opens any URL in the default browser
  open_google(query)       -> Google search
  open_youtube(query)      -> YouTube search
  open_github(query)       -> GitHub search
  open_maps(query)         -> Google Maps search
  open_wikipedia(query)    -> Wikipedia search
  open_reddit(query)       -> Reddit search
"""

from __future__ import annotations

import urllib.parse
import webbrowser


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _encode(query: str) -> str:
    """URL-encodes a query string safely."""
    return urllib.parse.quote_plus(query.strip())


def _open(url: str, label: str) -> str:
    """Opens *url* and returns a confirmation message."""
    try:
        webbrowser.open(url)
        return f"🌐 Opening {label}…\n  {url}"
    except Exception as exc:
        return f"Couldn't open browser: {exc}"


# ─── Public API ───────────────────────────────────────────────────────────────

def open_url(url: str) -> str:
    """
    Opens an arbitrary URL in the default browser.
    Prepends 'https://' if no scheme is present.
    Usage: open url <url>
    """
    url = url.strip()
    if not url:
        return "Which URL? Usage: open url <url>"

    if not url.startswith(("http://", "https://", "ftp://")):
        url = "https://" + url

    return _open(url, url)


def open_google(query: str) -> str:
    """
    Opens a Google search in the default browser.
    Usage: open google <query>
    """
    if not query.strip():
        return "What should I search on Google? Usage: open google <query>"

    url = f"https://www.google.com/search?q={_encode(query)}"
    return _open(url, f"Google search for: '{query}'")


def open_youtube(query: str) -> str:
    """
    Opens a YouTube search in the default browser.
    Usage: open youtube <query>
    """
    if not query.strip():
        return "What should I search on YouTube? Usage: open youtube <query>"

    url = f"https://www.youtube.com/results?search_query={_encode(query)}"
    return _open(url, f"YouTube search for: '{query}'")


def open_github(query: str) -> str:
    """
    Opens a GitHub code search in the default browser.
    Usage: open github <query>
    """
    if not query.strip():
        return "What should I search on GitHub? Usage: open github <query>"

    url = f"https://github.com/search?q={_encode(query)}"
    return _open(url, f"GitHub search for: '{query}'")


def open_maps(query: str) -> str:
    """
    Opens Google Maps for a location search.
    Usage: open maps <location>
    """
    if not query.strip():
        return "Where should I search? Usage: open maps <location>"

    url = f"https://www.google.com/maps/search/{_encode(query)}"
    return _open(url, f"Google Maps for: '{query}'")


def open_wikipedia(query: str) -> str:
    """
    Opens a Wikipedia search in the default browser.
    Usage: open wikipedia <query>
    """
    if not query.strip():
        return "What should I look up on Wikipedia? Usage: open wikipedia <query>"

    url = f"https://en.wikipedia.org/wiki/Special:Search?search={_encode(query)}"
    return _open(url, f"Wikipedia search for: '{query}'")


def open_reddit(query: str) -> str:
    """
    Opens a Reddit search in the default browser.
    Usage: open reddit <query>
    """
    if not query.strip():
        return "What should I search on Reddit? Usage: open reddit <query>"

    url = f"https://www.reddit.com/search/?q={_encode(query)}"
    return _open(url, f"Reddit search for: '{query}'")
