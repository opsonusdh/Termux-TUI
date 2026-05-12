from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Static, Input, Switch, RichLog
from textual.containers import Horizontal, Vertical, VerticalScroll, Grid
from textual import work
from rich.text import Text
import subprocess, os, random, time, json, re, threading, tempfile, shutil

from utils.constants import (
    CONFIG_PATH, ICONS, DEFAULT_MUSIC_DIRS, MUSIC_EXTENSIONS, 
    MUSIC_PLAYER_SETTING_CSS, MUSIC_PLAYER_CSS, FILE_EXPLORER_CSS, DIALER_CSS,
    YT_CONFIG_PATH, TEMP_DIR, TEMP_CURR, TEMP_NEXT, TEMP_PREV, DEFAULT_YT_DOWNLOAD_DIR,
    YTMP3_CSS, YTMP3_PLAYLIST_CSS, YTMP3_SETTINGS_CSS
)
from utils.helpers import (
    load_config, save_config, scan_music, mp_run, mp_info, to_mmss, fmt_size, run_cmd, 
    call_number, fetch_contacts, fetch_call_log, type_icon, clean_number, match_contacts,
    load_yt_config, save_yt_config, yt_search, yt_get_audio_url, yt_download_to_file, 
     yt_fetch_radio
)


# MUSIC SETTINGS SCREEN
class MusicPlayerSettingsScreen(Screen):

    CSS = MUSIC_PLAYER_SETTING_CSS

    def __init__(self, config, on_save):
        super().__init__()
        self._config  = load_config()
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
        self.app.set_theme(self._config.get("theme", "jarvis"))
            
    def on_button_pressed(self, event: Button.Pressed):
        bid = str(event.button.id)
        if bid == "set-close":
            self._on_save(self._config)
            self.dismiss()
        elif bid == "set-add-dir":
            inp = self.query_one("#set-dir-input", Input)
            if inp.display and inp.value.strip():
                # input is visible and has text — treat as submit
                path = inp.value.strip()
                if path not in self._config['music_dirs']:
                    self._config['music_dirs'].append(path)
                    scroll = self.query_one("#set-scroll", VerticalScroll)
                    scroll.mount(
                        Button(f"  📁 {path}", classes="set-dir-btn",
                               id=f"setdir-{abs(hash(path))}"),
                        before=self.query_one("#add-or-delete")
                    )
                inp.clear()
                inp.display = False
                event.button.label = "+ Add"
            else:
                # input is hidden or empty — show it
                inp.display = True
                inp.focus()
                # also change button label to hint
                event.button.label = "✓ Confirm"
                
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
                Button(f"  📁 {path}", classes="set-dir-btn",
                       id=f"setdir-{abs(hash(path))}"),
                before=self.query_one("#add-or-delete")
            )
        event.input.clear()
        event.input.display = False
        try:
            self.query_one("#set-add-dir", Button).label = "+ Add Folder"
        except Exception:
            pass

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
        self.app.set_theme(self._config.get("theme", "jarvis"))
        
        
        

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

        self.app.call_from_thread(update)
        
        # auto-advance when track ends (in worker thread)
        if self._is_playing and self._dur_sec > 0 \
                and self._pos_sec >= self._dur_sec:
            self._pos_sec    = 0
            self._dur_sec    = 0
            self._is_playing = False
            self._advance()

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
    _config = load_config()

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
        self.app.set_theme(self._config.get("theme", "jarvis"))

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
        


