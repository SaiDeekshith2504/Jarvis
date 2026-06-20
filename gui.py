"""
gui.py
------
Tkinter GUI for Jarvis — Day 6.

A lightweight desktop window with:
  • Chat-style output area (scrollable)
  • Text input field
  • Send / Voice / Clear / Exit buttons
  • Reminder ticker (checks every 30 s)
  • Timestamps on every message
  • Dark-themed, modern look

Run directly:
    python gui.py

Or from main.py when UI_MODE = "gui" in config.py.
"""

from __future__ import annotations

import datetime
import threading
import tkinter as tk
from tkinter import scrolledtext, font as tkfont, messagebox

import config
from core.commands  import handle_command
from core           import reminders as rem_engine
from core           import user_profile as profile_engine
from core.logger    import log_interaction

# ── Optional voice support ───────────────────────────────────────────────────
try:
    from core.voice import speak, listen, is_voice_available
    _voice_ok = True
except ImportError:
    _voice_ok = False
    def speak(t: str) -> None:  # type: ignore[misc]
        pass
    def listen() -> str | None:  # type: ignore[misc]
        return None
    def is_voice_available() -> bool:  # type: ignore[misc]
        return False


# ─── Colour palette ──────────────────────────────────────────────────────────
_BG        = "#0f0f1a"   # deep navy background
_PANEL     = "#1a1a2e"   # slightly lighter panel
_ACCENT    = "#6c63ff"   # electric violet
_ACCENT2   = "#00d4aa"   # teal highlight
_TEXT      = "#e8e8f0"   # near-white text
_MUTED     = "#888899"   # muted secondary text
_USER_CLR  = "#a8d8ea"   # user bubble colour
_BOT_CLR   = "#f7d794"   # Jarvis bubble colour
_ENTRY_BG  = "#16213e"   # input field background
_BTN_HOVER = "#7c73ff"   # button hover colour


