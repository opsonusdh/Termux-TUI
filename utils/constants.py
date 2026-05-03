SPLASH = (
    "\n\n"
    "  ╔══════════════════════════════════════╗\n"
    "  ║                                      ║\n"
    "  ║  ████████╗███████╗██████╗ ███╗       ║\n"
    "  ║     ██╔══╝██╔════╝██╔══██╗████╗      ║\n"
    "  ║     ██║   █████╗  ██████╔╝██╔██╗     ║\n"
    "  ║     ██║   ██╔══╝  ██╔══██╗██║╚██╗    ║\n"
    "  ║     ██║   ███████╗██║  ██║██║ ╚██╗   ║\n"
    "  ║     ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ║\n"
    "  ║                                      ║\n"
    "  ║     ◈  TERMUX DASHBOARD  v2.0  ◈     ║\n"
    "  ║     ◈   INITIALIZING SYSTEMS   ◈     ║\n"
    "  ║                                      ║\n"
    "  ╚══════════════════════════════════════╝\n"
)

# CONSTANTS

BASIC_COMMANDS = {
    'ls','rm','cd','mv','cp','cat','echo','pwd','clear','exit','mkdir','touch',
    'grep','find','chmod','ps','kill','top','df','du','man','which','whoami',
    'history','nano','vi','vim','less','more','head','tail','sort','uniq','wc',
    'tar','zip','unzip','python','python3','pip','apt','pkg','bash','sh','env',
}

TOOLS = [
    {"id":"apktool",   "name":"APKTool",        "desc":"Decompile & recompile Android APKs",  "cat":"Reverse Eng",
     "steps":["pkg install wget -y",
              "wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O $PREFIX/bin/apktool",
              "wget https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.9.3.jar -O $PREFIX/bin/apktool.jar",
              "chmod +x $PREFIX/bin/apktool"]},
    {"id":"metasploit","name":"Metasploit",      "desc":"Full penetration testing framework",  "cat":"Exploitation",
     "steps":["pkg install unstable-repo -y","pkg install metasploit -y"]},
    {"id":"termux-app-store","name":"Termux-App-Store","desc":"The first offline-first, source-based TUI package manager built natively for Termux.",   "cat":"Package Manager",
     "steps":["pip install termux-app-store"]},
    {"id":"nmap",      "name":"Nmap",            "desc":"Network scanner & port mapper",       "cat":"Recon",
     "steps":["pkg install nmap -y"]},
    {"id":"sqlmap",    "name":"SQLMap",          "desc":"Automatic SQL injection tool",        "cat":"Exploitation",
     "steps":["pkg install sqlmap -y"]},
    {"id":"hydra",     "name":"Hydra",           "desc":"Fast network login cracker",          "cat":"Cracking",
     "steps":["pkg install hydra -y"]},
    {"id":"john",      "name":"John the Ripper", "desc":"Password hash cracker",               "cat":"Cracking",
     "steps":["pkg install john -y"]},
    {"id":"tshark",    "name":"TShark",          "desc":"Network packet analyzer",             "cat":"Recon",
     "steps":["pkg install tshark -y"]},
    {"id":"ytdlp",     "name":"yt-dlp",          "desc":"Download from YouTube & 1000+ sites","cat":"Utilities",
     "steps":["pip install yt-dlp --break-system-packages"]},
    {"id":"ffmpeg",    "name":"FFmpeg",          "desc":"Video & audio converter",             "cat":"Utilities",
     "steps":["pkg install ffmpeg -y"]},
    {"id":"nodejs",    "name":"NodeJS",          "desc":"JavaScript runtime",                  "cat":"Dev",
     "steps":["pkg install nodejs -y"]},
    {"id":"golang",    "name":"Golang",          "desc":"Go programming language",             "cat":"Dev",
     "steps":["pkg install golang -y"]},
    {"id":"jadx",      "name":"JADX",            "desc":"Decompile APK to Java source",        "cat":"Reverse Eng",
     "steps":["pkg install wget unzip -y",
              "wget https://github.com/skylot/jadx/releases/download/v1.5.0/jadx-1.5.0.zip -O /tmp/jadx.zip",
              "mkdir -p $HOME/jadx && unzip -o /tmp/jadx.zip -d $HOME/jadx",
              "chmod +x $HOME/jadx/bin/jadx",
              "ln -sf $HOME/jadx/bin/jadx $PREFIX/bin/jadx"]},
    {"id":"aircrack",  "name":"Aircrack-ng",     "desc":"WiFi security auditing suite",        "cat":"Wireless",
     "steps":["pkg install aircrack-ng -y"]},
    {"id":"hashcat",   "name":"Hashcat",         "desc":"GPU-based hash cracker",              "cat":"Cracking",
     "steps":["pkg install hashcat -y"]},
    {"id":"scrcpy",    "name":"Scrcpy",          "desc":"Mirror & control Android via ADB",    "cat":"Utilities",
     "steps":["pkg install scrcpy -y"]},
    {"id":"openssh",   "name":"OpenSSH",         "desc":"SSH client & server",                 "cat":"Networking",
     "steps":["pkg install openssh -y"]},
    {"id":"tor",       "name":"Tor",             "desc":"Anonymous network routing",           "cat":"Networking",
     "steps":["pkg install tor -y"]},
    {"id":"rust",      "name":"Rust",            "desc":"Systems programming language",        "cat":"Dev",
     "steps":["pkg install rust -y"]},
    {"id":"ruby",      "name":"Ruby",            "desc":"Dynamic scripting language",          "cat":"Dev",
     "steps":["pkg install ruby -y"]},
    {"id":"git",       "name":"Git",             "desc":"Version control system",              "cat":"Dev",
     "steps":["pkg install git -y"]},
]