# DIALER
class DialerScreen(Screen):

    CSS = DIALER_CSS

    _typed        = ""
    _contacts     = []
    _log_offset   = 0
    _log_gen      = 0
    _contact_gen  = 0
    _active_tab   = "dialer"
    _config = load_config()

    def compose(self) -> ComposeResult:
        with Horizontal(id="dial-header"):
            yield Button("← Back", id="dial-back")

        with Horizontal(id="dial-tabs"):
            yield Button("📞 Dialer",   id="tab-dialer",   classes="dial-tab active")
            yield Button("📋 Logs",     id="tab-logs",     classes="dial-tab")
            yield Button("👥 Contacts", id="tab-contacts", classes="dial-tab")

        # DIALER PANEL
        with Vertical(id="panel-dialer"):
            with Vertical(id="dial-display"):
                yield Static("", id="dial-number")
                with Horizontal(id="dial-suggestions"):
                    for i in range(5):
                        yield Button("", id=f"suggest-{i}", classes="dial-suggest")

            with Vertical(id="dial-pad"):
                with Grid(id="dial-grid"):
                    yield Button("1", id="key-1", classes="dial-key")
                    yield Button("2", id="key-2", classes="dial-key")
                    yield Button("3", id="key-3", classes="dial-key")
                    yield Button("4", id="key-4", classes="dial-key")
                    yield Button("5", id="key-5", classes="dial-key")
                    yield Button("6", id="key-6", classes="dial-key")
                    yield Button("7", id="key-7", classes="dial-key")
                    yield Button("8", id="key-8", classes="dial-key")
                    yield Button("9", id="key-9", classes="dial-key")
                    yield Button("*", id="key-star", classes="dial-key")
                    yield Button("0", id="key-0", classes="dial-key")
                    yield Button("#", id="key-hash", classes="dial-key")
                with Horizontal(id="dial-call-row"):
                    yield Button("📞 CALL", id="dial-call")
                    yield Button("⌫",       id="dial-del")

        # LOGS PANEL
        with Vertical(id="panel-logs"):
            with VerticalScroll(id="logs-scroll"):
                yield Static("⏳ Loading logs...", id="logs-loading")

        # CONTACTS PANEL
        with Vertical(id="panel-contacts"):
            yield Input(placeholder="🔍 Search contacts...", id="contacts-search")
            with VerticalScroll(id="contacts-scroll"):
                yield Static("⏳ Loading contacts...", id="contacts-loading")

    def on_mount(self):
        self.load_contacts()
        self.app.set_theme(self._config.get("theme", "jarvis"))

    # TAB SWITCHING

    def _switch_tab(self, tab: str):
        self._active_tab = tab
        for t in ["dialer", "logs", "contacts"]:
            try:
                btn = self.query_one(f"#tab-{t}", Button)
                panel = self.query_one(f"#panel-{t}")
                if t == tab:
                    btn.add_class("active")
                    panel.styles.display = "block"
                else:
                    btn.remove_class("active")
                    panel.styles.display = "none"
            except Exception:
                pass
        # lazy load
        if tab == "logs" and self._log_offset == 0:
            self._log_offset = 0
            self.load_logs(reset=True)
        if tab == "contacts" and not self._contacts:
            self.load_contacts()

    # NUMPAD INPUT

    def _press_key(self, char: str):
        self._typed += char
        self.query_one("#dial-number", Static).update(self._typed)
        self._update_suggestions()

    def _delete_key(self):
        self._typed = self._typed[:-1]
        self.query_one("#dial-number", Static).update(self._typed)
        self._update_suggestions()

    def _update_suggestions(self):
        matches = match_contacts(self._typed, self._contacts)
        for i in range(5):
            btn = self.query_one(f"#suggest-{i}", Button)
            if i < len(matches):
                c = matches[i]
                btn.label = f"{c['name']}  {c['number']}"
                btn.styles.display = "block"
            else:
                btn.label = ""
                btn.styles.display = "none"

    # CONTACTS

    @work(thread=True)
    def load_contacts(self):
        contacts = fetch_contacts()
        self._contacts = contacts
        self.app.call_from_thread(self._render_contacts, contacts)

    def _render_contacts(self, contacts):
        self._contact_gen += 1
        gen    = self._contact_gen
        scroll = self.query_one("#contacts-scroll", VerticalScroll)
        scroll.remove_children()
        if not contacts or isinstance(contacts, dict):
            scroll.mount(Static("No contact found."))
            return

        for i, c in enumerate(contacts):
            name   = c.get('name', 'Unknown')
            number = c.get('number', '')

            row  = Horizontal(classes="contact-row")
            scroll.mount(row)                                    # mount row first
            info = Vertical(classes="contact-info")
            row.mount(info)                                      # then info into row
            info.mount(Static(name, classes="contact-name"))  # then statics into info
            info.mount(Static(number, classes="contact-num"))
            btn = Button("📞", id=f"ccall-{gen}-{i}", classes="contact-call-btn")
            row.mount(btn)
            row._call_number = number


    def on_input_changed(self, event: Input.Changed):
        if event.input.id != "contacts-search":
            return
        q = event.value.strip().lower()
        filtered = [c for c in self._contacts
                    if q in c.get('name','').lower()
                    or q in c.get('number','')]
        self._render_contacts(filtered)

    # CALL LOG

    @work(thread=True)
    def load_logs(self, reset=False):
        if reset:
            self._log_offset = 0

        # show loading on button before fetch
        def show_loading():
            for btn in self.query(".logs-load-more-btn"):
                btn.label = "⏳ Loading..."
                btn.disabled = True

        self.app.call_from_thread(show_loading)

        logs = fetch_call_log(limit=20, offset=self._log_offset)
        self._log_offset += 20
        self.app.call_from_thread(self._render_logs, logs, reset)

    def _render_logs(self, logs, reset):
        self._log_gen += 1
        gen    = self._log_gen
        scroll = self.query_one("#logs-scroll", VerticalScroll)

        if reset:
            scroll.remove_children()

        try:
            for old in self.query(".logs-load-more-btn"):
                old.remove()
        except Exception:
            pass

        if not logs and reset:
            scroll.mount(Static("No call logs found."))
            return

        for i, log in enumerate(logs):
            name   = log.get('name') or log.get('phone_number', 'Unknown')
            number = log.get('phone_number', '')
            icon   = type_icon(log.get('type', ''))
            date   = log.get('date', '')
            dur    = log.get('duration', '')

            row  = Horizontal(classes="log-row")
            scroll.mount(row)                                   # mount row first
            info = Vertical(classes="log-info")
            row.mount(info)                                     # then info into row
            info.mount(Static(f"{icon}  {name}", classes="log-name"))
            info.mount(Static(f"{number}  ·  {date}  ·  {dur}", classes="log-meta"))
            btn = Button("📞", id=f"lcall-{gen}-{i}", classes="log-call-btn")
            row.mount(btn)
            row._call_number = number

        scroll.mount(Button("⬇ Load More", id=f"logs-load-more-{self._log_gen}", classes="logs-load-more-btn"))

    # BUTTON HANDLER

    def on_button_pressed(self, event: Button.Pressed):
        bid = str(event.button.id)

        if bid == "dial-back":
            self.dismiss()

        elif bid in ("tab-dialer", "tab-logs", "tab-contacts"):
            self._switch_tab(bid[4:])  # strip "tab-"

        elif bid.startswith("key-"):
            key_map = {
                "key-0": "0", "key-1": "1", "key-2": "2", "key-3": "3",
                "key-4": "4", "key-5": "5", "key-6": "6", "key-7": "7",
                "key-8": "8", "key-9": "9", "key-star": "*", "key-hash": "#"
            }
            self._press_key(key_map.get(bid, ""))

        elif bid == "dial-del":
            self._delete_key()

        elif bid == "dial-call":
            if self._typed:
                call_number(self._typed)

        elif bid.startswith("suggest-"):
            idx = int(bid.split("-")[1])
            matches = match_contacts(self._typed, self._contacts)
            if idx < len(matches):
                number = clean_number(matches[idx]['number'])
                call_number(number)

        elif "logs-load-more-btn" in event.button.classes:
            self.load_logs(reset=False)

        elif bid.startswith("lcall-") or bid.startswith("ccall-"):
            # find the number from the parent row
            try:
                number = clean_number(event.button.parent.parent._call_number)
                if number:
                    call_number(number)
            except Exception:
                pass
        
        elif bid == "try-again-btn":
            self.load_contacts()



