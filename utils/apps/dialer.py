from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Static, Input
from textual.containers import Horizontal, Vertical, VerticalScroll, Grid
from textual import work
from utils.apps.app_utils.dialer_utils import *
from utils.helpers import load_config


class DialerScreen(Screen):

    CSS = DIALER_CSS

    def __init__(self):
        super().__init__()
        self._typed       = ""
        self._contacts    = []
        self._log_offset  = 0
        self._log_gen     = 0
        self._contact_gen = 0
        self._active_tab  = "dialer"
        self._config      = load_config()

    def compose(self) -> ComposeResult:
        with Horizontal(id="dial-header"):
            yield Button("← Back", id="dial-back")

        with Horizontal(id="dial-tabs"):
            yield Button("📞 Dialer",   id="tab-dialer",   classes="dial-tab active")
            yield Button("📋 Logs",     id="tab-logs",     classes="dial-tab")
            yield Button("👥 Contacts", id="tab-contacts", classes="dial-tab")

        # DIALER PANEL
        with Vertical(id="panel-dialer"):
            with Vertical(id="dial-display"):
                yield Static("", id="dial-number")
                with Horizontal(id="dial-suggestions"):
                    for i in range(5):
                        yield Button("", id=f"suggest-{i}", classes="dial-suggest")

            with Vertical(id="dial-pad"):
                with Grid(id="dial-grid"):
                    yield Button("1", id="key-1", classes="dial-key")
                    yield Button("2", id="key-2", classes="dial-key")
                    yield Button("3", id="key-3", classes="dial-key")
                    yield Button("4", id="key-4", classes="dial-key")
                    yield Button("5", id="key-5", classes="dial-key")
                    yield Button("6", id="key-6", classes="dial-key")
                    yield Button("7", id="key-7", classes="dial-key")
                    yield Button("8", id="key-8", classes="dial-key")
                    yield Button("9", id="key-9", classes="dial-key")
                    yield Button("*", id="key-star", classes="dial-key")
                    yield Button("0", id="key-0", classes="dial-key")
                    yield Button("#", id="key-hash", classes="dial-key")
                with Horizontal(id="dial-call-row"):
                    yield Button("📞 CALL", id="dial-call")
                    yield Button("⌫",       id="dial-del")

        # LOGS PANEL
        with Vertical(id="panel-logs"):
            with VerticalScroll(id="logs-scroll"):
                yield Static("⏳ Loading logs...", id="logs-loading")

        # CONTACTS PANEL
        with Vertical(id="panel-contacts"):
            yield Input(placeholder="🔍 Search contacts...", id="contacts-search")
            with VerticalScroll(id="contacts-scroll"):
                yield Static("⏳ Loading contacts...", id="contacts-loading")

    def on_mount(self):
        self.load_contacts()
        self.app.set_theme(self._config.get("theme", "jarvis"))

    # TAB SWITCHING

    def _switch_tab(self, tab: str):
        self._active_tab = tab
        for t in ["dialer", "logs", "contacts"]:
            try:
                btn = self.query_one(f"#tab-{t}", Button)
                panel = self.query_one(f"#panel-{t}")
                if t == tab:
                    btn.add_class("active")
                    panel.styles.display = "block"
                else:
                    btn.remove_class("active")
                    panel.styles.display = "none"
            except Exception:
                pass
        # lazy load
        if tab == "logs" and self._log_offset == 0:
            self._log_offset = 0
            self.load_logs(reset=True)
        if tab == "contacts" and not self._contacts:
            self.load_contacts()

    # NUMPAD INPUT

    def _press_key(self, char: str):
        self._typed += char
        self.query_one("#dial-number", Static).update(self._typed)
        self._update_suggestions()

    def _delete_key(self):
        self._typed = self._typed[:-1]
        self.query_one("#dial-number", Static).update(self._typed)
        self._update_suggestions()

    def _update_suggestions(self):
        matches = match_contacts(self._typed, self._contacts)
        for i in range(5):
            btn = self.query_one(f"#suggest-{i}", Button)
            if i < len(matches):
                c = matches[i]
                btn.label = f"{c['name']}  {c['number']}"
                btn.styles.display = "block"
            else:
                btn.label = ""
                btn.styles.display = "none"

    # CONTACTS

    @work(thread=True)
    def load_contacts(self):
        contacts = fetch_contacts()
        self._contacts = contacts
        self.app.call_from_thread(self._render_contacts, contacts)

    def _render_contacts(self, contacts):
        self._contact_gen += 1
        gen    = self._contact_gen
        scroll = self.query_one("#contacts-scroll", VerticalScroll)
        scroll.remove_children()
        if not contacts or isinstance(contacts, dict):
            scroll.mount(Static("No contact found."))
            return

        for i, c in enumerate(contacts):
            name   = c.get('name', 'Unknown')
            number = c.get('number', '')

            row  = Horizontal(classes="contact-row")
            scroll.mount(row)                                    # mount row first
            info = Vertical(classes="contact-info")
            row.mount(info)                                      # then info into row
            info.mount(Static(name, classes="contact-name"))  # then statics into info
            info.mount(Static(number, classes="contact-num"))
            btn = Button("📞", id=f"ccall-{gen}-{i}", classes="contact-call-btn")
            row.mount(btn)
            row._call_number = number


    def on_input_changed(self, event: Input.Changed):
        if event.input.id != "contacts-search":
            return
        q = event.value.strip().lower()
        filtered = [c for c in self._contacts
                    if q in c.get('name','').lower()
                    or q in c.get('number','')]
        self._render_contacts(filtered)

    # CALL LOG

    @work(thread=True)
    def load_logs(self, reset=False):
        if reset:
            self._log_offset = 0

        # show loading on button before fetch
        def show_loading():
            for btn in self.query(".logs-load-more-btn"):
                btn.label = "⏳ Loading..."
                btn.disabled = True

        self.app.call_from_thread(show_loading)

        logs = fetch_call_log(limit=20, offset=self._log_offset)
        self._log_offset += 20
        self.app.call_from_thread(self._render_logs, logs, reset)

    def _render_logs(self, logs, reset):
        self._log_gen += 1
        gen    = self._log_gen
        scroll = self.query_one("#logs-scroll", VerticalScroll)

        if reset:
            scroll.remove_children()

        try:
            for old in self.query(".logs-load-more-btn"):
                old.remove()
        except Exception:
            pass

        if not logs and reset:
            scroll.mount(Static("No call logs found."))
            return

        for i, log in enumerate(logs):
            name   = log.get('name') or log.get('phone_number', 'Unknown')
            number = log.get('phone_number', '')
            icon   = type_icon(log.get('type', ''))
            date   = log.get('date', '')
            dur    = log.get('duration', '')

            row  = Horizontal(classes="log-row")
            scroll.mount(row)                                   # mount row first
            info = Vertical(classes="log-info")
            row.mount(info)                                     # then info into row
            info.mount(Static(f"{icon}  {name}", classes="log-name"))
            info.mount(Static(f"{number}  ·  {date}  ·  {dur}", classes="log-meta"))
            btn = Button("📞", id=f"lcall-{gen}-{i}", classes="log-call-btn")
            row.mount(btn)
            row._call_number = number

        scroll.mount(Button("⬇ Load More", id=f"logs-load-more-{self._log_gen}", classes="logs-load-more-btn"))

    # BUTTON HANDLER

    def on_button_pressed(self, event: Button.Pressed):
        bid = str(event.button.id)

        if bid == "dial-back":
            self.dismiss()

        elif bid in ("tab-dialer", "tab-logs", "tab-contacts"):
            self._switch_tab(bid[4:])  # strip "tab-"

        elif bid.startswith("key-"):
            key_map = {
                "key-0": "0", "key-1": "1", "key-2": "2", "key-3": "3",
                "key-4": "4", "key-5": "5", "key-6": "6", "key-7": "7",
                "key-8": "8", "key-9": "9", "key-star": "*", "key-hash": "#"
            }
            self._press_key(key_map.get(bid, ""))

        elif bid == "dial-del":
            self._delete_key()

        elif bid == "dial-call":
            if self._typed:
                call_number(self._typed)

        elif bid.startswith("suggest-"):
            idx = int(bid.split("-")[1])
            matches = match_contacts(self._typed, self._contacts)
            if idx < len(matches):
                number = clean_number(matches[idx]['number'])
                call_number(number)

        elif "logs-load-more-btn" in event.button.classes:
            self.load_logs(reset=False)

        elif bid.startswith("lcall-") or bid.startswith("ccall-"):
            # find the number from the parent row
            try:
                number = clean_number(str(event.button.parent.parent._call_number))
                if number:
                    call_number(str(number))
            except Exception:
                pass
        
        elif bid == "try-again-btn":
            self.load_contacts()


