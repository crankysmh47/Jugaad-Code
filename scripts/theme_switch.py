# scripts/theme_switch.py
"""Toggle the green/white Jugaadi PK theme for Claude Code (user-level).

on  : installs ~/.claude/themes/jugaadi-pk.json and points settings.json at it
off : restores the previous theme value (or removes the theme key)
"""
import json
import os
import sys

HOME = os.path.expanduser("~")
CLAUDE_DIR = os.path.join(HOME, ".claude")
THEMES_DIR = os.path.join(CLAUDE_DIR, "themes")
THEME_FILE = os.path.join(THEMES_DIR, "jugaadi-pk.json")
SETTINGS_FILE = os.path.join(CLAUDE_DIR, "settings.json")
STATE_DIR = os.path.join(HOME, ".jugaadi-claude")
PREV_FILE = os.path.join(STATE_DIR, "prev-theme.json")

THEME_SLUG = "custom:jugaadi-pk"

# Green and white on a dark base. The orange Claude accent ("claude"
# token) becomes green; text stays white. Error stays red for signal.
PK_THEME = {
    "name": "Jugaadi PK",
    "base": "dark",
    "overrides": {
        "claude": "#2ecc71",
        "claudeShimmer": "#7ee8a4",
        "text": "#f4faf5",
        "inverseText": "#0c1610",
        "subtle": "#93b8a2",
        "inactive": "#5c7d69",
        "suggestion": "#b9f2cf",
        "permission": "#2ecc71",
        "permissionShimmer": "#7ee8a4",
        "remember": "#2ecc71",
        "success": "#eafff2",
        "error": "#ff6b6b",
        "warning": "#f5d76e",
        "warningShimmer": "#f5d76e",
        "promptBorder": "#2ecc71",
        "promptBorderShimmer": "#7ee8a4",
        "planMode": "#2ecc71",
        "autoAccept": "#2ecc71",
        "bashBorder": "#27ae60",
        "ide": "#2ecc71",
        "fastMode": "#2ecc71",
        "fastModeShimmer": "#7ee8a4",
        "inactiveShimmer": "#7ee8a4",
        "diffAdded": "#2ecc71",
        "diffRemoved": "#ff6b6b",
        "diffAddedDimmed": "#1c5c38",
        "diffRemovedDimmed": "#5c1c1c",
        "userMessageBackground": "#1b2a20",
        "userMessageBackgroundHover": "#22352a",
        "bashMessageBackgroundColor": "#142019",
        "memoryBackgroundColor": "#16231b",
        "selectionBg": "#1e3b2a",
    },
}


def load_settings():
    """Return (settings_dict, parse_error). Never clobber an invalid file."""
    if not os.path.exists(SETTINGS_FILE):
        return {}, None
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh), None
    except (json.JSONDecodeError, OSError) as e:
        return None, f"settings.json could not be parsed: {e}"


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=2)
        fh.write("\n")


def theme_on():
    first_run = not os.path.isdir(THEMES_DIR)
    os.makedirs(THEMES_DIR, exist_ok=True)
    os.makedirs(STATE_DIR, exist_ok=True)

    settings, err = load_settings()
    if err:
        return {"switched": False, "error": err}

    prev = settings.get("theme")
    with open(PREV_FILE, "w", encoding="utf-8") as fh:
        json.dump({"theme": prev, "existed": "theme" in settings}, fh, indent=2)

    with open(THEME_FILE, "w", encoding="utf-8") as fh:
        json.dump(PK_THEME, fh, indent=2)
        fh.write("\n")

    settings["theme"] = THEME_SLUG
    save_settings(settings)

    return {
        "switched": True,
        "theme": THEME_SLUG,
        "previous": prev,
        "settings": SETTINGS_FILE,
        "first_run": first_run,
    }


def theme_off():
    settings, err = load_settings()
    if err:
        return {"switched": False, "error": err}

    prev = None
    existed = False
    if os.path.exists(PREV_FILE):
        try:
            with open(PREV_FILE, "r", encoding="utf-8") as fh:
                backup = json.load(fh)
            prev = backup.get("theme")
            existed = backup.get("existed", False)
        except (json.JSONDecodeError, OSError):
            pass

    if existed and prev:
        settings["theme"] = prev
    else:
        settings.pop("theme", None)

    save_settings(settings)
    try:
        if os.path.exists(PREV_FILE):
            os.remove(PREV_FILE)
    except OSError:
        pass

    return {"switched": True, "theme": prev, "settings": SETTINGS_FILE}


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "on"
    if action == "on":
        result = theme_on()
    elif action == "off":
        result = theme_off()
    else:
        result = {"switched": False, "error": "Usage: theme_switch.py <on|off>"}
    print(json.dumps(result, indent=2))
