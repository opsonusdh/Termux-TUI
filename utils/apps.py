from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Static, Input, Switch, RichLog
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual import work
from rich.text import Text
import subprocess, os, random

from utils.constants import CONFIG_PATH, ICONS, DEFAULT_MUSIC_DIRS, MUSIC_EXTENSIONS, MUSIC_PLAYER_SETTING_CSS, MUSIC_PLAYER_CSS, FILE_EXPLORER_CSS
from utils.helpers import load_config, save_config, scan_music, mp_run, mp_info, to_mmss, fmt_size 

# CONFIG

config = load_config()


# MUSIC SETTINGS SCREEN
class MusicPlayerSettingsScreen(Screen):

    CSS = MUSIC_PLAYER_SETTING_CSS

    def __init__(self, config, on_save):
        super().__init__()
        self._config  = config
        self._on_save = on_save
        self._selected_dir = None

    def compose(self) -> ComposeResult:
        with Horizontal(id="set-header"):
            yield Static("◈  SETTINGS  ◈", id="set-title")
            yield Button("✕ Close", id="set-close")

        with VerticalScroll(id="set-scroll"):
            yield Static("▸ SCAN FOLDERS", classes="set-section")
            for d in self._config.get("music_dirs", DEFAULT_MUSIC_DIRS):
                yield Button(f"  📁 {d}", classes="set-dir-btn", id=f"setdir-{abs(hash(d))}")
            with Horizontal(id="add-or-delete"):
                yield Button("+ Add Folder", id="set-add-dir")
                yield Button("- Delete", id="set-delete-dir")
            yield Input(placeholder="Enter full path...", id="set-dir-input")

            yield Static("▸ PLAYBACK MODE", classes="set-section")
            with Horizontal(id="set-mode-row"):
                yield Button("➡ Sequential", id="setmode-sequential",
                             classes="mode-btn" + (" active" if self._config.get("music_mode") == "sequential" else ""))
                yield Button("🔀 Shuffle",   id="setmode-shuffle",
                             classes="mode-btn" + (" active" if self._config.get("music_mode") == "shuffle" else ""))
                yield Button("🔁 Repeat",    id="setmode-repeat",
                             classes="mode-btn" + (" active" if self._config.get("music_mode") == "repeat" else ""))

            yield Static("▸ BEHAVIOUR", classes="set-section")
            with Horizontal(id="set-stop-row"):
                yield Static("Stop music when closing player", id="set-stop-label")
                yield Switch(value=self._config.get("music_stop_on_close", True),
                             id="set-stop-switch")

    def on_mount(self):
        theme = config.get("theme", "jarvis")

        # remove old theme classes
        self.remove_class("theme-dark")
        self.remove_class("theme-light")

        # apply new one
        if theme == "dark":
            self.add_class("theme-dark")
        elif theme == "light":
            self.add_class("theme-light")
        
    def on_button_pressed(self, event: Button.Pressed):
        bid = str(event.button.id)
        if bid == "set-close":
            self._on_save(self._config)
            self.dismiss()
        elif bid == "set-add-dir":
            inp = self.query_one("#set-dir-input", Input)
            inp.display = True
            inp.focus()
        elif bid.startswith("setmode-"):
            mode = bid[8:]
            self._config['music_mode'] = mode
            for m in ["sequential", "shuffle", "repeat"]:
                try:
                    self.query_one(f"#setmode-{m}").remove_class("active")
                except Exception:
                    pass
            try:
                self.query_one(f"#setmode-{mode}").add_class("active")
            except Exception:
                pass
        elif bid == "set-delete-dir":
            if self._selected_dir and self._selected_dir in self._config['music_dirs']:
                dirs = self._config['music_dirs']
                dirs.remove(self._selected_dir)
                self._config['music_dirs'] = dirs
                # remove the widget
                tag = f"setdir-{abs(hash(self._selected_dir))}"
                try:
                    self.query_one(f"#{tag}").remove()
                except Exception:
                    pass
                self._selected_dir = None

        elif bid.startswith("setdir-"):
            # deselect previous
            for btn in self.query(".set-dir-btn"):
                btn.remove_class("selected")
            # select this one — find which dir it maps to
            for d in self._config.get("music_dirs", []):
                if f"setdir-{abs(hash(d))}" == bid:
                    self._selected_dir = d
                    break
            try:
                self.query_one(f"#{bid}").add_class("selected")
            except Exception:
                pass

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id != "set-dir-input":
            return
        path = event.value.strip()
        if path and path not in self._config['music_dirs']:
            self._config['music_dirs'].append(path)
            scroll = self.query_one("#set-scroll", VerticalScroll)
            scroll.mount(
                Button(f" 📁 {path}", classes="set-dir-btn",
                       id=f"setdir-{abs(hash(path))}"),
                before=self.query_one("#set-add-dir")
            )
        event.input.clear()
        event.input.display = False

    def on_switch_changed(self, event: Switch.Changed):
        if event.switch.id == "set-stop-switch":
            self._config['music_stop_on_close'] = event.value


