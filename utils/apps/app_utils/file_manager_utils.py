ICONS = {
    # Programming
    'py':   '',
    'js':   '',
    'ts':   '',
    'jsx':  '󰜈',
    'tsx':  '󰜈',
    'java': '',
    'c':    '',
    'cpp':  '',
    'h':    '',
    'hpp':  '',
    'rs':   '',
    'go':   '',
    'rb':   '',
    'php':  '',
    'swift':'',
    'kt':   '',
    'lua':  '',
    'r':    '󰟔',

    # Web
    'html': '',
    'css':  '',
    'scss': '',
    'sass': '',
    'json': '',
    'xml':  '󰗀',
    'yaml': '',
    'yml':  '',

    # Shell / Config
    'sh':   '',
    'bash': '',
    'zsh':  '',
    'fish': '',
    'conf': '',
    'ini':  '',
    'toml': '',
    'env':  '',

    # Documents
    'txt':  '',
    'md':   '󰍔',
    'pdf':  '',
    'doc':  '󰈬',
    'docx': '󰈬',
    'xls':  '󰈛',
    'xlsx': '󰈛',
    'ppt':  '󰈧',
    'pptx': '󰈧',

    # Images
    'jpg':  '󰉏',
    'jpeg': '󰉏',
    'png':  '󰉏',
    'gif':  '󰵸',
    'svg':  '󰜡',
    'webp': '󰉏',
    'ico':  '󰀻',

    # Audio
    'mp3':  '󰎆',
    'wav':  '󰎆',
    'flac': '󰎆',
    'ogg':  '󰎆',
    'm4a':  '󰎆',

    # Video
    'mp4':  '󰈫',
    'mkv':  '󰈫',
    'avi':  '󰈫',
    'mov':  '󰈫',
    'webm': '󰈫',

    # Archives
    'zip':  '',
    'tar':  '',
    'gz':   '',
    'xz':   '',
    '7z':   '',
    'rar':  '',

    # Databases
    'db':   '󰆼',
    'sqlite':'󰆼',
    'sql':  '󰆼',

    # Android
    'apk':  '',
    'aab':  '',

    # Git
    'git':      '',
    'gitignore':'',

    # Misc
    'log':  '󰌱',
    'lock': '󰌾',
    'bak':  '󰁯',
    'iso':  '󰗮',
    'torrent': '󰈖',
}

# CSS
FILE_EXPLORER_CSS="""
 FileBrowserScreen {
	background: #0a0a0f;
}

#file-header {
	height: auto;
	background: #000020;
	border-bottom: solid #1a1a3e;
}

#file-title {
    height: auto;
    margin-bottom: 1;
}

#file-loc{
    height: auto;
}

#file-header-title {
	width: 1fr;
	color: #00ffff;
	content-align: center middle;
	text-style: bold;
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