#  PLAYLIST SCREEN 

class YTmp3PlaylistScreen(Screen):

    CSS = YTMP3_PLAYLIST_CSS

    def __init__(self, config, on_open):
        super().__init__()
        self._config  = config
        self._on_open = on_open  # callback(playlist_name, tracks)

    def compose(self) -> ComposeResult:
        with Horizontal(id="pl-header"):
            yield Static("◈  PLAYLISTS  ◈", id="pl-title")
            yield Button("✕ Close", id="pl-close")
        with Horizontal(id="pl-new-row"):
            yield Input(placeholder="New playlist name...", id="pl-name-input")
            yield Button("+ Create", id="pl-create")
        with VerticalScroll(id="pl-scroll"):
            self._render_list()
    
    def on_mount(self):
        self.app.set_theme(load_config().get("theme", "jarvis"))
    
    def _render_list(self):
        try:
            scroll = self.query_one("#pl-scroll", VerticalScroll)
            scroll.remove_children()
        except Exception:
            pass
        playlists = self._config.get("playlists", {})
        if not playlists:
            try:
                self.query_one("#pl-scroll", VerticalScroll).mount(
                    Static("  No playlists yet. Create one above.",
                           id="pl-empty")
                )
            except Exception:
                pass
            return
        for name, tracks in playlists.items():
            row  = Horizontal(classes="pl-row")
            try:
                scroll = self.query_one("#pl-scroll", VerticalScroll)
                scroll.mount(row)
                info = Vertical()
                row.mount(info)
                info.mount(Static(name, classes="pl-name"))
                info.mount(Static(f"{len(tracks)} tracks", classes="pl-count"))
                row.mount(Button("▶ Open",   id=f"plopen-{abs(hash(name))}",
                                 classes="pl-open-btn"))
                row.mount(Button("✕ Delete", id=f"pldel-{abs(hash(name))}",
                                 classes="pl-del-btn"))
                row._pl_name = name
            except Exception:
                pass

    def on_button_pressed(self, event: Button.Pressed):
        bid = str(event.button.id)
        if bid == "pl-close":
            self.dismiss()
        elif bid == "pl-create":
            name = self.query_one("#pl-name-input", Input).value.strip()
            if name and name not in self._config.get("playlists", {}):
                self._config.setdefault("playlists", {})[name] = []
                save_yt_config(self._config)
                self.query_one("#pl-name-input", Input).clear()
                self._render_list()
        elif bid.startswith("plopen-"):
            try:
                name   = event.button.parent._pl_name
                tracks = self._config["playlists"].get(name, [])
                self._on_open(name, tracks)
                self.dismiss()
            except Exception:
                pass
        elif bid.startswith("pldel-"):
            try:
                name = event.button.parent._pl_name
                self._config["playlists"].pop(name, None)
                save_yt_config(self._config)
                self._render_list()
            except Exception:
                pass