# MUSIC PLAYER SCREEN
class MusicPlayerScreen(Screen):

    CSS = MUSIC_PLAYER_CSS

    _all_songs    = []
    _current_idx  = 0
    _pos_sec      = 0
    _dur_sec      = 0
    _is_playing   = False
    _poll_counter = 0
    _nav_gen      = 0
    _config       = {}

    def __init__(self):
        super().__init__()
        self._config = load_config()

    def compose(self) -> ComposeResult:
        # Search bar
        with Horizontal(id="mp-searchbar"):
            yield Input(placeholder="🔍 Search songs...", id="mp-search")
            yield Button("≡", id="mp-settings-btn")

        # Search results overlay (hidden by default)
        with VerticalScroll(id="mp-results"):
            pass

        # Main player
        with Vertical(id="mp-main"):
            yield Static("No track loaded", id="mp-track")
            yield Static("# STOPPED",      id="mp-status")
            with Horizontal(id="mp-progress-row"):
                yield Static("0:00", id="mp-time-pos")
                yield Static("░" * 20, id="mp-bar")
                yield Static("0:00", id="mp-time-dur")
            with Horizontal(id="mp-controls"):
                yield Button("⏮ ",   id="mp-prev")
                yield Button("▶",   id="mp-playpause")
                yield Button("⏭ ",   id="mp-next")

        # Bottom bar
        with Horizontal(id="mp-bottombar"):
            yield Button("← Back", id="mp-back")
            yield Static("", id="mp-nowplaying-bar")

    def on_mount(self):
        self.scan_and_load()
        self.set_interval(1, self.tick)
        
        theme = config.get("theme", "jarvis")

        # remove old theme classes
        self.remove_class("theme-dark")
        self.remove_class("theme-light")

        # apply new one
        if theme == "dark":
            self.add_class("theme-dark")
        elif theme == "light":
            self.add_class("theme-light")

    # scanning

    @work(thread=True)
    def scan_and_load(self):
        songs = scan_music(self._config.get("music_dirs", DEFAULT_MUSIC_DIRS))
        
        self._all_songs = songs
        self.app.call_from_thread(
            self.query_one("#mp-nowplaying-bar", Static).update,
            f"♫ {len(songs)} songs found"
        )

    # tick: internal clock + periodic sync

    @work(thread=True)
    def tick(self):
        self._poll_counter += 1

        # sync from termux every 10s or right after new song starts
        if self._poll_counter % 10 == 1:
            info = mp_info()
            status = info.get('status', 'stopped').lower()
            self._is_playing = (status == 'playing')
            if 'position' in info:
                self._pos_sec = info['position']
            if 'duration' in info:
                self._dur_sec = info['duration']
            if 'track' in info:
                name = os.path.basename(info['track'])
                self.app.call_from_thread(
                    self.query_one("#mp-track", Static).update, name
                )

        # advance internal clock
        if self._is_playing:
            self._pos_sec += 1

        # build UI values
        dur  = max(1, self._dur_sec)
        pos  = min(self._pos_sec, dur)
        
        bar_widget = self.query_one("#mp-bar", Static)
        width = max(1, int(bar_widget.size.width*0.8))
        
        pct  = int((pos / dur) * width)
        bar  = "█" * pct + "░" * (width - pct)
        pos_s = to_mmss(pos)
        dur_s = to_mmss(dur) if self._dur_sec else "0:00"
        emoji = "▶" if self._is_playing else "#"

        def update():
            self.query_one("#mp-bar",      Static).update(bar)
            self.query_one("#mp-time-pos", Static).update(pos_s)
            self.query_one("#mp-time-dur", Static).update(dur_s)
            self.query_one("#mp-status",   Static).update(
                f"{emoji}  {'PLAYING' if self._is_playing else 'STOPPED'}"
            )
            # auto-advance when track ends
            if self._is_playing and self._dur_sec > 0 \
                    and self._pos_sec >= self._dur_sec:
                self._pos_sec    = 0
                self._dur_sec    = 0
                self._is_playing = False
                self._advance()

        self.app.call_from_thread(update)

    # playback logic
    def _play_idx(self, idx: int, song_list=None):
        songs = song_list if song_list is not None else self._all_songs
        if not songs or not (0 <= idx < len(songs)):
            return
        path = songs[idx]
        mp_run('play', path)
        self._current_idx = idx
        self._pos_sec     = 0
        self._dur_sec     = 0
        self._is_playing  = True
        self._poll_counter = 0   # force sync next tick

        name = os.path.basename(path)
        self.query_one("#mp-track",       Static).update(name)
        self.query_one("#mp-status",      Static).update("▶")
        self.query_one("#mp-playpause",   Button).label = "| |"
        self.query_one("#mp-nowplaying-bar", Static).update(f"♫ {name}")

    def _advance(self):
        """Auto-advance based on mode."""
        n    = len(self._all_songs)
        mode = self._config.get("music_mode", "sequential")
        if n == 0:
            return
        if mode == "repeat":
            idx = self._current_idx
        elif mode == "shuffle":
            idx = random.randint(0, n - 1)
        else:
            idx = (self._current_idx + 1) % n
        self._play_idx(idx)

    def _next_idx(self):
        n    = len(self._all_songs)
        mode = self._config.get("music_mode", "sequential")
        if n == 0: return -1
        if mode == "shuffle": return random.randint(0, n - 1)
        return (self._current_idx + 1) % n

    def _prev_idx(self):
        n    = len(self._all_songs)
        mode = self._config.get("music_mode", "sequential")
        if n == 0: return -1
        if mode == "shuffle": return random.randint(0, n - 1)
        return (self._current_idx - 1) % n

    # search
    def on_input_changed(self, event: Input.Changed):
        if event.input.id != "mp-search":
            return
        q = event.value.strip().lower()
        results = self.query_one("#mp-results", VerticalScroll)

        if not q:
            results.remove_class("visible")
            results.remove_children()
            return

        filtered = [s for s in self._all_songs
                    if q in os.path.basename(s).lower()]
        results.remove_children()
        self._nav_gen += 1
        gen = self._nav_gen
        for i, path in enumerate(filtered):
            results.mount(Button(
                f"  🎵  {os.path.basename(path)}",
                id=f"mpres-{gen}-{i}",
                classes="mp-result"
            ))
            results.mount_data = filtered   # store for click handler
        results.add_class("visible")
        self._search_results = filtered

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "mp-search":
            # close search, clear
            results = self.query_one("#mp-results", VerticalScroll)
            results.remove_class("visible")
            results.remove_children()
            event.input.clear()

    # button handler

    def on_button_pressed(self, event: Button.Pressed):
        bid = str(event.button.id)

        if bid == "mp-back":
            if self._config.get("music_stop_on_close", True):
                mp_run('stop')
            save_config(self._config)
            self.dismiss()

        elif bid == "mp-settings-btn":
            def on_save(cfg):
                self._config = cfg
                save_config(cfg)
                # rescan with new dirs
                self.scan_and_load()
            self.app.push_screen(MusicPlayerSettingsScreen(self._config, on_save))

        elif bid == "mp-playpause":
            if self._is_playing:
                mp_run('pause')
                self._is_playing = False
                event.button.label = "▶"
                self.query_one("#mp-status", Static).update("| |")
            elif self._pos_sec > 0:
                mp_run('play')
                self._is_playing = True
                event.button.label = "| |"
                self.query_one("#mp-status", Static).update("▶  PLAYING")
            else:
                # nothing loaded — play first
                if self._all_songs:
                    self._play_idx(0)

        elif bid == "mp-prev":
            self._play_idx(self._prev_idx())

        elif bid == "mp-next":
            self._play_idx(self._next_idx())

        elif bid.startswith("mpres-"):
            # search result clicked
            idx  = int(bid.split("-")[-1])
            songs = getattr(self, '_search_results', [])
            if 0 <= idx < len(songs):
                # find real index in all_songs
                path = songs[idx]
                try:
                    real_idx = self._all_songs.index(path)
                except ValueError:
                    real_idx = 0
                self._current_idx = real_idx
                self._play_idx(real_idx)
                # close search
                results = self.query_one("#mp-results", VerticalScroll)
                results.remove_class("visible")
                results.remove_children()
                self.query_one("#mp-search", Input).clear()








