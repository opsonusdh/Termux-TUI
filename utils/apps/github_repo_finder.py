from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone

import requests
from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, HorizontalScroll, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from utils.helpers import load_config


GITHUB_CSS = """
 #repo-root {
	height: 100%;
}

#repo-header {
	height: 3;
	padding: 0 1;
}

#repo-back {
	width: 10;
}

#repo-title {
	width: 1fr;
	content-align: center middle;
	text-style: bold;
}

#repo-region {
	width: 17;
}

#repo-filters-label {
	padding: 0 1;
	text-style: bold;
}

.filter-label {
	padding: 0 1;
	text-style: bold;
	color: cyan;
}

#repo-time-scroll,
#repo-category-scroll {
	height: 5;
	padding: 0 1;
	overflow-x: auto;
	overflow-y: hidden;
}

.repo-time-chip,
.repo-category-chip {
	margin-right: 1;
	min-width: 16;
	height: 3;
	margin-right: 1;
}

.repo-time-chip.active,
.repo-category-chip.active {
	text-style: bold;
	background: $accent;
}

#repo-search {
	margin: 0 1 1 1;
	width: 100%;
}

#repo-scroll {
	width: 100%;
	height: 1fr;
	padding: 0 1;
}

/*
    .repo-card {
        layout: horizontal;
        height: auto;
        min-height: 7;
        padding: 1;
        margin-bottom: 1;
        border: tall $surface;
    }

    .repo-meta-block {
        width: 1fr;
        height: auto;
    }

    .repo-actions {
        width: 12;
        align: right middle;
    }
*/
.repo-card {
	layout: horizontal;
	height: 9;
	padding: 1;
	margin-bottom: 1;
	border: tall $surface;
}

.repo-actions {
	width: 12;
	height: 100%;
	content-align: center middle;
}

.repo-open {
	width: 10;
	height: 3;
}

.repo-meta-block {
	width: 1fr;
	height: 100%;
}

.repo-name {
	text-style: bold;
	color: cyan;
}

.repo-desc {
	color: white;
}

.repo-meta {
	color: gray;
}


.repo-actions {
	width: 18;
	align: right middle;
}

.repo-open {
	width: 8;
	margin-left: 1;
}

#repo-footer {
	height: 3;
	padding: 0 1;
	dock: bottom;
}

#repo-status {
	width: 1fr;
}

/* DARK */
RepoExploreScreen.theme-dark {
	background: #111116;
}

RepoExploreScreen.theme-dark #repo-header {
	background: #1a1a24;
}

RepoExploreScreen.theme-dark #repo-back {
	background: #22223a;
	color: #555570;
	border: tall #2a2a3a;
}

RepoExploreScreen.theme-dark #repo-title {
	color: #c9b8f0;
}

RepoExploreScreen.theme-dark #repo-region {
	background: #22223a;
	color: #7ec8e3;
	border: tall #2a2a3a;
}

RepoExploreScreen.theme-dark #repo-filters-label {
	color: #c9b8f0;
}

RepoExploreScreen.theme-dark .filter-label {
	color: #7ec8e3;
}

RepoExploreScreen.theme-dark .repo-time-chip {
	background: #22223a;
	color: #555570;
	border: tall #2a2a3a;
}

RepoExploreScreen.theme-dark .repo-category-chip {
	background: #22223a;
	color: #555570;
	border: tall #2a2a3a;
}

RepoExploreScreen.theme-dark .repo-time-chip.active {
	background: #1a2233;
	color: #7ec8e3;
	border: tall #5b8dd9;
}

RepoExploreScreen.theme-dark .repo-category-chip.active {
	background: #1a2233;
	color: #7ec8e3;
	border: tall #5b8dd9;
}

RepoExploreScreen.theme-dark #repo-search {
	background: #18181f;
	color: #7ec8e3;
	border: tall #2a2a3a;
}

RepoExploreScreen.theme-dark #repo-scroll {
	background: #0e0e14;
}

RepoExploreScreen.theme-dark .repo-card {
	border: tall #2a2a3a;
	background: #18181f;
}

RepoExploreScreen.theme-dark .repo-name {
	color: #c9b8f0;
}

RepoExploreScreen.theme-dark .repo-desc {
	color: #7ec8e3;
}

RepoExploreScreen.theme-dark .repo-meta {
	color: #555570;
}

RepoExploreScreen.theme-dark .repo-open {
	background: #1a2233;
	color: #7ec8e3;
	border: tall #5b8dd9;
}

RepoExploreScreen.theme-dark #repo-footer {
	background: #1a1a24;
	border-top: solid #2a2a3a;
}

RepoExploreScreen.theme-dark #repo-status {
	color: #555570;
}

RepoExploreScreen.theme-dark #repo-load-more {
	background: #22223a;
	color: #555570;
	border: tall #2a2a3a;
}

/* LIGHT */
RepoExploreScreen.theme-light {
	background: #f0f0f5;
}

RepoExploreScreen.theme-light #repo-header {
	background: #e0e0ec;
}

RepoExploreScreen.theme-light #repo-back {
	background: #e8e8f5;
	color: #888899;
	border: tall #ccccdd;
}

RepoExploreScreen.theme-light #repo-title {
	color: #1a1a99;
}

RepoExploreScreen.theme-light #repo-region {
	background: #e8e8f5;
	color: #1a1a99;
	border: tall #ccccdd;
}

RepoExploreScreen.theme-light #repo-filters-label {
	color: #1a1a99;
}

RepoExploreScreen.theme-light .filter-label {
	color: #3366cc;
}

RepoExploreScreen.theme-light .repo-time-chip {
	background: #e8e8f5;
	color: #888899;
	border: tall #ccccdd;
}

RepoExploreScreen.theme-light .repo-category-chip {
	background: #e8e8f5;
	color: #888899;
	border: tall #ccccdd;
}

RepoExploreScreen.theme-light .repo-time-chip.active {
	background: #e8f5e8;
	color: #116622;
	border: tall #228833;
}

RepoExploreScreen.theme-light .repo-category-chip.active {
	background: #e8f5e8;
	color: #116622;
	border: tall #228833;
}

RepoExploreScreen.theme-light #repo-search {
	background: #ffffff;
	color: #116622;
	border: tall #ccccdd;
}

RepoExploreScreen.theme-light #repo-scroll {
	background: #fafafa;
}

RepoExploreScreen.theme-light .repo-card {
	border: tall #ccccdd;
	background: #ffffff;
}

RepoExploreScreen.theme-light .repo-name {
	color: #1a1a99;
}

RepoExploreScreen.theme-light .repo-desc {
	color: #333333;
}

RepoExploreScreen.theme-light .repo-meta {
	color: #888899;
}

RepoExploreScreen.theme-light .repo-open {
	background: #e8f5e8;
	color: #116622;
	border: tall #228833;
}

RepoExploreScreen.theme-light #repo-footer {
	background: #e0e0ec;
	border-top: solid #ccccdd;
}

RepoExploreScreen.theme-light #repo-status {
	color: #888899;
}

RepoExploreScreen.theme-light #repo-load-more {
	background: #e8e8f5;
	color: #888899;
	border: tall #ccccdd;
}
"""

