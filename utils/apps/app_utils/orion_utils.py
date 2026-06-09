import subprocess, os, time, json, re, shutil

#  PATHS

ORION_DIR     = os.path.expanduser("~/Termux-AI")
CORE_DIR      = os.path.join(ORION_DIR, "core")
CONFIG_DIR    = os.path.join(ORION_DIR, "config")
STT_DIR       = os.path.expanduser("~/Termux-AI/Termux-STT")
API_KEYS_PATH = os.path.join(CONFIG_DIR, "api.keys")

ORION_CONFIG_PATH = os.path.expanduser(
    "~/.termux_tui_orion_config.json"
)

# Providers supported by Termux-AI (order = display order in the key screen)
ORION_PROVIDERS = [
    ("google", "GOOGLE", "Required · aistudio.google.com",         "AIza..."),
    ("nvidia", "NVIDIA", "Optional · build.nvidia.com",            "nvapi-..."),
    ("groq",   "GROQ",   "Optional · console.groq.com",            "gsk_..."),
]

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

TOOLS = [
    #  core 
    ("run_code",                      ""),
    ("save_memory",                   ""),
    ("retrieve_memory",               ""),
    ("read_file",                     ""),
    ("write_file",                    ""),
    ("index_files",                   ""),
    ("web_scrape",                    ""),
    ("sleep_mode",                    ""),
    ("intermediate_print",            ""),
    #  whatsapp 
    ("send_whatsapp_message",         ""),
    ("get_whatsapp_status",           ""),
    ("get_pending_whatsapp_messages", ""),
    ("fetch_whatsapp_chat_history",   ""),
    ("set_whatsapp_busy_mode",        ""),
    ("get_whatsapp_report",           ""),
    ("set_whatsapp_user_profile",     ""),
]
    
TOOL_PREFIXES = {
    "[EXECUTING]":          "run_code",
    "[MEMORY SAVED]":       "save_memory",
    "[MEMORY]":             "retrieve_memory",
    "[READING]":            "read_file",
    "[WRITING]":            "write_file",
    "[INDEXED]":            "index_files",
    "[SCRAPING]":           "web_scrape",
    "[SLEEP MODE ACTIVE]":  "sleep_mode",
    "AI (Intermediate)":    "intermediate_print",
    "[WP SEND]":            "send_whatsapp_message",
    "[WP STATUS]":          "get_whatsapp_status",
    "[WP PENDING]":         "get_pending_whatsapp_messages",
    "[WP HISTORY]":         "fetch_whatsapp_chat_history",
    "[WP BUSY]":            "set_whatsapp_busy_mode",
    "[WP REPORT]":          "get_whatsapp_report",
    "[WP PROFILE]":         "set_whatsapp_user_profile",
}

#  HELPERS
def orion_installed():
    return (os.path.isdir(ORION_DIR) and
            os.path.isfile(os.path.join(CORE_DIR, "__main__.py")) and
            os.path.isdir(CONFIG_DIR))

#  API key helpers (JSON format) 

def load_api_keys() -> dict:
    empty = {pid: [] for pid, *_ in ORION_PROVIDERS}
    try:
        with open(API_KEYS_PATH, "r", encoding="utf-8") as f:
            raw = f.read().strip()
        if not raw:
            return empty
        try:
            data = json.loads(raw)
            result = {pid: [] for pid, *_ in ORION_PROVIDERS}
            for pid in result:
                keys = data.get(pid, [])
                if isinstance(keys, list):
                    result[pid] = [k.strip() for k in keys if k.strip()]
                elif isinstance(keys, str) and keys.strip():
                    result[pid] = [keys.strip()]
            return result
        except json.JSONDecodeError:
            # Legacy plain-text treat all as Google keys
            keys = [l.strip() for l in raw.splitlines() if l.strip()]
            result = {pid: [] for pid, *_ in ORION_PROVIDERS}
            result["google"] = keys
            return result
    except Exception:
        return empty

def api_keys_exist() -> bool:
    """True if api.keys exists and has at least one Google key."""
    try:
        data = load_api_keys()
        return len(data.get("google", [])) > 0
    except Exception:
        return False

