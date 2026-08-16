#!/bin/bash
# install.sh — Linux / macOS / WSL setup for jugaad-code

set -e

echo "🇵🇰 Installing jugaad-code — Pakistan Resilience Layer for Claude Code"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Python
if command -v python3 &> /dev/null; then
    PY="python3"
elif command -v python &> /dev/null; then
    PY="python"
else
    echo "❌ Python not found. Install Python 3 first."
    exit 1
fi

# Install Python dependencies
echo "Installing dependencies..."
$PY -m pip install psutil --quiet || true

# Target directories
CLAUDE_DIR="$HOME/.claude"
CLAUDE_COMMANDS_DIR="$CLAUDE_DIR/commands"
CLAUDE_HOOKS_DIR="$CLAUDE_DIR/hooks"
CLAUDE_THEMES_DIR="$CLAUDE_DIR/themes"
APP_DIR="$HOME/.jugaad-code"
APP_SCRIPTS_DIR="$APP_DIR/scripts"
APP_UI_DIR="$APP_DIR/ui"

mkdir -p "$CLAUDE_COMMANDS_DIR" "$CLAUDE_HOOKS_DIR" "$CLAUDE_THEMES_DIR" "$APP_SCRIPTS_DIR" "$APP_UI_DIR"

# Copy scripts and UI to user app directory
if [ -d "scripts" ]; then
    cp -r scripts/* "$APP_SCRIPTS_DIR/"
fi
if [ -d "ui" ]; then
    cp -r ui/* "$APP_UI_DIR/"
fi

# Copy commands and hooks
if [ -d ".claude/commands" ]; then
    cp .claude/commands/* "$CLAUDE_COMMANDS_DIR/"
fi

# Export environment variable in shell rc
for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
    if [ -f "$rc" ] && ! grep -q "JUGAAD_CODE_SCRIPTS" "$rc"; then
        echo "export JUGAAD_CODE_SCRIPTS=\"$APP_SCRIPTS_DIR\"" >> "$rc"
        echo "export JUGAADI_CLAUDE_SCRIPTS=\"$APP_SCRIPTS_DIR\"" >> "$rc"
    fi
done
export JUGAAD_CODE_SCRIPTS="$APP_SCRIPTS_DIR"
export JUGAADI_CLAUDE_SCRIPTS="$APP_SCRIPTS_DIR"

# Wire hooks and statusline into settings.json (merge, never clobber)
SETTINGS_FILE="$CLAUDE_DIR/settings.json"
$PY - << EOF
import json
import os
import shutil
import sys

settings_path = "$SETTINGS_FILE"
settings = {}
if os.path.exists(settings_path):
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    except Exception as e:
        shutil.copy2(settings_path, settings_path + ".bak")
        print("[Error] ~/.claude/settings.json is not valid JSON.", file=sys.stderr)
        print(f"        Backed it up to {settings_path}.bak — fix it and re-run.", file=sys.stderr)
        sys.exit(1)

if not isinstance(settings, dict):
    settings = {}

PYTHON_BIN = "$PY"
# Bash-style fallback chain: env vars set by the installer, else installed path.
# Claude Code runs hook commands through bash even on Windows, so this expands.
SCRIPTS_REF = '"\${JUGAAD_CODE_SCRIPTS:-\${JUGAADI_CLAUDE_SCRIPTS:-\$HOME/.jugaad-code/scripts}}"'


def ensure_hook(event, matcher, command, timeout, status_message=None):
    hooks = settings.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        hooks = {}
        settings["hooks"] = hooks
    groups = hooks.setdefault(event, [])
    if not isinstance(groups, list):
        groups = []
        hooks[event] = groups
    script_name = command.rsplit("/", 1)[-1]
    for group in groups:
        for h in group.get("hooks", []):
            if script_name in h.get("command", ""):
                return  # already wired by a previous install
    entry = {"type": "command", "command": command, "timeout": timeout}
    if status_message:
        entry["statusMessage"] = status_message
    groups.append({"matcher": matcher, "hooks": [entry]})


ensure_hook(
    "SessionStart", "startup",
    PYTHON_BIN + " " + SCRIPTS_REF + "/guardian_boot.py", 10,
)
ensure_hook(
    "PreToolUse", "Bash|PowerShell",
    PYTHON_BIN + " " + SCRIPTS_REF + "/pre_tool_hook.py", 15,
    status_message="jugaad soch raha hai...",
)
ensure_hook(
    "PostToolUse", "Bash|PowerShell",
    PYTHON_BIN + " " + SCRIPTS_REF + "/post_tool_hook.py", 15,
)

statusline_cmd = PYTHON_BIN + " " + SCRIPTS_REF + "/statusline.py"
current_status = settings.get("statusLine")
if not (isinstance(current_status, dict) and "statusline.py" in str(current_status.get("command", ""))):
    settings["statusLine"] = {
        "type": "command",
        "command": statusline_cmd,
        "padding": 1,
        "refreshInterval": 30,
    }

with open(settings_path, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=2)

print("[OK] Wired hooks and statusline into", settings_path)
EOF

echo ""
echo "✅ jugaad-code installed successfully!"
echo ""
echo "Commands available in Claude Code:"
echo "  /doctor     — Full health check"
echo "  /pk on      — Activate Pakistan Mode"
echo "  /pk off     — Deactivate Pakistan Mode"
echo "  /pk status  — Show status"
echo "  /checkpoint — Emergency commit"
echo ""
echo "Theek hai. Kaam shuru karo."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
