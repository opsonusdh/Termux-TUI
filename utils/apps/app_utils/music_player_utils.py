import os, json, subprocess

MUSIC_CONFIG_PATH = os.path.expanduser(".termux_tui_music_config.json")
DEFAULT_MUSIC_DIRS=[ 
	os.path.expanduser("~/storage/music"),
	os.path.expanduser("~/storage/audio")
] 
MUSIC_EXTENSIONS= {
	'.mp3',
	'.flac',
	'.wav',
	'.ogg',
	'.m4a',
	'.aac',
	'.opus'
}

def load_music_config():
    try:
        with open(MUSIC_CONFIG_PATH) as f:
            return json.load(f)
    except Exception:
        return {
            "music_dirs": DEFAULT_MUSIC_DIRS, 
            "music_mode": "sequential", 
            "music_stop_on_close": False
        }
def save_music_config(cfg):
    try:
        with open(MUSIC_CONFIG_PATH, 'w') as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass
        
def scan_music(dirs):
    songs, seen = [], set()
    for d in dirs:
        try:
            with os.scandir(d) as it:
                for e in sorted(it, key=lambda x: x.name.lower()):
                    if e.is_file() and e.path not in seen and \
                       any(e.name.lower().endswith(x) for x in MUSIC_EXTENSIONS):
                        seen.add(e.path)
                        songs.append(e.path)
        except Exception:
            pass
    return songs


