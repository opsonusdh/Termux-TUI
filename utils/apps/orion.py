from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Static, Input, RichLog
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual import work
from rich.text import Text
import subprocess, os, threading, time, re

from utils.apps.app_utils.orion_utils import (
    ORION_DIR, STT_DIR, CONFIG, save_orion_config,
    orion_installed, stt_installed, api_keys_exist, save_api_keys,
    strip_ansi, ansi_to_rich, get_sys_stats, STT_MODELS,
    ORION_INSTALLER_CSS, ORION_APIKEY_CSS, ORION_CSS, ORION_LAUNCH_CSS
)


# ── API KEY SCREEN ────────────────────────────────────────────────

class OrionApiKeyScreen(Screen):
    CSS = ORION_APIKEY_CSS

    def __init__(self):
        super().__init__()
        self._keys    = []
        self._key_gen = 0
        self._load_keys_from_file()

    def _load_keys_from_file(self):
        keys_file = os.path.join(ORION_DIR, "api.keys")
        try:
            if os.path.exists(keys_file) and os.path.getsize(keys_file) > 0:
                with open(keys_file) as f:
                    for line in f:
                        key = line.strip()
                        if key and key not in self._keys:
                            self._keys.append(key)
        except Exception:
            self._keys = []

    def on_mount(self):
        self._refresh_keys()

    def compose(self) -> ComposeResult:
        with Vertical(id="api-box"):
            yield Static("◈  ORION  ◈\nGemini API Key Setup", id="api-title")
            yield Static(
                "Orion uses Google Gemini.\n"
                "Get a free key at: aistudio.google.com\n"
                "Add one or more keys — Orion rotates them automatically.",
                id="api-desc"
            )
            with VerticalScroll(id="api-keys-scroll"):
                yield Static("  No keys added yet.", id="api-empty")
            with Horizontal(id="api-input-row"):
                yield Input(placeholder="Paste API key (AIza...)", id="api-input")
                yield Button("+ Add", id="api-add")
            yield Static("", id="api-status")
            with Horizontal(id="api-btns"):
                yield Button("✅ Save & Continue", id="api-save")

    def _refresh_keys(self):
        self._key_gen += 1
        gen    = self._key_gen
        scroll = self.query_one("#api-keys-scroll", VerticalScroll)
        scroll.remove_children()
        if not self._keys:
            scroll.mount(Static("  No keys added yet.", id="api-empty"))
            return
        for i, key in enumerate(self._keys):
            masked = key[:12] + "..." + key[-4:] if len(key) > 16 else key
            row    = Horizontal(classes="api-key-row")
            scroll.mount(row)
            row.mount(Static(f"  🔑 {masked}", classes="api-key-label"))
            row.mount(Button("✕", id=f"apidel-{gen}-{i}", classes="api-key-del"))
            row._key_idx = i

    def on_button_pressed(self, event: Button.Pressed):
        bid = str(event.button.id)
        if bid == "api-add":
            self._add_key_from_input()
        elif bid == "api-save":
            self._do_save()
        elif bid.startswith("apidel-"):
            idx = int(bid.split("-")[-1])
            if 0 <= idx < len(self._keys):
                self._keys.pop(idx)
                self._refresh_keys()

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "api-input":
            self._add_key_from_input()

    def _add_key_from_input(self):
        val = self.query_one("#api-input", Input).value.strip()
        if val and val not in self._keys:
            self._keys.append(val)
            self._refresh_keys()
            self.query_one("#api-input", Input).clear()
            self.query_one("#api-status", Static).update(
                f"✅ {len(self._keys)} key(s) added"
            )

    def _do_save(self):
        if not self._keys:
            self.query_one("#api-status", Static).update(
                "✗ Add at least one API key"
            )
            return
        ok = save_api_keys(self._keys)
        if ok:
            self.query_one("#api-status", Static).update(
                f"✅ Saved {len(self._keys)} key(s)"
            )
            time.sleep(0.6)
            self.dismiss(True)
        else:
            self.query_one("#api-status", Static).update(
                "✗ Failed to save. Check permissions."
            )


