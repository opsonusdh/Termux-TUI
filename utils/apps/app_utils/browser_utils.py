import subprocess

BROWSERS = [
    ("browsh",  "browsh",       "pkg install browsh"),
    ("w3m",     "w3m",          "pkg install w3m"),
    ("lynx",    "lynx",         "pkg install lynx"),
    ("links",   "links",        "pkg install links"),
    ("elinks",  "elinks",       "pkg install elinks"),
]

def _which(cmd):
    r = subprocess.run(["which", cmd], capture_output=True, text=True)
    return r.returncode == 0

def _detect_browser():
    for cmd, name, _ in BROWSERS:
        if _which(cmd):
            return cmd, name
    return None, None

BROWSER_CSS = """
BrowserScreen {
	background: #0a0a0f;
	align: center middle;
}

#br-box {
	width: 1fr;
	height: 1fr;
	border: double #00ffff;
	background: #050510;
	padding: 2;
}

#br-title {
	color: #00ffff;
	text-align: center;
	height: 3;
	content-align: center middle;
}

#br-desc {
	color: #444466;
	text-align: center;
	height: 2;
	content-align: center middle;
}

/* Browser selector strip */
#br-tab-strip {
	height: 3;
	border-bottom: solid #1a1a3e;
	margin-bottom: 1;
}

.br-tab {
	width: 1fr;
	height: 3;
	background: #050510;
	color: #333355;
	border: none;
}

.br-tab.available {
	color: #00aa55;
}

.br-tab.active {
	background: #001a00;
	color: #00ff41;
	border-bottom: tall #00ff41;
}

.br-tab.unavailable {
	color: #222233;
}

.br-tab:hover {
	color: #00ffff;
}

/* URL row */
#br-url-row {
	height: 4;
}

#br-url {
	width: 1fr;
	background: #050510;
	color: #00ff41;
	border: tall #1a1a3e;
}

#br-go {
	width: 10;
	background: #003300;
	color: #00ff41;
	border: tall #00ff41;
	margin-left: 1;
}

#br-go:hover {
	background: #00ff41;
	color: #000000;
}

#br-go:disabled {
	background: #1a1a1a;
	color: #333333;
	border: tall #222222;
}

#br-status {
	color: #444466;
	height: 2;
	content-align: center middle;
}

#br-install-hint {
	color: #664400;
	height: 2;
	content-align: center middle;
}

#br-back {
	width: 20;
	background: #1a0000;
	color: #444466;
	border: tall #333355;
	margin-top: 1;
}

#br-back:hover {
	color: #00ffff;
}

/* Themes */
BrowserScreen.theme-dark {
	background: #111116;
}

BrowserScreen.theme-dark #br-box {
	background: #18181f;
	border: double #7c5cbf;
}

BrowserScreen.theme-dark #br-title {
	color: #c9b8f0;
}

BrowserScreen.theme-dark #br-desc {
	color: #555570;
}

BrowserScreen.theme-dark #br-tab-strip {
	background: #1a1a24;
	border-bottom: solid #2a2a3a;
}

BrowserScreen.theme-dark .br-tab {
	background: #22223a;
	color: #555570;
}

BrowserScreen.theme-dark .br-tab.available {
	color: #7ec8e3;
}

BrowserScreen.theme-dark .br-tab.active {
	background: #1a2233;
	color: #c9b8f0;
	border-bottom: tall #7c5cbf;
}

BrowserScreen.theme-dark #br-url {
	background: #18181f;
	color: #7ec8e3;
	border: tall #2a2a3a;
}

BrowserScreen.theme-dark #br-go {
	background: #1a2233;
	color: #7ec8e3;
	border: tall #5b8dd9;
}

BrowserScreen.theme-dark #br-status {
	color: #7ec8e3;
}

BrowserScreen.theme-dark #br-install-hint {
	color: #aa6633;
}

BrowserScreen.theme-dark #br-back {
	background: #22223a;
	color: #555570;
	border: tall #2a2a3a;
}

BrowserScreen.theme-light {
	background: #f0f0f5;
}

BrowserScreen.theme-light #br-box {
	background: #ffffff;
	border: double #3366cc;
}

BrowserScreen.theme-light #br-title {
	color: #1a1a99;
}

BrowserScreen.theme-light #br-desc {
	color: #888899;
}

BrowserScreen.theme-light #br-tab-strip {
	background: #e0e0ec;
	border-bottom: solid #ccccdd;
}

BrowserScreen.theme-light .br-tab {
	background: #e8e8f5;
	color: #888899;
}

BrowserScreen.theme-light .br-tab.available {
	color: #116622;
}

BrowserScreen.theme-light .br-tab.active {
	background: #d0d0e8;
	color: #1a1a99;
	border-bottom: tall #3366cc;
}

BrowserScreen.theme-light #br-url {
	background: #ffffff;
	color: #116622;
	border: tall #ccccdd;
}

BrowserScreen.theme-light #br-go {
	background: #e8f5e8;
	color: #116622;
	border: tall #228833;
}

BrowserScreen.theme-light #br-status {
	color: #116622;
}

BrowserScreen.theme-light #br-install-hint {
	color: #883300;
}

BrowserScreen.theme-light #br-back {
	background: #e8e8f5;
	color: #888899;
	border: tall #ccccdd;
}
    """