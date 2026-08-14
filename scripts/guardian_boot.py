# scripts/guardian_boot.py
"""Ensure the guardian daemon is running. Fast; safe to call at session start.

Spawns the guardian as a DETACHED process so it survives the Claude Code
session that started it — no OS-level startup script needed.
"""
import os
import subprocess
import sys

STATE_DIR = os.path.join(os.path.expanduser("~"), ".jugaadi-claude")
PID_FILE = os.path.join(STATE_DIR, "guardian.pid")
LOG_FILE = os.path.join(STATE_DIR, "guardian.log")
GUARDIAN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guardian.py")


def guardian_alive():
    try:
        with open(PID_FILE, "r") as fh:
            pid = int(fh.read().strip())
    except (OSError, ValueError):
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def main():
    if guardian_alive():
        print("guardian already running")
        return

    os.makedirs(STATE_DIR, exist_ok=True)
    log = open(LOG_FILE, "a", encoding="utf-8")

    kwargs = {
        "stdout": log,
        "stderr": subprocess.STDOUT,
        "close_fds": True,
    }
    if os.name == "nt":
        kwargs["creationflags"] = (
            subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        kwargs["start_new_session"] = True

    subprocess.Popen([sys.executable, GUARDIAN], **kwargs)
    print("guardian started (detached)")


if __name__ == "__main__":
    main()
