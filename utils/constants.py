import os 

VERSION="2.6.1"

def _make_splash(version): 
	inner_width=38 
	line=f"◈  TERMUX DASHBOARD  v{version}  ◈"
	padding=inner_width - len(line) 
	left=padding // 2
	right=padding - left 
	version_line=f"  ║{' ' * left}{line}{' ' * right}║"

	return ("\n\n"
		"  ╔══════════════════════════════════════╗\n"
		"  ║                                      ║\n"
		"  ║       ███                            ║\n"
		"  ║       ░░░███                         ║\n"
		"  ║         ░░░███                       ║\n"
		"  ║           ░░░███                     ║\n"
		"  ║            ███░                      ║\n"
		"  ║          ███░                        ║\n"
		"  ║        ███░        █████████         ║\n"
		"  ║        ░░░         ░░░░░░░░░         ║\n"
		"  ║                                      ║\n"
		f"{version_line}\n"
		"  ║     ◈   INITIALIZING SYSTEMS   ◈     ║\n"
		"  ║                                      ║\n"
		"  ╚══════════════════════════════════════╝\n"

	) 

SPLASH=_make_splash(VERSION) 

# CONSTANTS 
BASIC_COMMANDS= {
	'ls',
	'rm',
	'cd',
	'mv',
	'cp',
	'cat',
	'echo',
	'pwd',
	'clear',
	'exit',
	'mkdir',
	'touch',
	'grep',
	'find',
	'chmod',
	'ps',
	'kill',
	'top',
	'df',
	'du',
	'man',
	'which',
	'whoami',
	'history',
	'nano',
	'vi',
	'vim',
	'less',
	'more',
	'head',
	'tail',
	'sort',
	'uniq',
	'wc',
	'tar',
	'zip',
	'unzip',
	'python',
	'python3',
	'pip',
	'apt',
	'pkg',
	'bash',
	'sh',
	'env',
}

TOOLS=[ {
	"id": "apktool", "name":"APKTool", "desc":"Decompile & recompile Android APKs", "cat":"Reverse Eng",
		"steps":["pkg install wget -y",
			"wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O $PREFIX/bin/apktool",
			"wget https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.9.3.jar -O $PREFIX/bin/apktool.jar",
			"chmod +x $PREFIX/bin/apktool"]
	}

	,
	{
	"id": "metasploit", "name":"Metasploit", "desc":"Full penetration testing framework", "cat":"Exploitation",
		"steps":["pkg install unstable-repo -y", "pkg install metasploit -y"]
	}

	,
	{
	"id": "termux-app-store", "name":"Termux-App-Store", "desc":"The first offline-first, source-based TUI package manager built natively for Termux.", "cat":"Package Manager",
		"steps":["pip install termux-app-store"]
	}

	,
	{
	"id": "nmap", "name":"Nmap", "desc":"Network scanner & port mapper", "cat":"Recon",
		"steps":["pkg install nmap -y"]
	}

	,
	{
	"id": "sqlmap", "name":"SQLMap", "desc":"Automatic SQL injection tool", "cat":"Exploitation",
		"steps":["pkg install sqlmap -y"]
	}

	,
	{
	"id": "hydra", "name":"Hydra", "desc":"Fast network login cracker", "cat":"Cracking",
		"steps":["pkg install hydra -y"]
	}

	,
	{
	"id": "john", "name":"John the Ripper", "desc":"Password hash cracker", "cat":"Cracking",
		"steps":["pkg install john -y"]
	}

	,
	{
	"id": "tshark", "name":"TShark", "desc":"Network packet analyzer", "cat":"Recon",
		"steps":["pkg install tshark -y"]
	}

	,
	{
	"id": "ytdlp", "name":"yt-dlp", "desc":"Download from YouTube & 1000+ sites", "cat":"Utilities",
		"steps":["pip install yt-dlp --break-system-packages"]
	}

	,
	{
	"id": "ffmpeg", "name":"FFmpeg", "desc":"Video & audio converter", "cat":"Utilities",
		"steps":["pkg install ffmpeg -y"]
	}

	,
	{
	"id": "nodejs", "name":"NodeJS", "desc":"JavaScript runtime", "cat":"Dev",
		"steps":["pkg install nodejs -y"]
	}

	,
	{
	"id": "golang", "name":"Golang", "desc":"Go programming language", "cat":"Dev",
		"steps":["pkg install golang -y"]
	}

	,
	{
	"id": "jadx", "name":"JADX", "desc":"Decompile APK to Java source", "cat":"Reverse Eng",
		"steps":["pkg install wget unzip -y",
		"wget https://github.com/skylot/jadx/releases/download/v1.5.0/jadx-1.5.0.zip -O /tmp/jadx.zip",
		"mkdir -p $HOME/jadx && unzip -o /tmp/jadx.zip -d $HOME/jadx",
		"chmod +x $HOME/jadx/bin/jadx",
		"ln -sf $HOME/jadx/bin/jadx $PREFIX/bin/jadx"]
	}

	,
	{
	"id": "aircrack", "name":"Aircrack-ng", "desc":"WiFi security auditing suite", "cat":"Wireless",
		"steps":["pkg install aircrack-ng -y"]
	}

	,
	{
	"id": "hashcat", "name":"Hashcat", "desc":"GPU-based hash cracker", "cat":"Cracking",
		"steps":["pkg install hashcat -y"]
	}

	,
	{
	"id": "scrcpy", "name":"Scrcpy", "desc":"Mirror & control Android via ADB", "cat":"Utilities",
		"steps":["pkg install scrcpy -y"]
	}

	,
	{
	"id": "openssh", "name":"OpenSSH", "desc":"SSH client & server", "cat":"Networking",
		"steps":["pkg install openssh -y"]
	}

	,
	{
	"id": "tor", "name":"Tor", "desc":"Anonymous network routing", "cat":"Networking",
		"steps":["pkg install tor -y"]
	}

	,
	{
	"id": "rust", "name":"Rust", "desc":"Systems programming language", "cat":"Dev",
		"steps":["pkg install rust -y"]
	}

	,
	{
	"id": "ruby", "name":"Ruby", "desc":"Dynamic scripting language", "cat":"Dev",
		"steps":["pkg install ruby -y"]
	}

	,
	{
	"id": "git", "name":"Git", "desc":"Version control system", "cat":"Dev",
		"steps":["pkg install git -y"]
	}

] 