class JarvisGUI:
    """Main Tkinter window for the Jarvis assistant."""

    def __init__(self, root: tk.Tk) -> None:
        self.root       = root
        self.voice_mode = False
        self._build_window()
        self._build_layout()
        self._post_startup()
        self._start_reminder_ticker()

    # ── Window setup ─────────────────────────────────────────────────────────

    def _build_window(self) -> None:
        name = profile_engine.get_name() or "User"
        self.root.title(f"Jarvis  v{config.VERSION}  ·  {config.DAY}  —  Hello, {name}!")
        self.root.configure(bg=_BG)
        self.root.geometry("820x640")
        self.root.minsize(600, 480)
        self.root.resizable(True, True)

        # App icon (simple emoji fallback via title)
        try:
            self.root.iconbitmap(default="")  # no icon file needed
        except Exception:
            pass

    # ── Layout construction ───────────────────────────────────────────────────

    def _build_layout(self) -> None:
        # ── Top header bar ───────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=_PANEL, pady=10)
        header.pack(fill=tk.X, side=tk.TOP)

        tk.Label(
            header,
            text="⚡  JARVIS",
            bg=_PANEL, fg=_ACCENT,
            font=("Segoe UI", 18, "bold"),
        ).pack(side=tk.LEFT, padx=16)

        self._status_lbl = tk.Label(
            header,
            text="Ready",
            bg=_PANEL, fg=_ACCENT2,
            font=("Segoe UI", 9),
        )
        self._status_lbl.pack(side=tk.RIGHT, padx=16)

        self._clock_lbl = tk.Label(
            header,
            text="",
            bg=_PANEL, fg=_MUTED,
            font=("Segoe UI", 9),
        )
        self._clock_lbl.pack(side=tk.RIGHT, padx=8)
        self._tick_clock()

        # ── Chat area ────────────────────────────────────────────────────────
        chat_frame = tk.Frame(self.root, bg=_BG)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(6, 0))

        chat_font = tkfont.Font(family="Segoe UI", size=10)
        self._chat = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            bg=_BG,
            fg=_TEXT,
            insertbackground=_TEXT,
            font=chat_font,
            relief=tk.FLAT,
            borderwidth=0,
            padx=12,
            pady=8,
            state=tk.DISABLED,
        )
        self._chat.pack(fill=tk.BOTH, expand=True)

        # Text tags for colouring
        self._chat.tag_config("user",      foreground=_USER_CLR, font=("Segoe UI", 10, "bold"))
        self._chat.tag_config("bot",       foreground=_BOT_CLR,  font=("Segoe UI", 10))
        self._chat.tag_config("meta",      foreground=_MUTED,    font=("Segoe UI", 8))
        self._chat.tag_config("alert",     foreground="#ff6b6b",  font=("Segoe UI", 10, "bold"))
        self._chat.tag_config("separator", foreground=_PANEL)

        # ── Input row ────────────────────────────────────────────────────────
        input_frame = tk.Frame(self.root, bg=_PANEL, pady=8)
        input_frame.pack(fill=tk.X, side=tk.BOTTOM)
        input_frame.grid_columnconfigure(0, weight=1)

        entry_font = tkfont.Font(family="Segoe UI", size=11)
        self._entry = tk.Entry(
            input_frame,
            bg=_ENTRY_BG,
            fg=_TEXT,
            insertbackground=_TEXT,
            font=entry_font,
            relief=tk.FLAT,
            bd=6,
        )
        self._entry.grid(row=0, column=0, padx=(12, 6), pady=4, sticky="ew")
        self._entry.bind("<Return>", self._on_send)
        self._entry.bind("<Up>",     self._history_up)
        self._entry.bind("<Down>",   self._history_down)
        self._entry.focus()

        btn_cfg = dict(
            relief=tk.FLAT,
            bd=0,
            padx=14,
            pady=6,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        )

        self._send_btn = tk.Button(
            input_frame,
            text="Send ▶",
            bg=_ACCENT, fg="white",
            activebackground=_BTN_HOVER,
            command=self._on_send,
            **btn_cfg,
        )
        self._send_btn.grid(row=0, column=1, padx=3)

        self._voice_btn = tk.Button(
            input_frame,
            text="🎙 Voice",
            bg="#2d2d4e", fg=_TEXT,
            activebackground="#3d3d6e",
            command=self._on_voice,
            **btn_cfg,
        )
        self._voice_btn.grid(row=0, column=2, padx=3)

        tk.Button(
            input_frame,
            text="Clear",
            bg="#2d2d4e", fg=_TEXT,
            activebackground="#3d3d6e",
            command=self._on_clear,
            **btn_cfg,
        ).grid(row=0, column=3, padx=3)

        tk.Button(
            input_frame,
            text="✕ Exit",
            bg="#3d1a1a", fg="#ff6b6b",
            activebackground="#5c2020",
            command=self._on_exit,
            **btn_cfg,
        ).grid(row=0, column=4, padx=(3, 12))

        # ── Input history ────────────────────────────────────────────────────
        self._input_history: list[str] = []
        self._history_idx: int         = -1

    # ── Startup message ───────────────────────────────────────────────────────

    def _post_startup(self) -> None:
        name = profile_engine.get_name() or "there"
        now  = datetime.datetime.now().strftime("%A, %B %d  •  %I:%M %p")
        self._add_bot(
            f"👋  Hello, {name}!  It's {now}.\n"
            f"   Jarvis {config.VERSION} is ready — {config.DAY} milestone.\n"
            f"   Type a command or question below. Try 'help' to see everything I can do.",
        )

    # ── Chat display helpers ──────────────────────────────────────────────────

    def _add_line(self, text: str, tag: str) -> None:
        """Appends *text* to the chat area with the given colour tag."""
        self._chat.configure(state=tk.NORMAL)
        self._chat.insert(tk.END, text + "\n", tag)
        self._chat.configure(state=tk.DISABLED)
        self._chat.see(tk.END)

    def _add_user(self, text: str) -> None:
        ts = datetime.datetime.now().strftime("%H:%M")
        self._add_line(f"\n  You [{ts}]", "meta")
        self._add_line(f"  ❯  {text}", "user")

    def _add_bot(self, text: str, tag: str = "bot") -> None:
        ts = datetime.datetime.now().strftime("%H:%M")
        self._add_line(f"\n  Jarvis [{ts}]", "meta")
        for line in text.splitlines():
            self._add_line(f"  {line}", tag)
        self._add_line("  " + "─" * 60, "separator")

    def _add_alert(self, text: str) -> None:
        self._add_bot(f"⏰  {text}", tag="alert")

    def _set_status(self, msg: str) -> None:
        self._status_lbl.configure(text=msg)

    # ── Event handlers ────────────────────────────────────────────────────────

    def _on_send(self, _event=None) -> None:
        text = self._entry.get().strip()
        if not text:
            return

        self._entry.delete(0, tk.END)
        self._input_history.append(text)
        self._history_idx = len(self._input_history)

        self._add_user(text)

        lower = text.lower()
        if lower in ("exit", "quit", "bye", "goodbye", "stop", "close"):
            self._on_exit()
            return

        self._set_status("Thinking…")
        self._send_btn.configure(state=tk.DISABLED)
        threading.Thread(target=self._process, args=(text,), daemon=True).start()

    def _process(self, text: str) -> None:
        """Runs handle_command in a background thread and updates the UI."""
        try:
            parts    = text.strip().split(maxsplit=1)
            cmd_type = parts[0].lower() if parts else "unknown"
            response = handle_command(text, speak_fn=None)
            log_interaction(text, response, cmd_type)
        except Exception as exc:
            response = f"Unexpected error: {exc}"
            log_interaction(text, response, "error")

        # Marshal back to main thread
        self.root.after(0, self._show_response, response)

    def _show_response(self, response: str) -> None:
        self._add_bot(response)
        self._set_status("Ready")
        self._send_btn.configure(state=tk.NORMAL)
        self._entry.focus()

        # Speak if voice mode is on
        if self.voice_mode and _voice_ok:
            threading.Thread(target=speak, args=(response,), daemon=True).start()

    def _on_voice(self) -> None:
        if not _voice_ok or not is_voice_available():
            self._add_bot(
                "Voice libraries not installed.\n"
                "Install pyttsx3 + SpeechRecognition + pyaudio then restart.",
                tag="alert",
            )
            return

        self.voice_mode = not self.voice_mode
        label = "🎙 Voice ON" if self.voice_mode else "🎙 Voice"
        self._voice_btn.configure(
            text=label,
            bg=_ACCENT if self.voice_mode else "#2d2d4e",
        )
        self._add_bot(f"Voice mode {'enabled 🎙' if self.voice_mode else 'disabled ⌨️'}.")

        if self.voice_mode:
            threading.Thread(target=self._listen_loop, daemon=True).start()

    def _listen_loop(self) -> None:
        """Continuously listens for voice input while voice_mode is active."""
        while self.voice_mode:
            self.root.after(0, self._set_status, "Listening… 🎙")
            text = listen()
            if text:
                self.root.after(0, self._entry.delete, 0, tk.END)
                self.root.after(0, self._entry.insert, 0, text)
                self.root.after(0, self._on_send)
            else:
                self.root.after(0, self._set_status, "Ready")

    def _on_clear(self) -> None:
        self._chat.configure(state=tk.NORMAL)
        self._chat.delete("1.0", tk.END)
        self._chat.configure(state=tk.DISABLED)
        self._post_startup()

    def _on_exit(self) -> None:
        name    = profile_engine.get_name()
        farewell = f", {name}" if name else ""
        if messagebox.askyesno(
            "Exit Jarvis",
            f"Close Jarvis{farewell}? 👋",
            parent=self.root,
        ):
            self.root.destroy()

    # ── Input history navigation ──────────────────────────────────────────────

    def _history_up(self, _event=None) -> None:
        if not self._input_history:
            return
        self._history_idx = max(0, self._history_idx - 1)
        self._entry.delete(0, tk.END)
        self._entry.insert(0, self._input_history[self._history_idx])

    def _history_down(self, _event=None) -> None:
        if not self._input_history:
            return
        self._history_idx = min(len(self._input_history), self._history_idx + 1)
        self._entry.delete(0, tk.END)
        if self._history_idx < len(self._input_history):
            self._entry.insert(0, self._input_history[self._history_idx])

    # ── Clock & reminder ticker ───────────────────────────────────────────────

    def _tick_clock(self) -> None:
        now = datetime.datetime.now().strftime("%I:%M:%S %p")
        self._clock_lbl.configure(text=now)
        self.root.after(1000, self._tick_clock)

    def _start_reminder_ticker(self) -> None:
        """Checks for due reminders every 30 seconds."""
        self._reminder_tick()

    def _reminder_tick(self) -> None:
        alert = rem_engine.check_reminders()
        if alert:
            self._add_alert(alert)
            if self.voice_mode and _voice_ok:
                threading.Thread(target=speak, args=(alert,), daemon=True).start()
        self.root.after(30_000, self._reminder_tick)


# ─── Entry point ─────────────────────────────────────────────────────────────

def run_gui() -> None:
    """Creates the Tkinter root and starts the GUI event loop."""
    root = tk.Tk()
    JarvisGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
