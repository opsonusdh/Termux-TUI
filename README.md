# TermuxDash

```

███
░░░███
  ░░░███
    ░░░███
     ███░
   ███░
 ███░      █████████
░░░       ░░░░░░░░░

```

TermuxDash is a Python terminal dashboard for Termux. It gives you live system stats, package shortcuts, Termux API tools, and a few built-in utilities without requiring X11, XFCE, or root access.

### Tabs
![Tabs](assets/ss1.jpg)

### Apps
![Apps](assets/ss2.jpg)

## Overview

The app is built with Textual and runs inside the normal Termux terminal. It is meant to reduce command lookup for common phone and package tasks while still keeping a shell command input close by.

## Features

### Home
- Live clock
- Battery percentage, charging status, and high-temperature warning
- Memory usage with a five-second refresh
- Weather from wttr.in
- Recent command shortcuts from `~/.bash_history`
- Package update/install controls
- Shell command input with output log

### Packages
- Preconfigured install steps for common Termux tools
- Categories for security, reverse engineering, networking, development, and utilities
- Step-by-step install output
- Failure reporting when a command exits with a non-zero status

### System
- Shortcuts for Termux API commands such as battery, WiFi, location, camera, sensors, SMS, notifications, storage, and process views
- JSON output rendered as readable key/value rows
- Speedtest support through `speedtest-cli`

### Apps
- File manager
- Music player
- Dialer with contacts and call logs
- YT-MP3 search, playback, downloads, and playlists
- GitHub repository finder
- Text browser launcher
- Orion launcher for the local Termux-AI project

## Installation

```bash
git clone https://github.com/opsonusdh/Termux-TUI.git
cd Termux-TUI
```

```bash
pkg install python termux-api
pip install -r requirements.txt
```

```bash
python main.py
```

## Notes

Termux API features require the Termux:API app and Android permissions for the relevant data, such as contacts, call logs, location, SMS, or storage.

Some package shortcuts install security tools. Use them only on systems you own or have explicit permission to test.

## License

MIT License. See [LICENSE.md](LICENSE.md).