TIME_WINDOWS = {
    "today": 1,
    "week": 7,
    "month": 30,
    "year": 365,
}

REGION_ORDER = [
    "world",
    "america",
    "germany",
    "pakistan",
    "iran",
    "uk",
    "india",
    "japan",
]

REGION_LABELS = {
    "world": "󰭹 World",
    "america": "󰭹 America",
    "germany": "󰭹 Germany",
    "pakistan": "󰭹 Pakistan",
    "iran": "󰭹 Iran",
    "uk": "󰭹 UK",
    "india": "󰭹 India",
    "japan": "󰭹 Japan",
}

REGION_KEYWORDS = {
    "america": ["usa", "u.s.a", "united states", "america", "new york", "california", "texas"],
    "germany": ["germany", "deutschland", "berlin", "munich", "münchen", "hamburg"],
    "pakistan": ["pakistan", "karachi", "lahore", "islamabad", "rawalpindi"],
    "iran": ["iran", "tehran", "isfahan", "shiraz"],
    "uk": ["uk", "united kingdom", "england", "london", "scotland", "wales", "birmingham"],
    "india": ["india", "delhi", "mumbai", "kolkata", "bangalore", "bengaluru", "hyderabad", "chennai"],
    "japan": ["japan", "tokyo", "osaka", "kyoto"],
}

TIME_FILTERS = [
    ("today", "Today"),
    ("week", "This Week"),
    ("month", "This Month"),
    ("year", "All Time"),
]

CATEGORY_FILTERS = [
    ("all", "All"),
    ("ai", "AI"),
    ("security", "Cybersecurity"),
    ("android", "Android"),
    ("termux", "Termux"),
    ("beginner", "Beginner"),
    ("hidden", "Hidden Gems"),
]

