# scripts/cache_reader.py
"""Fast state reader for hooks: prints 'state on_ac battery_pct' on one line.

Uses the guardian's state cache when fresh (< 90s). When the cache is
stale or missing, falls back to a quick live power probe only — no
network checks, so tool calls never stall on a slow probe.
"""
import json
import os
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(os.path.expanduser("~"), ".jugaadi-claude", "state.json")
FRESH_WINDOW = 90  # seconds


def read_cache():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def main():
    cache = read_cache()
    if cache and time.time() - cache.get("updated_at", 0) < FRESH_WINDOW:
        power = cache.get("power", {})
        print(
            cache.get("state", "NONE"),
            str(power.get("on_ac", True)).lower(),
            power.get("battery_percent", 100),
        )
        return

    # Stale or missing: quick power-only probe
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPT_DIR, "power_check.py")],
            capture_output=True, text=True, timeout=8,
        )
        data = json.loads(result.stdout)
        print(
            "NONE",
            str(data.get("on_ac", True)).lower(),
            data.get("battery_percent", 100),
        )
    except Exception:
        print("NONE true 100")


if __name__ == "__main__":
    main()