def save_api_keys(keys_by_provider: dict) -> bool:
    """
    Write API keys to api.keys in JSON format.
    keys_by_provider: {"google": [...], "nvidia": [...], "groq": [...]}
    """
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        # Only keep non-empty lists
        cleaned = {
            pid: [k.strip() for k in klist if k.strip()]
            for pid, klist in keys_by_provider.items()
        }
        with open(API_KEYS_PATH, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, indent=2)
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
        stat = '' if d.get('status') == 'CHARGING' else ''
        stats['bat'] = f"{stat} {pct}%"
    except Exception:
        stats['bat'] = " N/A"
    try:
        total, used, _free = shutil.disk_usage("/storage/emulated/")
        total /= 1024**3
        used  /= 1024**3
        stats['cpu'] = f"{used:.1f}/{total:.1f}GB ({int(used/total*100)}%)"
    except Exception:
        stats['cpu'] = "N/A"
    return stats


#  STT WHISPER MODELS 
# Maps display label → choice number to pipe into setup.sh stdin

STT_MODELS = [
    ("tiny    (~75MB)  — fastest, low accuracy",   "1"),
    ("tiny.en (~75MB)  — fastest, English only",   "2"),
    ("base    (~142MB) — balanced",                "3"),
    ("base.en (~142MB) — balanced, English only",  "4"),
    ("small   (~466MB) — best quality",            "5"),
    ("small.en (~466MB) — best quality, English only", "6")
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
    /* DARK */
    OrionInstallScreen.theme-dark            { background: #111116; }
    OrionInstallScreen.theme-dark #inst-box  { background: #18181f; border: double #7c5cbf; }
    OrionInstallScreen.theme-dark #inst-title { color: #c9b8f0; }
    OrionInstallScreen.theme-dark #inst-desc  { color: #555570; }
    OrionInstallScreen.theme-dark #inst-log   { background: #0e0e14; border: solid #2a2a3a; }
    OrionInstallScreen.theme-dark #inst-status { color: #7ec8e3; }
    OrionInstallScreen.theme-dark #inst-go    { background: #1a2233; color: #7ec8e3; border: tall #5b8dd9; }
    OrionInstallScreen.theme-dark #inst-skip-voice { background: #22223a; color: #555570; border: tall #2a2a3a; }
    OrionInstallScreen.theme-dark #model-title { color: #c9b8f0; }
    OrionInstallScreen.theme-dark .model-btn  { background: #22223a; color: #555570; border: tall #2a2a3a; }
    OrionInstallScreen.theme-dark .model-btn.selected { background: #1a2233; color: #7ec8e3; border: tall #5b8dd9; }

    /* LIGHT */
    OrionInstallScreen.theme-light            { background: #f0f0f5; }
    OrionInstallScreen.theme-light #inst-box  { background: #ffffff; border: double #3366cc; }
    OrionInstallScreen.theme-light #inst-title { color: #1a1a99; }
    OrionInstallScreen.theme-light #inst-desc  { color: #888899; }
    OrionInstallScreen.theme-light #inst-log   { background: #fafafa; border: solid #ccccdd; }
    OrionInstallScreen.theme-light #inst-status { color: #116622; }
    OrionInstallScreen.theme-light #inst-go    { background: #e8f5e8; color: #116622; border: tall #228833; }
    OrionInstallScreen.theme-light #inst-skip-voice { background: #e8e8f5; color: #888899; border: tall #ccccdd; }
    OrionInstallScreen.theme-light #model-title { color: #1a1a99; }
    OrionInstallScreen.theme-light .model-btn  { background: #e8e8f5; color: #888899; border: tall #ccccdd; }
    OrionInstallScreen.theme-light .model-btn.selected { background: #d0d0e8; color: #1a1a99; border: tall #3366cc; }
    
    """

ORION_APIKEY_CSS = """
    OrionApiKeyScreen        { background: #060610; }
    #api-box                 { width: 1fr; height: 1fr;
                               background: #050515; padding: 2;
                               border: double #00ff41; }
    #api-title               { color: #00ff41; text-align: center;
                               height: 4; content-align: center middle; }
    #api-desc                { color: #444466; height: 3; padding: 0 2; }

    /* Provider tab strip */
    #api-tab-strip           { height: 3; border-bottom: solid #1a1a3e; }
    .api-tab                 { width: 1fr; height: 3; background: #050510;
                               color: #333355; border: none; }
    .api-tab.active          { background: #001a00; color: #00ff41;
                               border-bottom: tall #00ff41; }
    .api-tab:hover           { color: #00ffff; }

    /* Per-provider panel */
    #api-provider-hint       { color: #2a2a4a; height: 2;
                               content-align: left middle; padding: 0 1; }
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
    #api-save                { width: 26; background: #003300;
                               color: #00ff41; border: tall #00ff41; }
    #api-save:hover          { background: #00ff41; color: #000000; }
    #api-btns                { height: 5; align: center middle; }
   
     /* DARK */
    OrionApiKeyScreen.theme-dark             { background: #111116; }
    OrionApiKeyScreen.theme-dark #api-box    { background: #18181f; border: double #7c5cbf; }
    OrionApiKeyScreen.theme-dark #api-title  { color: #c9b8f0; }
    OrionApiKeyScreen.theme-dark #api-desc   { color: #555570; }
    OrionApiKeyScreen.theme-dark #api-tab-strip { background: #1a1a24; border-bottom: solid #2a2a3a; }
    OrionApiKeyScreen.theme-dark .api-tab    { background: #22223a; color: #555570; }
    OrionApiKeyScreen.theme-dark .api-tab.active { background: #1a2233; color: #c9b8f0; border-bottom: tall #7c5cbf; }
    OrionApiKeyScreen.theme-dark #api-provider-hint { color: #555570; }
    OrionApiKeyScreen.theme-dark #api-keys-scroll { background: #0e0e14; border: solid #2a2a3a; }
    OrionApiKeyScreen.theme-dark .api-key-label { color: #7ec8e3; }
    OrionApiKeyScreen.theme-dark #api-input  { background: #18181f; color: #7ec8e3; border: tall #2a2a3a; }
    OrionApiKeyScreen.theme-dark #api-add    { background: #1a2233; color: #7ec8e3; border: tall #5b8dd9; }
    OrionApiKeyScreen.theme-dark #api-save   { background: #1a2233; color: #7ec8e3; border: tall #5b8dd9; }
    OrionApiKeyScreen.theme-dark #api-status { color: #7ec8e3; }

    /* LIGHT */
    OrionApiKeyScreen.theme-light             { background: #f0f0f5; }
    OrionApiKeyScreen.theme-light #api-box    { background: #ffffff; border: double #3366cc; }
    OrionApiKeyScreen.theme-light #api-title  { color: #1a1a99; }
    OrionApiKeyScreen.theme-light #api-desc   { color: #888899; }
    OrionApiKeyScreen.theme-light #api-tab-strip { background: #e0e0ec; border-bottom: solid #ccccdd; }
    OrionApiKeyScreen.theme-light .api-tab    { background: #e8e8f5; color: #888899; }
    OrionApiKeyScreen.theme-light .api-tab.active { background: #d0d0e8; color: #1a1a99; border-bottom: tall #3366cc; }
    OrionApiKeyScreen.theme-light #api-provider-hint { color: #888899; }
    OrionApiKeyScreen.theme-light #api-keys-scroll { background: #fafafa; border: solid #ccccdd; }
    OrionApiKeyScreen.theme-light .api-key-label { color: #116622; }
    OrionApiKeyScreen.theme-light #api-input  { background: #ffffff; color: #116622; border: tall #ccccdd; }
    OrionApiKeyScreen.theme-light #api-add    { background: #e8f5e8; color: #116622; border: tall #228833; }
    OrionApiKeyScreen.theme-light #api-save   { background: #e8f5e8; color: #116622; border: tall #228833; }
    OrionApiKeyScreen.theme-light #api-status { color: #116622; }
    
    """

ORION_CSS = """
    OrionScreen             { background: #060610; }

    #orion-header           { height: 3; background: #000018;
                              border-bottom: double #00ffff; }
    .orion-nav-btns             { width: 12; background: #050515;
                              color: #333355; border: none; }
    .orion-nav-btns:hover       { color: #00ffff; }
    #orion-title            { width: 1fr; color: #00ffff;
                              content-align: center middle; }

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
    /* tool list scrolls both axes — 16 tools, some names are long */
    #orion-tool-scroll      { height: 1fr; overflow-y: auto; overflow-x: auto; }
    .tool-indicator         { height: 2; color: #333355; padding: 0 1 0 0; width: auto; }
    .tool-indicator.active  { color: #00ff41; text-style: bold; }

    #orion-panel            { width: 1fr; }

    /* Terminal window title bar — the "floating terminal" header */
    #orion-term-titlebar    { height: 1; background: #0a0a28;
                              color: #00ffff; content-align: left middle;
                              padding: 0 2; text-style: bold;
                              border-bottom: solid #1a1a4a; }

    #orion-log              { height: 1fr; background: #020208;
                              overflow-x: auto; overflow-y: auto; }

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
    OrionScreen.theme-dark #orion-title  { color: #c9b8f0; }
    OrionScreen.theme-dark #orion-back   { background: #0d0d1a; color: #555570; border: tall #1a1a3e; }
    OrionScreen.theme-dark #orion-apikey-btn { background: #0d0d1a; color: #555570; border: tall #1a1a3e; }
    OrionScreen.theme-dark #orion-sidebar { background: #0d0d1a; }
    OrionScreen.theme-dark #orion-sys-title  { color: #7ec8e3; }
    OrionScreen.theme-dark .sys-key      { color: #555570; }
    OrionScreen.theme-dark .sys-val      { color: #7ec8e3; }
    OrionScreen.theme-dark #orion-mem-bar { color: #7c5cbf; }
    OrionScreen.theme-dark #orion-tool-title { color: #7ec8e3; }
    OrionScreen.theme-dark #orion-tool-scroll { background: #0d0d1a; }
    OrionScreen.theme-dark .tool-indicator   { color: #333355; }
    OrionScreen.theme-dark .tool-indicator.active { color: #c9b8f0; }
    OrionScreen.theme-dark #orion-term-titlebar { background: #0d0d2e; color: #c9b8f0; }
    OrionScreen.theme-dark #orion-log    { background: #070710; }
    OrionScreen.theme-dark #orion-thinking-bar { background: #0d0d1a; color: #555570; border-top: solid #1a1a3e; }
    OrionScreen.theme-dark #orion-input-row { background: #0d0d1a; }
    OrionScreen.theme-dark #orion-prompt-label { color: #555570; }
    OrionScreen.theme-dark #orion-input  { background: #070710; color: #7ec8e3; border: tall #2a2a3a; }
    OrionScreen.theme-dark #orion-send   { background: #1a2233; color: #7ec8e3; border: tall #5b8dd9; }

    OrionScreen.theme-light             { background: #f0f0f5; }
    OrionScreen.theme-light #orion-header { background: #e0e0ec; border-bottom: double #3366cc; }
    OrionScreen.theme-light #orion-title  { color: #1a1a99; }
    OrionScreen.theme-light #orion-back   { background: #e0e0ec; color: #888899; border: tall #ccccdd; }
    OrionScreen.theme-light #orion-apikey-btn { background: #e0e0ec; color: #888899; border: tall #ccccdd; }
    OrionScreen.theme-light #orion-sidebar { background: #e8e8f5; border-right: solid #ccccdd; }
    OrionScreen.theme-light #orion-sys-title { color: #1a1a99; }
    OrionScreen.theme-light .sys-key     { color: #888899; }
    OrionScreen.theme-light .sys-val     { color: #116622; }
    OrionScreen.theme-light #orion-mem-bar { color: #3366cc; }
    OrionScreen.theme-light #orion-tool-title { color: #1a1a99; }
    OrionScreen.theme-light #orion-tool-scroll { background: #e8e8f5; }
    OrionScreen.theme-light .tool-indicator   { color: #888899; }
    OrionScreen.theme-light .tool-indicator.active { color: #1a1a99; }
    OrionScreen.theme-light #orion-term-titlebar { background: #d0d0e8; color: #1a1a99; border-bottom: solid #aaaacc; }
    OrionScreen.theme-light #orion-log   { background: #fafafa; }
    OrionScreen.theme-light #orion-thinking-bar { background: #e8e8f5; border-top: solid #ccccdd; color: #888899; }
    OrionScreen.theme-light #orion-input-row { background: #e0e0ec; border-top: double #ccccdd; }
    OrionScreen.theme-light #orion-prompt-label { color: #888899; }
    OrionScreen.theme-light #orion-input { background: #ffffff; color: #116622; border: tall #ccccdd; }
    OrionScreen.theme-light #orion-send  { background: #e8f5e8; color: #116622; border: tall #228833; }
    
    """

ORION_LAUNCH_CSS = """
    OrionLaunchScreen       { background: #060610; align: center middle; }
    #launch-msg             { color: #00ffff; text-align: center; }
    OrionLaunchScreen.theme-dark            { background: #111116; }
    OrionLaunchScreen.theme-dark #launch-msg { color: #c9b8f0; }

    OrionLaunchScreen.theme-light            { background: #f0f0f5; }
    OrionLaunchScreen.theme-light #launch-msg { color: #1a1a99; }
    """
