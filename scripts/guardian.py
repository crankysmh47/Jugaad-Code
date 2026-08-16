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
from survival_mode import determine_state

STATE_DIR = os.path.join(os.path.expanduser("~"), ".jugaad-code")
PID_FILE = os.path.join(STATE_DIR, "guardian.pid")
STATE_FILE = os.path.join(STATE_DIR, "state.json")
LOG_FILE = os.path.join(STATE_DIR, "guardian.log")

CHECK_INTERVAL = 60  # seconds
COMMIT_INTERVAL = 300  # auto-commit every 5 min if dirty
NET_CHECK_EVERY = 5  # run the network probe every N cycles
MAX_LOG_BYTES = 5 * 1024 * 1024  # rotate guardian.log past 5 MB

# Project the guardian was spawned from. Git checkpoints target this directory
# (passed by guardian_boot.py from CLAUDE_PROJECT_DIR) instead of the daemon's
# inherited CWD, which may point at a different project later.
PROJECT_DIR = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

last_commit_time = 0
last_power_state = (True, 100)  # (on_ac, battery_percent); assume AC on start
last_network = {"diagnosis": "ALL_OK", "recommendation": ""}
mirrors_switched = False
cycle = 0


def ensure_state_dir():
    os.makedirs(STATE_DIR, exist_ok=True)


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[jugaad-code {ts}] {msg}"
    print(line, flush=True)
    try:
        ensure_state_dir()
        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_BYTES:
            os.replace(LOG_FILE, LOG_FILE + ".1")
        with open(LOG_FILE, "a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now().strftime('%Y-%m-%d')} {line}\n")
    except Exception:
        pass


def write_pidfile():
    ensure_state_dir()
    with open(PID_FILE, "w") as fh:
        fh.write(str(os.getpid()))


def acquire_pidfile():
    """Claim the pidfile exclusively so two concurrent boots can't both
    become the daemon (O_CREAT|O_EXCL is atomic)."""
    ensure_state_dir()
    try:
        fd = os.open(PID_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w") as fh:
        fh.write(str(os.getpid()))
    return True


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
            "mirrors_switched": mirrors_switched,
            "project_dir": PROJECT_DIR,
            "updated_at": time.time(),
            "guardian_pid": os.getpid(),
        }
        with open(STATE_FILE, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
    except Exception:
        pass


def get_power():
    """Return (on_ac, battery_percent) or (None, None) when the probe fails."""
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPT_DIR, "power_check.py")],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        return data.get("on_ac"), data.get("battery_percent", 100)
    except Exception:
        return None, None


def git_run(args, timeout=10):
    """Run a git command inside the guardian's project directory."""
    return subprocess.run(
        args, cwd=PROJECT_DIR, capture_output=True, text=True, timeout=timeout
    )


def is_git_dirty():
    try:
        result = git_run(["git", "status", "--porcelain"], timeout=5)
        return bool(result.stdout.strip())
    except Exception:
        return False


def emergency_commit(reason="power-cut"):
    if not is_git_dirty():
        return False
    try:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        msg = f"chore: [PK-checkpoint] {reason} @ {ts}"
        git_run(["git", "add", "-A"])
        git_run(["git", "commit", "-m", msg])
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
            git_run(["git", "add", "-A"])
            git_run(["git", "commit", "-m", msg])
            last_commit_time = now
            log("Auto-checkpoint committed.")
        except Exception:
            pass


def check_net_and_switch():
    """Probe the network, switch to Asian mirrors when degraded, and restore
    the original registries once the international route recovers."""
    global mirrors_switched
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPT_DIR, "net_check.py")],
            capture_output=True, text=True, timeout=45
        )
        data = json.loads(result.stdout)
        diagnosis = data.get("diagnosis", "ALL_OK")

        if diagnosis in ["SUBMARINE_CABLE", "ISP_ROUTING"] and not mirrors_switched:
            mirrors = data.get("mirrors", {})
            switched_any = False
            for pm, url in (("npm", mirrors.get("npm")), ("pip", mirrors.get("pip"))):
                if not url:
                    continue
                r = subprocess.run(
                    [sys.executable, os.path.join(SCRIPT_DIR, "mirror_switch.py"), pm, url],
                    capture_output=True, text=True, timeout=15
                )
                try:
                    if json.loads(r.stdout).get("switched"):
                        switched_any = True
                except Exception:
                    pass
            if switched_any:
                mirrors_switched = True
                log(f"Network degraded ({diagnosis}). Switched to Asian mirrors.")

        elif diagnosis == "ALL_OK" and mirrors_switched:
            subprocess.run(
                [sys.executable, os.path.join(SCRIPT_DIR, "mirror_switch.py"), "reset", "all"],
                capture_output=True, text=True, timeout=20
            )
            mirrors_switched = False
            log("Network recovered. Restored original registries.")

        return data
    except Exception:
        return {"diagnosis": "UNKNOWN", "recommendation": ""}


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
    global last_power_state, last_network, cycle
    if already_running():
        print("Guardian already running (pidfile). Exiting.", flush=True)
        return
    if not acquire_pidfile():
        # A concurrent boot won the race. If the pidfile is stale (crashed
        # daemon), clear it and claim once more; otherwise exit quietly.
        if not already_running():
            remove_pidfile()
            if not acquire_pidfile():
                print("Could not acquire pidfile. Exiting.", flush=True)
                return
        else:
            print("Guardian already running (pidfile). Exiting.", flush=True)
            return
    atexit.register(remove_pidfile)
    log(f"jugaad-code Guardian started. Pakistan mode active. Project: {PROJECT_DIR}")

    while True:
        try:
            # Power check — fail soft: keep the last known state when the
            # probe errors out, instead of silently assuming AC power.
            on_ac, pct = get_power()
            if on_ac is None:
                log("Power probe failed — keeping last known power state.")
                on_ac, pct = last_power_state

            # Emergency checkpoint the moment AC power drops
            if last_power_state[0] is True and on_ac is False:
                log(f"Power cut detected. Battery at {pct}%. Taking an emergency checkpoint...")
                emergency_commit("bijli-cut")

            last_power_state = (on_ac, pct)

            # Auto-commit on a schedule
            auto_commit()

            # Net check every NET_CHECK_EVERY cycles (also on the first cycle)
            cycle += 1
            if cycle == 1 or cycle % NET_CHECK_EVERY == 0:
                last_network = check_net_and_switch()
                log(f"Net: {last_network.get('diagnosis')}")

            # Adaptive survival mode — computed in-process from the data we
            # already collected, so the network is never probed twice.
            state = determine_state(
                {"on_ac": on_ac, "battery_percent": pct if pct is not None else 100},
                last_network
            )
            log(f"Survival state: {state}")

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