# ── INSTALL SCREEN ────────────────────────────────────────────────

class OrionInstallScreen(Screen):
    CSS = ORION_INSTALLER_CSS

    def __init__(self, mode="install"):
        super().__init__()
        self._mode           = mode
        self._selected_model = "2"   # default: tiny.en

    def compose(self) -> ComposeResult:
        with Vertical(id="inst-box"):
            if self._mode == "install":
                yield Static("◈  ORION  ◈\nInstalling Termux-AI...", id="inst-title")
                yield Static(
                    "Orion AI is not installed.\n"
                    "This will clone the repo and run setup.sh",
                    id="inst-desc"
                )
            else:
                yield Static("◈  ORION  ◈\nVoice Service (Termux-STT)", id="inst-title")
                yield Static(
                    "Install voice input & wake-word detection?\n"
                    "Requires mpv, edge-tts and more.",
                    id="inst-desc"
                )
                with Vertical(id="model-section"):
                    yield Static("  Choose Whisper model quality:", id="model-title")
                    with VerticalScroll(id="model-scroll"):
                        for label, choice in STT_MODELS:
                            yield Button(
                                f"  {label}",
                                id=f"model-{choice}",
                                classes="model-btn" + (
                                    " selected" if choice == self._selected_model else ""
                                )
                            )

            yield RichLog(id="inst-log", markup=True)
            yield Static("", id="inst-status")
            with Horizontal(id="inst-btns"):
                yield Button("▶ Install Orion" if self._mode == "install"
                             else "▶ Install Voice", id="inst-go")
                if self._mode != "install":
                    yield Button("✕ Skip", id="inst-skip-voice")

    def on_button_pressed(self, event: Button.Pressed):
        bid = str(event.button.id)

        if bid.startswith("model-"):
            choice = bid[6:]
            self._selected_model = choice
            for _, c in STT_MODELS:
                try:
                    b = self.query_one(f"#model-{c}", Button)
                    b.add_class("selected") if c == choice else b.remove_class("selected")
                except Exception:
                    pass
            return

        if bid == "inst-go":
            event.button.disabled = True
            try:
                self.query_one("#model-section").styles.display = "none"
            except Exception:
                pass
            if self._mode == "install":
                self.run_install()
            else:
                self.run_voice_install(self._selected_model)

        elif bid == "inst-skip-voice":
            self.dismiss(False)

    @work(thread=True)
    def run_install(self):
        log = self.query_one("#inst-log", RichLog)
        def w(text, style="dim green"):
            self.app.call_from_thread(log.write, Text(text, style))
        def status(text):
            self.app.call_from_thread(
                self.query_one("#inst-status", Static).update, text
            )

        for cmd, msg in [
            ("pkg install -y git python",                                  "Installing git & python..."),
            (f"git clone https://github.com/opsonusdh/Termux-AI {ORION_DIR}", "Cloning Orion..."),
            (f"cd {ORION_DIR} && bash setup.sh",                           "Running setup.sh..."),
        ]:
            status(f"⏳ {msg}")
            w(f"$ {cmd}", "bold yellow")
            proc = subprocess.Popen(
                cmd, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            for line in proc.stdout:
                w(line.rstrip())
            proc.wait()
            if proc.returncode != 0:
                status("✗ Installation failed")
                w("Installation failed.", "bold red")
                return

        status("✅ Orion installed!")
        w("Done.", "bold green")
        time.sleep(0.5)
        self.app.call_from_thread(self.dismiss, True)

    @work(thread=True)
    def run_voice_install(self, model_choice):
        log = self.query_one("#inst-log", RichLog)
        def w(text, style="dim green"):
            self.app.call_from_thread(log.write, Text(text, style))
        def status(text):
            self.app.call_from_thread(
                self.query_one("#inst-status", Static).update, text
            )

        for cmd, msg in [
            ("pkg install -y mpv",           "Installing mpv..."),
            ("pip install edge-tts --quiet", "Installing edge-tts..."),
        ]:
            status(f"⏳ {msg}")
            w(f"$ {cmd}", "bold yellow")
            proc = subprocess.Popen(
                cmd, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            for line in proc.stdout:
                w(line.rstrip())
            proc.wait()

        status("⏳ Cloning Termux-STT...")
        w(f"$ git clone https://github.com/opsonusdh/Termux-STT {STT_DIR}", "bold yellow")
        proc = subprocess.Popen(
            f"git clone https://github.com/opsonusdh/Termux-STT {STT_DIR}",
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        for line in proc.stdout:
            w(line.rstrip())
        proc.wait()

        status(f"⏳ Running STT setup (model: {model_choice})...")
        w(f"$ bash {STT_DIR}/setup.sh  [model={model_choice}]", "bold yellow")
        proc = subprocess.Popen(
            f"bash {STT_DIR}/setup.sh",
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        try:
            proc.stdin.write(model_choice + "\n")
            proc.stdin.flush()
            proc.stdin.close()
        except Exception:
            pass
        for line in proc.stdout:
            w(line.rstrip())
        proc.wait()

        CONFIG["voice_enabled"] = True
        save_orion_config(CONFIG)
        status("✅ Voice installed!")
        w("Done.", "bold green")
        time.sleep(0.5)
        self.app.call_from_thread(self.dismiss, True)


# ── MAIN ORION SCREEN ─────────────────────────────────────────────

class OrionScreen(Screen):
    CSS = ORION_CSS

    _proc       = None
    _is_running = False
    _last_line = ""

    TOOLS = [
        ("run_code",        "💻"),
        ("save_memory",     "💾"),
        ("retrieve_memory", "🔍"),
        ("read_file",       "📄"),
        ("write_file",      "✏️"),
        ("web_scrape",      "🌐"),
        ("sleep_mode",      "😴"),
    ]

    def compose(self) -> ComposeResult:
        with Horizontal(id="orion-header"):
            yield Button("← Back",   id="orion-back")
            yield Static("◈  ORION  AI  ◈", id="orion-title")
            yield Button("API Keys", id="orion-apikey-btn")

        with Horizontal(id="orion-body"):
            with Vertical(id="orion-sidebar"):
                yield Static("[ SYSTEM ]", id="orion-sys-title")
                with Horizontal(classes="sys-row"):
                    yield Static("CPU", classes="sys-key")
                    yield Static("...", id="sys-cpu", classes="sys-val")
                with Horizontal(classes="sys-row"):
                    yield Static("MEM", classes="sys-key")
                    yield Static("...", id="sys-mem", classes="sys-val")
                with Horizontal(classes="sys-row"):
                    yield Static("BAT", classes="sys-key")
                    yield Static("...", id="sys-bat", classes="sys-val")
                yield Static("░" * 18, id="orion-mem-bar")
                yield Static("[ TOOLS ]", id="orion-tool-title")
                for name, icon in self.TOOLS:
                    yield Static(
                        f"  {icon} {name}",
                        id=f"tool-{name}",
                        classes="tool-indicator"
                    )

            with Vertical(id="orion-panel"):
                yield RichLog(id="orion-log", markup=True, wrap=True)
                yield Static("●  Ready", id="orion-thinking-bar")

#        with Horizontal(id="orion-input-row"):
#            yield Static("YOU ▸", id="orion-prompt-label")
#            yield Input(placeholder="Ask Orion anything...", id="orion-input")
#            yield Button("Send", id="orion-send")

    def on_mount(self):
        for cls in ["theme-dark", "theme-light"]:
            if cls in self.app.classes:
                self.add_class(cls)
        self._start_orion()
        self.set_interval(3, self._update_stats)
        self._update_stats()
        self._write_log("◈  ORION  AI  ◈", "bold cyan")
        self._write_log("Autonomous terminal agent — powered by Gemini", "dim #444466")
        self._write_log("─" * 50, "dim #1a1a3e")

    # ── stats ─────────────────────────────────────────────────────

    @work(thread=True)
    def _update_stats(self):
        stats = get_sys_stats()
        def apply():
            try:
                self.query_one("#sys-cpu", Static).update(stats.get('cpu', 'N/A'))
                self.query_one("#sys-bat", Static).update(stats.get('bat', 'N/A'))
                mem_str = stats.get('mem', '0/0GB (0%)')
                self.query_one("#sys-mem", Static).update(mem_str)
                try:
                    pct    = int(re.search(r'\((\d+)%\)', mem_str).group(1))
                    filled = int(pct / 100 * 18)
                    bar    = "█" * filled + "░" * (18 - filled)
                    self.query_one("#orion-mem-bar", Static).update(bar)
                except Exception:
                    pass
            except Exception:
                pass
        self.app.call_from_thread(apply)

    # ── subprocess ────────────────────────────────────────────────

    @work(thread=True)
    def _start_orion(self):
        try:
            subprocess.Popen(
                ['termux-terminal', '-e',
                 f'bash -c "cd {ORION_DIR} && python -u core; read"'],
            )
            self._is_running = True
            self._write_log("◈ Orion launched in external terminal", "bold cyan")
            self._write_log("Use the terminal window to interact with Orion.", "dim #444466")
            self.query_one("#orion-thinking-bar", Static).update(
                "●  Orion running in terminal"
            )
        except Exception as e:
            self._write_log(f"✗ Failed to launch: {e}", "bold red")

    # ── output handler ────────────────────────────────────────────

    def _handle_output_line(self, raw_line):
        line  = raw_line.rstrip()
        if line == self._last_line and line:
            return
        self._last_line = line
        clean = strip_ansi(line)
        rich  = ansi_to_rich(line)

        if not clean:
            self.app.call_from_thread(self._write_log, "", "")
            return
        


        # ── tool flash ────────────────────────────────────────────
        tool_map = {
            "[MEMORY]":    "retrieve_memory",
            "[EXECUTING]": "run_code",
            "[SCRAPING]":  "web_scrape",
            "[WRITING]":   "write_file",
            "[READING]":   "read_file",
        }
        for prefix, tool in tool_map.items():
            if clean.startswith(prefix):
                self._flash_tool(tool)
                break

        # ── status bar ────────────────────────────────────────────
        if "[Thinking]" in clean:
            self.app.call_from_thread(
                self.query_one("#orion-thinking-bar", Static).update,
                "◉  Orion is thinking..."
            )
        elif "[Listening...]" in clean:
            self.app.call_from_thread(
                self.query_one("#orion-thinking-bar", Static).update,
                "◎  Listening..."
            )
        elif re.match(r'YOU\s*(\(Voice\))?\s*[>▸]\s*\S', clean):
            self.app.call_from_thread(
                self.query_one("#orion-thinking-bar", Static).update,
                "⏵  Input received"
            )
        elif re.match(r'AI\s*[>▸]', clean):
            self.app.call_from_thread(
                self.query_one("#orion-thinking-bar", Static).update,
                "●  Responding..."
            )

        # ── EARLY RETURNS — suppress noise using clean text only ──

        # empty YOU > prompt — Orion prints this after receiving input
        if re.fullmatch(r'YOU\s*(\(Voice\))?\s*[>▸]\s*', clean):
            return

        # STT server / calibration noise — use clean to avoid red ANSI
        if re.match(r'\[server\]|\[calibrate\]|Calibrating', clean):
            self.app.call_from_thread(self._write_log, clean, "dim #1a2a2a")
            return

        # model rotation warnings — dim orange, no ANSI markup
        if re.match(r'Model (exhausted|overloaded)', clean):
            self.app.call_from_thread(self._write_log, clean, "dim #664400")
            return

        # ── STYLE and write everything else ───────────────────────

        if any(kw in clean for kw in ['[server]', '[calibrate]', 'Calibrating', 'whisper-server', 'threshold set']):
            style = "bold magenta"
        elif clean in ("[OUT]", "[ERR]"):
            style = "dim #445566"
        elif "[Thinking]" in clean:
            style = "bold yellow"
        elif "[Listening...]" in clean:
            style = "bold cyan"
        elif re.match(r'YOU\s*(\(Voice\))?\s*[>▸]', clean):
            style = "bold cyan"
        elif re.match(r'AI\s*[>▸]', clean):
            style = "bold green"
        elif re.match(r'(Error|Exception|Traceback|FAILED)', clean, re.IGNORECASE):
            style = "bold red"
        else:
            style = "dim green"

        self.app.call_from_thread(self._write_log, rich or clean, style)

    # ── helpers ───────────────────────────────────────────────────

    def _flash_tool(self, name):
        def on():
            try: self.query_one(f"#tool-{name}").add_class("active")
            except Exception: pass
        def off():
            try: self.query_one(f"#tool-{name}").remove_class("active")
            except Exception: pass
        self.app.call_from_thread(on)
        threading.Timer(2.0, lambda: self.app.call_from_thread(off)).start()

    def _write_log(self, text, style="dim green"):
        try:
            self.query_one("#orion-log", RichLog).write(Text(text, style))
        except Exception:
            pass

    def _send_message(self, text):
        if not self._is_running or not self._proc:
            self._write_log("✗ Orion is not running.", "bold red")
            return
        try:
            self._write_log(f"YOU > {text}", "bold cyan")
            self._proc.stdin.write(text + "\n")
            self._proc.stdin.flush()
        except Exception as e:
            self._write_log(f"✗ {e}", "bold red")

    # ── event handlers ────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed):
        bid = str(event.button.id)
        if bid == "orion-back":
            if self._proc:
                try: self._proc.terminate()
                except Exception: pass
            self.dismiss()
        elif bid == "orion-send":
            val = self.query_one("#orion-input", Input).value.strip()
            if val:
                self._send_message(val)
                self.query_one("#orion-input", Input).clear()
        elif bid == "orion-apikey-btn":
            self.app.push_screen(OrionApiKeyScreen())

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "orion-input":
            val = event.value.strip()
            if val:
                self._send_message(val)
                event.input.clear()


# ── ENTRY POINT ───────────────────────────────────────────────────

class OrionLaunchScreen(Screen):
    CSS = ORION_LAUNCH_CSS

    def compose(self) -> ComposeResult:
        yield Static("◈  ORION  ◈\nChecking...", id="launch-msg")

    def on_mount(self):
        self.check_and_launch()

    @work(thread=True)
    def check_and_launch(self):
        if not orion_installed():
            self.app.call_from_thread(
                self.app.push_screen,
                OrionInstallScreen("install"),
                self._after_install
            )
        elif not api_keys_exist():
            self.app.call_from_thread(
                self.app.push_screen,
                OrionApiKeyScreen(),
                self._after_apikey
            )
        elif CONFIG.get("first_run", True):
            CONFIG["first_run"] = False
            save_orion_config(CONFIG)
            if not stt_installed():
                self.app.call_from_thread(
                    self.app.push_screen,
                    OrionInstallScreen("voice"),
                    self._after_voice
                )
            else:
                self.app.call_from_thread(self._launch_orion)
        else:
            self.app.call_from_thread(self._launch_orion)

    def _after_install(self, success):
        if success:
            self.app.push_screen(OrionApiKeyScreen(), self._after_apikey)
        else:
            self.dismiss()

    def _after_apikey(self, success):
        if success and not stt_installed():
            self.app.push_screen(
                OrionInstallScreen("voice"), self._after_voice
            )
        elif success:
            self._launch_orion()
        else:
            self.dismiss()

    def _after_voice(self, success):
        self._launch_orion()

    def _launch_orion(self):
        self.app.switch_screen(OrionScreen())
