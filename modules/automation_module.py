"""
modules/automation_module.py
------------------------------
VS Code and developer workflow automation for Jarvis — Day 7.

All functions use subprocess / os.startfile so no extra libraries needed.
Extend APP_SHORTCUTS and PROJECT_MAP in config.py to add more targets.

Public API:
    open_vscode(path)          -> opens VS Code (optionally at a path)
    open_project(name)         -> opens a known project by short name
    open_github(repo)          -> opens GitHub (optionally a specific repo)
    run_flask_app(path)        -> starts a Flask dev server
    open_terminal(path)        -> opens Windows Terminal or CMD at a path
    launch_app(name)           -> generic launcher (checks APP_SHORTCUTS)
    kill_process(name)         -> kills a running process by name
"""

from __future__ import annotations

import os
import subprocess
import sys
import webbrowser
from pathlib import Path

import config


# ─── Safe subprocess helper ───────────────────────────────────────────────────

def _run(cmd: str | list, cwd: str | None = None, shell: bool = True) -> str:
    """Runs a command, returns stdout/stderr, never crashes Jarvis."""
    try:
        result = subprocess.Popen(
            cmd,
            shell=shell,
            cwd=cwd or None,
        )
        return f"Launched (PID {result.pid})."
    except FileNotFoundError:
        return f"Command not found: {cmd}"
    except Exception as exc:
        return f"Launch failed: {exc}"


# ─── VS Code ─────────────────────────────────────────────────────────────────

def open_vscode(path: str = "") -> str:
    """
    Opens VS Code.
    Usage: open vscode            → opens VS Code in current dir
           open vscode <path>     → opens VS Code at the given path
    """
    target = path.strip() or "."
    # 'code' is the VS Code CLI command; it must be on PATH
    result = _run(f'code "{target}"')
    if "not found" in result.lower():
        # Fallback: try common Windows install path
        vscode_exe = r"C:\Users\pandu\AppData\Local\Programs\Microsoft VS Code\Code.exe"
        if os.path.exists(vscode_exe):
            return _run(f'"{vscode_exe}" "{target}"')
        return (
            "VS Code not found. Make sure 'code' is on your PATH.\n"
            "  In VS Code: press Ctrl+Shift+P → 'Install code command in PATH'."
        )
    return f"Opening VS Code at: {os.path.abspath(target)}"


def open_project(name: str = "") -> str:
    """
    Opens a known project by short name (defined in config.PROJECT_MAP).
    Usage: open project jarvis   → opens the Jarvis project in VS Code
    """
    name = name.strip().lower()
    if not name:
        # List available projects
        if config.PROJECT_MAP:
            keys = ", ".join(config.PROJECT_MAP.keys())
            return f"Which project? Available: {keys}"
        return "No projects configured. Add paths to PROJECT_MAP in config.py."

    path = config.PROJECT_MAP.get(name)
    if not path:
        available = ", ".join(config.PROJECT_MAP.keys()) if config.PROJECT_MAP else "none"
        return f"Unknown project '{name}'. Available: {available}"

    if not os.path.exists(path):
        return f"Project path not found: {path}\n  Update PROJECT_MAP in config.py."

    return open_vscode(path)


# ─── GitHub ───────────────────────────────────────────────────────────────────

def open_github(query: str = "") -> str:
    """
    Opens GitHub in the browser.
    Usage: open github            → opens your GitHub profile
           open github jarvis     → opens your Jarvis repo
           open github flask      → opens github.com/search?q=flask
    """
    query = query.strip()

    # First check if it's a known repo shortcut
    if query and query.lower() in config.GITHUB_REPOS:
        url = config.GITHUB_REPOS[query.lower()]
        webbrowser.open(url)
        return f"Opening GitHub repo: {url}"

    if not query:
        url = config.GITHUB_PROFILE or "https://github.com"
        webbrowser.open(url)
        return f"Opening GitHub: {url}"

    # Generic search
    url = f"https://github.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Searching GitHub for: '{query}'"


# ─── Flask ────────────────────────────────────────────────────────────────────

def run_flask_app(path: str = "") -> str:
    """
    Starts a Flask development server.
    Usage: run flask              → runs app.py in the project root
           run flask <path>       → runs the given Python file
    """
    target = path.strip()
    if not target:
        # Look for app.py or wsgi.py in project root
        for candidate in ("app.py", "wsgi.py", "run.py", "server.py"):
            candidate_path = Path(config._BASE) / candidate
            if candidate_path.exists():
                target = str(candidate_path)
                break

    if not target or not os.path.exists(target):
        return (
            "No Flask app found. Usage: run flask <path/to/app.py>\n"
            "  Or place app.py in your project root."
        )

    app_dir = str(Path(target).parent)
    cmd = f'start cmd /k "python \"{target}\""'
    _run(cmd)
    return f"Starting Flask app: {target}\n  Server will open at http://127.0.0.1:5000"


# ─── Terminal ─────────────────────────────────────────────────────────────────

def open_terminal(path: str = "") -> str:
    """
    Opens Windows Terminal (wt) or falls back to CMD.
    Usage: open terminal          → opens terminal in project root
           open terminal <path>   → opens terminal at the given path
    """
    target = path.strip() or str(config._BASE)

    if not os.path.isabs(target):
        target = os.path.join(config._BASE, target)

    # Try Windows Terminal first, then CMD
    for cmd in (f'wt -d "{target}"', f'start cmd /k "cd /d {target}"'):
        try:
            subprocess.Popen(cmd, shell=True)
            return f"Opening terminal at: {target}"
        except Exception:
            continue

    return f"Could not open terminal at: {target}"


# ─── Generic launcher ─────────────────────────────────────────────────────────

def launch_app(name: str) -> str:
    """
    Opens an app by short name from config.APP_SHORTCUTS.
    Falls back to config.APP_MAP (Day 2 legacy).
    """
    key = name.strip().lower()
    cmd = config.APP_SHORTCUTS.get(key) or config.APP_MAP.get(key)

    if not cmd:
        all_keys = sorted(set(list(config.APP_SHORTCUTS.keys()) + list(config.APP_MAP.keys())))
        return f"Unknown app '{key}'. Available: {', '.join(all_keys)}"

    try:
        subprocess.Popen(cmd, shell=True)
        return f"Launching {key}..."
    except Exception as exc:
        return f"Failed to launch '{key}': {exc}"


# ─── Kill process ─────────────────────────────────────────────────────────────

def kill_process(name: str) -> str:
    """
    Kills a running process by its executable name.
    Usage: kill python  |  kill chrome  |  kill notepad
    """
    name = name.strip()
    if not name:
        return "Usage: kill <process name>  (e.g. kill notepad)"

    # Add .exe if missing on Windows
    if sys.platform == "win32" and not name.lower().endswith(".exe"):
        name_exe = name + ".exe"
    else:
        name_exe = name

    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", name_exe],
            capture_output=True, text=True
        )
        return f"Terminated process: {name}"
    except FileNotFoundError:
        try:
            subprocess.run(["kill", name], capture_output=True)
            return f"Terminated process: {name}"
        except Exception as exc:
            return f"Could not kill '{name}': {exc}"
    except Exception as exc:
        return f"Could not kill '{name}': {exc}"
