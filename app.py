from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header, Footer, Button, Static, RichLog, Log,
    TabbedContent, TabPane, Input
)
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual import work
from textual.command import Provider, Hit, Hits, DiscoveryHit
from functools import partial
from rich.text import Text
import subprocess, os, re, time, json
from datetime import datetime
from utils.constants import SPLASH, BASIC_COMMANDS, TOOLS, CAT_STYLE, SYSTEM_CMDS, ICONS, CSS_SPLASH_SCREEN, CSS_MAIN
from utils.helpers import strip_ansi, get_recent_programs, get_battery, get_memory, run_speedtest, fmt_speed, flatten_json, fmt_size

# SPLASH SCREEN

class SplashScreen(Screen):
    CSS = CSS_SPLASH_SCREEN

    def compose(self) -> ComposeResult:
        yield Static(SPLASH,                      id="splash-art")
        yield Static("[ PRESS ANY KEY TO SKIP ]", id="splash-sub")

    def on_mount(self):
        self.auto_dismiss()

    def on_key(self):
        self.dismiss()
        
    @work(thread=True)
    def auto_dismiss(self):
        time.sleep(2.5)
        self.app.call_from_thread(self.dismiss)


# Theme colour
class ThemeCommand(Provider):
    _themes = [
        ("Theme: Jarvis", "jarvis"),
        ("Theme: Dark", "dark"),
        ("Theme: Light", "light"),
    ]

    async def discover(self) -> Hits:
        """Shown when palette opens with no query."""
        for label, key in self._themes:
            yield DiscoveryHit(
                display=label,
                command=partial(self.app.set_theme, key),
                help="Switch colour palette",
            )

    async def search(self, query: str) -> Hits:
        """Shown when user types."""
        for label, key in self._themes:
            if query.lower() in label.lower():
                yield Hit(
                    score=1.0,
                    match_display=label,
                    command=partial(self.app.set_theme, key),
                    text=label,
                    help="Switch colour palette",
                )


# MAIN APP

