# Security Policy

## Important Disclaimer

Termux-TUI includes pre-configured installers for powerful security tools such as Metasploit,
Hydra, Aircrack-ng, SQLMap, and others. These tools are provided **for educational purposes,
personal learning, and authorized security research only**.

> **⚠️ Warning:** Do not use any tool from this project on systems, networks, or devices you
> do not own or do not have **explicit written permission** to test. Unauthorized use may
> constitute a criminal offense under applicable law and is strictly against the intent of
> this project.

---

## Supported Versions

| Version        | Supported          | Notes                        |
|----------------|--------------------|------------------------------|
| 2.x (current)  | ✅ Yes             | Actively maintained          |
| 1.x            | ❌ No              | No longer receiving updates  |

---

## Reporting a Vulnerability

If you discover a security vulnerability in this project — such as a code path that could be
exploited, unsafe shell command construction, or unvalidated user input — please
**do not open a public issue**, as this could expose other users before a fix is available.

Instead, report it responsibly through one of the following channels:

1. Go to the **[Security tab](../../security)** of this repository
2. Click **"Report a vulnerability"**
3. Fill in the details privately

If the Security tab is unavailable, send a **direct message to the maintainer via GitHub**.

### What to include in your report

- A clear description of the vulnerability
- Steps to reproduce it
- Potential impact
- Suggested fix (if you have one)

### What to expect

- Acknowledgment within **3 business days**
- A fix or workaround within **14 days** for critical issues
- Credit in the changelog (if you wish to be named)

---

## Responsible Use Reminder

Termux-TUI is a **terminal dashboard and tool installer** — it does not perform any
exploitation by itself. However, it simplifies the installation of tools that can cause
serious harm if misused.

By using this project, you agree to use all included tools **ethically, legally, and only
on systems you are authorized to test**.
