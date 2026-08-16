# scripts/mirror_switch.py
import subprocess
import sys
import json
import os

# Remember what the registries were BEFORE we switched them, so /pk off (and
# the guardian's auto-restore) puts back the exact previous value instead of
# hardcoding the official URLs over a user's custom registry.
BACKUP_FILE = os.path.join(os.path.expanduser("~"), ".jugaad-code", "registry_backup.json")

DEFAULTS = {
    "npm": "https://registry.npmjs.org/",
    "pip": "https://pypi.org/simple/"
}


def _load_backup():
    try:
        with open(BACKUP_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_backup(data):
    try:
        os.makedirs(os.path.dirname(BACKUP_FILE), exist_ok=True)
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def _run(cmd, timeout=15):
    use_shell = os.name == 'nt'
    return subprocess.run(cmd, capture_output=True, text=True, shell=use_shell, timeout=timeout)


def _read_npm_registry():
    try:
        r = _run(["npm", "config", "get", "registry"])
        value = r.stdout.strip()
        return value or None
    except Exception:
        return None


def _read_pip_index():
    try:
        r = _run([sys.executable, "-m", "pip", "config", "get", "global.index-url"])
        value = r.stdout.strip()
        return value or None
    except Exception:
        return None


def _record_previous(pm):
    backup = _load_backup()
    if pm in backup:
        return backup
    if pm == "npm":
        prev = _read_npm_registry()
    elif pm == "pip":
        prev = _read_pip_index()
    else:
        prev = None
    if prev:
        backup[pm] = prev
        _save_backup(backup)
    return backup


def switch_mirror(package_manager, mirror_url):
    try:
        if package_manager not in ("npm", "pip"):
            return {"switched": False, "error": f"Unknown package manager: {package_manager}"}

        _record_previous(package_manager)
        if package_manager == "npm":
            result = _run(["npm", "config", "set", "registry", mirror_url])
        else:
            result = _run([sys.executable, "-m", "pip", "config", "set", "global.index-url", mirror_url])

        ok = result.returncode == 0
        return {
            "switched": ok,
            "pm": package_manager,
            "mirror": mirror_url,
            "error": None if ok else (result.stderr.strip() or result.stdout.strip() or f"{package_manager} config set failed"),
        }
    except Exception as e:
        return {"switched": False, "pm": package_manager, "error": str(e)}


def reset_mirror(package_manager):
    """Restore the registry that existed before we switched it, falling back
    to the official default. Forgets the backup once restored."""
    try:
        if package_manager not in ("npm", "pip"):
            return {"switched": False, "error": f"Unknown package manager: {package_manager}"}

        backup = _load_backup()
        target = backup.get(package_manager) or DEFAULTS.get(package_manager, "")

        if package_manager == "npm":
            result = _run(["npm", "config", "set", "registry", target])
        else:
            result = _run([sys.executable, "-m", "pip", "config", "set", "global.index-url", target])

        ok = result.returncode == 0
        if ok and package_manager in backup:
            backup.pop(package_manager)
            _save_backup(backup)
        return {
            "switched": ok,
            "pm": package_manager,
            "mirror": target,
            "error": None if ok else (result.stderr.strip() or result.stdout.strip() or f"{package_manager} config set failed"),
        }
    except Exception as e:
        return {"switched": False, "pm": package_manager, "error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: mirror_switch.py <npm|pip|reset> [mirror_url]"}))
        sys.exit(1)

    pm = sys.argv[1]
    if pm == "reset":
        target_pm = sys.argv[2] if len(sys.argv) > 2 else "all"
        if target_pm == "all":
            npm_res = reset_mirror("npm")
            pip_res = reset_mirror("pip")
            print(json.dumps({"npm": npm_res, "pip": pip_res}, indent=2))
        else:
            print(json.dumps(reset_mirror(target_pm), indent=2))
    elif len(sys.argv) >= 3:
        url = sys.argv[2]
        print(json.dumps(switch_mirror(pm, url), indent=2))
    else:
        print(json.dumps({"error": "Usage: mirror_switch.py <npm|pip> <mirror_url>"}))
        sys.exit(1)
