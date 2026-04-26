import os, re, subprocess, json
from .constants import BASIC_COMMANDS

def strip_ansi(text):
    return re.sub(r'\x1b\[[0-9;]*m', '', text)

def get_recent_programs(n=4):
    history_file = os.path.expanduser("~/.bash_history")
    try:
        with open(history_file, 'r', errors='ignore') as f:
            lines = f.readlines()
    except:
        return ["nmap", "git", "curl"]
    seen, seen_cmds = [], set()
    for line in reversed(lines):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        cmd = line.split()[0]
        if cmd not in BASIC_COMMANDS and cmd not in seen_cmds and len(cmd) > 1:
            seen.append(line[:18])
            seen_cmds.add(cmd)
        if len(seen) >= n:
            break
    return seen or ["nmap", "git", "curl"]

def get_battery():
    try:
        r = subprocess.run(['termux-battery-status'], capture_output=True, text=True, timeout=5)
        d = json.loads(r.stdout)
        pct    = d.get('percentage', 'N/A')
        status = d.get('status', '')
        temp   = d.get('temperature', 0)
        s = f"{pct}%{' ⚡' if status == 'CHARGING' else ''}"
        if isinstance(temp, (int, float)) and temp >= 40:
            s += f"  🔥{temp}°C"
        return s
    except:
        return "N/A"

def get_memory():
    try:
        info = {}
        with open('/proc/meminfo') as f:
            for line in f:
                p = line.split()
                info[p[0].rstrip(':')] = int(p[1])
        total = info['MemTotal'] / 1024 / 1024
        used  = total - info['MemAvailable'] / 1024 / 1024
        return f"{used:.1f}/{total:.1f}GB ({int(used/total*100)}%)"
    except:
        return "N/A"

def run_speedtest():
    try:
        r = subprocess.run(['speedtest-cli'], capture_output=True, text=True, timeout=120)
        out = r.stdout
        result = {}
        for line in out.splitlines():
            if line.startswith("Testing from"):
                result["ISP"] = line.replace("Testing from ", "").strip()
            elif line.startswith("Hosted by"):
                result["Server"] = line.replace("Hosted by ", "").strip()
            elif line.startswith("Download:"):
                result["Download"] = line.replace("Download:", "").strip()
            elif line.startswith("Upload:"):
                result["Upload"] = line.replace("Upload:", "").strip()
            elif "ms" in line and "km" in line:
                ping = line.split("]: ")[-1].strip()
                result["Ping"] = ping
        return result
    except subprocess.TimeoutExpired:
        return {"Error": "Timed out"}
    except Exception as e:
        return {"Error": str(e)}

def fmt_speed(bps):
    if bps < 1024:         return f"{bps}B/s"
    if bps < 1024 * 1024:  return f"{bps/1024:.1f}KB/s"
    return f"{bps/1024/1024:.1f}MB/s"

def fmt_size(n):
    for u in ['B','KB','MB','GB']:
        if n < 1024: return f"{n:.0f}{u}"
        n /= 1024
    return f"{n:.1f}TB"

def flatten_json(data, prefix=""):
    out = []
    if isinstance(data, dict):
        for k, v in data.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, (dict, list)): out.extend(flatten_json(v, key))
            else: out.append((key, str(v)))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            key = f"{prefix}[{i}]"
            if isinstance(item, (dict, list)): out.extend(flatten_json(item, key))
            else: out.append((key, str(item)))
    return out