from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Static, Input
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual import work
import subprocess, os, re, threading, shutil

from utils.apps.app_utils.ytmp3_utils import *
from utils.apps.app_utils.music_player_utils import mp_run
from utils.helpers import to_mmss, load_config

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

    #  compose 

    def __init__(self):
        super().__init__()
        self._config          = load_yt_config()
        self._query           = ""
        self._search_results  = []
        self._search_offset   = 0
        self._result_gen      = 0
        self._queue           = []
        self._queue_idx       = -1
        self._is_playing      = False
        self._pos_sec         = 0
        self._dur_sec         = 0
        self._poll_counter    = 0
        self._dl_lock         = threading.Lock()
        self._playlist_mode   = False
        self._playlist_name   = ""
        self._radio_queue     = []
        self._radio_fetched   = False

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
            yield Static("◈  YT-MP3  ◈", id="yt-header-title")
            yield Button("♫ Playlists", id="yt-pl-btn")
            yield Button("⚙ Settings",  id="yt-settings-btn")

        with Horizontal(id="yt-searchbar"):
            yield Input(placeholder=" Search YouTube...", id="yt-search")
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
        msg = f" Saved to {dl_dir}" if ok else "✗  Download failed"
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
                mp_run('resume')
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
