# scripts/guardian.py
import time
import subprocess
import sys
import os
import json
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

CHECK_INTERVAL = 60  # seconds
COMMIT_INTERVAL = 300  # auto-commit every 5 min if dirty
last_commit_time = 0
last_power_state = True  # assume AC on start

PK_MESSAGES = [
    "Bijli watch karna ho raha hai...",
    "Internet check ho raha hai...",
    "Code safe hai. Abhi tak.",
    "Submarine cable theek hai.",
    "Guardian jaag raha hai.",
]

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[jugaadi-claude {ts}] {msg}", flush=True)

def get_power():
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "power_check.py")],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        return data.get("on_ac", True), data.get("battery_percent", 100)
    except:
        return True, 100

def is_git_dirty():
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=5
        )
        return bool(result.stdout.strip())
    except:
        return False

def emergency_commit(reason="power-cut"):
    if not is_git_dirty():
        return False
    try:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        msg = f"chore: [PK-checkpoint] {reason} @ {ts}"
        subprocess.run(["git", "add", "-A"], timeout=10)
        subprocess.run(["git", "commit", "-m", msg], timeout=10)
        log(f"Emergency commit: {msg}")
        return True
    except Exception as e:
        log(f"Commit failed: {e}")
        return False

def auto_commit():
    global last_commit_time
    now = time.time()
    if now - last_commit_time > COMMIT_INTERVAL and is_git_dirty():
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        msg = f"chore: [PK-auto] checkpoint @ {ts}"
        try:
            subprocess.run(["git", "add", "-A"], timeout=10)
            subprocess.run(["git", "commit", "-m", msg], timeout=10)
            last_commit_time = now
            log("Auto-checkpoint committed.")
        except:
            pass

def check_net_and_switch():
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "net_check.py")],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(result.stdout)
        diagnosis = data.get("diagnosis", "ALL_OK")
        
        if diagnosis in ["SUBMARINE_CABLE", "ISP_ROUTING"]:
            mirrors = data.get("mirrors", {})
            if mirrors.get("npm"):
                subprocess.run(
                    [sys.executable, 
                     os.path.join(os.path.dirname(os.path.abspath(__file__)), "mirror_switch.py"),
                     "npm", mirrors["npm"]],
                    timeout=10
                )
                log(f"Network degraded ({diagnosis}). Switched npm to Asian mirror.")
            if mirrors.get("pip"):
                subprocess.run(
                    [sys.executable, 
                     os.path.join(os.path.dirname(os.path.abspath(__file__)), "mirror_switch.py"),
                     "pip", mirrors["pip"]],
                    timeout=10
                )
                log(f"Network degraded ({diagnosis}). Switched pip to Asian mirror.")
        
        return diagnosis
    except:
        return "UNKNOWN"

def check_survival_mode():
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "survival_mode.py"), "--json"],
            capture_output=True, text=True, timeout=35
        )
        data = json.loads(result.stdout)
        state = data.get("state", "NORMAL")
        log(f"Survival state: {state}")
        return state, data
    except Exception as e:
        log(f"Survival state check failed: {e}")
        return "UNKNOWN", {}

def run():
    global last_power_state
    log("jugaadi-claude Guardian started. Pakistan mode active.")
    msg_index = 0

    while True:
        try:
            # Power check
            on_ac, pct = get_power()

            if last_power_state and not on_ac:
                log(f"⚡ BIJLI GONE! Battery: {pct}%. Emergency commit...")
                emergency_commit("bijli-cut")
            
            last_power_state = on_ac

            # Auto-commit on a schedule
            auto_commit()

            # Net check every 5 cycles
            if int(time.time() / CHECK_INTERVAL) % 5 == 0:
                diagnosis = check_net_and_switch()
                log(f"Net: {diagnosis}")

            # Adaptive survival mode
            state, survival = check_survival_mode()

            if state == "CRITICAL":
                log("🚨 CRITICAL: protect work, checkpoint now, avoid long operations.")
            elif state == "POWER_UNSTABLE":
                log("⚡ POWER UNSTABLE: workspace protection active.")
            elif state == "NETWORK_DEGRADED":
                log("🌐 NETWORK DEGRADED: cache/mirror/retry behavior active.")

            # Rotating message
            log(PK_MESSAGES[msg_index % len(PK_MESSAGES)])
            msg_index += 1

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            log("Guardian stopped. Allah hafiz.")
            sys.exit(0)
        except Exception as e:
            log(f"Error: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run()
