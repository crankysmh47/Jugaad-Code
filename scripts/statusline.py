# scripts/statusline.py
"""Claude Code statusline: survival state + rotating desi message.

Reads the session JSON Claude Code pipes to stdin and the guardian's
state cache; prints one short line to stdout.
"""
import json
import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(SCRIPT_DIR))

from ui.messages import get_message

STATE_FILE = os.path.join(os.path.expanduser("~"), ".jugaadi-claude", "state.json")
FRESH_WINDOW = 90  # seconds; matches the hooks' freshness window

STATE_LABELS = {
    "NORMAL": "normal",
    "NETWORK_DEGRADED": "net degraded",
    "POWER_UNSTABLE": "power unstable",
    "CRITICAL": "critical",
}


def read_state_cache():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def main():
    session = {}
    try:
        session = json.load(sys.stdin)
    except Exception:
        pass

    parts = []

    cache = read_state_cache()
    if cache and time.time() - cache.get("updated_at", 0) < FRESH_WINDOW:
        state = cache.get("state", "NORMAL")
        parts.append(STATE_LABELS.get(state, state.lower()))
        power = cache.get("power", {})
        if not power.get("on_ac", True):
            parts.append(f"battery {power.get('battery_percent', '?')}%")
    else:
        parts.append("idle")

    parts.append(get_message())

    line = "pk: " + " | ".join(parts)

    try:
        cols = int(os.environ.get("COLUMNS", "0"))
    except ValueError:
        cols = 0
    if cols > 10 and len(line) > cols - 4:
        line = line[: cols - 4] + "..."

    print(line)


if __name__ == "__main__":
    main()
