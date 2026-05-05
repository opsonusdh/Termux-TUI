# Changelog

All notable changes to Termux-TUI will be documented here.

---

## [2.0.0] — Current

### Added
- Splash screen on launch with animated intro
- Command Palette — press `Ctrl+P` to search and jump to any feature
- 3 main themes × 19 system themes = 57 total theme combinations
- `termux-app-store` added to Packages tab (offline-first TUI package manager)
- `fmt_size` helper for human-readable file sizes
- Speedtest now handled via dedicated `run_speedtest()` helper with 120s timeout and parsed KEY ▸ VALUE output
- `Package Manager` added as a new tool category with its own color style

### Fixed
- `fmt_size` import missing in `app.py` — caused Files tab to crash on load
- `#file-log` query error when invalid path is typed — now safely falls back to `#file-view-log`
- Speedtest was running through generic `subprocess.run` with 15s timeout instead of dedicated handler — always timed out
- `termux-app-store` category casing (`Package manager` → `Package Manager`) — category color now renders correctly

### Changed
- File browser now shows file type icons and sizes inline
- System tab commands now auto-parse JSON responses into KEY ▸ VALUE pairs

---

## [1.0.0] — Initial Release

### Added
- Home tab with live clock, battery, memory, weather, recent programs, and command input
- Packages tab with 20+ pre-configured security and dev tools
- System tab with 12 Termux API shortcuts
- Files tab with clickable directory browser and file viewer
- Jarvis-inspired color palette (cyan, matrix green, magenta)
- Single-file Python app powered by Textual
