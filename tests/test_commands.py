"""
tests/test_commands.py
----------------------
Unit tests for Jarvis Day 1 + Day 2 + Day 3 command handlers.
Run with: python -m pytest tests/ -v
"""

import datetime
import json
import os
import sys
import tempfile
import unittest.mock as mock

# Make sure the project root is on the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.commands import (
    # Day 1
    cmd_time, cmd_date, cmd_hello, cmd_help, cmd_about,
    # Day 2
    cmd_search, cmd_open, cmd_note, cmd_notes, cmd_status, cmd_joke,
    # Day 3
    cmd_create_note, cmd_write_note, cmd_list_notes, cmd_open_file,
    cmd_clear_notes, cmd_create_todo, cmd_list_todos, cmd_done_todo,
    cmd_sysinfo, cmd_quote, cmd_ask,
    # Dispatchers + router
    _dispatch_create, _dispatch_list, _dispatch_done, _dispatch_open,
    COMMAND_MAP, handle_command,
)
import config


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _tmp_dir():
    """Returns a fresh temporary directory path."""
    return tempfile.mkdtemp()


def _tmp_file(suffix=".txt"):
    f = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False)
    f.close()
    return f.name


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

    def test_has_day3_keys(self):
        required = {"create", "write", "list", "done", "sysinfo", "quote", "ask"}
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

    def test_lists_day3_commands(self):
        result = cmd_help("")
        assert "create note" in result and "todo" in result and "sysinfo" in result

    def test_mentions_ai_command(self):
        assert "ask" in cmd_help("")


class TestCmdAbout:
    def test_returns_string(self):
        assert isinstance(cmd_about(""), str)

    def test_mentions_jarvis(self):
        assert "jarvis" in cmd_about("").lower()

    def test_mentions_version(self):
        assert "0.3" in cmd_about("") or "Day 3" in cmd_about("")


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
        with mock.patch("webbrowser.open"):
            result = cmd_search("machine learning")
        assert "machine learning" in result.lower()


class TestCmdOpen:
    def test_no_args_lists_apps(self):
        result = cmd_open("")
        assert "available" in result.lower() or "open" in result.lower()

    def test_unknown_app(self):
        result = cmd_open("superrareapp123")
        assert "don't know" in result.lower() or "available" in result.lower()

    def test_known_app_tries_to_open(self):
        with mock.patch("subprocess.Popen"):
            result = cmd_open("notepad")
        assert "opening" in result.lower() or "notepad" in result.lower()


class TestCmdNote:
    def test_no_args_prompts_user(self):
        result = cmd_note("")
        assert "note" in result.lower()

    def test_saves_note_to_file(self):
        tmp_path = _tmp_file()
        try:
            with mock.patch("core.commands.NOTES_FILE", tmp_path):
                result = cmd_note("Test note from pytest")
            assert "saved" in result.lower() or "got it" in result.lower()
            with open(tmp_path, "r", encoding="utf-8") as f:
                assert "Test note from pytest" in f.read()
        finally:
            os.unlink(tmp_path)


class TestCmdNotes:
    def test_no_file_returns_message(self):
        original = config.NOTES_FILE
        config.NOTES_FILE = "/nonexistent/path/notes.txt"
        try:
            result = cmd_notes("")
            assert "no notes" in result.lower() or "note" in result.lower()
        finally:
            config.NOTES_FILE = original


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
        assert cmd_joke("") in config.JOKES


# ═══════════════════════════════════════════════════════════════════════════════
#  DAY 3 TESTS — Notes (file-per-note)
# ═══════════════════════════════════════════════════════════════════════════════

class TestCmdCreateNote:
    def test_no_args_prompts(self):
        result = cmd_create_note("")
        assert "title" in result.lower() or "usage" in result.lower()

    def test_creates_file(self):
        tmp = _tmp_dir()
        with mock.patch("core.commands.NOTES_DIR", tmp):
            result = cmd_create_note("pytest_note")
        assert "created" in result.lower() or "pytest_note" in result.lower()
        files = os.listdir(tmp)
        assert any("pytest_note" in f for f in files)

    def test_duplicate_returns_message(self):
        tmp = _tmp_dir()
        with mock.patch("core.commands.NOTES_DIR", tmp):
            cmd_create_note("duplicate_test")
            result = cmd_create_note("duplicate_test")
        assert "already exists" in result.lower()


class TestCmdWriteNote:
    def test_no_args_prompts(self):
        result = cmd_write_note("")
        assert "usage" in result.lower() or "title" in result.lower()

    def test_no_content_prompts(self):
        result = cmd_write_note("justatitle")
        assert "content" in result.lower() or "usage" in result.lower()

    def test_writes_to_file(self):
        tmp = _tmp_dir()
        with mock.patch("core.commands.NOTES_DIR", tmp):
            cmd_create_note("mytest")
            result = cmd_write_note("mytest hello world content")
        assert "written" in result.lower() or "mytest" in result.lower()

    def test_auto_creates_note(self):
        tmp = _tmp_dir()
        with mock.patch("core.commands.NOTES_DIR", tmp):
            result = cmd_write_note("brand_new_note some content here")
        assert "written" in result.lower() or "brand_new_note" in result.lower()


