# Changelog

All notable changes to Termux-TUI will be documented here.

---

## [2.9.5] - Current

### Added

**Orion integration** *(new: `utils/apps/orion.py`, `utils/apps/app_utils/orion_utils.py`)*
- `OrionScreen`: embedded terminal sub-screen approach — Termux-AI (`core/__main__.py`) is launched as a real subprocess with fully-piped stdin/stdout. The `RichLog` panel acts as the terminal screen; the input row sends keystrokes directly to the subprocess's stdin. No external terminal emulator is involved
- Subprocess is launched as `python -u __main__.py` with `cwd=CORE_DIR` (`~/Termux-AI/core/`) — necessary because `core/__main__.py` uses flat imports (`from interface import`, `from tools import *`) that only resolve when `core/` is on `sys.path`
- `OrionApiKeyScreen`: multi-provider tabbed API key setup — GOOGLE / NVIDIA / GROQ tabs, each with its own key list and input row. Keys saved to `api.keys` in JSON format `{"google": [...], "nvidia": [...], "groq": [...]}`
- `CONFIG_DIR` (`~/Termux-AI/config/`) added to `orion_utils.py` mirroring `Termux-AI/paths.py` — `API_KEYS_PATH` now points to `config/api.keys` following the updated Termux-AI structure. `orion_installed()` checks `config/` exists; `save_api_keys()` creates it
- Tool sidebar lists all 16 tools directly from `TOOLS_DESCRIPTION` in `core/tools.py` (run_code, save_memory, retrieve_memory, read_file, write_file, index_files, web_scrape, sleep_mode, intermediate_print, and all 6 WhatsApp tools) — each with a Nerd Font icon, wrapped in `ScrollableContainer` with `width: auto` for horizontal scrolling
- `_handle_output_line`: Rich markup tags (`[bold]`, `[/]`, etc.) emitted by the Orion renderer when stdout is a pipe are now parsed correctly — detected via `_RICH_TAG_RE` and written as plain strings to `RichLog(markup=True)` instead of being wrapped in `Text()` which treated them literally
- Status bar auto-resets to `● Ready` when the bare `YOU >` prompt is detected (signals Orion has finished responding and is waiting for input)
- `OrionInstallScreen`, `OrionApiKeyScreen`, `OrionLaunchScreen`, `OrionScreen`: full dark and light theme CSS added for every element in all four screens

**Browser — upgraded** *(changed: `utils/apps/browser.py` and `utils/apps/app_utils/browser_utils.py`)*
- `BrowshScreen` replaced by `BrowserScreen` supporting five text browsers: browsh → w3m → lynx → links → elinks, tried in priority order
- Auto-detects which browsers are installed on launch; tab strip shows available (green) vs missing (dim) — click to switch active browser
- Per-browser command arguments built without interpolating the URL into a shell string
- `BrowshScreen = BrowserScreen` alias retained for backward compatibility
- Full dark and light theme CSS added for tab strip, tabs, status bar, install hint, and back button

**App icon themes** *(changed: `utils/constants.py`)*
- Dark theme icons added for all apps
- Light theme icons added for Orion

### Changed

**Emoji to Nerd Font** *(changed: 12 files)*
- All graphic emoji (U+1F… codepoints) replaced with Nerd Font PUA glyphs across every Python file — these emoji render as boxes in Termux without a colour emoji font, while Nerd Font glyphs render correctly with any patched terminal font. Affected files: `main.py`, `utils/helpers.py`, `utils/constants.py`, `utils/apps/dialer.py`, `utils/apps/music_player.py`, `utils/apps/file_manager.py`, `utils/apps/ytmp3.py`, `utils/apps/github_repo_finder.py`, `utils/apps/orion.py`, and the three corresponding `app_utils/` files
- Plain Unicode symbols (`✗ ✓ ✕ ♫ ⚙ ⚠`) were left unchanged — they render correctly without Nerd Font

### Fixed

**`utils/apps/ytmp3.py`**
- `mp_info` was used without being imported, which broke playback status updates. Added the missing import from `music_player_utils`.

**`utils/apps/music_player.py`**
- `_play_idx()` called `self.app.call_from_thread(update_ui)` unconditionally — raises `RuntimeError: The call_from_thread method must run in a different thread` when invoked from the main thread via a button press. Fixed with a `try/except RuntimeError` fallback that calls `update_ui()` directly when already on the main thread

---

## [2.7.3]

### Added

- Files `__init__.py` in directory apps and app_utils - cause not error if user run termux-tui
- Another app called Github

### Changed

- `utils/__init__.py` - change input version for source of truth
- `utils/constants.py` - change import version to source of truth
- the file structure of source code is changed to make the code more distributed and easily readable.
- the current file structure is:
```
Termux-TUI
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE.md
├── README.md
├── SECURITY.md
├── assets
├── __main__.py
├── main.py
├── requirements.txt
└── utils
    ├── __init__.py
    ├── apps
    │   ├── __init__.py
    │   ├── app_utils
    │   │   ├── __init__.py
    │   │   ├── dialer_utils.py
    │   │   ├── file_manager_utils.py
    │   │   ├── music_player_utils.py
    │   │   └── ytmp3_utils.py
    │   ├── dialer.py
    │   ├── file_manager.py
    │   ├── music_player.py
    │   └── ytmp3.py
    ├── constants.py
    └── helpers.py

```
### Fixed
- bug fixes in github repo finder