CAT_STYLE = {
    "Reverse Eng":  "bold magenta",
    "Exploitation": "bold red",
    "Recon":        "bold cyan",
    "Cracking":     "bold yellow",
    "Utilities":    "bold green",
    "Dev":          "bold bright_blue",
    "Wireless":     "bold orange1",
    "Networking":   "bold bright_cyan",
    "Package Manager": "bold green",
}

SYSTEM_CMDS = [
    {"id":"battery",  "name":"🔋 Battery",    "cmd":"termux-battery-status",              "json":True},
    {"id":"wifi",     "name":"📡 WiFi Info",   "cmd":"termux-wifi-connectioninfo",         "json":True},
    {"id":"location", "name":"📍 Location",    "cmd":"termux-location -p gps",             "json":True},
    {"id":"device",   "name":"📱 Telephony",   "cmd":"termux-telephony-deviceinfo",        "json":True},
    {"id":"wifiscan", "name":"📶 WiFi Scan",   "cmd":"termux-wifi-scaninfo",               "json":True},
    {"id":"camera",   "name":"📷 Camera",      "cmd":"termux-camera-info",                 "json":True},
    {"id":"sensor",   "name":"🌡 Sensors",     "cmd":"termux-sensor -l",                   "json":True},
    {"id":"ip",       "name":"🌐 Public IP",   "cmd":"curl -s ifconfig.me",                "json":False},
    {"id":"storage",  "name":"💾 Storage",     "cmd":"df -h /data",                        "json":False},
    {"id":"uptime",   "name":"⏱ Uptime",       "cmd":"uptime",                             "json":False},
    {"id":"procs",    "name":"⚡ Processes",   "cmd":"ps -A | head -25",                   "json":False},
    {"id":"netstat",  "name":"🔌 Connections", "cmd":"netstat -tn 2>/dev/null | head -20", "json":False},    {"id":"speedtest", "name":"🚀 Speedtest", "cmd":"speedtest-cli", "json":False, "special":"speedtest"},
]

ICONS = {
    'py': '🐍', 'sh': '📜', 'txt': '📄', 'md': '📝',
    'jpg': '🖼️', 'png': '🖼️', 'gif': '🖼️',
    'zip': '📦', 'tar': '📦', 'gz': '📦',
    'mp3': '🎵', 'mp4': '🎬', 'pdf': '📕',
    'json': '🔧', 'html': '🌐', 'css': '🎨',
    'js': '⚡', 'apk': '🤖', 'db': '🗄️',
}

