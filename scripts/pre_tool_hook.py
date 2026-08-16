# scripts/pre_tool_hook.py
"""
Pre-tool execution hook for Claude Code (Cross-platform Python).
Checks cached power/survival state, triggers checkpoint on low battery,
and outputs a rotating desi message.
"""
import os
import sys
import subprocess
import time
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(SCRIPT_DIR))

# At most one low-battery auto-checkpoint every LOW_BATTERY_COMMIT_INTERVAL
# seconds, no matter how many tool calls happen in between.
LOW_BATTERY_COMMIT_INTERVAL = 300
LOW_BATTERY_MARKER = os.path.join(
    os.path.expanduser("~"), ".jugaad-code", "low_battery_commit.marker"
)

try:
    from scripts.cache_reader import get_cached_state
except ImportError:
    from cache_reader import get_cached_state

try:
    from ui.messages import get_message
except ImportError:
    def get_message():
        return "Kaam karo. Guardian jaag raha hai."


def _low_battery_committed_recently():
    try:
        if os.path.exists(LOW_BATTERY_MARKER):
            return time.time() - os.path.getmtime(LOW_BATTERY_MARKER) < LOW_BATTERY_COMMIT_INTERVAL
    except Exception:
        pass
    return False


def _mark_low_battery_commit():
    try:
        os.makedirs(os.path.dirname(LOW_BATTERY_MARKER), exist_ok=True)
        with open(LOW_BATTERY_MARKER, "w") as fh:
            fh.write(str(time.time()))
    except Exception:
        pass

def main():
    try:
        cache = get_cached_state()
        state = cache.get("state", "NORMAL")
        power = cache.get("power", {})
        on_ac = power.get("on_ac", True)
        pct = power.get("battery_percent", 100)

        if state == "CRITICAL":
            print("[jugaad-code] Critical state: checkpoint your work and avoid long operations.")
        elif state == "POWER_UNSTABLE":
            print("[jugaad-code] Power unstable: workspace protection active.")
        elif state == "NETWORK_DEGRADED":
            print("[jugaad-code] Network degraded: cache, mirrors and retries active.")

        # Low battery auto-checkpoint (deduped — at most once per 5 minutes)
        if not on_ac and pct < 20 and not _low_battery_committed_recently():
            print(f"[jugaad-code] Battery at {pct}%. Power is out. Taking an auto-checkpoint.")
            project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
            try:
                subprocess.run(["git", "add", "-A"], cwd=project_dir, capture_output=True, timeout=5)
                ts = datetime.now().strftime("%H:%M")
                subprocess.run(["git", "commit", "-m", f"chore: [PK-checkpoint] low-battery @ {ts}"], cwd=project_dir, capture_output=True, timeout=5)
                _mark_low_battery_commit()
            except Exception:
                pass

        # Desi flavor message
        msg = get_message()
        if msg:
            print(f"\"{msg}\"")

    except Exception:
        pass

if __name__ == "__main__":
    main()
