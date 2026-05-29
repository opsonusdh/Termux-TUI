from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Static, Input
from textual.containers import Horizontal, Vertical
from textual import work
import subprocess, os

class BrowshScreen(Screen):

    CSS = """
    BrowshScreen            { background: #0a0a0f; align: center middle; }
    #browsh-box             { width: 1fr; height: 1fr; border: double #00ffff;
                              background: #050510; padding: 2;
                              align: center middle; }
    #browsh-title           { color: #00ffff; text-align: center; height: 3;
                              content-align: center middle; }
    #browsh-desc            { color: #444466; text-align: center; height: 3;
                              content-align: center middle; }
    #browsh-url-row         { height: 4; width: 60; }
    #browsh-url             { width: 1fr; background: #050510; color: #00ff41;
                              border: tall #1a1a3e; }
    #browsh-go              { width: 10; background: #003300; color: #00ff41;
                              border: tall #00ff41; margin-left: 1; }
    #browsh-go:hover        { background: #00ff41; color: #000000; }
    #browsh-back            { width: 20; background: #1a0000; color: #444466;
                              border: tall #333355; margin-top: 1; }
    #browsh-back:hover      { color: #00ffff; }
    #browsh-status          { color: #444466; height: 2;
                              content-align: center middle; }
    #browsh-not-found       { color: red; text-align: center; height: 2;
                              content-align: center middle; display: none; }

    BrowshScreen.theme-dark { background: #111116; }
    BrowshScreen.theme-dark #browsh-box   { background: #18181f; border: double #7c5cbf; }
    BrowshScreen.theme-dark #browsh-title { color: #c9b8f0; }
    BrowshScreen.theme-dark #browsh-url   { background: #18181f; color: #7ec8e3; border: tall #2a2a3a; }
    BrowshScreen.theme-dark #browsh-go    { background: #1a2233; color: #7ec8e3; border: tall #5b8dd9; }

    BrowshScreen.theme-light { background: #f0f0f5; }
    BrowshScreen.theme-light #browsh-box   { background: #ffffff; border: double #3366cc; }
    BrowshScreen.theme-light #browsh-title { color: #1a1a99; }
    BrowshScreen.theme-light #browsh-url   { background: #ffffff; color: #116622; border: tall #ccccdd; }
    BrowshScreen.theme-light #browsh-go    { background: #e8f5e8; color: #116622; border: tall #228833; }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="browsh-box"):
            yield Static("󰇙  BROWSH  BROWSER  󰇙", id="browsh-title")
            yield Static(
                "Text-based web browser\nOpens in a new Termux terminal",
                id="browsh-desc"
            )
            with Horizontal(id="browsh-url-row"):
                yield Input(
                    placeholder="https://example.com",
                    id="browsh-url"
                )
                yield Button("Go", id="browsh-go")
            yield Static("", id="browsh-status")
            yield Static(
                " browsh not found. Install: pkg install browsh",
                id="browsh-not-found"
            )
            yield Button("← Back", id="browsh-back")

    def on_mount(self):
        for cls in ["theme-dark", "theme-light"]:
            if cls in self.app.classes:
                self.add_class(cls)
        self._check_installed()

    def _check_installed(self):
        result = subprocess.run(
            ['which', 'browsh'],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            self.query_one("#browsh-not-found").styles.display = "block"
            self.query_one("#browsh-go", Button).disabled = True
            self.query_one("#browsh-status", Static).update(
                "Run: pkg install browsh"
            )

    def _launch(self, url=""):
        cmd = f"browsh {url}" if url else "browsh"
        with self.app.suspend():
            subprocess.run(cmd, shell=True)
        self.query_one("#browsh-status", Static).update("󰇙 Returned from browsh")

    def on_button_pressed(self, event: Button.Pressed):
        bid = str(event.button.id)
        if bid == "browsh-back":
            self.dismiss()
        elif bid == "browsh-go":
            url = self.query_one("#browsh-url", Input).value.strip()
            if url and not url.startswith("http"):
                url = "https://" + url
            self._launch(url)

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "browsh-url":
            url = event.value.strip()
            if url and not url.startswith("http"):
                url = "https://" + url
            self._launch(url)