CAT_STYLE= {
	"Reverse Eng": "bold magenta",
	"Exploitation": "bold red",
	"Recon": "bold cyan",
	"Cracking": "bold yellow",
	"Utilities": "bold green",
	"Dev": "bold bright_blue",
	"Wireless": "bold orange",
	"Networking": "bold bright_cyan",
	"Package Manager": "bold green",
}

SYSTEM_CMDS=[
    # timeout=seconds per command; omit to use default (15s)
    {
        "id": "battery", "name": "🔋 Battery",
        "cmd": "termux-battery-status", "json": True, "timeout": 8
    },
    {
        "id": "wifi", "name": "📡 WiFi Info",
        "cmd": "termux-wifi-connectioninfo", "json": True, "timeout": 10
    },
    {
        # GPS can take 60s+ to get a fix; network provider is instant
        "id": "location", "name": "📍 Location",
        "cmd": "termux-location -p network -r once", "json": True, "timeout": 20
    },
    {
        "id": "device", "name": "📱 Telephony",
        "cmd": "termux-telephony-deviceinfo", "json": True, "timeout": 8
    },
    {
        # trigger a fresh scan first (fire-and-forget), then read cached results
        "id": "wifiscan", "name": "📶 WiFi Scan",
        "cmd": "termux-wifi-enable true; sleep 2; termux-wifi-scaninfo", "json": True, "timeout": 20
    },
    {
        "id": "camera", "name": "📷 Camera",
        "cmd": "termux-camera-info", "json": True, "timeout": 8
    },
    {
        # -n 1 = one sample; -c cleans up the sensor listener properly
        "id": "sensor", "name": "🌡 Sensors",
        "cmd": "termux-sensor -a -n 1 -d 500", "json": True, "timeout": 15
    },
    {
        # primary: fast API; fallback: curl ipinfo in same shell
        "id": "ip", "name": "🌐 Public IP",
        "cmd": "curl -s --max-time 8 https://ipinfo.io || curl -s --max-time 8 ifconfig.me",
        "json": False, "timeout": 12
    },
    {
        # show both internal storage and sdcard if present
        "id": "storage", "name": "💾 Storage",
        "cmd": "df -h /data /sdcard 2>/dev/null || df -h /data", "json": False, "timeout": 6
    },
    {
        "id": "uptime", "name": "⏱ Uptime",
        "cmd": "uptime && echo '' && free -h", "json": False, "timeout": 5
    },
    {
        # ps -A can be huge; show top CPU consumers instead
        "id": "procs", "name": "⚡ Processes",
        "cmd": "ps -eo pid,pcpu,pmem,comm --sort=-pcpu 2>/dev/null | head -20 || ps -A | head -20",
        "json": False, "timeout": 8
    },
    {
        # netstat not available in Termux by default; use ss or /proc/net
        "id": "netstat", "name": "🔌 Connections",
        "cmd": "ss -tn 2>/dev/null | head -20 || cat /proc/net/tcp6 2>/dev/null | awk 'NR>1{print $3}' | head -15",
        "json": False, "timeout": 8
    },
    {
        "id": "speedtest", "name": "🚀 Speedtest",
        "cmd": "speedtest-cli", "json": False, "special": "speedtest"
    },
    {
        "id": "notifications", "name": "🔔 Notifications",
        "cmd": "termux-notification-list", "json": True, "timeout": 8
    },
    {
        "id": "sms", "name": "💬 SMS Inbox",
        "cmd": "termux-sms-list -l 10", "json": True, "timeout": 12
    },
] 
ICONS= {
	'py': '🐍', 'sh': '📜', 'txt': '📄', 'md': '📝',
	'jpg': '🖼️', 'png': '🖼️', 'gif': '🖼️',
	'zip': '📦', 'tar': '📦', 'gz': '📦',
	'mp3': '🎵', 'mp4': '🎬', 'pdf': '📕',
	'json': '🔧', 'html': '🌐', 'css': '🎨',
	'js': '⚡', 'apk': '🤖', 'db': '🗄️',
}

