# scripts/guardian_boot.py
"""Ensure the guardian daemon is running. Fast; safe to call at session start.

Spawns the guardian as a DETACHED process so it survives the Claude Code
session that started it — no OS-level startup script needed.
"""
import ctypes
import os
import subprocess
import sys

STATE_DIR = os.path.join(os.path.expanduser("~"), ".jugaad-code")
PID_FILE = os.path.join(STATE_DIR, "guardian.pid")
LOG_FILE = os.path.join(STATE_DIR, "guardian.log")
GUARDIAN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guardian.py")


def _pid_alive_windows(pid):
    # os.kill(pid, 0) is NOT an existence check on Windows — it terminates.
    # OpenProcess with query-only access is the safe way.
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
        if not handle:
            return False
        kernel32.CloseHandle(handle)
        return True
    except Exception:
        return False


def guardian_alive():
    try:
        with open(PID_FILE, "r") as fh:
            pid = int(fh.read().strip())
    except (OSError, ValueError):
        return False
    if os.name == "nt":
        return _pid_alive_windows(pid)
    try:
        os.kill(pid, 0)  # POSIX: signal 0 is a safe existence check
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