## [2.6.1]

### Fixed
- on main splash screen, clicking on any button skipped the diagnosis. Fixed that.

## [2.6.0]

### Fixed

**`main.py`**
- `SplashScreen.on_key` was commented out — pressing any key no longer failed to skip the splash screen
- Battery/temperature parsing in `tick_sysinfo` could raise `ValueError`/`IndexError` if the string format was unexpected — now wrapped in try/except
- `query_one("#sys-info-box")` was called directly inside a worker thread for `.add_class`/`.remove_class` — now properly routed through `call_from_thread` to prevent race condition crashes
- `run_sys_cmd` now reads a per-command `timeout` field instead of a hardcoded 15s flat timeout for all commands
- `run_sys_cmd` now shows stderr output when stdout is empty, and displays a helpful permissions hint when both are empty
- Timeout error message now includes the actual timeout value and a reason hint

**`utils/apps.py`**
- `_play_track` (YTmp3Screen) contained a broken leftover line `self.query_one(...).label.__class__` that called a class constructor with no effect and could raise a TypeError — removed
- `FileBrowserScreen`: `_file_entries`, `_nav_gen`, `_current_path`, `_config` were class-level variables — shared state between instances caused navigation corruption. Moved to `__init__`
- `DialerScreen`: `_typed`, `_contacts`, `_log_offset`, `_log_gen`, `_contact_gen`, `_active_tab`, `_config` were class-level variables — same shared-state bug. Moved to `__init__`
- `MusicPlayerScreen`: `_all_songs`, `_current_idx`, `_pos_sec`, `_dur_sec`, `_is_playing`, `_poll_counter`, `_nav_gen` were class-level variables. Moved to `__init__`
- `YTmp3Screen`: all state variables (`_queue`, `_search_results`, `_is_playing`, `_radio_queue`, etc.) were class-level — shared between instances. Moved to `__init__`
- `MusicPlayerScreen._play_idx` called `self.query_one(...).update()` directly, but `_play_idx` is also invoked from `_advance()` inside the `tick` worker thread — now wrapped in `call_from_thread` to prevent UI thread violations
- `MusicPlayerScreen` resume (play/pause button, `_pos_sec > 0` branch) used `mp_run('play')` which starts a new file instead of resuming — corrected to `mp_run('resume')`
- `YTmp3Screen` resume from paused state used `mp_run('play')` — corrected to `mp_run('resume')`
- `music_stop_on_close` default was `True` in the back-button handler but `False` in `helpers.py` and the Settings Switch — unified to `False` everywhere

**`utils/helpers.py`**
- `strip_ansi` regex only stripped color codes (`\x1b[...m`), missing cursor moves, clear-screen, and other escape sequences — causing garbled characters in weather output. Replaced with a complete ANSI escape sequence regex

**`utils/constants.py`**
- `DEFAULT_YT_DOWNLOAD_DIR` was set to `/YouTube` (root filesystem path, not writable in Termux) — corrected to `~/YouTube`
- `SYSTEM_CMDS` — per-command fixes for System tab hangs and errors:
  - **Location**: `-p gps` could wait 60+ seconds for a GPS fix — changed to `-p network -r once` for instant cell/WiFi location
  - **WiFi Scan**: reading stale cached data caused timeout — now triggers a fresh scan first (`termux-wifi-enable true; sleep 2`) before reading results
  - **Sensors**: `-n 1` could hang without proper cleanup — added `-d 500` delay flag
  - **Public IP**: `curl ifconfig.me` was slow and had no timeout flag — switched to `ipinfo.io` with `--max-time 8`, with `ifconfig.me` as fallback
  - **Storage**: only showed `/data` — now also includes `/sdcard` if present
  - **Processes**: `ps -A` dumped all processes unsorted — changed to sort by CPU usage and show top 20
  - **Connections**: `netstat` is not available in Termux by default — replaced with `ss` (from iproute2), with `/proc/net/tcp6` as fallback
  - All commands now have individual `timeout` values (5–20s) instead of the global 15s hardcoded in `run_sys_cmd`

---

## [2.5.2]

### Changed
- Visual Improvement: added a separator between the json output to make it better distinguishable

## [2.5.1]

### Fixed
- crash in dialer.

## [2.5.0]

### Added
- 4 apps in apps tab

### Fixed
- theme crash in various sub parts of the app
- sudden crashes are fixed
- real diagnosis and system initialisation in splash screen

### Changed
- app interface changed to `grid` from `horizontal`
- Termux-TUI logo


## [2.0.0]

### Added
- Splash screen on launch with animated intro
- Command Palette. press `Ctrl+P` to search and jump to any feature
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