CONFIG_PATH=os.path.expanduser(".termux_tui_config.json") 
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

# YouTube Music Configuration 
YT_CONFIG_PATH=os.path.expanduser(".termux_tui_yt.json") 
TEMP_DIR=os.path.join(os.path.expanduser(".termux_tui_temp"), "yt") 
os.makedirs(TEMP_DIR, exist_ok=True) 
TEMP_CURR=os.path.join(TEMP_DIR, "current.mp3") 
TEMP_NEXT=os.path.join(TEMP_DIR, "next.mp3") 
TEMP_PREV=os.path.join(TEMP_DIR, "prev.mp3") 
DEFAULT_YT_DOWNLOAD_DIR=os.path.expanduser("~/YouTube")


# CSS 

CSS_SPLASH_SCREEN="""
 SplashScreen {
	align: center middle;
	background: #0a0a0f;
}

#splash-art {
	color: #00ffff;
	text-align: center;
}

#splash-sub {
	color: #00ff41;
	text-align: center;
	margin-top: 1;
}

"""

CSS_MAIN="""
 Screen {
	background: #0a0a0f;
}

/*  HOME  */
#info-row {
	height: 18;
}

#sys-info-box {
	width: 1fr;
	border: double cyan;
	align: center middle;
	background: #050510;
}

#sys-info-box.alert {
	border: double red;
}

#sys-info {
	text-align: center;
	color: #00ffff;
}

#weather {
	width: 1fr;
	border: double #00ff41;
	padding: 1;
	height: 100%;
	background: #050510;
	color: #00ff41;
}

#recent {
	height: 7;
	border: tall #1a1a2e;
	padding: 1;
	background: #050510;
}

.recent-btn {
	margin: 0 1;
	background: #0d0d1a;
	color: #00ffff;
	border: tall #00ffff;
}

.recent-btn:hover {
	background: #00ffff;
	color: #000000;
}

#action-row {
	height: 5;
}

#update-btn {
	width: 1fr;
	background: #003300;
	color: #00ff41;
	border: tall #00ff41;
}

#update-btn:hover {
	background: #00ff41;
	color: #000000;
}

#install-btn {
	width: 1fr;
	background: #00001a;
	color: #00ffff;
	border: tall #00ffff;
}

#install-btn:hover {
	background: #00ffff;
	color: #000000;
}

#pkg-input {
	display: none;
}

#cmd-input {
	margin-top: 1;
	background: #050510;
	color: #00ff41;
	border: tall #333355;
}

#log-view {
	border: double #1a1a3e;
	background: #020208;
	color: #00ff41;
	height: 1fr;
}

/*  PACKAGES  */
#pkg-scroll {
	height: 1fr;
	background: #050510;
}

.tool-card {
	height: 7;
	border: solid #1a1a3e;
	margin: 0 0 1 0;
	padding: 0 1;
	background: #050510;
}

.tool-card:hover {
	border: solid #00ffff;
	background: #080818;
}

.tool-info {
	width: 1fr;
}

.tool-name {
	color: #00ffff;
}

.tool-desc {
	color: #444466;
}

.install-btn {
	width: 14;
	background: #001a00;
	color: #00ff41;
	border: tall #00ff41;
	margin: 1 0;
}

.install-btn:hover {
	background: #00ff41;
	color: #000000;
}

#pkg-log {
	height: 14;
	border: double #1a1a3e;
	background: #020208;
}

/*  SYSTEM  */
#sys-scroll {
	height: 1fr;
}

.sys-row {
	height: 5;
}

.sys-btn {
	width: 1fr;
	margin: 0 1 1 0;
	background: #0d0d1a;
	color: #00ffff;
	border: tall #1a1a3e;
}

.sys-btn:hover {
	background: #00ffff;
	color: #000000;
}

#sys-log {
	height: 1fr;
	border: double #1a1a3e;
	background: #020208;
}


/*  GLOBAL  */
Header {
	background: #000020;
	color: #00ffff;
}

Footer {
	background: #000020;
	color: #333355;
}

TabbedContent {
	background: #0a0a0f;
}

Tab {
	color: #333366;
}

Tab.-active {
	color: #00ffff;
	background: #000020;
}

/* APPS */
#apps-grid {
	grid-size: 3;
	grid-gutter: 1 2;
	padding: 2;
}

.apps {
	width: 20;
}

#app-music {
	background: #330033;
	color: #ff66cc;
	border: tall #ff66cc;
}

#app-music:hover {
	background: #ff66cc;
	color: #000000;
}

#app-files {
	background: #332600;
	color: #ffd700;
	border: tall #ffd700;
}

#app-files:hover {
	background: #ffd700;
	color: #000000;
}

#app-dialer {
	background: #003300;
	color: #00ff41;
	border: tall #00ff41;
}

#app-dialer:hover {
	background: #00ff41;
	color: #000000;
}

#app-ytmp3 {
	background: #320000;
	color: #ff0000;
	border: tall #ff0000;
}

#app-ytmp3:hover {
	background: #ff0000;
	color: #000000;
}

/* ── DARK theme ── */
.theme-dark Screen {
	background: #111116;
}

.theme-dark #sys-info-box {
	border: double #7c5cbf;
	background: #18181f;
}

.theme-dark #sys-info {
	color: #c9b8f0;
}

.theme-dark #weather {
	border: double #5b8dd9;
	background: #18181f;
	color: #7ec8e3;
}

.theme-dark #recent {
	border: tall #2a2a3a;
	background: #18181f;
}

.theme-dark .recent-btn {
	background: #22223a;
	color: #c9b8f0;
	border: tall #7c5cbf;
}

.theme-dark .recent-btn:hover {
	background: #7c5cbf;
	color: #ffffff;
}

.theme-dark #update-btn {
	background: #1a2233;
	color: #7ec8e3;
	border: tall #5b8dd9;
}

.theme-dark #update-btn:hover {
	background: #5b8dd9;
	color: #ffffff;
}

.theme-dark #install-btn {
	background: #22223a;
	color: #c9b8f0;
	border: tall #7c5cbf;
}

.theme-dark #install-btn:hover {
	background: #7c5cbf;
	color: #ffffff;
}

.theme-dark #cmd-input {
	background: #18181f;
	color: #7ec8e3;
	border: tall #2a2a3a;
}

.theme-dark #log-view {
	border: double #2a2a3a;
	background: #0e0e14;
	color: #7ec8e3;
}

.theme-dark #pkg-scroll {
	background: #18181f;
}

.theme-dark .tool-card {
	border: solid #2a2a3a;
	background: #18181f;
}

.theme-dark .tool-card:hover {
	border: solid #7c5cbf;
	background: #22223a;
}

.theme-dark .tool-name {
	color: #c9b8f0;
}

.theme-dark .tool-desc {
	color: #555570;
}

.theme-dark .install-btn {
	background: #1a2233;
	color: #7ec8e3;
	border: tall #5b8dd9;
}

.theme-dark .install-btn:hover {
	background: #5b8dd9;
	color: #ffffff;
}

.theme-dark #pkg-log {
	border: double #2a2a3a;
	background: #0e0e14;
}

.theme-dark .sys-btn {
	background: #22223a;
	color: #c9b8f0;
	border: tall #2a2a3a;
}

.theme-dark .sys-btn:hover {
	background: #7c5cbf;
	color: #ffffff;
}

.theme-dark #sys-log {
	border: double #2a2a3a;
	background: #0e0e14;
}

.theme-dark Header {
	background: #1a1a24;
	color: #c9b8f0;
}

.theme-dark Footer {
	background: #1a1a24;
	color: #444460;
}

.theme-dark TabbedContent {
	background: #111116;
}

.theme-dark Tab {
	color: #444460;
}

.theme-dark Tab.-active {
	color: #c9b8f0;
	background: #1a1a24;
}


/* ── LIGHT theme ── */
.theme-light Screen {
	background: #f0f0f5;
}

.theme-light #sys-info-box {
	border: double #3366cc;
	background: #ffffff;
}

.theme-light #sys-info {
	color: #1a1a99;
}

.theme-light #weather {
	border: double #228833;
	background: #ffffff;
	color: #116622;
}

.theme-light #recent {
	border: tall #ccccdd;
	background: #ffffff;
}

.theme-light .recent-btn {
	background: #e8e8f5;
	color: #1a1a99;
	border: tall #3366cc;
}

.theme-light .recent-btn:hover {
	background: #3366cc;
	color: #ffffff;
}

.theme-light #update-btn {
	background: #e8f5e8;
	color: #116622;
	border: tall #228833;
}

.theme-light #update-btn:hover {
	background: #228833;
	color: #ffffff;
}

.theme-light #install-btn {
	background: #e8e8f5;
	color: #1a1a99;
	border: tall #3366cc;
}

.theme-light #install-btn:hover {
	background: #3366cc;
	color: #ffffff;
}

.theme-light #cmd-input {
	background: #ffffff;
	color: #116622;
	border: tall #ccccdd;
}

.theme-light #log-view {
	border: double #ccccdd;
	background: #fafafa;
	color: #116622;
}

.theme-light #pkg-scroll {
	background: #ffffff;
}

.theme-light .tool-card {
	border: solid #ccccdd;
	background: #ffffff;
}

.theme-light .tool-card:hover {
	border: solid #3366cc;
	background: #e8e8f5;
}

.theme-light .tool-name {
	color: #1a1a99;
}

.theme-light .tool-desc {
	color: #888899;
}

.theme-light .install-btn {
	background: #e8f5e8;
	color: #116622;
	border: tall #228833;
}

.theme-light .install-btn:hover {
	background: #228833;
	color: #ffffff;
}

.theme-light #pkg-log {
	border: double #ccccdd;
	background: #fafafa;
}

.theme-light .sys-btn {
	background: #e8e8f5;
	color: #1a1a99;
	border: tall #ccccdd;
}

.theme-light .sys-btn:hover {
	background: #3366cc;
	color: #ffffff;
}

.theme-light #sys-log {
	border: double #ccccdd;
	background: #fafafa;
}

.theme-light Header {
	background: #e0e0ec;
	color: #1a1a99;
}

.theme-light Footer {
	background: #e0e0ec;
	color: #8888aa;
}

.theme-light TabbedContent {
	background: #f0f0f5;
}

.theme-light Tab {
	color: #8888aa;
}

.theme-light Tab.-active {
	color: #1a1a99;
	background: #e0e0ec;
}

.theme-light #app-music {
	background: #d7b4e4;
	color: #ff66cc;
	border: tall #ff66cc;
}

.theme-light #app-music:hover {
	background: #ff66cc;
	color: #000000;
}

.theme-light #app-files {
	background: #f6e1a2;
	color: #b39800;
	border: tall #ffd700;
}

.theme-light #app-files:hover {
	background: #ffd700;
	color: #000000;
}

.theme-light #app-dialer {
	background: #99ff99;
	color: #00cc33;
	border: tall #00cc33;
}

.theme-light #app-dialer:hover {
	background: #00cc33;
	color: #000000;
}

.theme-light #app-ytmp3 {
	background: #ff9999;
	color: #ff0000;
	border: tall #ff0000;
}

.theme-light #app-ytmp3:hover {
	background: #ff0000;
	color: #000000;
}

"""


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