class FileBrowserScreen(Screen):
    CSS = FILE_EXPLORER_CSS

    _file_entries = {}
    _nav_gen      = 0
    _current_path = os.path.expanduser("~")

    def compose(self) -> ComposeResult:
        with Horizontal(id="file-header"):
            yield Button("← Back", id="file-back-main")
            yield Button("⬆ Up",   id="file-up-btn")
            yield Static(self._current_path, id="file-path-display")
        with VerticalScroll(id="file-scroll"):
            yield Static("Loading...")
        yield Input(
            placeholder="📁 type path + Enter to jump anywhere...",
            id="file-input"
        )

    def on_mount(self):
        self.list_directory(self._current_path)

    @work(thread=True)
    def list_directory(self, path):
        self._nav_gen += 1
        gen = self._nav_gen
        self.app.call_from_thread(
            self.query_one("#file-path-display", Static).update,
            f"  📁 {path}"
        )
        try:    entries = sorted(os.listdir(path))
        except: entries = []

        dirs  = [e for e in entries if os.path.isdir(os.path.join(path, e))]
        files = [e for e in entries if not os.path.isdir(os.path.join(path, e))]

        file_entries = {}
        idx = 0
        for d in dirs:
            file_entries[idx] = os.path.join(path, d); idx += 1
        for f in files:
            file_entries[idx] = os.path.join(path, f); idx += 1

        def rebuild():
            self._file_entries = file_entries
            scroll = self.query_one("#file-scroll", VerticalScroll)
            scroll.remove_children()
            i = 0
            for d in dirs:
                scroll.mount(Button(
                    f"  📁  {d}/", id=f"fentry-{gen}-{i}",
                    classes="file-dir-btn"
                ))
                i += 1
            for f in files:
                try:    size = fmt_size(os.path.getsize(os.path.join(path, f)))
                except: size = "?"
                ext  = f.split(".")[-1].lower() if "." in f else ""
                icon = ICONS.get(ext, "📄")
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
        import time; time.sleep(0.1)
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
                for line in r.stdout.splitlines(): w(f"  {line}", "dim green")
            else:
                with open(path, 'r', errors='replace') as f:
                    for line in f.readlines()[:300]: w(f"  {line.rstrip()}", "dim green")
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
        if event.input.id != "file-input": return
        val    = event.value.strip()
        target = val if os.path.isabs(val) else os.path.join(self._current_path, val)
        target = os.path.normpath(target)
        if os.path.isdir(target):
            self._current_path = target
            self.list_directory(target)
        elif os.path.isfile(target):
            self.open_file(target)
        event.input.clear()