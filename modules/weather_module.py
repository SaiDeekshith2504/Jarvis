"""
modules/weather_module.py
--------------------------
Live weather data via the OpenWeatherMap free API — Day 7.

Requires:
    pip install requests python-dotenv

Setup:
    1. Sign up free at https://openweathermap.org/api
    2. Copy your API key into .env:
           OPENWEATHER_API_KEY=your_key_here
    3. Optionally change WEATHER_CITY in config.py (default: Hyderabad)

Public API:
    get_weather()  -> dict with keys: temp, feels_like, condition,
                      description, humidity, wind_speed, city, icon
    format_weather(data) -> one-line human-readable summary string
"""

from __future__ import annotations
import os

import config

# Load .env silently
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Weather condition → ASCII emoji map
_ICONS: dict[str, str] = {
    "Clear":        "☀️",
    "Clouds":       "☁️",
    "Rain":         "🌧️",
    "Drizzle":      "🌦️",
    "Thunderstorm": "⛈️",
    "Snow":         "❄️",
    "Mist":         "🌫️",
    "Smoke":        "🌫️",
    "Haze":         "🌫️",
    "Dust":         "🌫️",
    "Fog":          "🌫️",
    "Tornado":      "🌪️",
}


def _api_key() -> str:
    return os.getenv("OPENWEATHER_API_KEY", "") or config.OPENWEATHER_API_KEY


def get_weather(city: str = "") -> dict:
    """
    Fetches current weather for *city* (falls back to config.WEATHER_CITY).

    Returns a dict on success, or a dict with key 'error' on failure.
    """
    api_key = _api_key()
    if not api_key:
        return {
            "error": (
                "OpenWeatherMap API key not set.\n"
                "  -> Add OPENWEATHER_API_KEY=your_key to your .env file\n"
                "  -> Get a free key at https://openweathermap.org/api"
            )
        }

    target_city = (city or config.WEATHER_CITY or "Hyderabad").strip()

    try:
        import requests
    except ImportError:
        return {"error": "The 'requests' package is not installed. Run: pip install requests"}

    try:
        resp = requests.get(
            _BASE_URL,
            params={
                "q":     target_city,
                "appid": api_key,
                "units": "metric",   # Celsius
            },
            timeout=8,
        )

        if resp.status_code == 401:
            return {"error": "Invalid OpenWeatherMap API key. Check your .env file."}
        if resp.status_code == 404:
            return {"error": f"City '{target_city}' not found. Check WEATHER_CITY in config.py."}
        if resp.status_code != 200:
            return {"error": f"Weather API returned HTTP {resp.status_code}."}

        data = resp.json()
        condition = data["weather"][0]["main"]
        return {
            "city":        data.get("name", target_city),
            "country":     data.get("sys", {}).get("country", ""),
            "temp":        round(data["main"]["temp"]),
            "feels_like":  round(data["main"]["feels_like"]),
            "humidity":    data["main"]["humidity"],
            "condition":   condition,
            "description": data["weather"][0]["description"].capitalize(),
            "wind_speed":  round(data["wind"]["speed"] * 3.6, 1),  # m/s -> km/h
            "icon":        _ICONS.get(condition, "🌡️"),
        }

    except requests.exceptions.ConnectionError:
        return {"error": "No internet connection. Cannot fetch weather."}
    except requests.exceptions.Timeout:
        return {"error": "Weather request timed out. Try again later."}
    except Exception as exc:
        return {"error": f"Weather fetch failed: {exc}"}


def format_weather(data: dict) -> str:
    """
    Converts a weather dict into a readable one-liner for terminal or TTS.
    Example: "Hyderabad: 31°C, Scattered clouds | Humidity 72% | Wind 18 km/h"
    """
    if "error" in data:
        return data["error"]

    icon = data.get("icon", "")
    return (
        f"{icon}  {data['city']}: {data['temp']}°C, {data['description']}  |  "
        f"Feels like {data['feels_like']}°C  |  "
        f"Humidity {data['humidity']}%  |  "
        f"Wind {data['wind_speed']} km/h"
    )