#  MAIN YT SCREEN 

#  YT SETTINGS SCREEN 

class YTSettingsScreen(Screen):

    CSS = YTMP3_SETTINGS_CSS

    def __init__(self, config, on_save):
        super().__init__()
        self._config  = dict(config)
        self._on_save = on_save

    def compose(self) -> ComposeResult:
        with Horizontal(id="yts-header"):
            yield Static("⚙  YT SETTINGS  ⚙", id="yts-title")
            yield Button("✕ Close", id="yts-close")
        with VerticalScroll(id="yts-scroll"):
            yield Static("▸ TEMP DIRECTORY", classes="yts-section")
            yield Static("Where current / next / prev audio is cached between plays:", classes="yts-desc")
            yield Input(
                value=self._config.get("temp_dir", TEMP_DIR),
                placeholder=TEMP_DIR,
                id="yts-temp-dir",
                classes="yts-input"
            )
            yield Static("▸ DOWNLOAD DIRECTORY", classes="yts-section")
            yield Static("Where ⬇ Save sends your MP3 files:", classes="yts-desc")
            yield Input(
                value=self._config.get("download_dir", DEFAULT_YT_DOWNLOAD_DIR),
                placeholder=DEFAULT_YT_DOWNLOAD_DIR,
                id="yts-dl-dir",
                classes="yts-input"
            )
            yield Static("▸ CONFIG / PLAYLIST FILE", classes="yts-section")
            yield Static("Where playlists and settings are stored (JSON):", classes="yts-desc")
            yield Input(
                value=self._config.get("config_path", YT_CONFIG_PATH),
                placeholder=YT_CONFIG_PATH,
                id="yts-cfg-path",
                classes="yts-input"
            )
            with Horizontal(id="yts-btn-row"):
                yield Button("✓ Save", id="yts-save")
                yield Button("↺ Reset Defaults", id="yts-reset")

    def on_mount(self):
        self.app.set_theme(load_config().get("theme", "jarvis"))

    def on_button_pressed(self, event: Button.Pressed):
        bid = str(event.button.id)
        if bid == "yts-close":
            self.dismiss()
        elif bid == "yts-save":
            temp_dir = self.query_one("#yts-temp-dir",  Input).value.strip()
            dl_dir   = self.query_one("#yts-dl-dir",    Input).value.strip()
            cfg_path = self.query_one("#yts-cfg-path",  Input).value.strip()
            self._config["temp_dir"]     = temp_dir or TEMP_DIR
            self._config["download_dir"] = dl_dir   or DEFAULT_YT_DOWNLOAD_DIR
            self._config["config_path"]  = cfg_path or YT_CONFIG_PATH
            os.makedirs(self._config["temp_dir"], exist_ok=True)
            self._on_save(self._config)
            self.dismiss()
        elif bid == "yts-reset":
            self.query_one("#yts-temp-dir",  Input).value = TEMP_DIR
            self.query_one("#yts-dl-dir",    Input).value = DEFAULT_YT_DOWNLOAD_DIR
            self.query_one("#yts-cfg-path",  Input).value = YT_CONFIG_PATH