FILE_EXPLORER_CSS="""
 FileBrowserScreen {
	background: #0a0a0f;
}

#file-header {
	height: auto;
	background: #000020;
	border-bottom: solid #1a1a3e;
}

#file-back-btn {
	height: 3;
	padding: 1;
}

#file-back-main {
	width: 12;
	background: #0d0d1a;
	color: #444466;
	border: none;
}

#file-back-main:hover {
	color: #00ffff;
}

#file-up-btn {
	width: 10;
	background: #0d0d1a;
	color: #00ffff;
	border: tall #00ffff;
}

#file-path-display {
	width: 1fr;
	color: #444466;
	padding: 1;
}

#file-scroll {
	border: double #1a1a3e;
	background: #020208;
	height: 1fr;
}

.file-dir-btn {
	width: 100%;
	background: #020208;
	color: #00ffff;
	border: none;
	height: 1;
	margin: 0;
	padding: 0 2;
}

.file-file-btn {
	width: 100%;
	background: #020208;
	color: #00ff41;
	border: none;
	height: 1;
	margin: 0;
	padding: 0 2;
}

.file-dir-btn:hover {
	background: #0a0a2f;
}

.file-file-btn:hover {
	background: #0a1a0a;
}

.file-footer {
	color: #444466;
	width: 100%;
	height: 1;
}

#file-input {
	background: #050510;
	color: #00ff41;
	border: tall #333355;
}


/* DARK */
FileBrowserScreen.theme-dark {
	background: #111116;
}

FileBrowserScreen.theme-dark #file-header {
	background: #1a1a24;
	border-bottom: solid #2a2a3a;
}

FileBrowserScreen.theme-dark #file-back-main {
	background: #22223a;
	color: #555570;
}

FileBrowserScreen.theme-dark #file-back-main:hover {
	color: #c9b8f0;
}

FileBrowserScreen.theme-dark #file-up-btn {
	background: #22223a;
	color: #c9b8f0;
	border: tall #7c5cbf;
}

FileBrowserScreen.theme-dark #file-path-display {
	color: #555570;
}

FileBrowserScreen.theme-dark #file-scroll {
	border: double #2a2a3a;
	background: #0e0e14;
}

FileBrowserScreen.theme-dark .file-dir-btn {
	background: #0e0e14;
	color: #c9b8f0;
}

FileBrowserScreen.theme-dark .file-file-btn {
	background: #0e0e14;
	color: #7ec8e3;
}

FileBrowserScreen.theme-dark .file-dir-btn:hover {
	background: #22223a;
}

FileBrowserScreen.theme-dark .file-file-btn:hover {
	background: #1a2233;
}

FileBrowserScreen.theme-dark .file-footer {
	color: #555570;
}

FileBrowserScreen.theme-dark #file-input {
	background: #18181f;
	color: #7ec8e3;
	border: tall #2a2a3a;
}


/* LIGHT */
FileBrowserScreen.theme-light {
	background: #f0f0f5;
}

FileBrowserScreen.theme-light #file-header {
	background: #e0e0ec;
	border-bottom: solid #ccccdd;
}

FileBrowserScreen.theme-light #file-back-main {
	background: #e8e8f5;
	color: #888899;
}

FileBrowserScreen.theme-light #file-back-main:hover {
	color: #1a1a99;
}

FileBrowserScreen.theme-light #file-up-btn {
	background: #e8e8f5;
	color: #1a1a99;
	border: tall #3366cc;
}

FileBrowserScreen.theme-light #file-path-display {
	color: #888899;
}

FileBrowserScreen.theme-light #file-scroll {
	border: double #ccccdd;
	background: #fafafa;
}

FileBrowserScreen.theme-light .file-dir-btn {
	background: #fafafa;
	color: #1a1a99;
}

FileBrowserScreen.theme-light .file-file-btn {
	background: #fafafa;
	color: #116622;
}

FileBrowserScreen.theme-light .file-dir-btn:hover {
	background: #dde8ff;
}

FileBrowserScreen.theme-light .file-file-btn:hover {
	background: #ddffd8;
}

FileBrowserScreen.theme-light .file-footer {
	color: #888899;
}

FileBrowserScreen.theme-light #file-input {
	background: #ffffff;
	color: #116622;
	border: tall #ccccdd;
}

"""


