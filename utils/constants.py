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
    {"id":"termux-app-store","name":"Termux-App-Store","desc":"The first offline-first, source-based TUI package manager built natively for Termux.",   "cat":"Package manager",
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
