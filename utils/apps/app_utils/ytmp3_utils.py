import json
import os
import subprocess

YT_CONFIG_PATH = os.path.expanduser("~/.termux_tui_yt_config.json")
TEMP_DIR = os.path.join(os.path.expanduser("~/.termux_tui_temp"), "yt")
os.makedirs(TEMP_DIR, exist_ok=True) 
TEMP_CURR=os.path.join(TEMP_DIR, "current.mp3") 
TEMP_NEXT=os.path.join(TEMP_DIR, "next.mp3") 
TEMP_PREV=os.path.join(TEMP_DIR, "prev.mp3") 
DEFAULT_YT_DOWNLOAD_DIR=os.path.expanduser("~/YouTube")

def _read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def load_yt_config():
    default = {
        "playlists": {},
        "download_dir": DEFAULT_YT_DOWNLOAD_DIR,
        "temp_dir": TEMP_DIR,
        "config_path": YT_CONFIG_PATH,
    }
    try:
        data = _read_json(YT_CONFIG_PATH)
        config_path = os.path.expanduser(data.get("config_path", YT_CONFIG_PATH))
        if config_path != YT_CONFIG_PATH and os.path.exists(config_path):
            data = {**data, **_read_json(config_path)}
        return {**default, **data}
    except (json.JSONDecodeError, OSError):
        return default


