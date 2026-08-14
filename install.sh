#!/bin/bash
# install.sh — one command setup (Linux / macOS / WSL)

set -e

echo "Installing jugaadi-claude — Pakistan Resilience Layer for Claude Code"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Python
if command -v python3 &> /dev/null; then
    PY="python3"
elif command -v python &> /dev/null; then
    PY="python"
else
    echo "Python not found. Install Python 3 first."
    exit 1
fi

# Install Python deps
$PY -m pip install psutil --quiet || true

# Copy slash commands and hooks (single source of truth: .claude/)
mkdir -p "$HOME/.claude/commands" "$HOME/.claude/hooks"
cp .claude/commands/doctor.md "$HOME/.claude/commands/doctor.md"
cp .claude/commands/pk.md "$HOME/.claude/commands/pk.md"
cp .claude/commands/checkpoint.md "$HOME/.claude/commands/checkpoint.md"
cp .claude/hooks/pre_tool_call.sh "$HOME/.claude/hooks/pre_tool_call.sh"
cp .claude/hooks/post_tool_call.sh "$HOME/.claude/hooks/post_tool_call.sh"
chmod +x "$HOME/.claude/hooks/"*.sh 2>/dev/null || true

# Store scripts path in shell rc files (idempotent)
SCRIPT_DIR="$(pwd)/scripts"
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$rc" ] && ! grep -q "JUGAADI_CLAUDE_SCRIPTS" "$rc"; then
        echo "export JUGAADI_CLAUDE_SCRIPTS=\"$SCRIPT_DIR\"" >> "$rc"
    fi
done

# Wire hooks and statusline into the user settings (preserving existing keys)
$PY - <<'PYEOF'
import json
import os

path = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")
try:
    with open(path, encoding="utf-8") as fh:
        settings = json.load(fh)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

settings["hooks"] = {
    "PreToolUse": [{"matcher": "Bash|PowerShell", "hooks": [{
        "type": "command",
        "command": 'bash "$HOME/.claude/hooks/pre_tool_call.sh"',
        "timeout": 15,
        "statusMessage": "jugaadi soch raha hai...",
    }]}],
    "PostToolUse": [{"matcher": "Bash|PowerShell", "hooks": [{
        "type": "command",
        "command": 'bash "$HOME/.claude/hooks/post_tool_call.sh"',
        "timeout": 15,
    }]}],
}
settings["statusLine"] = {
    "type": "command",
    "command": 'python "${JUGAADI_CLAUDE_SCRIPTS}/statusline.py"',
    "padding": 1,
    "refreshInterval": 30,
}

os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w", encoding="utf-8") as fh:
    json.dump(settings, fh, indent=2)
    fh.write("\n")
print(f"[OK] Hooks and statusline wired into {path}")
PYEOF

echo ""
echo "[OK] jugaadi-claude installed successfully!"
echo ""
echo "Commands available in Claude Code:"
echo "  /doctor     — Full health check"
echo "  /pk on      — Activate Pakistan Mode (green theme + guardian)"
echo "  /pk off     — Deactivate Pakistan Mode"
echo "  /pk status  — Show Pakistan Mode state"
echo "  /checkpoint — Emergency commit"
echo ""
echo "Theek hai. Kaam shuru karo."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