class TestCmdListNotes:
    def test_no_dir_returns_message(self):
        with mock.patch("core.commands.NOTES_DIR", "/nonexistent/dir/xyz"):
            result = cmd_list_notes("")
        assert "no notes" in result.lower() or "folder" in result.lower()

    def test_empty_dir_returns_message(self):
        tmp = _tmp_dir()
        with mock.patch("core.commands.NOTES_DIR", tmp):
            result = cmd_list_notes("")
        assert "no notes" in result.lower() or "create note" in result.lower()

    def test_lists_files(self):
        tmp = _tmp_dir()
        open(os.path.join(tmp, "alpha.txt"), "w").close()
        open(os.path.join(tmp, "beta.txt"), "w").close()
        with mock.patch("core.commands.NOTES_DIR", tmp):
            result = cmd_list_notes("")
        assert "alpha.txt" in result and "beta.txt" in result


class TestCmdOpenFile:
    def test_no_args_prompts(self):
        result = cmd_open_file("")
        assert "usage" in result.lower() or "file" in result.lower()

    def test_nonexistent_file_returns_error(self):
        result = cmd_open_file("/totally/nonexistent/file.txt")
        assert "not found" in result.lower()

    def test_opens_existing_file(self):
        tmp = _tmp_file()
        try:
            with mock.patch("os.startfile") as mocked:
                result = cmd_open_file(tmp)
            assert "opening" in result.lower()
            mocked.assert_called_once_with(tmp)
        finally:
            os.unlink(tmp)


class TestCmdClearNotes:
    def test_no_dir_returns_message(self):
        with mock.patch("core.commands.NOTES_DIR", "/nonexistent/xyz"):
            result = cmd_clear_notes("")
        assert "no notes" in result.lower()

    def test_clears_files(self):
        tmp = _tmp_dir()
        for name in ("a.txt", "b.txt", "c.txt"):
            open(os.path.join(tmp, name), "w").close()
        with mock.patch("core.commands.NOTES_DIR", tmp):
            result = cmd_clear_notes("")
        assert "cleared" in result.lower() or "3" in result
        assert len([f for f in os.listdir(tmp) if f.endswith(".txt")]) == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  DAY 3 TESTS — Todos
# ═══════════════════════════════════════════════════════════════════════════════

class TestCmdCreateTodo:
    def test_no_args_prompts(self):
        result = cmd_create_todo("")
        assert "task" in result.lower() or "usage" in result.lower()

    def test_adds_todo(self):
        tmp = _tmp_file(".json")
        os.unlink(tmp)  # start fresh
        with mock.patch("core.commands.TODOS_FILE", tmp):
            result = cmd_create_todo("Learn FastAPI")
        assert "todo added" in result.lower() or "learn fastapi" in result.lower()
        with open(tmp, "r") as f:
            data = json.load(f)
        assert data[0]["task"] == "Learn FastAPI"
        os.unlink(tmp)


class TestCmdListTodos:
    def test_empty_returns_message(self):
        with mock.patch("core.commands.TODOS_FILE", "/nonexistent/todos.json"):
            result = cmd_list_todos("")
        assert "no todos" in result.lower() or "todo" in result.lower()

    def test_shows_tasks(self):
        tmp = _tmp_file(".json")
        todos = [
            {"id": 1, "task": "Buy milk", "done": False, "created": "2026-01-01 10:00"},
            {"id": 2, "task": "Read docs", "done": True,  "created": "2026-01-01 11:00"},
        ]
        with open(tmp, "w") as f:
            json.dump(todos, f)
        with mock.patch("core.commands.TODOS_FILE", tmp):
            result = cmd_list_todos("")
        assert "Buy milk" in result
        assert "Read docs" in result
        os.unlink(tmp)


class TestCmdDoneTodo:
    def test_non_digit_prompts(self):
        result = cmd_done_todo("abc")
        assert "number" in result.lower() or "usage" in result.lower()

    def test_marks_done(self):
        tmp = _tmp_file(".json")
        todos = [{"id": 1, "task": "Test task", "done": False, "created": "2026-01-01"}]
        with open(tmp, "w") as f:
            json.dump(todos, f)
        with mock.patch("core.commands.TODOS_FILE", tmp):
            result = cmd_done_todo("1")
        assert "done" in result.lower() or "complete" in result.lower()
        with open(tmp, "r") as f:
            data = json.load(f)
        assert data[0]["done"] is True
        os.unlink(tmp)

    def test_already_done(self):
        tmp = _tmp_file(".json")
        todos = [{"id": 1, "task": "Already done", "done": True, "created": "2026-01-01"}]
        with open(tmp, "w") as f:
            json.dump(todos, f)
        with mock.patch("core.commands.TODOS_FILE", tmp):
            result = cmd_done_todo("1")
        assert "already" in result.lower()
        os.unlink(tmp)

    def test_missing_id(self):
        with mock.patch("core.commands.TODOS_FILE", "/nonexistent/todos.json"):
            result = cmd_done_todo("99")
        assert "no todo" in result.lower() or "found" in result.lower()


