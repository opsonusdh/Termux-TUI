from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Static, Input, RichLog
from textual.containers import Horizontal, VerticalScroll, Vertical
from textual import work
from rich.text import Text
import os
import subprocess
import time

from utils.apps.app_utils.file_manager_utils import FILE_EXPLORER_CSS, ICONS
from utils.helpers import load_config, fmt_size


class FileBrowserScreen(Screen):
    CSS = FILE_EXPLORER_CSS

    def __init__(self):
        super().__init__()
        self._file_entries = {}
        self._nav_gen      = 0
        self._current_path = os.path.expanduser("~")
        self._config       = load_config()

    def compose(self) -> ComposeResult:
        with Vertical(id="file-header"):
            with Horizontal(id="file-title"):
                yield Button("← Back", id="file-back-main")
                yield Static("◈  FILE MANAGER  ◈", id="file-header-title")
            with Horizontal(id="file-loc"):
                yield Button("⬆ Up",   id="file-up-btn")
                yield Static(self._current_path, id="file-path-display")
        with VerticalScroll(id="file-scroll"):
            yield Static("Loading...")
        yield Input(
            placeholder=" type path + Enter to jump anywhere...",
            id="file-input"
        )

    def on_mount(self):
        self.list_directory(self._current_path)
        self.app.set_theme(self._config.get("theme", "jarvis"))

    @work(thread=True)
    def list_directory(self, path):
        self._nav_gen += 1
        gen = self._nav_gen
        self.app.call_from_thread(
            self.query_one("#file-path-display", Static).update,
            f"   {path}"
        )
        try:
            entries = sorted(os.listdir(path))
        except OSError:
            entries = []

        dirs  = [e for e in entries if os.path.isdir(os.path.join(path, e))]
        files = [e for e in entries if not os.path.isdir(os.path.join(path, e))]

        file_entries = {}
        idx = 0
        for d in dirs:
            file_entries[idx] = os.path.join(path, d)
            idx += 1
        for f in files:
            file_entries[idx] = os.path.join(path, f)
            idx += 1

        def rebuild():
            self._file_entries = file_entries
            scroll = self.query_one("#file-scroll", VerticalScroll)
            scroll.remove_children()
            i = 0
            for d in dirs:
                scroll.mount(Button(
                    f"    {d}/", id=f"fentry-{gen}-{i}",
                    classes="file-dir-btn"
                ))
                i += 1
            for f in files:
                try:
                    size = fmt_size(os.path.getsize(os.path.join(path, f)))
                except OSError:
                    size = "?"
                ext  = f.split(".")[-1].lower() if "." in f else ""
                icon = ICONS.get(ext, "")
                scroll.mount(Button(
                    f"  {icon}  {f}  [{size}]", id=f"fentry-{gen}-{i}",
                    classes="file-file-btn"
                ))
                i += 1
            scroll.mount(Static(
                f"  {len(dirs)} dirs   {len(files)} files",
                classes="file-footer"
            ))
        self.app.call_from_thread(rebuild)

    @work(thread=True)
    def open_file(self, path):
        scroll = self.query_one("#file-scroll", VerticalScroll)
        def show():
            scroll.remove_children()
            rlog = RichLog(markup=True, id="file-view-log")
            scroll.mount(rlog)
            scroll.mount(Button(
                "⬆ Back to folder", id="file-back-btn",
                classes="file-dir-btn"
            ))
        self.app.call_from_thread(show)
        time.sleep(0.1)
        rlog = self.query_one("#file-view-log", RichLog)
        def w(text, style=""):
            self.app.call_from_thread(
                rlog.write, Text(text, style) if style else Text(text)
            )
        w(f"◈ {path}", "bold cyan")
        w("─" * 42, "dim #1a1a3e")
        try:
            size = os.path.getsize(path)
            if size > 50000:
                w(f"⚠ Large file ({fmt_size(size)}) — first 100 lines", "bold yellow")
                r = subprocess.run(['head','-100', path], capture_output=True, text=True)
                for line in r.stdout.splitlines():
                    w(f"  {line}", "dim green")
            else:
                with open(path, 'r', errors='replace') as f:
                    for line in f.readlines()[:300]:
                        w(f"  {line.rstrip()}", "dim green")
        except Exception as e:
            w(f"✗ {e}", "bold red")

    def on_button_pressed(self, event: Button.Pressed):
        bid = str(event.button.id)
        if bid == "file-back-main":
            self.dismiss()
        elif bid == "file-up-btn":
            parent = os.path.dirname(self._current_path)
            self._current_path = parent
            self.list_directory(parent)
        elif bid == "file-back-btn":
            self.list_directory(self._current_path)
        elif bid.startswith("fentry-"):
            idx    = int(bid.split("-")[-1])
            target = self._file_entries.get(idx)
            if target and os.path.isdir(target):
                self._current_path = target
                self.list_directory(target)
            elif target and os.path.isfile(target):
                self.open_file(target)

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id != "file-input":
            return
        val    = event.value.strip()
        target = val if os.path.isabs(val) else os.path.join(self._current_path, val)
        target = os.path.normpath(target)
        if os.path.isdir(target):
            self._current_path = target
            self.list_directory(target)
        elif os.path.isfile(target):
            self.open_file(target)
        event.input.clear()
