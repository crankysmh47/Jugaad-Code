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
THEME_FILE = os.path.join(THEMES_DIR, "pk.json")
SETTINGS_FILE = os.path.join(CLAUDE_DIR, "settings.json")
BACKUP_DIR = os.path.join(os.path.expanduser("~"), ".jugaad-code")
BACKUP_FILE = os.path.join(BACKUP_DIR, "previous_theme.txt")

# Claude Code custom-theme schema: {"name", "base", "overrides"}, with the
# settings value "custom:<slug>". Monochrome green on a white base — no
# reds, yellows, or orange; darkest greens for text, pale greens for panels.
PK_THEME_DEF = {
    "name": "Pakistan Green",
    "base": "dark",
    "overrides": {
        "claude": "#00E676",
        "claudeShimmer": "#00FF66",
        "text": "#E9F7EE",
        "inverseText": "#021A0D",
        "subtle": "#7A9E82",
        "inactive": "#4A6B57",
        "suggestion": "#00E676",
        "permission": "#00E676",
        "permissionShimmer": "#6FCF97",
        "remember": "#00E676",
        "success": "#00E676",
        "error": "#FF5252",
        "warning": "#FFD600",
        "warningShimmer": "#FFE082",
        "promptBorder": "#00A859",
        "promptBorderShimmer": "#00E676",
        "planMode": "#00E676",
        "autoAccept": "#00E676",
        "bashBorder": "#00A859",
        "ide": "#00E676",
        "fastMode": "#00E676",
        "fastModeShimmer": "#6FCF97",
        "inactiveShimmer": "#6FCF97",
        "diffAdded": "#00E676",
        "diffRemoved": "#FF5252",
        "diffAddedDimmed": "#0F5F36",
        "diffRemovedDimmed": "#5A1A1A",
        "userMessageBackground": "#052614",
        "userMessageBackgroundHover": "#08381D",
        "bashMessageBackgroundColor": "#031E10",
        "memoryBackgroundColor": "#052614",
        "selectionBg": "#0A4D27"
    }
}

# Values that are not real user themes — never back these up or restore them.
SENTINELS = {"pk", "custom:pk", "default", ""}


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
    with open(THEME_FILE, "w", encoding="utf-8") as f:
        json.dump(PK_THEME_DEF, f, indent=2)

    settings = load_settings()
    current = settings.get("theme", "")

    # Only back up a real previous theme, not one of our own values
    previous = None
    if current and current not in SENTINELS:
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            f.write(str(current))
        previous = current
    else:
        try:
            if os.path.exists(BACKUP_FILE):
                os.remove(BACKUP_FILE)
        except OSError:
            pass

    settings["theme"] = "custom:pk"
    save_settings(settings)
    return {"status": "ACTIVE", "theme": "custom:pk", "previous": previous}


def set_theme_off():
    ensure_dirs()
    prev = ""
    if os.path.exists(BACKUP_FILE):
        try:
            with open(BACKUP_FILE, "r", encoding="utf-8") as f:
                prev = f.read().strip()
        except Exception:
            prev = ""

    settings = load_settings()
    if prev and prev not in SENTINELS:
        settings["theme"] = prev
    else:
        # No previous theme on record — remove the key entirely so Claude
        # Code falls back to its default colors.
        settings.pop("theme", None)
    save_settings(settings)

    try:
        if os.path.exists(BACKUP_FILE):
            os.remove(BACKUP_FILE)
    except OSError:
        pass

    return {"status": "INACTIVE", "theme": prev or None}


def get_status():
    settings = load_settings()
    theme = settings.get("theme", "")
    return {
        "active": theme == "custom:pk",
        "theme": theme or None
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
