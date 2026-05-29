import subprocess, os, time, json, re

#  PATHS

ORION_DIR = os.path.expanduser("~/Termux-AI")
STT_DIR   = os.path.expanduser("~/Termux-AI/Termux-STT")
API_KEYS_PATH = os.path.join(ORION_DIR, "api.keys")

ORION_CONFIG_PATH = os.path.expanduser(
    "~/.termux_tui_orion_config.json"
)

#  CONFIG SYSTEM

DEFAULT_CONFIG = {
    "first_run": True,
    "voice_enabled": False,
}

def load_orion_config():
    try:
        with open(ORION_CONFIG_PATH, "r") as f:
            data = json.load(f)
        for k, v in DEFAULT_CONFIG.items():
            if k not in data:
                data[k] = v
        return data
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_orion_config(cfg):
    try:
        with open(ORION_CONFIG_PATH, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

CONFIG = load_orion_config()

#  HELPERS

def orion_installed():
    return os.path.isdir(ORION_DIR) and \
           os.path.isfile(os.path.join(ORION_DIR, "core", "__main__.py"))

def api_keys_exist():
    """Check if api.keys exists and has at least one non-empty line."""
    try:
        with open(API_KEYS_PATH) as f:
            keys = [l.strip() for l in f if l.strip()]
        return len(keys) > 0
    except Exception:
        return False

def save_api_keys(keys):
    """Write list of API keys to api.keys file."""
    try:
        os.makedirs(ORION_DIR, exist_ok=True)
        with open(API_KEYS_PATH, 'w') as f:
            f.write('\n'.join(k.strip() for k in keys if k.strip()))
            f.write('\n')
        return True
    except Exception:
        return False

def stt_installed():
    return os.path.isdir(STT_DIR)

def voice_enabled():
    return CONFIG.get("voice_enabled", False)

def strip_ansi(text):
    return re.sub(r'\x1b\[[0-9;]*[mKGH]', '', text)

def ansi_to_rich(line):
    line = line.rstrip()
    replacements = [
        (r'\x1b\[1;32m', '[bold green]'),
        (r'\x1b\[1;36m', '[bold cyan]'),
        (r'\x1b\[1;34m', '[bold blue]'),
        (r'\x1b\[1;33m', '[bold yellow]'),
        (r'\x1b\[1;31m', '[bold red]'),
        (r'\x1b\[1;35m', '[bold magenta]'),
        (r'\x1b\[0;32m', '[green]'),
        (r'\x1b\[0;36m', '[cyan]'),
        (r'\x1b\[0;33m', '[yellow]'),
        (r'\x1b\[0;31m', '[red]'),
        (r'\x1b\[0;35m', '[magenta]'),
        (r'\x1b\[0m',    '[/]'),
        (r'\x1b\[m',     '[/]'),
        (r'\x1b\[1m',    '[bold]'),
        (r'\x1b\[[0-9;]*m', ''),
    ]
    result = line
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result)
    return result

def get_sys_stats():
    stats = {}
    try:
        with open('/proc/meminfo') as f:
            info = {}
            for l in f:
                p = l.split()
                info[p[0].rstrip(':')] = int(p[1])
        total = info['MemTotal'] / 1024 / 1024
        used  = total - info['MemAvailable'] / 1024 / 1024
        stats['mem'] = f"{used:.1f}/{total:.1f}GB ({int(used/total*100)}%)"
    except Exception:
        stats['mem'] = "N/A"
    try:
        r = subprocess.run(['termux-battery-status'],
                           capture_output=True, text=True, timeout=3)
        d = json.loads(r.stdout)
        pct  = d.get('percentage', '?')
        stat = '⚡' if d.get('status') == 'CHARGING' else '🔋'
        stats['bat'] = f"{stat} {pct}%"
    except Exception:
        stats['bat'] = "🔋 N/A"
    try:
        def rs():
            with open('/proc/stat') as f:
                v = list(map(int, f.readline().split()[1:]))
            return v[3], sum(v)
        i1, t1 = rs()
        time.sleep(0.2)
        i2, t2 = rs()
        cpu = 100 * (1 - (i2 - i1) / (t2 - t1))
        stats['cpu'] = f"{cpu:.0f}%"
    except Exception:
        stats['cpu'] = "N/A"
    return stats