def mp_run(*args):
    try:
        r = subprocess.run(['termux-media-player', *args],
                           capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except Exception:
        return ""


def mp_info():
    out = mp_run('info')
    result = {}
    for line in out.splitlines():
        if line.startswith("Status:"):
            result['status'] = line.split(":", 1)[1].strip().lower()
        elif line.startswith("Track:"):
            result['track'] = line.split(":", 1)[1].strip()
        elif line.startswith("Current Position:"):
            times = line.split(":", 1)[1].strip().split("/")
            if len(times) == 2:
                def to_sec(t):
                    p = t.strip().split(":")
                    return int(p[0]) * 60 + int(p[1]) if len(p) == 2 else 0
                result['position'] = to_sec(times[0])
                result['duration'] = to_sec(times[1])
    return result
    
MUSIC_PLAYER_SETTING_CSS="""
 SettingsScreen {
	background: #0a0a0f;
}

#set-header {
	height: 3;
	background: #000020;
	border-bottom: solid #1a1a3e;
}

#set-title {
	width: 1fr;
	color: #00ffff;
	content-align: center middle;
}

#set-close {
	width: 12;
	background: #0d0d1a;
	color: #444466;
	border: none;
}

#set-close:hover {
	color: #00ffff;
}

#set-scroll {
	height: 1fr;
	background: #0a0a0f;
	padding: 1;
}

.set-section {
	color: #00ffff;
	margin: 1 0 0 0;
	height: 2;
	content-align: left middle;
}

.set-row {
	height: 3;
	margin: 0 0 0 2;
}

.set-label {
	width: 1fr;
	color: #00ff41;
	content-align: left middle;
}

.set-dir-btn {
	width: 100%;
	background: #050510;
	color: #00ff41;
	border: solid #1a1a3e;
	height: 3;
	margin: 0 0 1 0;
	content-align: left middle;
}

.set-dir-btn:hover {
	border: solid #00ff41;
}

#set-add-dir {
	width: 80%;
	background: #003300;
	color: #00ff41;
	border: tall #00ff41;
	margin: 1 0;
}

#set-delete-dir {
	width: 20%;
	background: #1a0000;
	color: red;
	border: tall red;
	margin: 1 0;
}

#set-delete-dir:hover {
	background: red;
	color: #000000;
}

.set-dir-btn.selected {
	border: solid red;
	color: red;
}

#set-dir-input {
	display: none;
	background: #050510;
	color: #00ff41;
	border: tall #333355;
}

#set-mode-row {
	height: 4;
	align: center middle;
}

#add-or-delete {
	height: auto;
}

.mode-btn {
	width: 14;
	background: #0d0d1a;
	color: #444466;
	border: tall #333355;
	margin: 0 1;
}

.mode-btn.active {
	background: #003300;
	color: #00ff41;
	border: tall #00ff41;
}

#set-stop-row {
	height: 3;
	margin: 1 0;
}

#set-stop-label {
	width: 1fr;
	color: #00ff41;
	content-align: left middle;
}


/* DARK theme */
MusicPlayerSettingsScreen.theme-dark {
	background: #111116;
}

MusicPlayerSettingsScreen.theme-dark #set-header {
	background: #1a1a24;
	border-bottom: solid #2a2a3a;
}

MusicPlayerSettingsScreen.theme-dark #set-title {
	color: #c9b8f0;
}

MusicPlayerSettingsScreen.theme-dark #set-close {
	background: #22223a;
	color: #555570;
}

MusicPlayerSettingsScreen.theme-dark #set-close:hover {
	color: #c9b8f0;
}

MusicPlayerSettingsScreen.theme-dark #set-scroll {
	background: #111116;
}

MusicPlayerSettingsScreen.theme-dark .set-section {
	color: #c9b8f0;
}

MusicPlayerSettingsScreen.theme-dark .set-dir-btn {
	background: #18181f;
	color: #7ec8e3;
	border: solid #2a2a3a;
}

MusicPlayerSettingsScreen.theme-dark .set-dir-btn:hover {
	border: solid #7c5cbf;
}

MusicPlayerSettingsScreen.theme-dark .set-dir-btn.selected {
	border: solid red;
	color: red;
}

MusicPlayerSettingsScreen.theme-dark #set-add-dir {
	background: #1a2233;
	color: #7ec8e3;
	border: tall #5b8dd9;
}

MusicPlayerSettingsScreen.theme-dark #set-delete-dir {
	background: #1a0000;
	color: red;
	border: tall red;
}

MusicPlayerSettingsScreen.theme-dark #set-delete-dir:hover {
	background: red;
	color: #000000;
}

MusicPlayerSettingsScreen.theme-dark #set-dir-input {
	background: #18181f;
	color: #7ec8e3;
	border: tall #2a2a3a;
}

MusicPlayerSettingsScreen.theme-dark .mode-btn {
	background: #22223a;
	color: #555570;
	border: tall #2a2a3a;
}

MusicPlayerSettingsScreen.theme-dark .mode-btn.active {
	background: #1a2233;
	color: #7ec8e3;
	border: tall #5b8dd9;
}

MusicPlayerSettingsScreen.theme-dark #set-stop-label {
	color: #7ec8e3;
}


/* LIGHT theme */
MusicPlayerSettingsScreen.theme-light {
	background: #f0f0f5;
}

MusicPlayerSettingsScreen.theme-light #set-header {
	background: #e0e0ec;
	border-bottom: solid #ccccdd;
}

MusicPlayerSettingsScreen.theme-light #set-title {
	color: #1a1a99;
}

MusicPlayerSettingsScreen.theme-light #set-close {
	background: #e8e8f5;
	color: #888899;
}

MusicPlayerSettingsScreen.theme-light #set-close:hover {
	color: #1a1a99;
}

MusicPlayerSettingsScreen.theme-light #set-scroll {
	background: #f0f0f5;
}

MusicPlayerSettingsScreen.theme-light .set-section {
	color: #1a1a99;
}

MusicPlayerSettingsScreen.theme-light .set-dir-btn {
	background: #ffffff;
	color: #116622;
	border: solid #ccccdd;
}

MusicPlayerSettingsScreen.theme-light .set-dir-btn:hover {
	border: solid #228833;
}

MusicPlayerSettingsScreen.theme-light .set-dir-btn.selected {
	border: solid red;
	color: red;
}

MusicPlayerSettingsScreen.theme-light #set-add-dir {
	background: #e8f5e8;
	color: #116622;
	border: tall #228833;
}

MusicPlayerSettingsScreen.theme-light #set-delete-dir {
	background: #fff0f0;
	color: red;
	border: tall red;
}

MusicPlayerSettingsScreen.theme-light #set-delete-dir:hover {
	background: red;
	color: #ffffff;
}

MusicPlayerSettingsScreen.theme-light #set-dir-input {
	background: #ffffff;
	color: #116622;
	border: tall #ccccdd;
}

MusicPlayerSettingsScreen.theme-light .mode-btn {
	background: #e8e8f5;
	color: #888899;
	border: tall #ccccdd;
}

MusicPlayerSettingsScreen.theme-light .mode-btn.active {
	background: #e8f5e8;
	color: #116622;
	border: tall #228833;
}

MusicPlayerSettingsScreen.theme-light #set-stop-label {
	color: #116622;
}

MusicPlayerSettingsScreen.theme-light #set-stop-switch {
	background: #b3b3b3;
	border: tall #999999;
}

"""


MUSIC_PLAYER_CSS="""
 MusicPlayerScreen {
	background: #0a0a0f;
}

/* header bar */
#mp-header {
	height: 4;
	background: #000020;
	border-bottom: double #1a1a3e;
	padding: 0 1;
}
#mp-header-title {
	width: 1fr;
	color: #00ffff;
	content-align: center middle;
	text-style: bold;
}

/* search bar */
#mp-searchbar {
	height: 4;
	background: #000020;
	border-bottom: solid #1a1a3e;
	padding: 0 1;
}

#mp-search {
	width: 1fr;
	background: #050510;
	color: #00ff41;
	border: tall #1a1a3e;
}

#mp-settings-btn {
	width: 5;
	background: #0d0d1a;
	color: #00ffff;
	border: tall #1a1a3e;
	margin-left: 1;
	padding: 0;
}

#mp-settings-btn:hover {
	background: #1a1a3e;
}

/* search results overlay */
#mp-results {
	display: none;
	height: 1fr;
	background: #020208;
	border: solid #1a1a3e;
}

#mp-results.visible {
	display: block;
}

.mp-result {
	width: 100%;
	background: #020208;
	color: #00ff41;
	border: none;
	height: 1;
	margin: 0;
	padding: 0 2;
}

.mp-result:hover {
	background: #0a1a0a;
}

/* main player area */
#mp-main {
	height: 1fr;
	align: center middle;
	background: #0a0a0f;
}

#mp-track {
	text-align: center;
	color: #00ffff;
	width: 100%;
	height: 3;
	content-align: center middle;
}

#mp-status {
	text-align: center;
	color: #00ff41;
	width: 100%;
	height: 2;
	content-align: center middle;
}

#mp-progress-row {
	height: 2;
	width: 100%;
	align: center middle;
}

#mp-time-pos {
	width: 7;
	color: #444466;
	content-align: right middle;
}

#mp-bar {
	width: 1fr;
	color: #00ffff;
	content-align: center middle;
}

#mp-time-dur {
	width: 7;
	color: #444466;
	content-align: left middle;
}

#mp-controls {
	height: 5;
	width: 100%;
	align: center middle;
}

#mp-prev {
	width: 11;
	background: #0d0d1a;
	color: #00ffff;
	border: tall #00ffff;
	margin: 0 1;
}

#mp-playpause {
	width: 13;
	background: #003300;
	color: #00ff41;
	border: tall #00ff41;
	margin: 0 1;
}

#mp-next {
	width: 11;
	background: #0d0d1a;
	color: #00ffff;
	border: tall #00ffff;
	margin: 0 1;
}

/* bottom bar */
#mp-bottombar {
	height: 3;
	background: #000020;
	border-top: solid #1a1a3e;
}

#mp-back {
	width: 1fr;
	background: #0d0d1a;
	color: #444466;
	border: none;
}

#mp-back:hover {
	color: #00ffff;
}

#mp-nowplaying-bar {
	width: 2fr;
	color: #444466;
	content-align: center middle;
}

/* DARK */
MusicPlayerScreen.theme-dark {
	background: #111116;
}

MusicPlayerScreen.theme-dark #mp-searchbar {
	background: #1a1a24;
	border-bottom: solid #2a2a3a;
}

MusicPlayerScreen.theme-dark #mp-search {
	background: #18181f;
	color: #7ec8e3;
	border: tall #2a2a3a;
}

MusicPlayerScreen.theme-dark #mp-settings-btn {
	background: #22223a;
	color: #c9b8f0;
	border: tall #2a2a3a;
}

MusicPlayerScreen.theme-dark #mp-settings-btn:hover {
	background: #2a2a3a;
}

MusicPlayerScreen.theme-dark #mp-results {
	background: #0e0e14;
	border: solid #2a2a3a;
}

MusicPlayerScreen.theme-dark .mp-result {
	background: #0e0e14;
	color: #7ec8e3;
}

MusicPlayerScreen.theme-dark .mp-result:hover {
	background: #1a2233;
}

MusicPlayerScreen.theme-dark #mp-main {
	background: #111116;
}

MusicPlayerScreen.theme-dark #mp-track {
	color: #c9b8f0;
}

MusicPlayerScreen.theme-dark #mp-status {
	color: #7ec8e3;
}

MusicPlayerScreen.theme-dark #mp-time-pos {
	color: #555570;
}

MusicPlayerScreen.theme-dark #mp-bar {
	color: #7c5cbf;
}

MusicPlayerScreen.theme-dark #mp-time-dur {
	color: #555570;
}

MusicPlayerScreen.theme-dark #mp-prev {
	background: #22223a;
	color: #c9b8f0;
	border: tall #7c5cbf;
}

MusicPlayerScreen.theme-dark #mp-playpause {
	background: #1a2233;
	color: #7ec8e3;
	border: tall #5b8dd9;
}

MusicPlayerScreen.theme-dark #mp-next {
	background: #22223a;
	color: #c9b8f0;
	border: tall #7c5cbf;
}

MusicPlayerScreen.theme-dark #mp-bottombar {
	background: #1a1a24;
	border-top: solid #2a2a3a;
}

MusicPlayerScreen.theme-dark #mp-back {
	background: #22223a;
	color: #555570;
}

MusicPlayerScreen.theme-dark #mp-back:hover {
	color: #c9b8f0;
}

MusicPlayerScreen.theme-dark #mp-nowplaying-bar {
	color: #555570;
}


/* LIGHT */
MusicPlayerScreen.theme-light {
	background: #f0f0f5;
}

MusicPlayerScreen.theme-light #mp-searchbar {
	background: #e0e0ec;
	border-bottom: solid #ccccdd;
}

MusicPlayerScreen.theme-light #mp-search {
	background: #ffffff;
	color: #116622;
	border: tall #ccccdd;
}

MusicPlayerScreen.theme-light #mp-settings-btn {
	background: #e8e8f5;
	color: #1a1a99;
	border: tall #ccccdd;
}

MusicPlayerScreen.theme-light #mp-settings-btn:hover {
	background: #dde8ff;
}

MusicPlayerScreen.theme-light #mp-results {
	background: #fafafa;
	border: solid #ccccdd;
}

MusicPlayerScreen.theme-light .mp-result {
	background: #fafafa;
	color: #116622;
}

MusicPlayerScreen.theme-light .mp-result:hover {
	background: #ddffd8;
}

MusicPlayerScreen.theme-light #mp-main {
	background: #f0f0f5;
}

MusicPlayerScreen.theme-light #mp-track {
	color: #1a1a99;
}

MusicPlayerScreen.theme-light #mp-status {
	color: #116622;
}

MusicPlayerScreen.theme-light #mp-time-pos {
	color: #888899;
}

MusicPlayerScreen.theme-light #mp-bar {
	color: #3366cc;
}

MusicPlayerScreen.theme-light #mp-time-dur {
	color: #888899;
}

MusicPlayerScreen.theme-light #mp-prev {
	background: #e8e8f5;
	color: #1a1a99;
	border: tall #3366cc;
}

MusicPlayerScreen.theme-light #mp-playpause {
	background: #e8f5e8;
	color: #116622;
	border: tall #228833;
}

MusicPlayerScreen.theme-light #mp-next {
	background: #e8e8f5;
	color: #1a1a99;
	border: tall #3366cc;
}

MusicPlayerScreen.theme-light #mp-bottombar {
	background: #e0e0ec;
	border-top: solid #ccccdd;
}

MusicPlayerScreen.theme-light #mp-back {
	background: #e8e8f5;
	color: #888899;
}

MusicPlayerScreen.theme-light #mp-back:hover {
	color: #1a1a99;
}

MusicPlayerScreen.theme-light #mp-nowplaying-bar {
	color: #888899;
}

"""