CATEGORY_TERMS = {
    "ai": "ai machine-learning deep-learning",
    "security": "security pentest hacking",
    "android": "android kotlin java",
    "termux": "termux",
    "beginner": "beginner tutorial",
    "hidden": "stars:10..500",
}

class RepoExploreScreen(Screen):
    CSS = GITHUB_CSS

    def __init__(self):
        super().__init__()
        cfg = load_config()
        self._token = (
            os.environ.get("GITHUB_TOKEN", "").strip()
            or cfg.get("github_token", "").strip()
        )
        self._headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Termux-TUI",
        }
        if self._token:
            self._headers["Authorization"] = f"Bearer {self._token}"

        self._active_time = "week"
        self._active_category = "all"
        self._active_region = "world"
        self._search_text = ""
        self._page = 1
        self._per_page = 10
        self._repos = []
        self._owner_location_cache = {}
        self._request_id = 0

    def compose(self) -> ComposeResult:
        with Vertical(id="repo-root"):
            with Horizontal(id="repo-header"):
                yield Button("← Back", id="repo-back")
                yield Static("󰭹 GitHub", id="repo-title")
                yield Button(REGION_LABELS[self._active_region], id="repo-region")

            yield Static("Filters", id="repo-filters-label")

            yield Static("Time", classes="filter-label")

            with HorizontalScroll(id="repo-time-scroll"):
                for key, label in TIME_FILTERS:
                    classes = "repo-time-chip active" if key == self._active_time else "repo-time-chip"
                    yield Button(label, id=f"repo-time-{key}", classes=classes)

            yield Static("Categories", classes="filter-label")

            with HorizontalScroll(id="repo-category-scroll"):
                for key, label in CATEGORY_FILTERS:
                    classes = "repo-category-chip active" if key == self._active_category else "repo-category-chip"
                    yield Button(label, id=f"repo-category-{key}", classes=classes)

            yield Input(
                placeholder="Search repos by name, description, or readme...",
                id="repo-search",
            )

            with VerticalScroll(id="repo-scroll"):
                yield Static("Pick a filter, then load repositories.", id="repo-empty")

            with Horizontal(id="repo-footer"):
                yield Static("", id="repo-status")
                yield Button("Load more", id="repo-load-more")

    def on_mount(self):
        self.app.set_theme(load_config().get("theme", "jarvis"))
        self.refresh_results(reset=True)

    def _set_status(self, text: str):
        try:
            self.query_one("#repo-status", Static).update(text)
        except Exception:
            pass

    def _clear_results(self):
        scroll = self.query_one("#repo-scroll", VerticalScroll)
        scroll.remove_children()
        self._repos = []

    def _build_query(self) -> str:
        parts = []

        # SEARCH
        if self._search_text:
            parts.append(self._search_text)
            parts.append("in:name,description,readme")

        # CATEGORY
        elif self._active_category != "all":
            category_term = CATEGORY_TERMS.get(self._active_category, "")
            if category_term:
                parts.append(category_term)
                parts.append("in:name,description,readme")

        else:
            parts.append("stars:>0")

        # TIME
        if self._active_time in TIME_WINDOWS:
            days = TIME_WINDOWS[self._active_time]

            # "year" now means all time
            if days != 365:
                since = (
                    datetime.now(timezone.utc)
                    - timedelta(days=days)
                ).strftime("%Y-%m-%d")

                parts.append(f"pushed:>={since}")

        return " ".join(parts).strip()

    def _region_match(self, location: str) -> bool:
        if self._active_region == "world":
            return True
        loc = (location or "").lower()
        for key in REGION_KEYWORDS.get(self._active_region, []):
            if key in loc:
                return True
        return False

    def _owner_location(self, login: str) -> str:
        if login in self._owner_location_cache:
            return self._owner_location_cache[login]

        location = ""
        try:
            r = requests.get(
                f"https://api.github.com/users/{login}",
                headers=self._headers,
                timeout=12,
            )
            if r.ok:
                location = r.json().get("location") or ""
        except Exception:
            location = ""

        self._owner_location_cache[login] = location
        return location

    @work(thread=True)
    def refresh_results(self, reset: bool = False):
        self._request_id += 1
        request_id = self._request_id

        if reset:
            self._page = 1
            self.app.call_from_thread(self._clear_results)

        q = self._build_query()
        self.app.call_from_thread(
            self._set_status,
            f"Loading page {self._page} • {self._active_time} • {self._active_category} • {self._active_region}",
        )

        try:
            r = requests.get(
                "https://api.github.com/search/repositories",
                headers=self._headers,
                params={
                    "q": q,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": self._per_page,
                    "page": self._page,
                },
                timeout=15,
            )
            data = r.json()
            items = data.get("items", [])

            if self._active_region != "world":
                filtered = []
                for item in items:
                    owner = (item.get("owner") or {}).get("login", "")
                    location = self._owner_location(owner) if owner else ""
                    if self._region_match(location):
                        filtered.append(item)
                items = filtered

            if request_id != self._request_id:
                return

            self.app.call_from_thread(self._append_results, items, q)

        except Exception as e:
            if request_id != self._request_id:
                return
            self.app.call_from_thread(self._show_error, str(e))

    def _append_results(self, items, q: str):
        scroll = self.query_one("#repo-scroll", VerticalScroll)

        if not items and not self._repos:
            scroll.remove_children()
            scroll.mount(Static("No repositories found.", id="repo-empty"))
            self._set_status(f"No results for: {q}")
            return

        if not self._repos:
            scroll.remove_children()

        for item in items:
            idx = len(self._repos)
            self._repos.append(item)

            full_name = item.get("full_name", "unknown/repo")
            desc = item.get("description") or "No description provided."
            lang = item.get("language") or "Unknown"
            stars = item.get("stargazers_count", 0)
            forks = item.get("forks_count", 0)
            owner = (item.get("owner") or {}).get("login", "")
            url = item.get("html_url", "")

            meta = Vertical(
                Static(full_name, classes="repo-name"),
                Static(desc, classes="repo-desc"),
                Static(
                    f" {stars}   |   forks {forks}   |   {lang}   |   @{owner}",
                    classes="repo-meta"
                ),
                classes="repo-meta-block"
            )

            actions = Vertical(
                Button("Open", id=f"repo-open-{idx}", classes="repo-open"),
                classes="repo-actions"
            )

            row = Horizontal(
                meta,
                actions,
                classes="repo-card"
            )

            row._repo_url = url
            scroll.mount(row)
            scroll.refresh(layout=True)
        self._set_status(
            f"Loaded {len(self._repos)} repo(s) • page {self._page} • {self._active_time} • {self._active_category} • {self._active_region}"
        )

    def _show_error(self, message: str):
        scroll = self.query_one("#repo-scroll", VerticalScroll)
        scroll.remove_children()
        scroll.mount(Static(f"Error: {message}", id="repo-empty"))
        self._set_status("Request failed")

    def _open_repo(self, url: str):
        if not url:
            return
        for cmd in (["termux-open-url", url], ["xdg-open", url]):
            try:
                subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                return
            except Exception:
                pass
        self._set_status(url)

    def _copy_url(self, url: str):
        if not url:
            return
        try:
            subprocess.run(
                ["termux-clipboard-set"],
                input=url,
                text=True,
                capture_output=True,
                timeout=5,
            )
            self._set_status("Repository URL copied")
        except Exception:
            self._set_status(url)

    def _sync_active_chips(self):
        for btn in self.query(".repo-time-chip"):
            btn.remove_class("active")

        for btn in self.query(".repo-category-chip"):
            btn.remove_class("active")

        try:
            self.query_one(
                f"#repo-time-{self._active_time}",
                Button
            ).add_class("active")
        except Exception:
            pass

        try:
            self.query_one(
                f"#repo-category-{self._active_category}",
                Button
            ).add_class("active")
        except Exception:
            pass

        try:
            self.query_one(
                "#repo-region",
                Button
            ).label = REGION_LABELS[self._active_region]
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed):
        bid = str(event.button.id)

        if bid == "repo-back":
            self.dismiss()
            return

        if bid == "repo-load-more":
            self._page += 1
            self.refresh_results(reset=False)
            return

        if bid == "repo-region":
            current = REGION_ORDER.index(self._active_region)
            self._active_region = REGION_ORDER[(current + 1) % len(REGION_ORDER)]
            self._sync_active_chips()
            self.refresh_results(reset=True)
            return

        if bid.startswith("repo-time-"):
            self._active_time = bid.removeprefix("repo-time-")
            self._sync_active_chips()
            self.refresh_results(reset=True)
            return

        if bid.startswith("repo-category-"):
            self._active_category = bid.removeprefix("repo-category-")
            self._sync_active_chips()
            self.refresh_results(reset=True)
            return

        if bid.startswith("repo-open-"):
            idx = int(bid.removeprefix("repo-open-"))
            if 0 <= idx < len(self._repos):
                self._open_repo(self._repos[idx].get("html_url", ""))
            return

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id != "repo-search":
            return
        self._search_text = event.value.strip()
        self.refresh_results(reset=True)