class TermuxDashboard(App):
    COMMANDS = App.COMMANDS | {ThemeCommand}
    _tick_count   = 0
    _cached_batt  = "..."
    _cached_mem   = "..."
    _net_rx_prev  = 0
    _net_tx_prev  = 0
    _alert_blink  = False
    _file_entries = {} # index → full path
    _nav_gen = 0
    _current_path = os.path.expanduser("~")

    CSS = CSS_MAIN
   

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():

            # HOME
            with TabPane("🏠 Home"):
                with Vertical():
                    with Horizontal(id="info-row"):
                        with Vertical(id="sys-info-box"):
                            yield Static("", id="sys-info")
                        yield Static("⏳ Loading weather...", id="weather")
                    with Horizontal(id="recent"):
                        for prog in get_recent_programs():
                            yield Button(prog, classes="recent-btn")
                    with Horizontal(id="action-row"):
                        yield Button("📦 Update",  id="update-btn",  variant="success")
                        yield Button("⬇ Install",  id="install-btn", variant="primary")
                    yield Input(placeholder="Package name...",          id="pkg-input")
                    yield Input(placeholder="$ Enter any command...",   id="cmd-input")
                    yield Log(id="log-view")

            # PACKAGES 
            with TabPane("📦 Packages"):
                with Vertical():
                    with VerticalScroll(id="pkg-scroll"):
                        for tool in TOOLS:
                            cs = CAT_STYLE.get(tool['cat'], "white")
                            with Horizontal(classes="tool-card"):
                                with Vertical(classes="tool-info"):
                                    yield Static(
                                        f"[{cs}][{tool['cat']}][/{cs}]  "
                                        f"[bold cyan]{tool['name']}[/bold cyan]",
                                        classes="tool-name"
                                    )
                                    yield Static(tool['desc'], classes="tool-desc")
                                yield Button("▸ INSTALL", id=f"tool-{tool['id']}", classes="install-btn")
                    yield RichLog(id="pkg-log", markup=True)

            # SYSTEM
            with TabPane("⚙ System"):
                with Vertical():
                    with VerticalScroll(id="sys-scroll"):
                        rows = [SYSTEM_CMDS[i:i+3] for i in range(0, len(SYSTEM_CMDS), 3)]
                        for row in rows:
                            with Horizontal(classes="sys-row"):
                                for cmd in row:
                                    yield Button(cmd['name'], id=f"syscmd-{cmd['id']}", classes="sys-btn")
                    yield RichLog(id="sys-log", markup=True)

            # FILES
            with TabPane("📁 Files"):
                with Vertical():
                    with Horizontal(id="file-nav"):
                        yield Button("⬆ Up", id="file-up-btn")
                        yield Static(self._current_path, id="file-path-display")
                    with VerticalScroll(id="file-scroll"):
                        yield Static("Loading...", id="file-placeholder")
                    yield Input(
                        placeholder="📁 type path + Enter to jump anywhere...",
                        id="file-input"
                    )

        yield Footer()

    # MOUNT

    def on_mount(self):
        self.push_screen(SplashScreen())
        self.fetch_weather()
        self.set_interval(1, self.tick_sysinfo)
        self.list_directory(self._current_path)
    
    def set_theme(self, key: str):
        for k in ["dark", "light"]:
            self.remove_class(f"theme-{k}")
        if key != "jarvis":
            self.add_class(f"theme-{key}")

    # SYSINFO TICK

    @work(thread=True)
    def tick_sysinfo(self):
        self._tick_count += 1
        time_str = datetime.now().strftime("%H:%M:%S")

        # battery + memory every 5 seconds
        if self._tick_count % 5 == 1:
            self._cached_batt = get_battery()
            self._cached_mem  = get_memory()

        # network speed every second

        text = (
            f"[ {time_str} ]\n\n"
            f"PWR  ▸ {self._cached_batt}\n\n"
            f"MEM  ▸ {self._cached_mem}\n\n"
        )
        self.call_from_thread(self.query_one("#sys-info", Static).update, text)

        # alert pulse when battery < 20%
        try:
            pct = int(self._cached_batt.split('%')[0].strip())
            temp = float(self._cached_batt.split('°C')[0].split("🔥")[1].strip()) if "🔥" in self._cached_batt else 0
            box = self.query_one("#sys-info-box")
            if pct < 20 or temp >= 40:
                self._alert_blink = not self._alert_blink
                if self._alert_blink:
                    self.call_from_thread(box.add_class, "alert")
                else:
                    self.call_from_thread(box.remove_class, "alert")
            else:
                self.call_from_thread(box.remove_class, "alert")
        except:
            pass

    # WEATHER

    @work(thread=True)
    def fetch_weather(self):
        try:
            r = subprocess.run(
                ['curl', '-s', '--max-time', '8', 'wttr.in/?0'],
                capture_output=True, text=True
            )
            weather = strip_ansi(r.stdout.strip())
        except:
            weather = "Weather unavailable"
        self.call_from_thread(self.query_one("#weather", Static).update, weather)

    # FILE BROWSER

    @work(thread=True)
    def list_directory(self, path):
        self._nav_gen += 1
        gen = self._nav_gen


        self.call_from_thread(
            self.query_one("#file-path-display", Static).update,
            f"  📁 {path}"
        )

        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            entries = []

        dirs  = [e for e in entries if os.path.isdir(os.path.join(path, e))]
        files = [e for e in entries if not os.path.isdir(os.path.join(path, e))]

        # Build entries map before going to main thread
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
                    f"  📁  {d}/",
                    id=f"fentry-{gen}-{i}",
                    classes="file-dir-btn"
                ))
                i += 1

            for f in files:
                try:   size = fmt_size(os.path.getsize(os.path.join(path, f)))
                except: size = "?"
                ext  = f.split(".")[-1].lower() if "." in f else ""
                icon = ICONS.get(ext, "📄")
                scroll.mount(Button(
                    f"  {icon}  {f}  [{size}]",
                    id=f"fentry-{gen}-{i}",
                    classes="file-file-btn"
                ))
                i += 1

            scroll.mount(Static(
                f"  {len(dirs)} dirs   {len(files)} files",
                classes="file-footer"
            ))

        self.call_from_thread(rebuild)

    @work(thread=True)
    def open_file(self, path):
        scroll = self.query_one("#file-scroll", VerticalScroll)

        def show():
            scroll.remove_children()
            rlog = RichLog(markup=True, id="file-view-log")
            scroll.mount(rlog)
            back = Button("⬆ Back to folder", id="file-back-btn", classes="file-dir-btn")
            scroll.mount(back)

        self.call_from_thread(show)
        time.sleep(0.1)  # let mount settle

        rlog = self.query_one("#file-view-log", RichLog)

        def w(text, style=""):
            self.call_from_thread(rlog.write, Text(text, style) if style else Text(text))

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

    # BUTTON HANDLER

    def on_button_pressed(self, event: Button.Pressed):
        bid = str(event.button.id)

        if bid == "update-btn":
            self.run_home_cmd(["pkg", "update", "-y"], "📦 Running update...")
        elif bid == "install-btn":
            inp = self.query_one("#pkg-input", Input)
            inp.display = True; inp.focus()
        elif "recent-btn" in event.button.classes:
            self.run_home_shell(str(event.button.label))
        elif bid.startswith("tool-"):
            tool = next((t for t in TOOLS if t['id'] == bid[5:]), None)
            if tool: self.install_tool(tool)
        elif bid.startswith("syscmd-"):
            cfg = next((c for c in SYSTEM_CMDS if c['id'] == bid[7:]), None)
            if cfg: self.run_sys_cmd(cfg)
        elif bid == "file-up-btn":
            parent = os.path.dirname(self._current_path)
            self._current_path = parent
            self.list_directory(parent)
        elif bid == "file-back-btn":
            self.list_directory(self._current_path)

        elif bid.startswith("fentry-"):
            idx = int(bid.split("-")[-1])  # always last segment
            target = self._file_entries.get(idx)
            if target and os.path.isdir(target):
                self._current_path = target
                self.list_directory(target)
            elif target and os.path.isfile(target):
                self.open_file(target)

    # INPUT HANDLER

    def on_input_submitted(self, event: Input.Submitted):
        val = event.value.strip()
        if not val: return

        if event.input.id == "pkg-input":
            self.run_home_cmd(["pkg", "install", val, "-y"], f"⬇ Installing {val}...")
            event.input.clear(); event.input.display = False

        elif event.input.id == "cmd-input":
            self.run_home_shell(val); event.input.clear()

        elif event.input.id == "file-input":
            target = val if os.path.isabs(val) else os.path.join(self._current_path, val)
            target = os.path.normpath(target)
            if os.path.isdir(target):
                self._current_path = target
                self.list_directory(target)
            elif os.path.isfile(target):
                self.open_file(target)
            else:
                # show error in file-view-log if open, otherwise mount a temporary one
                try:
                    rlog = self.query_one("#file-view-log", RichLog)
                except Exception:
                    scroll = self.query_one("#file-scroll", VerticalScroll)
                    scroll.remove_children()
                    rlog = RichLog(markup=True, id="file-view-log")
                    scroll.mount(rlog)
                    back = Button("⬆ Back to folder", id="file-back-btn", classes="file-dir-btn")
                    scroll.mount(back)
                rlog.write(Text(f"✗ Not found: {target}", "bold red"))
            event.input.clear()

    # WORKERS

    @work(thread=True)
    def run_home_cmd(self, cmd, msg):
        log = self.query_one("#log-view", Log)
        self.call_from_thread(log.write_line, msg)
        r = subprocess.run(cmd, capture_output=True, text=True)
        for line in (r.stdout + r.stderr).splitlines():
            self.call_from_thread(log.write_line, line)
        self.call_from_thread(log.write_line, "✅ Done!")

    @work(thread=True)
    def run_home_shell(self, cmd):
        log = self.query_one("#log-view", Log)
        self.call_from_thread(log.write_line, f"$ {cmd}")
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        out = r.stdout + r.stderr
        for line in (out.splitlines() if out.strip() else ["(no output)"]):
            self.call_from_thread(log.write_line, line)

    @work(thread=True)
    def install_tool(self, tool):
        rlog = self.query_one("#pkg-log", RichLog)
        def w(text, style=""):
            self.call_from_thread(rlog.write, Text(text, style) if style else Text(text))
        self.call_from_thread(rlog.clear)
        w(f"◈ Installing {tool['name']}", "bold cyan")
        w("─" * 36, "dim #1a1a3e")
        for i, step in enumerate(tool['steps']):
            w(f"\n[{i+1}/{len(tool['steps'])}] $ {step}", "bold yellow")
            r = subprocess.run(step, shell=True, capture_output=True, text=True)
            for line in (r.stdout + r.stderr).strip().splitlines():
                w(f"  {line}", "dim green")
        w("\n" + "─" * 36, "dim #1a1a3e")
        w(f"✅  {tool['name']} installed!", "bold green")

    @work(thread=True)
    def run_sys_cmd(self, cfg):
        rlog = self.query_one("#sys-log", RichLog)
        self.call_from_thread(rlog.clear)

        def w_header(text):
            t = Text(); t.append(f"\n◈ {text}\n", "bold cyan")
            self.call_from_thread(rlog.write, t)

        def w_kv(key, val):
            t = Text()
            t.append(f"  {key:<30}", "bold magenta")
            t.append("▸  ",          "dim white")
            t.append(str(val),        "bold green")
            self.call_from_thread(rlog.write, t)

        def w_raw(line):
            self.call_from_thread(rlog.write, Text(f"  {line}", "dim green"))

        w_header(cfg['name'])
        self.call_from_thread(rlog.write, Text("─" * 40, "dim #1a1a3e"))

        # special: speedtest
        if cfg.get('special') == 'speedtest':
            w_raw("⏳ Running speedtest, please wait (~30s)...")
            result = run_speedtest()
            for key, val in result.items():
                w_kv(key, val)
            return

        try:
            r = subprocess.run(
                cfg['cmd'], shell=True, capture_output=True, text=True, timeout=15
            )
            out = r.stdout.strip()
            if cfg['json'] and out:
                try:
                    for key, val in flatten_json(json.loads(out)):
                        w_kv(key, val)
                except json.JSONDecodeError:
                    for line in out.splitlines(): w_raw(line)
            else:
                for line in out.splitlines(): w_raw(line)
        except subprocess.TimeoutExpired:
            w_raw("⏱ Command timed out")
        except Exception as e:
            w_raw(f"✗ {e}")


app = TermuxDashboard()
app.run()
