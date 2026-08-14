# scripts/demo.py
"""
jugaadi-claude Interactive Demonstration
Runs all resilience layer components and displays a full Pakistan Health Report.
"""
import sys
import os
import json
import time

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(SCRIPT_DIR))

from ui.messages import get_message
from ui.errors import translate_error

def run_script(name, *args):
    import subprocess
    cmd = [sys.executable, os.path.join(SCRIPT_DIR, name)] + list(args)
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(res.stdout)
    except Exception:
        return {"raw": res.stdout.strip(), "error": res.stderr.strip()}

def main():
    print("=" * 55)
    print("  🇵🇰 jugaad-code Developer Health Report")
    print("=" * 55)

    print("\n[1/4] Checking Power & Bijli Status...")
    power = run_script("power_check.py")
    on_ac = power.get("on_ac", True)
    pct = power.get("battery_percent", 100)
    mins = power.get("estimated_minutes", 999)
    status_str = "AC Connected" if on_ac else "On Battery / UPS"
    print(f"  POWER Status   : {status_str}")
    print(f"     Battery        : {pct}%")
    print(f"     Remaining Time : {mins if mins < 900 else 'N/A'} mins")

    print("\n[2/4] Detecting ISP & Regional Quirks...")
    isp_data = run_script("isp_detect.py")
    isp = isp_data.get("isp", "Unknown")
    city = isp_data.get("city", "Unknown")
    country = isp_data.get("country", "Pakistan")
    quirks = isp_data.get("quirks", {})
    known_issues = quirks.get("known_issues", ["Standard routing profile"])
    print(f"  ISP Detected   : {isp} ({city}, {country})")
    print(f"     Known Quirks   : {', '.join(known_issues)}")

    print("\n[3/4] Layered Network Diagnostics...")
    net = run_script("net_check.py")
    endpoints = net.get("endpoints", {})
    for ep, data in endpoints.items():
        st = "[OK]" if data.get("status") == "ok" else f"[{data.get('status', 'FAIL').upper()}]"
        ms = data.get('ttfb_ms') or data.get('tcp_ms') or data.get('dns_ms') or 0
        print(f"     - {ep:<20}: {st:<10} ({ms}ms) [{data.get('cable')}]")

    diagnosis = net.get("diagnosis", "ALL_OK")
    recommendation = net.get("recommendation", "Network looks good.")
    print(f"\n  DIAGNOSIS       : {diagnosis}")
    print(f"  RECOMMENDATION  : {recommendation}")

    print("\n[4/4] Adaptive Survival Mode Engine...")
    survival = run_script("survival_mode.py", "--json")
    state = survival.get("state", "NORMAL")
    actions = survival.get("actions", [])
    print(f"  SURVIVAL STATE  : {state}")
    print("     Active Policies:")
    for a in actions:
        print(f"       - {a}")

    print("\n" + "=" * 55)
    print(f"Desi Dev Message : \"{get_message()}\"")
    print("=" * 55)

if __name__ == "__main__":
    main()
