# scripts/cache_reader.py
"""
Fast cached state reader for jugaadi-claude hooks and statusline.
Reads ~/.jugaadi-claude/state.json written by guardian.py daemon.
Falls back to quick local evaluation if cache is absent.
"""
import os
import sys
import json
import time

STATE_DIR = os.path.join(os.path.expanduser("~"), ".jugaadi-claude")
STATE_FILE = os.path.join(STATE_DIR, "state.json")

def get_cached_state(max_age_seconds=120):
    if os.path.exists(STATE_FILE):
        try:
            mtime = os.path.getmtime(STATE_FILE)
            if time.time() - mtime < max_age_seconds:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass

    # Quick fallback if cache is missing or stale
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        import subprocess
        res = subprocess.run(
            [sys.executable, os.path.join(script_dir, "power_check.py")],
            capture_output=True, text=True, timeout=3
        )
        p_data = json.loads(res.stdout) if res.stdout.strip() else {}
        on_ac = p_data.get("on_ac", True)
        return {
            "state": "NORMAL" if on_ac else "POWER_UNSTABLE",
            "power": p_data,
            "network": {"diagnosis": "ALL_OK"},
            "cached": False,
            "timestamp": time.time()
        }
    except Exception:
        return {
            "state": "NORMAL",
            "power": {"on_ac": True, "battery_percent": 100},
            "network": {"diagnosis": "ALL_OK"},
            "cached": False
        }

if __name__ == "__main__":
    print(json.dumps(get_cached_state(), indent=2))
