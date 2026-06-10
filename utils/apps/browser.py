from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Static, Input
from textual.containers import Horizontal, Vertical
import subprocess

from utils.apps.app_utils.browser_utils import BROWSERS, _which, _detect_browser, BROWSER_CSS

class BrowserScreen(Screen):

    CSS = BROWSER_CSS

    def __init__(self):
        super().__init__()
        self._active_cmd, self._active_name = _detect_browser()
        # availability map: cmd -> bool
        self._avail = {cmd: _which(cmd) for cmd, *_ in BROWSERS}

    def compose(self) -> ComposeResult:
        with Vertical(id="br-box"):
            yield Static("\uf0ac  TEXT BROWSER  \uf0ac", id="br-title")
            yield Static(
                "Runs in-terminal · suspends TUI while browsing",
                id="br-desc"
            )

            # Browser selector tabs
            with Horizontal(id="br-tab-strip"):
                for cmd, name, _ in BROWSERS:
                    avail = self._avail.get(cmd, False)
                    active = (cmd == self._active_cmd)
                    classes = "br-tab"
                    if active:
                        classes += " active available"
                    elif avail:
                        classes += " available"
                    else:
                        classes += " unavailable"
                    yield Button(name, id=f"brtab-{cmd}", classes=classes)

            with Horizontal(id="br-url-row"):
                yield Input(
                    placeholder="https://example.com",
                    id="br-url"
                )
                yield Button("Go", id="br-go",
                             disabled=(self._active_cmd is None))

            yield Static("", id="br-status")
            yield Static("", id="br-install-hint")
            yield Button("← Back", id="br-back")

    def on_mount(self):
        for cls in ["theme-dark", "theme-light"]:
            if cls in self.app.classes:
                self.add_class(cls)
        self._update_status()
        try:
            self.query_one("#br-url", Input).focus()
        except Exception:
            pass

    def _update_status(self):
        if self._active_cmd:
            self.query_one("#br-status", Static).update(
                f"Using: {self._active_name}   "
                f"({sum(self._avail.values())}/{len(BROWSERS)} browsers installed)"
            )
            self.query_one("#br-install-hint", Static).update("")
            self.query_one("#br-go", Button).disabled = False
        else:
            self.query_one("#br-status", Static).update(
                "No text browser found"
            )
            self.query_one("#br-install-hint", Static).update(
                f"Install one: {BROWSERS[0][2]}"
            )
            self.query_one("#br-go", Button).disabled = True

    def _select_browser(self, cmd: str):
        name = next((n for c, n, _ in BROWSERS if c == cmd), cmd)
        if not self._avail.get(cmd, False):
            hint = next((h for c, n, h in BROWSERS if c == cmd), "")
            self.query_one("#br-status", Static).update(
                f"{name} not installed"
            )
            self.query_one("#br-install-hint", Static).update(
                f"Install: {hint}"
            )
            return
        self._active_cmd  = cmd
        self._active_name = name
        # Update tab styles
        for c, *_ in BROWSERS:
            try:
                btn = self.query_one(f"#brtab-{c}", Button)
                if c == cmd:
                    btn.add_class("active")
                else:
                    btn.remove_class("active")
            except Exception:
                pass
        self._update_status()

    def _normalize_url(self, url: str) -> str:
        url = url.strip()
        if url and not url.startswith(("http://", "https://", "ftp://")):
            url = "https://" + url
        return url

    def _launch(self, url: str = ""):
        if not self._active_cmd:
            return
        url = self._normalize_url(url)
        cmd = self._active_cmd

        if url:
            if cmd == "browsh":
                command = ["browsh", "--startup-url", url]
            else:
                command = [cmd, url]
        else:
            command = [cmd]

        self.query_one("#br-status", Static).update(
            f"Launching {self._active_name}..."
        )
        try:
            with self.app.suspend():
                subprocess.run(command)
        except OSError as exc:
            self.query_one("#br-status", Static).update(f"Launch failed: {exc}")
            return
        self.query_one("#br-status", Static).update(
            f"◈ Returned from {self._active_name}"
        )

    def on_button_pressed(self, event: Button.Pressed):
        bid = str(event.button.id)
        if bid == "br-back":
            self.dismiss()
        elif bid == "br-go":
            url = self.query_one("#br-url", Input).value.strip()
            self._launch(url)
        elif bid.startswith("brtab-"):
            self._select_browser(bid[6:])

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "br-url":
            self._launch(event.value.strip())
