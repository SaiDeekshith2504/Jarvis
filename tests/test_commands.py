"""
tests/test_commands.py
----------------------
Unit tests for Jarvis Day 1 + Day 2 command handlers.
Run with: python -m pytest tests/ -v
"""

import datetime
import os
import sys
import tempfile

# Make sure the project root is on the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.commands import (
    cmd_time, cmd_date, cmd_hello, cmd_help, cmd_about,
    cmd_search, cmd_open, cmd_note, cmd_notes, cmd_status, cmd_joke,
    COMMAND_MAP, handle_command,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  DAY 1 TESTS (unchanged)
# ═══════════════════════════════════════════════════════════════════════════════

class TestCommandMap:
    def test_has_day1_keys(self):
        required = {"time", "date", "hello", "hi", "help"}
        assert required.issubset(set(COMMAND_MAP.keys()))

    def test_has_day2_keys(self):
        required = {"search", "open", "note", "notes", "status", "joke"}
        assert required.issubset(set(COMMAND_MAP.keys()))

    def test_all_values_are_callable(self):
        for key, fn in COMMAND_MAP.items():
            assert callable(fn), f"Command '{key}' is not callable"


class TestCmdTime:
    def test_returns_string(self):
        assert isinstance(cmd_time(""), str)

    def test_contains_time_keyword(self):
        assert "time" in cmd_time("").lower()


class TestCmdDate:
    def test_returns_string(self):
        assert isinstance(cmd_date(""), str)

    def test_contains_current_year(self):
        assert str(datetime.datetime.now().year) in cmd_date("")


class TestCmdHello:
    def test_returns_string(self):
        assert isinstance(cmd_hello(""), str)

    def test_not_empty(self):
        assert len(cmd_hello("")) > 0


class TestCmdHelp:
    def test_returns_string(self):
        assert isinstance(cmd_help(""), str)

    def test_lists_day1_commands(self):
        result = cmd_help("")
        assert "time" in result and "date" in result

    def test_lists_day2_commands(self):
        result = cmd_help("")
        assert "search" in result and "note" in result and "joke" in result


class TestCmdAbout:
    def test_returns_string(self):
        assert isinstance(cmd_about(""), str)

    def test_mentions_jarvis(self):
        assert "jarvis" in cmd_about("").lower()

    def test_mentions_version(self):
        assert "0.2" in cmd_about("") or "Day 2" in cmd_about("")


# ═══════════════════════════════════════════════════════════════════════════════
#  DAY 2 TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestCmdSearch:
    def test_returns_string(self):
        assert isinstance(cmd_search("python"), str)

    def test_no_args_prompts_user(self):
        result = cmd_search("")
        assert "search" in result.lower()

    def test_with_query_mentions_query(self):
        # We can't actually open a browser in tests, but we can patch webbrowser.
        import unittest.mock as mock
        with mock.patch("webbrowser.open"):
            result = cmd_search("machine learning")
        assert "machine learning" in result.lower()


class TestCmdOpen:
    def test_no_args_lists_apps(self):
        result = cmd_open("")
        # Should mention available apps
        assert "available" in result.lower() or "open" in result.lower()

    def test_unknown_app(self):
        result = cmd_open("superrareapp123")
        assert "don't know" in result.lower() or "available" in result.lower()

    def test_known_app_tries_to_open(self):
        import unittest.mock as mock
        with mock.patch("subprocess.Popen"):
            result = cmd_open("notepad")
        # Should confirm it's opening
        assert "opening" in result.lower() or "notepad" in result.lower()


class TestCmdNote:
    def test_no_args_prompts_user(self):
        result = cmd_note("")
        assert "note" in result.lower()

    def test_saves_note_to_file(self):
        import unittest.mock as mock

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                         delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Patch the name that cmd_note actually uses at runtime
            with mock.patch("core.commands.NOTES_FILE", tmp_path):
                result = cmd_note("Test note from pytest")

            assert "saved" in result.lower() or "got it" in result.lower()

            with open(tmp_path, "r", encoding="utf-8") as f:
                contents = f.read()
            assert "Test note from pytest" in contents
        finally:
            os.unlink(tmp_path)


class TestCmdNotes:
    def test_no_file_returns_message(self):
        import config
        original_path = config.NOTES_FILE
        config.NOTES_FILE = "/nonexistent/path/notes.txt"
        try:
            result = cmd_notes("")
            assert "no notes" in result.lower() or "note" in result.lower()
        finally:
            config.NOTES_FILE = original_path


class TestCmdStatus:
    def test_returns_string(self):
        assert isinstance(cmd_status(""), str)

    def test_contains_system_info(self):
        result = cmd_status("")
        assert "user" in result.lower() or "python" in result.lower()


class TestCmdJoke:
    def test_returns_string(self):
        assert isinstance(cmd_joke(""), str)

    def test_not_empty(self):
        assert len(cmd_joke("")) > 0

    def test_is_from_joke_list(self):
        from config import JOKES
        result = cmd_joke("")
        assert result in JOKES


class TestHandleCommand:
    def test_known_command_returns_string(self):
        collected = []
        result = handle_command("time", speak_fn=None)
        assert isinstance(result, str)

    def test_unknown_command_returns_suggestion(self):
        result = handle_command("foobar", speak_fn=None)
        assert "help" in result.lower()

    def test_speak_fn_is_called(self):
        calls = []
        handle_command("joke", speak_fn=lambda t: calls.append(t))
        assert len(calls) == 1