# ── STT WHISPER MODELS ────────────────────────────────────────────
# Maps display label → choice number to pipe into setup.sh stdin

STT_MODELS = [
    ("tiny    (~75MB)  — fastest, low accuracy",   "1"),
    ("tiny.en (~75MB)  — fastest, English only",   "2"),
    ("base    (~142MB) — balanced",                "3"),
    ("base.en (~142MB) — balanced, English only",  "4"),
    ("small   (~466MB) — best quality",            "5"),
]


ORION_INSTALLER_CSS = """
    OrionInstallScreen       { background: #060610; }

    #inst-box                { width: 1fr; height: 1fr;
                               background: #050515; padding: 2;
                               border: double #00ffff; }
    #inst-title              { color: #00ffff; text-align: center;
                               height: 4; content-align: center middle; }
    #inst-desc               { color: #444466; text-align: center;
                               height: 3; }
    #inst-log                { height: 1fr; border: solid #1a1a3e;
                               background: #020208; }
    #inst-status             { color: #00ff41; text-align: center;
                               height: 2; content-align: center middle; }
    #inst-btns               { height: 5; align: center middle; }
    #inst-go                 { width: 24; background: #003300;
                               color: #00ff41; border: tall #00ff41;
                               margin: 0 2; }
    #inst-go:hover           { background: #00ff41; color: #000000; }
    #inst-skip-voice         { width: 18; background: #1a0000;
                               color: #444466; border: tall #333355;
                               margin: 0 2; }
    #inst-skip-voice:hover   { color: #00ffff; }

    /* model picker */
    #model-section           { height: auto; }
    #model-title             { color: #00ffff; height: 2;
                               content-align: left middle; }
    .model-btn               { width: 100%; height: 3; background: #0d0d1a;
                               color: #444466; border: tall #1a1a3e;
                               margin: 0 0 1 0; }
    .model-btn:hover         { color: #00ffff; border: tall #00ffff; }
    .model-btn.selected      { background: #003300; color: #00ff41;
                               border: tall #00ff41; }
    """

ORION_APIKEY_CSS = """
    OrionApiKeyScreen        { background: #060610; }
    #api-box                 { width: 1fr; height: 1fr;
                               background: #050515; padding: 2;
                               border: double #00ff41; }
    #api-title               { color: #00ff41; text-align: center;
                               height: 4; content-align: center middle; }
    #api-desc                { color: #444466; height: 4; padding: 0 2; }
    #api-keys-scroll         { height: 1fr; border: solid #1a1a3e;
                               background: #020208; }
    .api-key-row             { height: 3; border-bottom: solid #1a1a3e; }
    .api-key-label           { width: 1fr; color: #00ff41;
                               content-align: left middle; padding: 0 1; }
    .api-key-del             { width: 8; background: #1a0000; color: red;
                               border: tall red; margin: 0; }
    .api-key-del:hover       { background: red; color: #000000; }
    #api-input-row           { height: 4; }
    #api-input               { width: 1fr; background: #050510;
                               color: #00ff41; border: tall #1a1a3e; }
    #api-add                 { width: 12; background: #003300;
                               color: #00ff41; border: tall #00ff41;
                               margin-left: 1; }
    #api-add:hover           { background: #00ff41; color: #000000; }
    #api-status              { color: #00ff41; height: 2;
                               content-align: center middle; }
    #api-save                { width: 22; background: #003300;
                               color: #00ff41; border: tall #00ff41; }
    #api-save:hover          { background: #00ff41; color: #000000; }
    #api-btns                { height: 5; align: center middle; }
    """

