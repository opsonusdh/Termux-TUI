import os
from utils import VERSION

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

CONFIG_PATH=os.path.expanduser(".termux_tui_config.json")


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

#app-github {
	background: #1a1a1a;
	color: #e0e0e0;
	border: tall #e0e0e0;
}

#app-github:hover {
	 background: #e0e0e0;
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

.theme-light #app-github {
	background: hsl(0, 0%, 88%); 
	color: #333333; 
	border: tall #333333; 
}

.theme-light #app-github:hover {
	background: #666666; 
	color: #000000; 
}
"""
