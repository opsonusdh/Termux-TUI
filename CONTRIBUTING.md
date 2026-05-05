# Contributing to Termux-TUI

1. Fork the repo
2. Create a new branch
3. Make changes
4. Submit a pull request
5. Vibe coding allowed

Be clear, keep code clean, don’t break stuff.

Thanks for taking the time to contribute! Here's everything you need to know.

---

## Getting Started

1. Fork this repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Termux-TUI.git`
3. Create a new branch: `git checkout -b your-feature-name`
4. Make your changes
5. Push and open a Pull Request

---

## How to Add a New Tool to the Packages Tab

Tools are defined in `utils/constants.py` inside the `TOOLS` list. Each tool is a dict with these fields:

```python
{
    "id":    "tool-id",           # unique lowercase string, no spaces
    "name":  "Tool Name",         # display name shown in the UI
    "desc":  "Short description", # one sentence, shown below the name
    "cat":   "Category",          # must be one of the valid categories below
    "steps": [                    # list of shell commands to install the tool
        "pkg install something -y",
        "pip install something",
    ]
}
```

### Valid Categories

The `cat` field must exactly match one of these values (case-sensitive):

| Category | Color in UI |
|---|---|
| `Recon` | Cyan |
| `Exploitation` | Red |
| `Reverse Eng` | Magenta |
| `Cracking` | Yellow |
| `Wireless` | Orange |
| `Networking` | Bright Cyan |
| `Dev` | Blue |
| `Utilities` | Green |
| `Package Manager` | Green |

> ⚠️ If `cat` doesn't match exactly, the tool will render without a color. Capitalization matters.

### Example

```python
{
    "id":    "httpx",
    "name":  "HTTPX",
    "desc":  "Fast HTTP toolkit for probing web servers",
    "cat":   "Recon",
    "steps": ["pip install httpx-toolkit --break-system-packages"]
},
```

---

## How to Add a New System Command to the System Tab

System commands live in `SYSTEM_CMDS` inside `utils/constants.py`. Each entry is a dict:

```python
{
    "id":      "unique-id",
    "name":    "🔧 Display Name",
    "cmd":     "shell command to run",
    "json":    True,   # True if the output is JSON (auto-parsed as KEY ▸ VALUE)
                       # False if plain text output
}
```

---

## Code Style

- Keep code clean and readable
- No unnecessary dependencies
- Test manually in Termux before submitting
- One feature or fix per Pull Request — don't bundle unrelated changes

---

## Reporting Bugs

Open an issue and include:
- What you did
- What you expected to happen
- What actually happened
- Your Termux and Python version (`python --version`)

---

## Questions

If you have a general question or idea and don't want to open a formal issue, ask the maintainer to enable **GitHub Discussions** on this repo — it's a better place for open-ended conversations.
