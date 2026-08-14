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
if [ -d ".claude/hooks" ]; then
    cp .claude/hooks/* "$CLAUDE_HOOKS_DIR/"
    chmod +x "$CLAUDE_HOOKS_DIR/"*.sh 2>/dev/null || true
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

# Wire hooks and statusline into settings.json
SETTINGS_FILE="$CLAUDE_DIR/settings.json"
$PY - << EOF
import json, os

settings_path = "$SETTINGS_FILE"
settings = {}
if os.path.exists(settings_path):
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    except Exception:
        settings = {}

settings["hooks"] = {
    "PreToolUse": [
        {
            "matcher": "Bash|PowerShell",
            "hooks": [
                {
                    "type": "command",
                    "command": "bash \"$HOME/.claude/hooks/pre_tool_call.sh\"",
                    "timeout": 15,
                    "statusMessage": "jugaad soch raha hai..."
                }
            ]
        }
    ],
    "PostToolUse": [
        {
            "matcher": "Bash|PowerShell",
            "hooks": [
                {
                    "type": "command",
                    "command": "bash \"$HOME/.claude/hooks/post_tool_call.sh\"",
                    "timeout": 15
                }
            ]
        }
    ]
}

settings["statusLine"] = {
    "type": "command",
    "command": 'python "\${JUGAAD_CODE_SCRIPTS}/statusline.py"',
    "padding": 1,
    "refreshInterval": 30
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