#  MAIN YT SCREEN 

class YTmp3Screen(Screen):

    CSS = YTMP3_CSS

    #  state 
    _config          = {}
    _query           = ""
    _search_results  = []   # all fetched so far
    _search_offset   = 0
    _result_gen      = 0
    _queue           = []   # list of track dicts currently playing from
    _queue_idx       = -1   # current index in _queue
    _is_playing      = False
    _pos_sec         = 0
    _dur_sec         = 0
    _poll_counter    = 0
    _dl_lock         = threading.Lock()
    _playlist_mode   = False   # True when playing from a playlist
    _playlist_name   = ""
    _radio_queue     = []   # YouTube algo recommendations for current track
    _radio_fetched   = False

    def __init__(self):
        super().__init__()
        self._config = load_yt_config()

    #  config-aware temp paths 

    @property
    def _temp_curr(self):
        td = self._config.get('temp_dir', TEMP_DIR)
        os.makedirs(td, exist_ok=True)
        return os.path.join(td, 'current.mp3')

    @property
    def _temp_next(self):
        return os.path.join(self._config.get('temp_dir', TEMP_DIR), 'next.mp3')

    @property
    def _temp_prev(self):
        return os.path.join(self._config.get('temp_dir', TEMP_DIR), 'prev.mp3')

    #  compose 

    def compose(self) -> ComposeResult:
        with Horizontal(id="yt-header"):
            yield Button("← Back",    id="yt-back")
            yield Button("♫ Playlists", id="yt-pl-btn")
            yield Button("⚙ Settings",  id="yt-settings-btn")

        with Horizontal(id="yt-searchbar"):
            yield Input(placeholder="🔍 Search YouTube...", id="yt-search")
            yield Button("Search", id="yt-search-btn")

        with VerticalScroll(id="yt-results"):
            yield Static("Search for a song above.", id="yt-empty")

        with Vertical(id="yt-nowplaying"):
            yield Static("Nothing playing", id="yt-np-title")
            yield Static("⏹  STOPPED",     id="yt-np-status")
            with Horizontal(id="yt-np-progress-row"):
                yield Static("0:00",   id="yt-np-pos")
                yield Static("░" * 20, id="yt-np-bar")
                yield Static("0:00",   id="yt-np-dur")
            with Horizontal(id="yt-controls"):
                yield Button("⏮",        id="yt-prev")
                yield Button("▶",        id="yt-playpause")
                yield Button("⏭",        id="yt-next")
                yield Button("⬇ Save",   id="yt-dl-current")
            with Vertical(id="disclaimer-box"):
                yield Static(
                    "⚠ Package yt-dlp or/and ffmpeg is not installed. Please install to use the app.",
                    id="disclaimer"
                )
                yield Button("OK", id="disclaimer-ok-btn")

    def on_mount(self):
        self.app.set_theme(load_config().get("theme", "jarvis"))
        if subprocess.run(['which', 'yt-dlp'], capture_output=True).returncode != 0 \
                or subprocess.run(['which', 'ffmpeg'], capture_output=True).returncode != 0:
            self.query_one("#disclaimer-box", Vertical).styles.display = "block"
            self.query_one("#disclaimer-box", Vertical).refresh()
        self.set_interval(1, self.tick)

    #  tick 

    @work(thread=True)
    def tick(self):
        self._poll_counter += 1
        if self._poll_counter % 10 == 1 and self._is_playing:
            info   = mp_info()
            status = info.get('status', 'stopped').lower()
            self._is_playing = (status == 'playing')
            if 'position' in info: self._pos_sec = info['position']
            if 'duration'  in info: self._dur_sec  = info['duration']

        if self._is_playing:
            self._pos_sec += 1

        dur   = max(1, self._dur_sec)
        pos   = min(self._pos_sec, dur)

        bar_widget = self.query_one("#yt-np-bar", Static)
        width = max(1, int(bar_widget.size.width*0.8))

        pct   = int((pos / dur) * width)
        bar   = "█" * pct + "░" * (width - pct)
        emoji = "▶" if self._is_playing else "| |"

        def update():
            self.query_one("#yt-np-bar",    Static).update(bar)
            self.query_one("#yt-np-pos",    Static).update(to_mmss(pos))
            self.query_one("#yt-np-dur",    Static).update(
                to_mmss(dur) if self._dur_sec else "0:00"
            )
            self.query_one("#yt-np-status", Static).update(
                f"{emoji}  {'PLAYING' if self._is_playing else 'STOPPED'}"
            )

        self.app.call_from_thread(update)
        
        # auto advance (in worker thread)
        if self._is_playing and self._dur_sec > 0 \
                and self._pos_sec >= self._dur_sec:
            self._pos_sec    = 0
            self._dur_sec    = 0
            self._is_playing = False
            self._advance()

    #  search 

    @work(thread=True)
    def do_search(self, query, reset=False):
        if reset:
            self._search_offset  = 0
            self._search_results = []

        self.app.call_from_thread(self._set_loading, reset)
        results = yt_search(query, limit=10, offset=self._search_offset)
        self._search_results.extend(results)
        self._search_offset += len(results)
        self.app.call_from_thread(self._render_results, results, reset)

    def _set_loading(self, reset):
        results = self.query_one("#yt-results", VerticalScroll)
        if reset:
            results.remove_children()
            results.mount(Static("⏳ Searching...", id="yt-loading"))
        else:
            for btn in self.query(".yt-load-more-btn"):
                btn.label = "⏳ Loading..."
                btn.disabled = True

    def _render_results(self, new_results, reset):
        self._result_gen += 1
        gen     = self._result_gen
        scroll  = self.query_one("#yt-results", VerticalScroll)

        if reset:
            scroll.remove_children()

        for btn in self.query(".yt-load-more-btn"):
            btn.remove()

        if not new_results and reset:
            scroll.mount(Static("No results found.", id="yt-empty"))
            return

        offset = self._search_offset - len(new_results)
        for i, track in enumerate(new_results):
            real_i = offset + i
            row = Horizontal(classes="yt-result-row")
            scroll.mount(row)
            info = Vertical(classes="yt-result-info")
            row.mount(info)
            info.mount(Static(track['title'],
                              classes="yt-result-title"))
            info.mount(Static(
                f"{track['uploader']}  ·  {track['duration']}",
                classes="yt-result-meta"
            ))
            row.mount(Button("▶ Play", id=f"ytplay-{gen}-{real_i}",
                             classes="yt-play-btn"))
            row.mount(Button("⬇",     id=f"ytdl-{gen}-{real_i}",
                             classes="yt-dl-btn"))
            row.mount(Button("♫+",    id=f"ytadd-{gen}-{real_i}",
                             classes="yt-addpl-btn"))
            row._track_idx = real_i

        scroll.mount(Button(
            "⬇ Load More",
            id=f"yt-load-more-{gen}",
            classes="yt-load-more-btn"
        ))

    #  playback 

    def _play_queue(self, tracks, start_idx=0):
        """Set queue and play from start_idx."""
        self._queue       = tracks
        self._queue_idx   = start_idx
        self._play_track(tracks[start_idx])

    @work(thread=True)
    def _play_track(self, track):
        """Download and play a track. Also pre-fetch next and prev."""
        self.app.call_from_thread(
            self.query_one("#yt-np-title",  Static).update,
            f"⏳ Loading: {track['title'][:40]}..."
        )
        self.app.call_from_thread(
            self.query_one("#yt-np-status", Static).update,
            "⬇  DOWNLOADING..."
        )

        # promote current → prev so ⏮ plays it without re-downloading
        if os.path.exists(self._temp_curr):
            shutil.copy2(self._temp_curr, self._temp_prev)

        # download current
        ok = yt_download_to_file(track['url'], self._temp_curr)
        if not ok:
            self.app.call_from_thread(
                self.query_one("#yt-np-status", Static).update,
                "✗  Download failed"
            )
            return

        # play it
        mp_run('play', self._temp_curr)
        self._is_playing  = True
        self._pos_sec     = 0
        self._dur_sec     = 0
        self._poll_counter = 0

        # fetch YouTube algo radio in background
        self._radio_queue   = []
        self._radio_fetched = False
        threading.Thread(
            target=self._fetch_radio_bg,
            args=(track['id'],),
            daemon=True
        ).start()

        self.app.call_from_thread(
            self.query_one("#yt-np-title",    Static).update,
            track['title']
        )
        self.app.call_from_thread(
            self.query_one("#yt-np-status",   Static).update,
            "▶  PLAYING"
        )
        self.app.call_from_thread(
            self.query_one("#yt-playpause",   Button).label.__class__,
        )
        def set_pause():
            self.query_one("#yt-playpause", Button).label = "⏸"
        self.app.call_from_thread(set_pause)

        

    @work(thread=True)
    def _play_from_prefetch(self, temp_path, track, save_prev=True):
        """Play from pre-fetched temp file. Falls back to fresh download."""
        if os.path.exists(temp_path):
            if save_prev and os.path.exists(self._temp_curr):
                shutil.copy2(self._temp_curr, self._temp_prev)
            shutil.copy2(temp_path, self._temp_curr)
            mp_run('play', self._temp_curr)
            self._is_playing   = True
            self._pos_sec      = 0
            self._dur_sec      = 0
            self._poll_counter = 0
            def update():
                self.query_one("#yt-np-title",  Static).update(track['title'])
                self.query_one("#yt-np-status", Static).update("▶  PLAYING")
                self.query_one("#yt-playpause", Button).label = "⏸"
            self.app.call_from_thread(update)
        else:
            # fallback: download fresh
            self._play_track(track)

    def _advance(self):
        if self._radio_fetched and self._radio_queue:
            # use YouTube's algo — pop next from radio queue
            next_track = self._radio_queue.pop(0)
            # inject into queue so prev works
            self._queue.insert(self._queue_idx + 1, next_track)
            self._queue_idx += 1
            self._play_from_prefetch(self._temp_next, next_track)
        elif self._queue:
            # fallback to search list
            self._queue_idx = (self._queue_idx + 1) % len(self._queue)
            self._play_from_prefetch(self._temp_next, self._queue[self._queue_idx])

    def _go_prev(self):
        if not self._queue:
            return
        self._queue_idx = (self._queue_idx - 1) % len(self._queue)
        self._play_from_prefetch(self._temp_prev, self._queue[self._queue_idx], save_prev=False)

    def _go_next(self):
        self._advance()

    #  download to library 

    @work(thread=True)
    def download_track(self, track):
        dl_dir = self._config.get("download_dir", DEFAULT_YT_DOWNLOAD_DIR)
        os.makedirs(dl_dir, exist_ok=True)
        safe  = re.sub(r'[^\w\s-]', '', track['title']).strip()[:60]
        dest  = os.path.join(dl_dir, safe + ".mp3")

        self.app.call_from_thread(
            self.query_one("#yt-np-status", Static).update,
            f"⬇  Saving: {safe[:30]}..."
        )
        ok = yt_download_to_file(track['url'], dest)
        msg = f"✅ Saved to {dl_dir}" if ok else "✗  Download failed"
        self.app.call_from_thread(
            self.query_one("#yt-np-status", Static).update, msg
        )

    #  add to playlist picker 

    def _show_playlist_picker(self, track):
        """Show a quick picker to add track to a playlist."""
        playlists = self._config.get("playlists", {})
        if not playlists:
            # auto-create default
            self._config.setdefault("playlists", {})["Favorites"] = []
            save_yt_config(self._config)
            playlists = self._config["playlists"]

        # just add to first playlist for simplicity if only one
        # otherwise push playlist screen
        def on_open(name, tracks):
            lst = self._config["playlists"].setdefault(name, [])
            if not any(t.get('id') == track.get('id') for t in lst):
                lst.append(track)
                save_yt_config(self._config)

        self.app.push_screen(YTmp3PlaylistScreen(self._config, on_open))

    
    def _fetch_radio_bg(self, video_id):
        """Background: fetch YouTube Radio mix and store as algo queue."""
        tracks = yt_fetch_radio(video_id, limit=25)
        if tracks:
            self._radio_queue   = tracks
            self._radio_fetched = True
            # pre-fetch first radio track
            threading.Thread(
                target=yt_download_to_file,
                args=(tracks[0]['url'], self._temp_next),
                daemon=True
            ).start()

    #  button handler 

    def on_button_pressed(self, event: Button.Pressed):
        bid = str(event.button.id)

        if bid == "yt-back":
            mp_run('stop')
            self.dismiss()
        elif bid == "disclaimer-ok-btn":
            self.dismiss()

        elif bid == "yt-pl-btn":
            def on_open(name, tracks):
                if tracks:
                    self._playlist_mode = True
                    self._playlist_name = name
                    self._play_queue(tracks, 0)
            self.app.push_screen(YTmp3PlaylistScreen(self._config, on_open))

        elif bid == "yt-settings-btn":
            def on_settings_save(cfg):
                self._config = cfg
                save_yt_config(cfg)
            self.app.push_screen(YTSettingsScreen(self._config, on_settings_save))

        elif bid == "yt-search-btn":
            q = self.query_one("#yt-search", Input).value.strip()
            if q:
                self._query = q
                self.do_search(q, reset=True)

        elif bid.startswith("yt-load-more-"):
            if self._query:
                self.do_search(self._query, reset=False)

        elif bid == "yt-playpause":
            info   = mp_info()
            status = info.get('status', 'stopped').lower()
            if status == 'playing':
                mp_run('pause')
                self._is_playing = False
                event.button.label = "▶"
                self.query_one("#yt-np-status", Static).update("⏸  PAUSED")
            elif status == 'paused':
                mp_run('play')
                self._is_playing = True
                event.button.label = "⏸"
                self.query_one("#yt-np-status", Static).update("▶  PLAYING")
            else:
                if self._queue and self._queue_idx >= 0:
                    self._play_track(self._queue[self._queue_idx])

        elif bid == "yt-prev":
            self._go_prev()

        elif bid == "yt-next":
            self._go_next()

        elif bid == "yt-dl-current":
            if self._queue and 0 <= self._queue_idx < len(self._queue):
                self.download_track(self._queue[self._queue_idx])

        elif bid.startswith("ytplay-"):
            real_i = int(bid.split("-")[-1])
            if 0 <= real_i < len(self._search_results):
                self._playlist_mode = False
                # queue = all search results, start at clicked
                self._play_queue(self._search_results, real_i)

        elif bid.startswith("ytdl-"):
            real_i = int(bid.split("-")[-1])
            if 0 <= real_i < len(self._search_results):
                self.download_track(self._search_results[real_i])

        elif bid.startswith("ytadd-"):
            real_i = int(bid.split("-")[-1])
            if 0 <= real_i < len(self._search_results):
                self._show_playlist_picker(self._search_results[real_i])

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "yt-search":
            q = event.value.strip()
            if q:
                self._query = q
                self.do_search(q, reset=True)
