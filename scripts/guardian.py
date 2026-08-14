# scripts/guardian.py
import atexit
import json
import os
import subprocess
import sys
import time
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(SCRIPT_DIR))

from ui.messages import get_message

STATE_DIR = os.path.join(os.path.expanduser("~"), ".jugaadi-claude")
PID_FILE = os.path.join(STATE_DIR, "guardian.pid")
STATE_FILE = os.path.join(STATE_DIR, "state.json")
LOG_FILE = os.path.join(STATE_DIR, "guardian.log")

CHECK_INTERVAL = 60  # seconds
COMMIT_INTERVAL = 300  # auto-commit every 5 min if dirty
last_commit_time = 0
last_power_state = True  # assume AC on start
last_network = {"diagnosis": "ALL_OK", "recommendation": ""}


def ensure_state_dir():
    os.makedirs(STATE_DIR, exist_ok=True)


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[jugaadi-claude {ts}] {msg}"
    print(line, flush=True)
    try:
        ensure_state_dir()
        with open(LOG_FILE, "a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now().strftime('%Y-%m-%d')} {line}\n")
    except Exception:
        pass


def write_pidfile():
    ensure_state_dir()
    with open(PID_FILE, "w") as fh:
        fh.write(str(os.getpid()))


def remove_pidfile():
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    except Exception:
        pass


def write_state_cache(state, power, network):
    try:
        ensure_state_dir()
        payload = {
            "state": state,
            "power": {
                "on_ac": power.get("on_ac", True),
                "battery_percent": power.get("battery_percent", 100),
            },
            "network": {
                "diagnosis": network.get("diagnosis", "ALL_OK"),
                "recommendation": network.get("recommendation", ""),
            },
            "updated_at": time.time(),
            "guardian_pid": os.getpid(),
        }
        with open(STATE_FILE, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
    except Exception:
        pass


def get_power():
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPT_DIR, "power_check.py")],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        return data.get("on_ac", True), data.get("battery_percent", 100)
    except Exception:
        return True, 100


def is_git_dirty():
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=5
        )
        return bool(result.stdout.strip())
    except Exception:
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
        except Exception:
            pass


def check_net_and_switch():
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPT_DIR, "net_check.py")],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(result.stdout)
        diagnosis = data.get("diagnosis", "ALL_OK")

        if diagnosis in ["SUBMARINE_CABLE", "ISP_ROUTING"]:
            mirrors = data.get("mirrors", {})
            if mirrors.get("npm"):
                subprocess.run(
                    [sys.executable,
                     os.path.join(SCRIPT_DIR, "mirror_switch.py"),
                     "npm", mirrors["npm"]],
                    timeout=10
                )
                log(f"Network degraded ({diagnosis}). Switched npm to Asian mirror.")
            if mirrors.get("pip"):
                subprocess.run(
                    [sys.executable,
                     os.path.join(SCRIPT_DIR, "mirror_switch.py"),
                     "pip", mirrors["pip"]],
                    timeout=10
                )
                log(f"Network degraded ({diagnosis}). Switched pip to Asian mirror.")

        return data
    except Exception:
        return {"diagnosis": "UNKNOWN", "recommendation": ""}


def check_survival_mode():
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPT_DIR, "survival_mode.py"), "--json"],
            capture_output=True, text=True, timeout=35
        )
        data = json.loads(result.stdout)
        state = data.get("state", "NORMAL")
        log(f"Survival state: {state}")
        return state, data
    except Exception as e:
        log(f"Survival state check failed: {e}")
        return "UNKNOWN", {}


def _pid_alive_windows(pid):
    # os.kill(pid, 0) is NOT an existence check on Windows — it terminates.
    # OpenProcess with query-only access is the safe way.
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
        if not handle:
            return False
        kernel32.CloseHandle(handle)
        return True
    except Exception:
        return False


def already_running():
    try:
        with open(PID_FILE, "r") as fh:
            pid = int(fh.read().strip())
    except (OSError, ValueError):
        return False
    if pid == os.getpid():
        return False
    if os.name == "nt":
        return _pid_alive_windows(pid)
    try:
        os.kill(pid, 0)  # POSIX: signal 0 is a safe existence check
        return True
    except OSError:
        return False


def run():
    global last_power_state
    if already_running():
        print("Guardian already running (pidfile). Exiting.", flush=True)
        return
    write_pidfile()
    atexit.register(remove_pidfile)
    log("jugaadi-claude Guardian started. Pakistan mode active.")

    while True:
        try:
            # Power check
            on_ac, pct = get_power()

            if last_power_state and not on_ac:
                log(f"Power cut detected. Battery at {pct}%. Taking an emergency checkpoint...")
                emergency_commit("bijli-cut")

            last_power_state = on_ac

            # Auto-commit on a schedule
            auto_commit()

            # Net check every 5 cycles
            if int(time.time() / CHECK_INTERVAL) % 5 == 0:
                last_network = check_net_and_switch()
                log(f"Net: {last_network.get('diagnosis')}")

            # Adaptive survival mode
            state, survival = check_survival_mode()

            if state == "CRITICAL":
                log("Critical state: checkpoint your work and avoid long operations.")
            elif state == "POWER_UNSTABLE":
                log("Power unstable: workspace protection active.")
            elif state == "NETWORK_DEGRADED":
                log("Network degraded: cache, mirrors and retries active.")

            # State cache for hooks and statusline
            write_state_cache(state, {"on_ac": on_ac, "battery_percent": pct}, last_network)

            # Rotating message
            log(get_message())

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            log("Guardian stopped. Allah hafiz.")
            remove_pidfile()
            sys.exit(0)
        except Exception as e:
            log(f"Error: {e}")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run()
