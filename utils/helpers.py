import os, re, subprocess, json
from .constants import (
    BASIC_COMMANDS, MUSIC_EXTENSIONS, DEFAULT_MUSIC_DIRS, CONFIG_PATH,
    YT_CONFIG_PATH, DEFAULT_YT_DOWNLOAD_DIR, TEMP_CURR, TEMP_NEXT, TEMP_PREV
)

def strip_ansi(text):
    return re.sub(r'\x1b(?:[@-Z\\-_]|\[[0-9;]*[ -/]*[@-~])', '', text)

def get_recent_programs(n=4):
    history_file = os.path.expanduser("~/.bash_history")
    try:
        with open(history_file, 'r', errors='ignore') as f:
            lines = f.readlines()
    except:
        return ["nmap", "git", "curl"]
    seen, seen_cmds = [], set()
    for line in reversed(lines):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        cmd = line.split()[0]
        if cmd not in BASIC_COMMANDS and cmd not in seen_cmds and len(cmd) > 1:
            seen.append(line[:18])
            seen_cmds.add(cmd)
        if len(seen) >= n:
            break
    return seen or ["nmap", "git", "curl"]

def get_battery():
    try:
        r = subprocess.run(['termux-battery-status'], capture_output=True, text=True, timeout=5)
        d = json.loads(r.stdout)
        pct    = d.get('percentage', 'N/A')
        status = d.get('status', '')
        temp   = d.get('temperature', 0)
        s = f"{pct}%{' ⚡' if status == 'CHARGING' else ''}"
        if isinstance(temp, (int, float)) and temp >= 40:
            s += f"  🔥{temp}°C"
        return s
    except:
        return "N/A"

def get_memory():
    try:
        info = {}
        with open('/proc/meminfo') as f:
            for line in f:
                p = line.split()
                info[p[0].rstrip(':')] = int(p[1])
        total = info['MemTotal'] / 1024 / 1024
        used  = total - info['MemAvailable'] / 1024 / 1024
        return f"{used:.1f}/{total:.1f}GB ({int(used/total*100)}%)"
    except:
        return "N/A"

def run_speedtest():
    try:
        r = subprocess.run(['speedtest-cli'], capture_output=True, text=True, timeout=120)
        out = r.stdout
        result = {}
        for line in out.splitlines():
            if line.startswith("Testing from"):
                result["ISP"] = line.replace("Testing from ", "").strip()
            elif line.startswith("Hosted by"):
                result["Server"] = line.replace("Hosted by ", "").strip()
            elif line.startswith("Download:"):
                result["Download"] = line.replace("Download:", "").strip()
            elif line.startswith("Upload:"):
                result["Upload"] = line.replace("Upload:", "").strip()
            elif "ms" in line and "km" in line:
                ping = line.split("]: ")[-1].strip()
                result["Ping"] = ping
        return result
    except subprocess.TimeoutExpired:
        return {"Error": "Timed out"}
    except Exception as e:
        return {"Error": str(e)}

def fmt_speed(bps):
    if bps < 1024:         return f"{bps}B/s"
    if bps < 1024 * 1024:  return f"{bps/1024:.1f}KB/s"
    return f"{bps/1024/1024:.1f}MB/s"

def fmt_size(n):
    for u in ['B','KB','MB','GB']:
        if n < 1024: return f"{n:.0f}{u}"
        n /= 1024
    return f"{n:.1f}TB"

   
SEPARATOR = ("__SEP__", "")

def flatten_json(data, prefix=""):
    out = []
    if isinstance(data, dict):
        for k, v in data.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, (dict, list)): out.extend(flatten_json(v, key))
            else: out.append((key, str(v)))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if i > 0:
                out.append(SEPARATOR)   # separator between items
            key = f"{prefix}[{i}]"
            if isinstance(item, (dict, list)): out.extend(flatten_json(item, key))
            else: out.append((key, str(item)))
    return out
    
def load_config():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except Exception:
        return {"theme": "jarvis", 
            "music_dirs": DEFAULT_MUSIC_DIRS, 
            "music_mode": "sequential", 
            "music_stop_on_close": False
            }


def save_config(cfg):
    try:
        with open(CONFIG_PATH, 'w') as f:
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
    
def to_mmss(sec):
    sec = max(0, int(sec))
    return f"{sec // 60}:{sec % 60:02d}"
    
def run_cmd(*args, timeout=10):
    try:
        r = subprocess.run(list(args), capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return "[]"

def call_number(number):
    try:
        subprocess.Popen(['termux-telephony-call', number])
    except Exception:
        pass

def fetch_contacts():
    out = run_cmd('termux-contact-list', timeout=15)
    try:
        return json.loads(out)
    except Exception:
        return []

def fetch_call_log(limit=20, offset=0):
    out = run_cmd('termux-call-log', '-l', str(limit), '-o', str(offset), timeout=10)
    try:
        logs = json.loads(out)
        return list(reversed(logs))
    except Exception:
        return []

def type_icon(t):
    t = t.upper()
    if t == "INCOMING":  return "↓"
    if t == "OUTGOING":  return "↑"
    if t == "MISSED":    return "×"
    return "📞"

def clean_number(n):
    return re.sub(r'[^\d+]', '', n)

def match_contacts(typed, contacts):
    if not typed:
        return []
    digits = re.sub(r'\D', '', typed)
    if not digits:
        return []
    matches = []
    for c in contacts:
        num = re.sub(r'\D', '', c.get('number', ''))
        if digits in num:
            matches.append(c)
        if len(matches) >= 5:
            break
    return matches


#  YouTube Music Functions 

def load_yt_config():
    """Load YouTube music configuration from file."""
    try:
        with open(YT_CONFIG_PATH) as f:
            return json.load(f)
    except Exception:
        return {
            "playlists": {},
            "download_dir": DEFAULT_YT_DOWNLOAD_DIR,
        }


def save_yt_config(cfg):
    """Save YouTube music configuration to file."""
    try:
        with open(YT_CONFIG_PATH, 'w') as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


def yt_search(query, limit=10, offset=0):
    """Search YouTube using yt-dlp, return list of track dicts."""
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
            except Exception:
                continue
        return results[offset:]
    except Exception:
        return []


def yt_get_audio_url(yt_url):
    """Get direct audio stream URL from YouTube (no download needed for streaming)."""
    try:
        r = subprocess.run([
            'yt-dlp', '-f', 'bestaudio[ext=m4a]/bestaudio/best',
            '--get-url', '--no-warnings', '--quiet', yt_url
        ], capture_output=True, text=True, timeout=20)
        return r.stdout.strip().splitlines()[0] if r.stdout.strip() else None
    except Exception:
        return None


def yt_download_to_file(yt_url, output_path):
    """Download best audio as mp3 to output_path. Returns True on success."""
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
    except Exception:
        return False

def yt_fetch_radio(video_id, limit=25):
    """
    Fetch YouTube's algorithmic Radio mix for a video.
    URL format https://youtube.com/watch?v=ID&list=RDID is YouTube's
    own recommendation engine — same algo as Watch Next autoplay.
    """
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
                    continue   # skip seed track
                results.append({
                    'id':       vid_id,
                    'title':    data.get('title', 'Unknown'),
                    'duration': data.get('duration_string', '--:--'),
                    'uploader': data.get('uploader', ''),
                    'url':      f"https://www.youtube.com/watch?v={vid_id}",
                })
            except Exception:
                continue
        return results
    except Exception:
        return []
