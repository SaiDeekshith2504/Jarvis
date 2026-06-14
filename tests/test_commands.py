"""
tests/test_commands.py
----------------------
Unit tests for Jarvis Day 1 command handlers.
Run with: python -m pytest tests/ -v
"""

import datetime
import sys
import os

# Make sure the project root is on the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.commands import cmd_time, cmd_date, cmd_hello, cmd_help, cmd_about, COMMAND_MAP


class TestCommandMap:
    def test_command_map_has_required_keys(self):
        required = {"time", "date", "hello", "hi", "help"}
        assert required.issubset(set(COMMAND_MAP.keys()))

    def test_all_values_are_callable(self):
        for key, fn in COMMAND_MAP.items():
            assert callable(fn), f"Command '{key}' is not callable"


class TestCmdTime:
    def test_returns_string(self):
        result = cmd_time("")
        assert isinstance(result, str)

    def test_contains_time_keyword(self):
        result = cmd_time("")
        assert "time" in result.lower()


class TestCmdDate:
    def test_returns_string(self):
        result = cmd_date("")
        assert isinstance(result, str)

    def test_contains_current_year(self):
        result = cmd_date("")
        assert str(datetime.datetime.now().year) in result


class TestCmdHello:
    def test_returns_string(self):
        result = cmd_hello("")
        assert isinstance(result, str)

    def test_not_empty(self):
        result = cmd_hello("")
        assert len(result) > 0


class TestCmdHelp:
    def test_returns_string(self):
        result = cmd_help("")
        assert isinstance(result, str)

    def test_lists_at_least_one_command(self):
        result = cmd_help("")
        assert "time" in result or "date" in result


class TestCmdAbout:
    def test_returns_string(self):
        result = cmd_about("")
        assert isinstance(result, str)

    def test_mentions_jarvis(self):
        result = cmd_about("")
        assert "Jarvis" in result or "jarvis" in result.lower()