# ═══════════════════════════════════════════════════════════════════════════════
#  DAY 3 TESTS — Sysinfo, Quote, Ask
# ═══════════════════════════════════════════════════════════════════════════════

class TestCmdSysinfo:
    def test_returns_string(self):
        assert isinstance(cmd_sysinfo(""), str)

    def test_contains_info_or_install_hint(self):
        result = cmd_sysinfo("")
        # Either psutil works and shows CPU/RAM, or shows install hint
        assert (
            "cpu" in result.lower()
            or "ram" in result.lower()
            or "psutil" in result.lower()
        )


class TestCmdQuote:
    def test_returns_string(self):
        assert isinstance(cmd_quote(""), str)

    def test_not_empty(self):
        assert len(cmd_quote("")) > 0

    def test_is_from_quotes_list(self):
        result = cmd_quote("")
        assert any(q in result for q in config.QUOTES)


class TestCmdAsk:
    def test_no_args_prompts(self):
        result = cmd_ask("")
        assert "usage" in result.lower() or "ask" in result.lower()

    def test_no_provider_configured(self):
        original = config.AI_PROVIDER
        config.AI_PROVIDER = ""
        try:
            result = cmd_ask("What is Python?")
            assert "not configured" in result.lower() or "ai_provider" in result.lower()
        finally:
            config.AI_PROVIDER = original

    def test_gemini_no_key_returns_message(self):
        original = config.AI_PROVIDER
        config.AI_PROVIDER = "gemini"
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            with mock.patch.object(config, "GEMINI_API_KEY", ""):
                result = cmd_ask("Hello")
        config.AI_PROVIDER = original
        assert "api key" in result.lower() or "gemini" in result.lower()


# ═══════════════════════════════════════════════════════════════════════════════
#  DAY 3 TESTS — Dispatchers & Router
# ═══════════════════════════════════════════════════════════════════════════════

class TestDispatchers:
    def test_dispatch_create_note(self):
        tmp = _tmp_dir()
        with mock.patch("core.commands.NOTES_DIR", tmp):
            result = _dispatch_create("note dispatcher_test")
        assert "created" in result.lower() or "dispatcher_test" in result.lower()

    def test_dispatch_create_todo(self):
        tmp = _tmp_file(".json")
        os.unlink(tmp)
        with mock.patch("core.commands.TODOS_FILE", tmp):
            result = _dispatch_create("todo Buy groceries")
        assert "todo added" in result.lower() or "buy groceries" in result.lower()
        os.unlink(tmp)

    def test_dispatch_create_unknown(self):
        result = _dispatch_create("something random")
        assert "note" in result.lower() or "todo" in result.lower()

    def test_dispatch_list_notes(self):
        tmp = _tmp_dir()
        with mock.patch("core.commands.NOTES_DIR", tmp):
            result = _dispatch_list("notes")
        assert isinstance(result, str)

    def test_dispatch_list_todos(self):
        with mock.patch("core.commands.TODOS_FILE", "/nonexistent/todos.json"):
            result = _dispatch_list("todos")
        assert isinstance(result, str)

    def test_dispatch_done_todo(self):
        with mock.patch("core.commands.TODOS_FILE", "/nonexistent/todos.json"):
            result = _dispatch_done("todo 99")
        assert isinstance(result, str)

    def test_dispatch_open_file(self):
        result = _dispatch_open("file /nonexistent/file.txt")
        assert "not found" in result.lower()

    def test_dispatch_open_app(self):
        with mock.patch("subprocess.Popen"):
            result = _dispatch_open("notepad")
        assert "opening" in result.lower() or "notepad" in result.lower()


class TestHandleCommand:
    def test_known_command_returns_string(self):
        result = handle_command("time", speak_fn=None)
        assert isinstance(result, str)

    def test_unknown_command_returns_suggestion(self):
        result = handle_command("foobar", speak_fn=None)
        assert "help" in result.lower() or "search" in result.lower()

    def test_question_auto_searches(self):
        with mock.patch("webbrowser.open") as wb:
            result = handle_command("what is Python?", speak_fn=None)
        assert wb.called or "question" in result.lower() or "search" in result.lower()

    def test_speak_fn_is_called(self):
        calls = []
        handle_command("joke", speak_fn=lambda t: calls.append(t))
        assert len(calls) == 1

    def test_stop_keyword_not_routed_as_command(self):
        # 'stop' is handled in assistant.py, so handle_command treats it as unknown
        result = handle_command("stop", speak_fn=None)
        assert isinstance(result, str)
