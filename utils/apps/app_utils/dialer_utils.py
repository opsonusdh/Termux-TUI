import subprocess, re, json
def run_cmd(*args, timeout=10):
    try:
        r = subprocess.run(list(args), capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return "[]"

def call_number(number):
    try:
        subprocess.run(['termux-telephony-call', number])
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
    if t == "INCOMING":  return ""
    if t == "OUTGOING":  return ""
    if t == "MISSED":    return ""
    return ""

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

# CSS
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
	height: 10;
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
