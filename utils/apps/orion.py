from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Static, Input, RichLog
from textual.containers import Horizontal, Vertical, VerticalScroll, ScrollableContainer
from textual import work
from rich.text import Text
import subprocess, os, threading, time, re

from utils.apps.app_utils.orion_utils import (
    ORION_DIR, CORE_DIR, STT_DIR, CONFIG, save_orion_config,
    orion_installed, stt_installed, api_keys_exist,
    load_api_keys, save_api_keys,
    strip_ansi, ansi_to_rich, get_sys_stats, STT_MODELS,
    ORION_PROVIDERS, TOOLS, TOOL_PREFIXES,
    ORION_INSTALLER_CSS, ORION_APIKEY_CSS, ORION_CSS, ORION_LAUNCH_CSS,
)


class OrionApiKeyScreen(Screen):
    CSS = ORION_APIKEY_CSS

    def __init__(self):
        super().__init__()
        self._keys       = load_api_keys()
        self._active_pid = ORION_PROVIDERS[0][0]
        self._gen        = 0

    def compose(self) -> ComposeResult:
        with Vertical(id="api-box"):
            yield Static(
                "◈  ORION  ◈\nAPI Key Setup",
                id="api-title"
            )
            yield Static(
                "Google is required. NVIDIA and Groq are optional fallbacks.\n"
                "Orion rotates keys automatically to avoid rate limits.",
                id="api-desc"
            )

            with Horizontal(id="api-tab-strip"):
                for pid, label, _hint, _ph in ORION_PROVIDERS:
                    yield Button(label, id=f"apitab-{pid}", classes="api-tab")

            yield Static("", id="api-provider-hint")

            with VerticalScroll(id="api-keys-scroll"):
                pass

            with Horizontal(id="api-input-row"):
                yield Input(placeholder="Paste key here...", id="api-input")
                yield Button("+ Add", id="api-add")

            yield Static("", id="api-status")
            with Horizontal(id="api-btns"):
                yield Button(" Save & Continue", id="api-save")

    def on_mount(self):
        self._switch_tab(self._active_pid)

    def _switch_tab(self, pid: str):
        self._active_pid = pid
        for p, *_ in ORION_PROVIDERS:
            try:
                btn = self.query_one(f"#apitab-{p}", Button)
                btn.add_class("active") if p == pid else btn.remove_class("active")
            except Exception:
                pass
        for p, _label, hint, _ph in ORION_PROVIDERS:
            if p == pid:
                self.query_one("#api-provider-hint", Static).update(f"  {hint}")
                break
        for p, _label, _hint, ph in ORION_PROVIDERS:
            if p == pid:
                self.query_one("#api-input", Input).placeholder = f"Paste key ({ph})"
                break
        self._refresh_keys()

    def _refresh_keys(self):
        self._gen += 1
        gen    = self._gen
        pid    = self._active_pid
        scroll = self.query_one("#api-keys-scroll", VerticalScroll)
        scroll.remove_children()

        keys = self._keys.get(pid, [])
        if not keys:
            scroll.mount(Static(
                "  No keys added yet." + (
                    "" if pid != "google" else "  (Google key required!)"
                ),
                classes="api-key-label"
            ))
            return

        for i, key in enumerate(keys):
            masked = key[:14] + "..." + key[-4:] if len(key) > 18 else key
            row = Horizontal(classes="api-key-row")
            scroll.mount(row)
            row.mount(Static(f"   {masked}", classes="api-key-label"))
            row.mount(Button("✕", id=f"apidel-{gen}-{pid}-{i}",
                             classes="api-key-del"))

    #  events 

    def on_button_pressed(self, event: Button.Pressed):
        bid = str(event.button.id)

        if bid.startswith("apitab-"):
            self._switch_tab(bid[7:])

        elif bid == "api-add":
            self._add_key()

        elif bid == "api-save":
            self._do_save()

        elif bid.startswith("apidel-"):
            parts = bid.split("-")
            if len(parts) >= 4:
                del_pid = parts[2]
                idx     = int(parts[3])
                if del_pid in self._keys and 0 <= idx < len(self._keys[del_pid]):
                    self._keys[del_pid].pop(idx)
                    self._refresh_keys()

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "api-input":
            self._add_key()

    def _add_key(self):
        pid = self._active_pid
        val = self.query_one("#api-input", Input).value.strip()
        if not val:
            return
        if pid not in self._keys:
            self._keys[pid] = []
        if val not in self._keys[pid]:
            self._keys[pid].append(val)
            self._refresh_keys()
            self.query_one("#api-input", Input).clear()
            total = sum(len(v) for v in self._keys.values())
            self.query_one("#api-status", Static).update(
                f" {total} key(s) across all providers"
            )

    def _do_save(self):
        if not self._keys.get("google"):
            self.query_one("#api-status", Static).update(
                "✗ At least one Google key is required"
            )
            return
        ok = save_api_keys(self._keys)
        if ok:
            total = sum(len(v) for v in self._keys.values())
            self.query_one("#api-status", Static).update(
                f" Saved {total} key(s)"
            )
            time.sleep(0.5)
            self.dismiss(True)
        else:
            self.query_one("#api-status", Static).update(
                "✗ Failed to save. Check permissions."
            )


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
                    "Orion is not installed.\n"
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
            ("pkg install -y git python",
             "Installing git & python..."),
            (f"git clone https://github.com/opsonusdh/Termux-AI {ORION_DIR}",
             "Cloning Termux-AI..."),
            (f"cd {ORION_DIR} && bash setup.sh",
             "Running setup.sh..."),
        ]:
            status(f"󱦟 {msg}")
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

        status(" Orion installed!")
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
            status(f"󱦟 {msg}")
            w(f"$ {cmd}", "bold yellow")
            proc = subprocess.Popen(
                cmd, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            for line in proc.stdout:
                w(line.rstrip())
            proc.wait()

        status("󱦟 Cloning Termux-STT...")
        w(f"$ git clone https://github.com/opsonusdh/Termux-STT {STT_DIR}",
          "bold yellow")
        proc = subprocess.Popen(
            f"git clone https://github.com/opsonusdh/Termux-STT {STT_DIR}",
            shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        for line in proc.stdout:
            w(line.rstrip())
        proc.wait()

        status(f"󱦟 Running STT setup (model: {model_choice})...")
        w(f"$ bash {STT_DIR}/setup.sh  [model={model_choice}]", "bold yellow")
        proc = subprocess.Popen(
            f"bash {STT_DIR}/setup.sh",
            shell=True, stdin=subprocess.PIPE,
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
        status(" Voice installed!")
        w("Done.", "bold green")
        time.sleep(0.5)
        self.app.call_from_thread(self.dismiss, True)

class OrionScreen(Screen):
    CSS = ORION_CSS

    _proc          = None
    _is_running    = False
    _last_line     = ""
    _reader_thread = None

    def compose(self) -> ComposeResult:
        with Horizontal(id="orion-header"):
            yield Button("← Back",   classes="orion-nav-btns", id="orion-back")
            yield Static("◈  ORION  ◈", id="orion-title")
            yield Button("API Keys", id="orion-apikey-btn", classes="orion-nav-btns")

        with Horizontal(id="orion-body"):

            with Vertical(id="orion-sidebar"):
                yield Static("[ SYSTEM ]", id="orion-sys-title")              
                with Horizontal(classes="sys-row"):
                    yield Static("BAT", classes="sys-key")
                    yield Static("...", id="sys-bat", classes="sys-val")
                with Horizontal(classes="sys-row"):
                    yield Static("MEM", classes="sys-key")
                    yield Static("...", id="sys-cpu", classes="sys-val")
                with Horizontal(classes="sys-row"):
                    yield Static("RAM", classes="sys-key")
                    yield Static("...", id="sys-mem", classes="sys-val")
                
                yield Static("░" * 18, id="orion-mem-bar")
                yield Static("[ TOOLS ]", id="orion-tool-title")
                with ScrollableContainer(id="orion-tool-scroll"):
                    for name, icon in TOOLS:
                        yield Static(
                            f"  {icon} {name}",
                            id=f"tool-{name}",
                            classes="tool-indicator"
                        )

            with Vertical(id="orion-panel"):
                yield Static(
                    "● ◌ ◌   ORION TERMINAL",
                    id="orion-term-titlebar"
                )
                
                yield RichLog(id="orion-log", markup=True, wrap=False)
                yield Static("●  Ready", id="orion-thinking-bar")

        with Horizontal(id="orion-input-row"):
            yield Static("YOU ▸", id="orion-prompt-label")
            yield Input(placeholder="Ask Orion anything...", id="orion-input")
            yield Button("Send", id="orion-send")

    def on_mount(self):
        for cls in ["theme-dark", "theme-light"]:
            if cls in self.app.classes:
                self.add_class(cls)
        self._write_log("" * 50, "dim #1a1a3e")
        self._start_orion()
        self.set_interval(3, self._update_stats)
        self._update_stats()
        try:
            self.query_one("#orion-input", Input).focus()
        except Exception:
            pass

    @work(thread=True)
    def _update_stats(self):
        stats = get_sys_stats()
        def apply():
            try:
                self.query_one("#sys-cpu", Static).update(stats.get("cpu", "N/A"))
                self.query_one("#sys-bat", Static).update(stats.get("bat", "N/A"))
                mem_str = stats.get("mem", "0/0GB (0%)")
                self.query_one("#sys-mem", Static).update(mem_str)
                try:
                    pct    = int(re.search(r"\((\d+)%\)", mem_str).group(1))
                    filled = int(pct / 100 * 18)
                    bar    = "█" * filled + "░" * (18 - filled)
                    self.query_one("#orion-mem-bar", Static).update(bar)
                except Exception:
                    pass
            except Exception:
                pass
        self.app.call_from_thread(apply)

    def _start_orion(self):
        if not os.path.isfile(os.path.join(CORE_DIR, "__main__.py")):
            self._write_log(
                f"✗ Orion not found at {CORE_DIR}/__main__.py\n"
                "  Install Orion first via the launcher.",
                "bold red"
            )
            return

        try:
            self._proc = subprocess.Popen(
                ["python", "-u", "__main__.py"],
                cwd=CORE_DIR,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            self._is_running = True
            self._write_log(
                f"◈ Orion started (pid {self._proc.pid}) — engine loading...",
                "bold cyan"
            )
            self.query_one("#orion-thinking-bar", Static).update(
                "󱦟  Starting Orion..."
            )

            self._reader_thread = threading.Thread(
                target=self._read_output,
                daemon=True,
                name="orion-stdout-reader"
            )
            self._reader_thread.start()

        except FileNotFoundError:
            self._write_log(
                "✗ 'python' not found — install Python: pkg install python",
                "bold red"
            )
            self._is_running = False
        except Exception as e:
            self._write_log(f"✗ Failed to start Orion: {e}", "bold red")
            self._is_running = False

    def _read_output(self):
        try:
            for raw_line in iter(self._proc.stdout.readline, ""):
                if raw_line:
                    self._handle_output_line(raw_line)
        except Exception:
            pass
        finally:
            self._is_running = False
            try:
                self.app.call_from_thread(
                    self.query_one("#orion-thinking-bar", Static).update,
                    "●  Orion process ended"
                )
            except Exception:
                pass

    def _handle_output_line(self, raw_line: str):
        line  = raw_line.rstrip()
        if line == self._last_line and line:
            return
        self._last_line = line
        clean = strip_ansi(line)
        rich  = ansi_to_rich(line)

        if not clean:
            self.app.call_from_thread(self._write_log, "", "")
            return

        for prefix, tool in TOOL_PREFIXES.items():
            if clean.startswith(prefix):
                self._flash_tool(tool)
                break

        if "[Thinking]" in clean:
            self.app.call_from_thread(
                self.query_one("#orion-thinking-bar", Static).update,
                "◉  Orion is thinking..."
            )
        elif "[Listening...]" in clean:
            self.app.call_from_thread(
                self.query_one("#orion-thinking-bar", Static).update,
                "◎  Listening for voice..."
            )
        elif re.match(r"YOU\s*(\(Voice\))?\s*[>▸]", clean):
            self.app.call_from_thread(
                self.query_one("#orion-thinking-bar", Static).update,
                "⏵  Input received"
            )
        elif re.match(r"AI\s*(\(Voice\)|Intermediate\s*)?\s*[>▸]", clean):
            self.app.call_from_thread(
                self.query_one("#orion-thinking-bar", Static).update,
                "●  Responding..."
            )
        elif clean in ("Terminal AI ready. Type 'exit' to quit.",):
            self.app.call_from_thread(
                self.query_one("#orion-thinking-bar", Static).update,
                "●  Ready"
            )

        if re.fullmatch(r"YOU\s*(\(Voice\))?\s*[>▸]\s*", clean):
            self.app.call_from_thread(
                self.query_one("#orion-thinking-bar", Static).update,
                "●  Ready"
            )
            return

        if re.match(r"AI\s*(Intermediate\s*)?[>▸]", clean):
            style = "bold green"
        elif re.match(r"AI\s*\(Voice\)\s*[>▸]", clean):
            style = "bold green"
        elif re.match(r"YOU\s*(\(Voice\))?\s*[>▸]", clean):
            style = "bold cyan"
        elif "[Thinking]" in clean:
            style = "bold yellow"
        elif "[Listening...]" in clean:
            style = "bold cyan"
        elif clean.startswith("[EXECUTING]"):
            style = "bold magenta"
        elif re.match(r"\[(MEMORY|READING|WRITING|SCRAPING|MEMORY SAVED|OK|OUT)\]", clean):
            style = "dim #00aa55"
        elif re.match(r"\[(ERR|ERROR|EXCEPTION)\]", clean, re.IGNORECASE):
            style = "bold red"
        elif re.match(r"(Traceback|Error:|Exception:)", clean):
            style = "bold red"
        elif re.match(r"\[WARN\]|\[SKIP\]", clean):
            style = "dim yellow"
        elif clean.startswith("Terminal AI ready"):
            style = "bold cyan"
        else:
            style = "dim green"

        self.app.call_from_thread(self._write_log, rich or clean, style)

    def _flash_tool(self, name: str):
        def on():
            try:
                self.query_one(f"#tool-{name}").add_class("active")
            except Exception:
                pass
        def off():
            try:
                self.query_one(f"#tool-{name}").remove_class("active")
            except Exception:
                pass
        self.app.call_from_thread(on)
        threading.Timer(2.0, lambda: self.app.call_from_thread(off)).start()

    _RICH_TAG_RE = re.compile(
        r"\[/?(?:bold|dim|italic|underline|strike|reverse|blink|"
        r"red|green|yellow|blue|magenta|cyan|white|black|"
        r"bright_\w+|#[0-9a-fA-F]{6}|on\s+\w+|link[^\]]*)[^\]]*\]"
    )

    def _write_log(self, text, style="dim green"):
        try:
            log = self.query_one("#orion-log", RichLog)
            if self._RICH_TAG_RE.search(text):
                try:
                    log.write(text)
                except Exception:
                    log.write(Text(re.sub(r"\[[^\]]*\]", "", text), style))
            else:
                log.write(Text(text, style))
        except Exception:
            pass

    def _send_message(self, text: str):
        if not self._is_running or self._proc is None:
            self._write_log(
                "✗ Orion is not running. Please wait for it to start.",
                "bold red"
            )
            return
        try:
            self._write_log(f"YOU > {text}", "bold cyan")
            self._proc.stdin.write(text + "\n")
            self._proc.stdin.flush()
        except BrokenPipeError:
            self._write_log("✗ Orion process closed unexpectedly.", "bold red")
            self._is_running = False
        except Exception as e:
            self._write_log(f"✗ Send error: {e}", "bold red")

    def _shutdown_proc(self):
        self._is_running = False
        if self._proc is not None:
            try:
                self._proc.stdin.close()
            except Exception:
                pass
            try:
                self._proc.terminate()
            except Exception:
                pass
            self._proc = None

    def on_button_pressed(self, event: Button.Pressed):
        bid = str(event.button.id)
        if bid == "orion-back":
            self._shutdown_proc()
            self.dismiss()
        elif bid == "orion-send":
            try:
                val = self.query_one("#orion-input", Input).value.strip()
                if val:
                    self._send_message(val)
                    self.query_one("#orion-input", Input).clear()
                    self.query_one("#orion-input", Input).focus()
            except Exception:
                pass
        elif bid == "orion-apikey-btn":
            self.app.push_screen(OrionApiKeyScreen())

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "orion-input":
            val = event.value.strip()
            if val:
                self._send_message(val)
                event.input.clear()

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

    def _after_voice(self, _success):
        self._launch_orion()

    def _launch_orion(self):
        self.app.switch_screen(OrionScreen())