ORION_CSS = """
    OrionScreen             { background: #060610; }

    #orion-header           { height: 3; background: #000018;
                              border-bottom: double #00ffff; }
    #orion-back             { width: 12; background: #050515;
                              color: #333355; border: none; }
    #orion-back:hover       { color: #00ffff; }
    #orion-title            { width: 1fr; color: #00ffff;
                              content-align: center middle; }
    #orion-voice-btn        { width: 14; background: #050515;
                              color: #333355; border: none; }
    #orion-voice-btn.active { color: #00ff41; }
    #orion-voice-btn:hover  { color: #00ffff; }

    #orion-body             { height: 1fr; }

    #orion-sidebar          { width: 22; border-right: solid #1a1a3e;
                              background: #050510; }
    #orion-sys-title        { color: #00ffff; height: 2;
                              content-align: center middle;
                              border-bottom: solid #1a1a3e; }
    .sys-row                { height: 3; border-bottom: solid #0a0a1e;
                              padding: 0 1; }
    .sys-key                { color: #333355; width: 6;
                              content-align: left middle; }
    .sys-val                { color: #00ff41; width: 1fr;
                              content-align: left middle; }
    #orion-mem-bar          { color: #00ffff; height: 1; padding: 0 1; }
    #orion-tool-title       { color: #00ffff; height: 2;
                              content-align: center middle;
                              border-bottom: solid #1a1a3e;
                              margin-top: 1; }
    .tool-indicator         { height: 2; color: #333355; padding: 0 1; }
    .tool-indicator.active  { color: #00ff41; }

    #orion-panel            { width: 1fr; }
    #orion-log                 { height: 1fr; background: #020208; overflow-x: hidden; }
    
    #orion-thinking-bar     { height: 2; background: #050510;
                              border-top: solid #1a1a3e;
                              content-align: left middle; padding: 0 1; }

    #orion-input-row        { height: 4; background: #000018;
                              border-top: double #1a1a3e; padding: 0 1; }
    #orion-prompt-label     { width: 12; color: #00ffff;
                              content-align: left middle; }
    #orion-input            { width: 1fr; background: #050510;
                              color: #00ff41; border: tall #1a1a3e; }
    #orion-send             { width: 10; background: #003300;
                              color: #00ff41; border: tall #00ff41;
                              margin-left: 1; }
    #orion-send:hover       { background: #00ff41; color: #000000; }

    OrionScreen.theme-dark              { background: #0a0a12; }
    OrionScreen.theme-dark #orion-header { background: #0d0d1a; }
    OrionScreen.theme-dark #orion-sidebar { background: #0d0d1a; }
    OrionScreen.theme-dark #orion-log   { background: #070710; }
    OrionScreen.theme-dark #orion-input-row { background: #0d0d1a; }
    OrionScreen.theme-dark #orion-title { color: #c9b8f0; }

    OrionScreen.theme-light             { background: #f0f0f5; }
    OrionScreen.theme-light #orion-header { background: #e0e0ec; border-bottom: double #3366cc; }
    OrionScreen.theme-light #orion-title  { color: #1a1a99; }
    OrionScreen.theme-light #orion-sidebar { background: #e8e8f5; border-right: solid #ccccdd; }
    OrionScreen.theme-light #orion-sys-title { color: #1a1a99; }
    OrionScreen.theme-light .sys-key    { color: #888899; }
    OrionScreen.theme-light .sys-val    { color: #116622; }
    OrionScreen.theme-light #orion-log  { background: #fafafa; }
    OrionScreen.theme-light #orion-thinking-bar { background: #e8e8f5; border-top: solid #ccccdd; }
    OrionScreen.theme-light #orion-input-row { background: #e0e0ec; border-top: double #ccccdd; }
    OrionScreen.theme-light #orion-input { background: #ffffff; color: #116622; border: tall #ccccdd; }
    OrionScreen.theme-light #orion-send { background: #e8f5e8; color: #116622; border: tall #228833; }
    """

ORION_LAUNCH_CSS = """
    OrionLaunchScreen       { background: #060610; align: center middle; }
    #launch-msg             { color: #00ffff; text-align: center; }
    """
