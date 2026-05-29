from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Static, Input, Switch
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual import work
import os, random

from utils.apps.app_utils.music_player_utils import *
from utils.helpers import to_mmss, load_config

# MUSIC SETTINGS SCREEN
class MusicPlayerSettingsScreen(Screen):

    CSS = MUSIC_PLAYER_SETTING_CSS

    def __init__(self, config, on_save):
        super().__init__()
        self._config  = load_music_config()
        self._main_config = load_config()
        self._on_save = on_save
        
        self._selected_dir = None

    def compose(self) -> ComposeResult:
        with Horizontal(id="set-header"):
            yield Static("󰇙  SETTINGS  󰇙", id="set-title")
            yield Button(" Close", id="set-close")

        with VerticalScroll(id="set-scroll"):
            yield Static("▸ SCAN FOLDERS", classes="set-section")
            for d in self._config.get("music_dirs", DEFAULT_MUSIC_DIRS):
                yield Button(f"   {d}", classes="set-dir-btn", id=f"setdir-{abs(hash(d))}")
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
                yield Switch(value=self._config.get("music_stop_on_close", False),
                             id="set-stop-switch")
    
    def on_mount(self):
        self.app.set_theme(self._main_config.get("theme", "jarvis"))
            
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
                        Button(f"   {path}", classes="set-dir-btn",
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
                event.button.label = " Confirm"
                
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
                Button(f"   {path}", classes="set-dir-btn",
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

    def __init__(self):
        super().__init__()
        self._config       = load_music_config()
        self._all_songs    = []
        self._current_idx  = 0
        self._pos_sec      = 0
        self._dur_sec      = 0
        self._is_playing   = False
        self._poll_counter = 0
        self._nav_gen      = 0
        

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
                yield Button("󰒮 ",   id="mp-prev")
                yield Button("",   id="mp-playpause")
                yield Button("󰒭 ",   id="mp-next")

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
            f"󰎆 {len(songs)} songs found"
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
        emoji = "" if self._is_playing else "#"

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
        self._current_idx  = idx
        self._pos_sec      = 0
        self._dur_sec      = 0
        self._is_playing   = True
        self._poll_counter = 0   # force sync next tick

        name = os.path.basename(path)
        def update_ui():
            self.query_one("#mp-track",          Static).update(name)
            self.query_one("#mp-status",          Static).update("")
            self.query_one("#mp-playpause",       Button).label = "| |"
            self.query_one("#mp-nowplaying-bar",  Static).update(f"󰎆 {name}")
        self.app.call_from_thread(update_ui)
        

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
                f"  󰎆  {os.path.basename(path)}",
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
            if self._config.get("music_stop_on_close", False):
                mp_run('stop')
            save_music_config(self._config)
            self.dismiss()

        elif bid == "mp-settings-btn":
            def on_save(cfg):
                self._config = cfg
                save_music_config(cfg)
                # rescan with new dirs
                self.scan_and_load()
            self.app.push_screen(MusicPlayerSettingsScreen(self._config, on_save))

        elif bid == "mp-playpause":
            if self._is_playing:
                mp_run('pause')
                self._is_playing = False
                event.button.label = ""
                self.query_one("#mp-status", Static).update("| |")
            elif self._pos_sec > 0:
                mp_run('resume')
                self._is_playing = True
                event.button.label = "| |"
                self.query_one("#mp-status", Static).update("  PLAYING")
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