DIALER_CSS="""
 DialerScreen {
	background: #0a0a0f;
}

/* header */
#dial-header {
	height: 3;
	background: #000020;
	border-bottom: solid #1a1a3e;
}

#dial-back {
	width: 12;
	background: #0d0d1a;
	color: #444466;
	border: none;
}

#dial-back:hover {
	color: #00ffff;
}

/* tab bar */
#dial-tabs {
	height: 4;
	background: #000020;
	border-bottom: solid #1a1a3e;
}

.dial-tab {
	width: 1fr;
	background: #0d0d1a;
	color: #444466;
	border: none;
	height: 3;
}

.dial-tab.active {
	color: #00ffff;
	background: #000030;
	border-bottom: tall #00ffff;
}

.dial-tab:hover {
	color: #00ffff;
}

/* panels */
#panel-dialer {
	height: 1fr;
	display: block;
}

#panel-logs {
	height: 1fr;
	display: none;
}

#panel-contacts {
	height: 1fr;
	display: none;
}

/* dialer display */
#dial-display {
	height: 1fr;
	background: #050510;
	border-bottom: solid #1a1a3e;
	padding: 0 2;
}

#dial-number {
	width: 1fr;
	color: #00ffff;
	content-align: left middle;
	height: 3;
}

#dial-suggestions {
	height: 2;
}

.dial-suggest {
	width: 1fr;
	background: #050510;
	color: #444466;
	border: none;
	height: 2;
	margin: 0 1 0 0;
}

.dial-suggest:hover {
	color: #00ffff;
	background: #0a0a2f;
}

/* numpad */
#dial-pad {
	height: 1fr;
	align: center middle;
	background: #0a0a0f;
}

#dial-grid {
	display: block;
	grid-size: 3 4;
	grid-gutter: 1;
	width: 100%;
	padding: 1;
}

.dial-key {
	width: 1fr;
	height: 1fr;
	background: #0d0d1a;
	color: #00ffff;
	border: tall #1a1a3e;
}

.dial-key:hover {
	background: #1a1a3e;
	border: tall #00ffff;
}

.dial-key {
	width: 10;
	height: 4;
	background: #0d0d1a;
	color: #00ffff;
	border: tall #1a1a3e;
	margin: 0 1;
}

.dial-key:hover {
	background: #1a1a3e;
	border: tall #00ffff;
}

#dial-call-row {
	height: 5;
	align: center middle;
}

#dial-call {
	width: 22;
	height: 4;
	background: #003300;
	color: #00ff41;
	border: tall #00ff41;
}

#dial-call:hover {
	background: #00ff41;
	color: #000000;
}

#dial-del {
	width: 10;
	height: 4;
	background: #1a0000;
	color: red;
	border: tall red;
	margin-left: 2;
}

#dial-del:hover {
	background: red;
	color: #000000;
}

/* logs */
#logs-scroll {
	height: 1fr;
	background: #020208;
}

.log-row {
	height: 6;
	border-bottom: solid #1a1a3e;
	padding: 0 1;
}

.log-info {
	width: 1fr;
}

.log-name {
	color: #00ffff;
	height: 2;
	content-align: left middle;
}

.log-meta {
	color: #444466;
	height: 2;
	content-align: left middle;
}

.log-call-btn {
	width: 10;
	background: #003300;
	color: #00ff41;
	border: tall #00ff41;
	margin: 1 0;
}

.log-call-btn:hover {
	background: #00ff41;
	color: #000000;
}

.logs-load-more-btn {
	width: 100%;
	height: 3;
	background: #0d0d1a;
	color: #444466;
	border: tall #1a1a3e;
}

.logs-load-more-btn:hover {
	color: #00ffff;
}

#logs-loading {
	color: #444466;
	text-align: center;
	content-align: center middle;
	height: 3;
}

/* contacts */
#contacts-search {
	background: #050510;
	color: #00ff41;
	border: tall #1a1a3e;
}

#contacts-scroll {
	height: 1fr;
	background: #020208;
}

.contact-row {
	height: 6;
	border-bottom: solid #1a1a3e;
	padding: 0 1;
}

.contact-info {
	width: 1fr;
}

.contact-name {
	color: #00ffff;
	height: 2;
	content-align: left middle;
}

.contact-num {
	color: #444466;
	height: 2;
	content-align: left middle;
}

.contact-call-btn {
	width: 10;
	background: #003300;
	color: #00ff41;
	border: tall #00ff41;
	margin: 1 0;
}

.contact-call-btn:hover {
	background: #00ff41;
	color: #000000;
}

#contacts-loading {
	color: #444466;
	text-align: center;
	content-align: center middle;
	height: 3;
}

/* themes */
DialerScreen.theme-dark {
	background: #111116;
}

DialerScreen.theme-dark #dial-header {
	background: #1a1a24;
	border-bottom: solid #2a2a3a;
}

DialerScreen.theme-dark #dial-back {
	background: #22223a;
	color: #555570;
}

DialerScreen.theme-dark #dial-back:hover {
	color: #c9b8f0;
}

DialerScreen.theme-dark #dial-tabs {
	background: #1a1a24;
	border-bottom: solid #2a2a3a;
}

DialerScreen.theme-dark .dial-tab {
	background: #22223a;
	color: #555570;
}

DialerScreen.theme-dark .dial-tab.active {
	color: #c9b8f0;
	background: #1a1a2e;
	border-bottom: tall #7c5cbf;
}

DialerScreen.theme-dark #dial-display {
	background: #18181f;
	border-bottom: solid #2a2a3a;
}

DialerScreen.theme-dark #dial-number {
	color: #c9b8f0;
}

DialerScreen.theme-dark .dial-suggest {
	background: #18181f;
	color: #555570;
}

DialerScreen.theme-dark .dial-suggest:hover {
	color: #c9b8f0;
	background: #22223a;
}

DialerScreen.theme-dark #dial-pad {
	background: #111116;
}

DialerScreen.theme-dark .dial-key {
	background: #22223a;
	color: #c9b8f0;
	border: tall #2a2a3a;
}

DialerScreen.theme-dark .dial-key:hover {
	background: #2a2a3a;
	border: tall #7c5cbf;
}

DialerScreen.theme-dark #dial-call {
	background: #1a2233;
	color: #7ec8e3;
	border: tall #5b8dd9;
}

DialerScreen.theme-dark #dial-call:hover {
	background: #5b8dd9;
	color: #000000;
}

DialerScreen.theme-dark #dial-del {
	background: #330000;
	color: #ff6666;
	border: tall #ff6666;
}

DialerScreen.theme-dark #dial-del:hover {
	background: #ff6666;
	color: #ffffff;
}

DialerScreen.theme-dark #logs-scroll {
	background: #0e0e14;
}

DialerScreen.theme-dark .log-row {
	border-bottom: solid #2a2a3a;
}

DialerScreen.theme-dark .log-name {
	color: #c9b8f0;
}

DialerScreen.theme-dark .log-meta {
	color: #555570;
}

DialerScreen.theme-dark .log-call-btn {
	background: #1a2233;
	color: #7ec8e3;
	border: tall #5b8dd9;
}

DialerScreen.theme-dark .log-call-btn:hover {
	background: #5b8dd9;
	color: #000000;
}

DialerScreen.theme-dark #contacts-search {
	background: #18181f;
	color: #7ec8e3;
	border: tall #2a2a3a;
}

DialerScreen.theme-dark #contacts-scroll {
	background: #0e0e14;
}

DialerScreen.theme-dark .contact-row {
	border-bottom: solid #2a2a3a;
}

DialerScreen.theme-dark .contact-name {
	color: #c9b8f0;
}

DialerScreen.theme-dark .contact-num {
	color: #555570;
}

DialerScreen.theme-dark .contact-call-btn {
	background: #1a2233;
	color: #7ec8e3;
	border: tall #5b8dd9;
}

DialerScreen.theme-dark .contact-call-btn:hover {
	background: #5b8dd9;
	color: #000000;
}

DialerScreen.theme-light {
	background: #f0f0f5;
}

DialerScreen.theme-light #dial-header {
	background: #e0e0ec;
	border-bottom: solid #ccccdd;
}

DialerScreen.theme-light #dial-back {
	background: #e8e8f5;
	color: #888899;
}

DialerScreen.theme-light #dial-back:hover {
	color: #1a1a99;
}

DialerScreen.theme-light #dial-tabs {
	background: #e0e0ec;
	border-bottom: solid #ccccdd;
}

DialerScreen.theme-light .dial-tab {
	background: #e8e8f5;
	color: #888899;
}

DialerScreen.theme-light .dial-tab.active {
	color: #1a1a99;
	background: #ffffff;
	border-bottom: tall #3366cc;
}

DialerScreen.theme-light #dial-display {
	background: #ffffff;
	border-bottom: solid #ccccdd;
}

DialerScreen.theme-light #dial-number {
	color: #1a1a99;
}

DialerScreen.theme-light .dial-suggest {
	background: #ffffff;
	color: #888899;
}

DialerScreen.theme-light .dial-suggest:hover {
	color: #1a1a99;
	background: #dde8ff;
}

DialerScreen.theme-light #dial-pad {
	background: #f0f0f5;
}

DialerScreen.theme-light .dial-key {
	background: #e8e8f5;
	color: #1a1a99;
	border: tall #ccccdd;
}

DialerScreen.theme-light .dial-key:hover {
	background: #dde8ff;
	border: tall #3366cc;
}

DialerScreen.theme-light #dial-call {
	background: #e8f5e8;
	color: #116622;
	border: tall #228833;
}

DialerScreen.theme-light #dial-call:hover {
	background: #228833;
	color: #ffffff;
}

DialerScreen.theme-light #dial-del {
	background: #ffcccc;
	color: #cc0000;
	border: tall #ff6666;
}

DialerScreen.theme-light #dial-del:hover {
	background: #ff6666;
	color: #ffffff;
}

DialerScreen.theme-light #logs-scroll {
	background: #fafafa;
}

DialerScreen.theme-light .log-row {
	border-bottom: solid #ccccdd;
}

DialerScreen.theme-light .log-name {
	color: #1a1a99;
}

DialerScreen.theme-light .log-meta {
	color: #888899;
}

DialerScreen.theme-light .log-call-btn {
	background: #e8f5e8;
	color: #116622;
	border: tall #228833;
}

DialerScreen.theme-light .log-call-btn:hover {
	background: #228833;
	color: #ffffff;
}

DialerScreen.theme-light #contacts-search {
	background: #ffffff;
	color: #116622;
	border: tall #ccccdd;
}

DialerScreen.theme-light #contacts-scroll {
	background: #fafafa;
}

DialerScreen.theme-light .contact-row {
	border-bottom: solid #ccccdd;
}

DialerScreen.theme-light .contact-name {
	color: #1a1a99;
}

DialerScreen.theme-light .contact-num {
	color: #888899;
}

DialerScreen.theme-light .contact-call-btn {
	background: #e8f5e8;
	color: #116622;
	border: tall #228833;
}

DialerScreen.theme-light .contact-call-btn:hover {
	background: #228833;
	color: #ffffff;
}

"""


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
