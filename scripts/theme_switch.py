# scripts/theme_switch.py
"""
Manages the Pakistan Green & White theme for Claude Code.
Switches user theme in ~/.claude/settings.json and ~/.claude/themes/pk.json.
"""
import os
import sys
import json

CLAUDE_DIR = os.path.join(os.path.expanduser("~"), ".claude")
THEMES_DIR = os.path.join(CLAUDE_DIR, "themes")
SETTINGS_FILE = os.path.join(CLAUDE_DIR, "settings.json")
BACKUP_DIR = os.path.join(os.path.expanduser("~"), ".jugaad-code")
BACKUP_FILE = os.path.join(BACKUP_DIR, "previous_theme.txt")

PK_THEME_DEF = {
    "name": "Pakistan Green",
    "type": "dark",
    "colors": {
        "primary": "#01411C",
        "secondary": "#00A859",
        "background": "#0A140D",
        "foreground": "#FFFFFF",
        "accent": "#00FF66",
        "highlight": "#118032",
        "muted": "#7A9E82",
        "border": "#004D26",
        "success": "#00E676",
        "warning": "#FFD600",
        "error": "#FF5252"
    }
}

def ensure_dirs():
    os.makedirs(THEMES_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_settings(data):
    os.makedirs(CLAUDE_DIR, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def set_theme_on():
    ensure_dirs()
    # Write pk theme file
    pk_theme_file = os.path.join(THEMES_DIR, "pk.json")
    with open(pk_theme_file, "w", encoding="utf-8") as f:
        json.dump(PK_THEME_DEF, f, indent=2)

    settings = load_settings()
    current_theme = settings.get("theme", "default")
    
    # Only backup if not already pk
    if current_theme != "pk":
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            f.write(str(current_theme))

    settings["theme"] = "pk"
    save_settings(settings)
    return {"status": "ACTIVE", "theme": "pk", "previous": current_theme}

def set_theme_off():
    ensure_dirs()
    prev = "default"
    if os.path.exists(BACKUP_FILE):
        try:
            with open(BACKUP_FILE, "r", encoding="utf-8") as f:
                prev = f.read().strip() or "default"
        except Exception:
            prev = "default"
    
    settings = load_settings()
    settings["theme"] = prev
    save_settings(settings)
    return {"status": "INACTIVE", "theme": prev}

def get_status():
    settings = load_settings()
    theme = settings.get("theme", "default")
    return {
        "active": theme == "pk",
        "theme": theme
    }

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "on":
        res = set_theme_on()
        print(json.dumps(res, indent=2))
    elif action == "off":
        res = set_theme_off()
        print(json.dumps(res, indent=2))
    else:
        res = get_status()
        print(json.dumps(res, indent=2))
