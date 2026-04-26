# TermuxDash 🖥️
A futuristic, Jarvis-style terminal dashboard for Termux — built entirely in Python with no display server, no XFCE, no GUI required.

## 🧠 What is this?
Most Termux users spend more time remembering commands than actually doing things. TermuxDash replaces that friction with a fully interactive terminal UI — live system stats, one-tap package installs, a clickable file browser, and direct access to all Termux API commands — all in a single Python script that runs inside the Termux terminal itself.
No root. No X11. No display server. Just Python.
## ✨ Features
### 🏠 Home Tab
- Live clock — updates every second
- Battery monitor — percentage, charging status, temperature alert (🔥 at 40°C+)
- Memory usage — used/total GB with percentage, updates every 5 seconds
- Weather panel — fetches live ASCII weather for your city from wttr.in
- Recent programs — reads ~/.bash_history and shows your most-used tools as quick-launch buttons
- Package install — one-tap update or type a package name to install
- Command input — run any shell command and see output in the live log
- Alert pulse — border flashes red when battery drops below 20%
### 📦 Packages Tab
- 20+ pre-configured tools across categories: Recon, Exploitation, Reverse Engineering, Cracking, Wireless, Dev, Utilities, Networking
- One-tap multi-step installs — complex tools like APKTool and JADX that normally require multiple wget, chmod, and ln commands install automatically
- Color-coded categories for fast scanning
- Live install log — every step streams into the output panel in real time
### ⚙️ System Tab
- 12 Termux API shortcuts — Battery, WiFi, Location, Telephony, Camera, Sensors, Public IP, Storage, Processes, Connections and more
- JSON auto-parsing — API responses are displayed as pink KEY ▸ green VALUE pairs instead of raw JSON
- Scrollable grid — add as many commands as you want without overflow
- Speedtest — runs speedtest-cli and displays Download/Upload/Ping/Server as parsed key-value pairs
### 📁 Files Tab
- Clickable file browser — tap any folder to navigate in, tap any file to view its contents
- File type icons — Python 🐍, Markdown 📝, APK 🤖, audio 🎵, video 🎬, archives 📦 and more
- File size display — next to every file entry
- Safe large file handling — files over 50KB show only the first 100 lines
- Up button + path jump — navigate up or type any absolute path to jump directly
## 🚀 Installation
### Requirements
``` bash
pkg install python termux-api
pip install -r requirements.txt
```
### Run
``` bash
python tui.py
```

## 🎨 Design
TermuxDash uses a custom Jarvis-inspired color palette:
| Element            | Color                      |
|--------------------|----------------------------|
| Primary text       | #00ffff (Cyan)             |
| Success / output   | #00ff41 (Matrix green)     |
| Keys / labels      | bold magenta               |
| Values             | bold green                 |
| Background         | #0a0a0f (Near-black)       |
| Borders            | double cyan / double green |
The UI is built with Textual — a Python framework for building terminal apps with CSS-like styling.
## ⚠️ Disclaimer
This tool is for personal use, learning, and ethical research only. Some included tools (Metasploit, Hydra, Aircrack-ng etc.) are powerful security tools — use them only on systems you own or have explicit permission to test.
## 📄 License
MIT License — do what you want, just don't be evil.