def save_yt_config(cfg):
    try:
        path = os.path.expanduser(cfg.get("config_path", YT_CONFIG_PATH))
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        if path != YT_CONFIG_PATH:
            with open(YT_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({"config_path": path}, f, indent=2)
    except OSError:
        pass


def yt_search(query, limit=10, offset=0):
    search_query = f"ytsearch{limit + offset}:{query}"
    try:
        r = subprocess.run([
            'yt-dlp', '--flat-playlist', '-j',
            '--no-warnings', '--quiet',
            search_query
        ], capture_output=True, text=True, timeout=30)

        results = []
        for line in r.stdout.strip().splitlines():
            try:
                data = json.loads(line)
                results.append({
                    'id':       data.get('id', ''),
                    'title':    data.get('title', 'Unknown'),
                    'duration': data.get('duration_string', '--:--'),
                    'uploader': data.get('uploader', ''),
                    'url':      f"https://www.youtube.com/watch?v={data.get('id','')}",
                })
            except (KeyError, json.JSONDecodeError, TypeError):
                continue
        return results[offset:]
    except (OSError, subprocess.SubprocessError):
        return []


def yt_get_audio_url(yt_url):
    try:
        r = subprocess.run([
            'yt-dlp', '-f', 'bestaudio[ext=m4a]/bestaudio/best',
            '--get-url', '--no-warnings', '--quiet', yt_url
        ], capture_output=True, text=True, timeout=20)
        return r.stdout.strip().splitlines()[0] if r.stdout.strip() else None
    except (IndexError, OSError, subprocess.SubprocessError):
        return None


def yt_download_to_file(yt_url, output_path):
    try:
        base = output_path.replace('.mp3', '')
        r = subprocess.run([
            'yt-dlp', '-f', 'bestaudio',
            '-x', '--audio-format', 'mp3',
            '--audio-quality', '0',
            '--no-warnings', '--quiet',
            '--force-overwrites',
            '-o', base + '.%(ext)s',
            yt_url
        ], capture_output=True, text=True, timeout=120)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False

def yt_fetch_radio(video_id, limit=25):
    radio_url = f"https://www.youtube.com/watch?v={video_id}&list=RD{video_id}"
    try:
        r = subprocess.run([
            'yt-dlp', '--flat-playlist', '-j',
            '--no-warnings', '--quiet',
            '--playlist-items', f'1:{limit}',
            radio_url
        ], capture_output=True, text=True, timeout=30)

        results = []
        for line in r.stdout.strip().splitlines():
            try:
                data   = json.loads(line)
                vid_id = data.get('id', '')
                if not vid_id or vid_id == video_id:
                    continue
                results.append({
                    'id':       vid_id,
                    'title':    data.get('title', 'Unknown'),
                    'duration': data.get('duration_string', '--:--'),
                    'uploader': data.get('uploader', ''),
                    'url':      f"https://www.youtube.com/watch?v={vid_id}",
                })
            except (KeyError, json.JSONDecodeError, TypeError):
                continue
        return results
    except (OSError, subprocess.SubprocessError):
        return []

# CSS
YTMP3_CSS="""
 YTmp3Screen {
	background: #0a0a0f;
}

/* header */
#yt-header {
	height: 3;
	background: #000020;
	border-bottom: solid #1a1a3e;
}

#yt-back {
	width: 12;
	background: #0d0d1a;
	color: #444466;
	border: none;
}

#yt-back:hover {
	color: #00ffff;
}

#yt-header-title {
	width: 1fr;
	color: #00ffff;
	content-align: center middle;
}

#yt-pl-btn {
	width: 14;
	background: #0d0d1a;
	color: #444466;
	border: none;
}

#yt-pl-btn:hover {
	color: #ff66cc;
}

#yt-settings-btn {
	width: 14;
	background: #0d0d1a;
	color: #444466;
	border: none;
}

#yt-settings-btn:hover {
	color: #00ffff;
}

/* search bar */
#yt-searchbar {
	height: 4;
	background: #000020;
	border-bottom: solid #1a1a3e;
	padding: 0 1;
}

#yt-search {
	width: 1fr;
	background: #050510;
	color: #00ff41;
	border: tall #1a1a3e;
}

#yt-search-btn {
	width: 12;
	background: #003300;
	color: #00ff41;
	border: tall #00ff41;
	margin-left: 1;
}

#yt-search-btn:hover {
	background: #00ff41;
	color: #000000;
}

/* results */
#yt-results {
	height: 1fr;
	background: #020208;
}

.yt-result-row {
	height: 5;
	border-bottom: solid #1a1a3e;
	padding: 0 1;
}

.yt-result-info {
	width: 1fr;
}

.yt-result-title {
	color: #00ffff;
	height: 3;
	content-align: left middle;
}

.yt-result-meta {
	color: #444466;
	height: 2;
	content-align: left middle;
}

.yt-play-btn {
	width: 8;
	background: #003300;
	color: #00ff41;
	border: tall #00ff41;
	margin: 1 1 1 0;
}

.yt-play-btn:hover {
	background: #00ff41;
	color: #000000;
}

.yt-dl-btn {
	width: 8;
	background: #001a33;
	color: #00aaff;
	border: tall #00aaff;
	margin: 1 1 1 0;
}

.yt-dl-btn:hover {
	background: #00aaff;
	color: #000000;
}

.yt-addpl-btn {
	width: 8;
	background: #1a0033;
	color: #ff66cc;
	border: tall #ff66cc;
	margin: 1 0;
}

.yt-addpl-btn:hover {
	background: #ff66cc;
	color: #000000;
}

.yt-load-more-btn {
	width: 100%;
	height: 3;
	background: #0d0d1a;
	color: #444466;
	border: tall #1a1a3e;
}

.yt-load-more-btn:hover {
	color: #00ffff;
}

#yt-empty {
	color: #444466;
	text-align: center;
	content-align: center middle;
	height: 5;
}

/* now playing */
#yt-nowplaying {
	height: 11;
	border-top: double #00ffff;
	background: #020212;
	padding: 1 2;
}

#yt-np-title {
	color: #00ffff;
	height: 2;
	content-align: center middle;
	text-align: center;
	text-style: bold;
	width: 100%;
}

#yt-np-status {
	color: #00ff41;
	height: 1;
	content-align: center middle;
	text-align: center;
	width: 100%;
}

#yt-np-progress-row {
	height: 2;
	align: center middle;
	width: 100%;
}

#yt-np-pos {
	width: 7;
	color: #336655;
	content-align: right middle;
}

#yt-np-bar {
	width: 1fr;
	color: #00ffff;
	content-align: center middle;
}

#yt-np-dur {
	width: 7;
	color: #336655;
	content-align: left middle;
}

#yt-controls {
	height: 4;
	align: center middle;
	width: 100%;
}

#yt-prev {
	width: 9;
	background: #071a24;
	color: #00aacc;
	border: tall #00aacc;
	margin: 0 1;
}

#yt-prev:hover {
	background: #00aacc;
	color: #000000;
}

#yt-playpause {
	width: 13;
	background: #002a00;
	color: #00ff41;
	border: tall #00ff41;
	margin: 0 1;
	text-style: bold;
}

#yt-playpause:hover {
	background: #00ff41;
	color: #000000;
}

#yt-next {
	width: 9;
	background: #071a24;
	color: #00aacc;
	border: tall #00aacc;
	margin: 0 1;
}

#yt-next:hover {
	background: #00aacc;
	color: #000000;
}

#yt-dl-current {
	width: 12;
	background: #001a33;
	color: #00aaff;
	border: tall #00aaff;
	margin: 0 1;
}

#yt-dl-current:hover {
	background: #00aaff;
	color: #000000;
}

#disclaimer-box {
	color: #444466;
	text-align: center;
	content-align: center middle;
	height: auto;
	padding: 0 1;
	display: none;
	position: absolute;
	layer: overlay;
	align: center middle;
	width: 50%;


}

#disclaimer-ok-btn {
	/* adding a green button with padding*/
	width: 6;
	background: #003300;
	color: #00ff41;
	border: tall #00ff41;
	height: 3;
	margin-top: 2;
}

/* theme: dark */
YTmp3Screen.theme-dark {
	background: #111116;
}

YTmp3Screen.theme-dark #yt-header {
	background: #1a1a24;
}

YTmp3Screen.theme-dark #yt-back {
	background: #22223a;
	color: #555570;
}

YTmp3Screen.theme-dark #yt-back:hover {
	color: #c9b8f0;
}

YTmp3Screen.theme-dark #yt-header-title {
	color: #c9b8f0;
}

YTmp3Screen.theme-dark #yt-searchbar {
	background: #1a1a24;
}

YTmp3Screen.theme-dark #yt-search {
	background: #18181f;
	color: #7ec8e3;
	border: tall #2a2a3a;
}

YTmp3Screen.theme-dark #yt-search-btn {
	background: #1a2233;
	color: #7ec8e3;
	border: tall #5b8dd9;
}

YTmp3Screen.theme-dark #yt-results {
	background: #0e0e14;
}

YTmp3Screen.theme-dark .yt-result-title {
	color: #c9b8f0;
}

YTmp3Screen.theme-dark .yt-result-meta {
	color: #555570;
}

YTmp3Screen.theme-dark .yt-result-row {
	border-bottom: solid #2a2a3a;
}

YTmp3Screen.theme-dark #yt-nowplaying {
	background: #0e0e18;
	border-top: double #7c5cbf;
}

YTmp3Screen.theme-dark #yt-np-title {
	color: #c9b8f0;
}

YTmp3Screen.theme-dark #yt-np-status {
	color: #7ec8e3;
}

YTmp3Screen.theme-dark #yt-np-bar {
	color: #7c5cbf;
}

YTmp3Screen.theme-dark #yt-np-pos {
	color: #444460;
}

YTmp3Screen.theme-dark #yt-np-dur {
	color: #444460;
}

YTmp3Screen.theme-dark #yt-prev {
	background: #1a1a2e;
	color: #c9b8f0;
	border: tall #7c5cbf;
}

YTmp3Screen.theme-dark #yt-prev:hover {
	background: #7c5cbf;
	color: #000000;
}

YTmp3Screen.theme-dark #yt-playpause {
	background: #1a2233;
	color: #7ec8e3;
	border: tall #5b8dd9;
}

YTmp3Screen.theme-dark #yt-playpause:hover {
	background: #5b8dd9;
	color: #000000;
}

YTmp3Screen.theme-dark #yt-next {
	background: #1a1a2e;
	color: #c9b8f0;
	border: tall #7c5cbf;
}

YTmp3Screen.theme-dark #yt-next:hover {
	background: #7c5cbf;
	color: #000000;
}

YTmp3Screen.theme-dark #yt-settings-btn {
	background: #22223a;
	color: #555570;
}

YTmp3Screen.theme-dark #yt-settings-btn:hover {
	color: #c9b8f0;
}

/* theme: light */
YTmp3Screen.theme-light {
	background: #f0f0f5;
}

YTmp3Screen.theme-light #yt-header {
	background: #e0e0ec;
}

YTmp3Screen.theme-light #yt-back {
	background: #e8e8f5;
	color: #888899;
}

YTmp3Screen.theme-light #yt-header-title {
	color: #1a1a99;
}

YTmp3Screen.theme-light #yt-searchbar {
	background: #e0e0ec;
}

YTmp3Screen.theme-light #yt-search {
	background: #ffffff;
	color: #116622;
	border: tall #ccccdd;
}

YTmp3Screen.theme-light #yt-search-btn {
	background: #e8f5e8;
	color: #116622;
	border: tall #228833;
}

YTmp3Screen.theme-light #yt-results {
	background: #fafafa;
}

YTmp3Screen.theme-light .yt-result-title {
	color: #1a1a99;
}

YTmp3Screen.theme-light .yt-result-meta {
	color: #888899;
}

YTmp3Screen.theme-light .yt-result-row {
	border-bottom: solid #ccccdd;
}

YTmp3Screen.theme-light #yt-nowplaying {
	background: #f5f5ff;
	border-top: double #3366cc;
}

YTmp3Screen.theme-light #yt-np-title {
	color: #1a1a99;
}

YTmp3Screen.theme-light #yt-np-status {
	color: #116622;
}

YTmp3Screen.theme-light #yt-np-bar {
	color: #3366cc;
}

YTmp3Screen.theme-light #yt-np-pos {
	color: #888899;
}

YTmp3Screen.theme-light #yt-np-dur {
	color: #888899;
}

YTmp3Screen.theme-light #yt-settings-btn {
	background: #e8e8f5;
	color: #888899;
}

YTmp3Screen.theme-light #yt-settings-btn:hover {
	color: #1a1a99;
}

YTmp3Screen.theme-light #yt-pl-btn {
	background: #bcbcde;
	color: #888899;
}

YTmp3Screen.theme-light #yt-pl-btn:hover {
	color: #ff66cc;
}

YTmp3Screen.theme-light #yt-playpause {
	background: #b3c2e0;
	color: #116622;
	border: tall #228833;
}

YTmp3Screen.theme-light #yt-playpause:hover {
	background: #228833;
	color: #ffffff;
}

YTmp3Screen.theme-light #yt-prev {
	background: #b3b3d9;
	color: #1a1a99;
	border: tall #3366cc;
}

YTmp3Screen.theme-light #yt-prev:hover {
	background: #3366cc;
	color: #ffffff;
}

YTmp3Screen.theme-light #yt-next {
	background: #b3b3d9;
	color: #1a1a99;
	border: tall #3366cc;
}

YTmp3Screen.theme-light #yt-next:hover {
	background: #3366cc;
	color: #ffffff;
}

YTmp3Screen.theme-light #yt-dl-current {
	background: #6699ff;
	color: #ffffff;
	border: tall #3366cc;
}

YTmp3Screen.theme-light #yt-dl-current:hover {
	background: #3366cc;
	color: #ffffff;
}

"""

YTMP3_PLAYLIST_CSS="""
 PlaylistScreen {
	background: #0a0a0f;
}

#pl-header {
	height: 3;
	background: #000020;
	border-bottom: solid #1a1a3e;
}

#pl-title {
	width: 1fr;
	color: #00ffff;
	content-align: center middle;
}

#pl-close {
	width: 12;
	background: #0d0d1a;
	color: #444466;
	border: none;
}

#pl-close:hover {
	color: #00ffff;
}

#pl-new-row {
	height: 5;
	padding: 1;
}

#pl-name-input {
	width: 1fr;
	background: #050510;
	color: #00ff41;
	border: tall #1a1a3e;
}

#pl-create {
	width: 16;
	background: #003300;
	color: #00ff41;
	border: tall #00ff41;
}

#pl-create:hover {
	background: #00ff41;
	color: #000000;
}

#pl-scroll {
	height: 1fr;
	background: #020208;
}

.pl-row {
	height: 5;
	border-bottom: solid #1a1a3e;
	padding: 0 1;
}

.pl-name {
	width: 1fr;
	color: #00ffff;
	height: 3;
	content-align: left middle;
}

.pl-count {
	width: 1fr;
	color: #444466;
	height: 2;
	content-align: left middle;
}

.pl-open-btn {
	width: 12;
	background: #003300;
	color: #00ff41;
	border: tall #00ff41;
	margin: 1 1 1 0;
}

.pl-open-btn:hover {
	background: #00ff41;
	color: #000000;
}

.pl-del-btn {
	width: 10;
	background: #1a0000;
	color: red;
	border: tall red;
	margin: 1 0;
}

.pl-del-btn:hover {
	background: red;
	color: #000000;
}



/* DARK theme */
PlaylistScreen.theme-dark {
background: #111116;
}

PlaylistScreen.theme-dark #pl-header {
background: #1a1a24;
border-bottom: solid #2a2a3a;
}

PlaylistScreen.theme-dark #pl-title {
color: #c9b8f0;
}

PlaylistScreen.theme-dark #pl-close {
background: #22223a;
color: #555570;
}

PlaylistScreen.theme-dark #pl-close:hover {
color: #c9b8f0;
}

PlaylistScreen.theme-dark #pl-name-input {
background: #18181f;
color: #7ec8e3;
border: tall #2a2a3a;
}

PlaylistScreen.theme-dark #pl-create {
background: #1a2233;
color: #7ec8e3;
border: tall #5b8dd9;
}

PlaylistScreen.theme-dark #pl-create:hover {
background: #5b8dd9;
color: #000000;
}

PlaylistScreen.theme-dark #pl-scroll {
background: #0e0e14;
}

PlaylistScreen.theme-dark .pl-row {
border-bottom: solid #2a2a3a;
}

PlaylistScreen.theme-dark .pl-name {
color: #c9b8f0;
}

PlaylistScreen.theme-dark .pl-count {
color: #555570;
}

PlaylistScreen.theme-dark .pl-open-btn {
background: #1a2233;
color: #7ec8e3;
border: tall #5b8dd9;
}

PlaylistScreen.theme-dark .pl-open-btn:hover {
background: #5b8dd9;
color: #000000;
}

PlaylistScreen.theme-dark .pl-del-btn {
background: #1a0000;
color: red;
border: tall red;
}

PlaylistScreen.theme-dark .pl-del-btn:hover {
background: red;
color: #ffffff;
}

/* LIGHT theme */
PlaylistScreen.theme-light {
background: #f0f0f5;
}

PlaylistScreen.theme-light #pl-header {
background: #e0e0ec;
border-bottom: solid #ccccdd;
}

PlaylistScreen.theme-light #pl-title {
color: #1a1a99;
}

PlaylistScreen.theme-light #pl-close {
background: #e8e8f5;
color: #888899;
}

PlaylistScreen.theme-light #pl-close:hover {
color: #1a1a99;
}

PlaylistScreen.theme-light #pl-name-input {
background: #ffffff;
color: #116622;
border: tall #ccccdd;
}

PlaylistScreen.theme-light #pl-create {
background: #b3c2e0;
color: #116622;
border: tall #228833;
}

PlaylistScreen.theme-light #pl-create:hover {
background: #228833;
color: #ffffff;
}

PlaylistScreen.theme-light #pl-scroll {
background: #fafafa;
}

PlaylistScreen.theme-light .pl-row {
border-bottom: solid #ccccdd;
}

PlaylistScreen.theme-light .pl-name {
color: #1a1a99;
}

PlaylistScreen.theme-light .pl-count {
color: #888899;
}

PlaylistScreen.theme-light .pl-open-btn {
background: #b3c2e0;
color: #116622;
border: tall #228833;
}

PlaylistScreen.theme-light .pl-open-btn:hover {
background: #228833;
color: #ffffff;
}

PlaylistScreen.theme-light .pl-del-btn {
background: #ffcccc;
color: #cc0000;
border: tall #ff6666;
}

PlaylistScreen.theme-light .pl-del-btn:hover {
background: #ff6666;
color: #ffffff;
}

"""


YTMP3_SETTINGS_CSS="""
 YTSettingsScreen {
	background: #0a0a0f;
}

#yts-header {
	height: 3;
	background: #000020;
	border-bottom: solid #1a1a3e;
}

#yts-title {
	width: 1fr;
	color: #00ffff;
	content-align: center middle;
}

#yts-close {
	width: 12;
	background: #0d0d1a;
	color: #444466;
	border: none;
}

#yts-close:hover {
	color: #00ffff;
}

#yts-scroll {
	height: 1fr;
	background: #0a0a0f;
	padding: 1 2;
}

.yts-section {
	color: #00ffff;
	margin: 2 0 0 0;
	height: 2;
	content-align: left middle;
	text-style: bold;
}

.yts-desc {
	color: #444466;
	height: 2;
	content-align: left middle;
	margin: 0 0 0 1;
}

.yts-input {
	background: #050510;
	color: #00ff41;
	border: tall #1a1a3e;
	margin: 0 0 1 0;
}

.yts-input:focus {
	border: tall #00ffff;
}

#yts-btn-row {
	height: 5;
	align: center middle;
	margin-top: 2;
}

#yts-save {
	width: 16;
	background: #003300;
	color: #00ff41;
	border: tall #00ff41;
	margin: 0 2;
}

#yts-save:hover {
	background: #00ff41;
	color: #000000;
}

#yts-reset {
	width: 20;
	background: #1a1000;
	color: #ffaa00;
	border: tall #ffaa00;
	margin: 0 2;
}

#yts-reset:hover {
	background: #ffaa00;
	color: #000000;
}

/* dark theme */
YTSettingsScreen.theme-dark {
	background: #111116;
}

YTSettingsScreen.theme-dark #yts-header {
	background: #1a1a24;
	border-bottom: solid #2a2a3a;
}

YTSettingsScreen.theme-dark #yts-title {
	color: #c9b8f0;
}

YTSettingsScreen.theme-dark #yts-close {
	background: #22223a;
	color: #555570;
}

YTSettingsScreen.theme-dark #yts-close:hover {
	color: #c9b8f0;
}

YTSettingsScreen.theme-dark #yts-scroll {
	background: #111116;
}

YTSettingsScreen.theme-dark .yts-section {
	color: #c9b8f0;
}

YTSettingsScreen.theme-dark .yts-desc {
	color: #555570;
}

YTSettingsScreen.theme-dark .yts-input {
	background: #18181f;
	color: #7ec8e3;
	border: tall #2a2a3a;
}

YTSettingsScreen.theme-dark .yts-input:focus {
	border: tall #7c5cbf;
}

YTSettingsScreen.theme-dark #yts-save {
	background: #1a2233;
	color: #7ec8e3;
	border: tall #5b8dd9;
}

YTSettingsScreen.theme-dark #yts-save:hover {
	background: #5b8dd9;
	color: #000000;
}

/* light theme */
YTSettingsScreen.theme-light {
	background: #f0f0f5;
}

YTSettingsScreen.theme-light #yts-header {
	background: #e0e0ec;
	border-bottom: solid #ccccdd;
}

YTSettingsScreen.theme-light #yts-title {
	color: #1a1a99;
}

YTSettingsScreen.theme-light #yts-close {
	background: #e8e8f5;
	color: #888899;
}

YTSettingsScreen.theme-light #yts-close:hover {
	color: #1a1a99;
}

YTSettingsScreen.theme-light #yts-scroll {
	background: #f0f0f5;
}

YTSettingsScreen.theme-light .yts-section {
	color: #1a1a99;
}

YTSettingsScreen.theme-light .yts-desc {
	color: #888899;
}

YTSettingsScreen.theme-light .yts-input {
	background: #ffffff;
	color: #116622;
	border: tall #ccccdd;
}

YTSettingsScreen.theme-light .yts-input:focus {
	border: tall #3366cc;
}

YTSettingsScreen.theme-light #yts-save {
	background: #b3c2e0;
	color: #116622;
	border: tall #228833;
}

YTSettingsScreen.theme-light #yts-save:hover {
	background: #228833;
	color: #ffffff;
}

YTSettingsScreen.theme-light #yts-reset {
	background: #ffe6b3;
	color: #b36600;
	border: tall #ffaa00;
}

"""
