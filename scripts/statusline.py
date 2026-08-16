# scripts/statusline.py
"""
Statusline generator for Claude Code.
Outputs survival state + rotating Roman Urdu messages.
"""
import os
import sys
import json

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(SCRIPT_DIR))

try:
    from scripts.cache_reader import get_cached_state
except ImportError:
    from cache_reader import get_cached_state

try:
    from ui.messages import get_message
except ImportError:
    def get_message():
        return "Kaam karo. Guardian jaag raha hai."

def render_statusline():
    cache = get_cached_state()
    state = cache.get("state", "NORMAL")
    
    icons = {
        "NORMAL": "[PK: NORMAL]",
        "NETWORK_DEGRADED": "[PK: NET DEGRADED]",
        "POWER_UNSTABLE": "[PK: POWER UNSTABLE]",
        "CRITICAL": "[PK: CRITICAL]"
    }
    
    prefix = icons.get(state, "[PK]")
    msg = get_message()
    return f"{prefix} {msg}"

if __name__ == "__main__":
    print(render_statusline())