CSS_SPLASH_SCREEN = """
SplashScreen  { align: center middle; background: #0a0a0f; }
#splash-art   { color: #00ffff; text-align: center; }
#splash-sub   { color: #00ff41; text-align: center; margin-top: 1; }
"""
CSS_MAIN = """
Screen { background: #0a0a0f; }

/*  HOME  */
#info-row          { height: 18; }
#sys-info-box      { width: 1fr; border: double cyan; align: center middle; background: #050510; }
#sys-info-box.alert{ border: double red; }
#sys-info          { text-align: center; color: #00ffff; }
#weather           { width: 1fr; border: double #00ff41; padding: 1; height: 100%; background: #050510; color: #00ff41; }
#recent            { height: 7; border: tall #1a1a2e; padding: 1; background: #050510; }
.recent-btn        { margin: 0 1; background: #0d0d1a; color: #00ffff; border: tall #00ffff; }
.recent-btn:hover  { background: #00ffff; color: #000000; }
#action-row        { height: 5; }
#update-btn        { width: 1fr; background: #003300; color: #00ff41; border: tall #00ff41; }
#update-btn:hover  { background: #00ff41; color: #000000; }
#install-btn       { width: 1fr; background: #00001a; color: #00ffff; border: tall #00ffff; }
#install-btn:hover { background: #00ffff; color: #000000; }
#pkg-input         { display: none; }
#cmd-input         { margin-top: 1; background: #050510; color: #00ff41; border: tall #333355; }
#log-view          { border: double #1a1a3e; background: #020208; color: #00ff41; height: 1fr; }

/*  PACKAGES  */
#pkg-scroll        { height: 1fr; background: #050510; }
.tool-card         { height: 7; border: solid #1a1a3e; margin: 0 0 1 0; padding: 0 1; background: #050510; }
.tool-card:hover   { border: solid #00ffff; background: #080818; }
.tool-info         { width: 1fr; }
.tool-name         { color: #00ffff; }
.tool-desc         { color: #444466; }
.install-btn       { width: 14; background: #001a00; color: #00ff41; border: tall #00ff41; margin: 1 0; }
.install-btn:hover { background: #00ff41; color: #000000; }
#pkg-log           { height: 14; border: double #1a1a3e; background: #020208; }

/*  SYSTEM  */
#sys-scroll        { height: 1fr; }
.sys-row           { height: 5; }
.sys-btn           { width: 1fr; margin: 0 1 1 0; background: #0d0d1a; color: #00ffff; border: tall #1a1a3e; }
.sys-btn:hover     { background: #00ffff; color: #000000; }
#sys-log           { height: 14; border: double #1a1a3e; background: #020208; }

/*  FILES  */
#file-nav          { height: 3; }
#file-up-btn       { width: 10; background: #0d0d1a; color: #00ffff; border: tall #00ffff; }
#file-path-display { width: 1fr; color: #444466; padding: 1; }
#file-scroll      { border: double #1a1a3e; background: #020208; height: 1fr; content-align: right middle; }
.file-dir-btn  { width: 100%; background: #020208; color: #00ffff; border: none; align-horizontal: left; height: 1; margin: 0; padding: 0 2; }
.file-file-btn { width: 100%; background: #020208; color: #00ff41; border: none; align-horizontal: left; height: 1; margin: 0; padding: 0 2; }
.file-dir-btn:hover  { background: #0a0a2f; }
.file-file-btn:hover { background: #0a1a0a; }
.file-footer      { color: #444466; width: 100%; height: 1; }
#file-input        { background: #050510; color: #00ff41; border: tall #333355; }

/*  GLOBAL  */
Header          { background: #000020; color: #00ffff; }
Footer          { background: #000020; color: #333355; }
TabbedContent   { background: #0a0a0f; }
Tab             { color: #333366; }
Tab.-active     { color: #00ffff; background: #000020; }


 /* ── DARK theme ── */
.theme-dark Screen             { background: #111116; }
.theme-dark #sys-info-box      { border: double #7c5cbf; background: #18181f; }
.theme-dark #sys-info          { color: #c9b8f0; }
.theme-dark #weather           { border: double #5b8dd9; background: #18181f; color: #7ec8e3; }
.theme-dark #recent            { border: tall #2a2a3a; background: #18181f; }
.theme-dark .recent-btn        { background: #22223a; color: #c9b8f0; border: tall #7c5cbf; }
.theme-dark .recent-btn:hover  { background: #7c5cbf; color: #ffffff; }
.theme-dark #update-btn        { background: #1a2233; color: #7ec8e3; border: tall #5b8dd9; }
.theme-dark #update-btn:hover  { background: #5b8dd9; color: #ffffff; }
.theme-dark #install-btn       { background: #22223a; color: #c9b8f0; border: tall #7c5cbf; }
.theme-dark #install-btn:hover { background: #7c5cbf; color: #ffffff; }
.theme-dark #cmd-input         { background: #18181f; color: #7ec8e3; border: tall #2a2a3a; }
.theme-dark #log-view          { border: double #2a2a3a; background: #0e0e14; color: #7ec8e3; }
.theme-dark #pkg-scroll        { background: #18181f; }
.theme-dark .tool-card         { border: solid #2a2a3a; background: #18181f; }
.theme-dark .tool-card:hover   { border: solid #7c5cbf; background: #22223a; }
.theme-dark .tool-name         { color: #c9b8f0; }
.theme-dark .tool-desc         { color: #555570; }
.theme-dark .install-btn       { background: #1a2233; color: #7ec8e3; border: tall #5b8dd9; }
.theme-dark .install-btn:hover { background: #5b8dd9; color: #ffffff; }
.theme-dark #pkg-log           { border: double #2a2a3a; background: #0e0e14; }
.theme-dark .sys-btn           { background: #22223a; color: #c9b8f0; border: tall #2a2a3a; }
.theme-dark .sys-btn:hover     { background: #7c5cbf; color: #ffffff; }
.theme-dark #sys-log           { border: double #2a2a3a; background: #0e0e14; }
.theme-dark #file-up-btn       { background: #22223a; color: #c9b8f0; border: tall #7c5cbf; }
.theme-dark #file-path-display { color: #555570; }
.theme-dark #file-scroll       { border: double #2a2a3a; background: #0e0e14; }
.theme-dark .file-dir-btn      { background: #0e0e14; color: #c9b8f0; }
.theme-dark .file-file-btn     { background: #0e0e14; color: #7ec8e3; }
.theme-dark .file-dir-btn:hover  { background: #22223a; }
.theme-dark .file-file-btn:hover { background: #1a2233; }
.theme-dark .file-footer       { color: #555570; }
.theme-dark #file-input        { background: #18181f; color: #7ec8e3; border: tall #2a2a3a; }
.theme-dark Header             { background: #1a1a24; color: #c9b8f0; }
.theme-dark Footer             { background: #1a1a24; color: #444460; }
.theme-dark TabbedContent      { background: #111116; }
.theme-dark Tab                { color: #444460; }
.theme-dark Tab.-active        { color: #c9b8f0; background: #1a1a24; }


/* ── LIGHT theme ── */
.theme-light Screen              { background: #f0f0f5; }
.theme-light #sys-info-box       { border: double #3366cc; background: #ffffff; }
.theme-light #sys-info           { color: #1a1a99; }
.theme-light #weather            { border: double #228833; background: #ffffff; color: #116622; }
.theme-light #recent             { border: tall #ccccdd; background: #ffffff; }
.theme-light .recent-btn         { background: #e8e8f5; color: #1a1a99; border: tall #3366cc; }
.theme-light .recent-btn:hover   { background: #3366cc; color: #ffffff; }
.theme-light #update-btn         { background: #e8f5e8; color: #116622; border: tall #228833; }
.theme-light #update-btn:hover   { background: #228833; color: #ffffff; }
.theme-light #install-btn        { background: #e8e8f5; color: #1a1a99; border: tall #3366cc; }
.theme-light #install-btn:hover  { background: #3366cc; color: #ffffff; }
.theme-light #cmd-input          { background: #ffffff; color: #116622; border: tall #ccccdd; }
.theme-light #log-view           { border: double #ccccdd; background: #fafafa; color: #116622; }
.theme-light #pkg-scroll         { background: #ffffff; }
.theme-light .tool-card          { border: solid #ccccdd; background: #ffffff; }
.theme-light .tool-card:hover    { border: solid #3366cc; background: #e8e8f5; }
.theme-light .tool-name          { color: #1a1a99; }
.theme-light .tool-desc          { color: #888899; }
.theme-light .install-btn        { background: #e8f5e8; color: #116622; border: tall #228833; }
.theme-light .install-btn:hover  { background: #228833; color: #ffffff; }
.theme-light #pkg-log            { border: double #ccccdd; background: #fafafa; }
.theme-light .sys-btn            { background: #e8e8f5; color: #1a1a99; border: tall #ccccdd; }
.theme-light .sys-btn:hover      { background: #3366cc; color: #ffffff; }
.theme-light #sys-log            { border: double #ccccdd; background: #fafafa; }
.theme-light #file-up-btn        { background: #e8e8f5; color: #1a1a99; border: tall #3366cc; }
.theme-light #file-path-display  { color: #888899; }
.theme-light #file-scroll        { border: double #ccccdd; background: #fafafa; }
.theme-light .file-dir-btn       { background: #fafafa; color: #1a1a99; }
.theme-light .file-file-btn      { background: #fafafa; color: #116622; }
.theme-light .file-dir-btn:hover  { background: #dde8ff; }
.theme-light .file-file-btn:hover { background: #ddffd8; }
.theme-light .file-footer        { color: #888899; }
.theme-light #file-input         { background: #ffffff; color: #116622; border: tall #ccccdd; }
.theme-light Header              { background: #e0e0ec; color: #1a1a99; }
.theme-light Footer              { background: #e0e0ec; color: #8888aa; }
.theme-light TabbedContent       { background: #f0f0f5; }
.theme-light Tab                 { color: #8888aa; }
.theme-light Tab.-active         { color: #1a1a99; background: #e0e0ec; }
"""