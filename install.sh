#!/bin/bash
# install.sh — one command setup

set -e

echo "🇵🇰 Installing jugaadi-claude — Pakistan Resilience Layer for Claude Code"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Python
if command -v python3 &> /dev/null; then
    PY="python3"
elif command -v python &> /dev/null; then
    PY="python"
else
    echo "❌ Python not found. Install it first."
    exit 1
fi

# Install Python deps
$PY -m pip install psutil --quiet || true

# Create Claude Code commands directory
CLAUDE_DIR="$HOME/.claude/commands"
mkdir -p "$CLAUDE_DIR"

# Copy slash commands
cp commands/doctor.md "$CLAUDE_DIR/doctor.md"
cp commands/pk.md "$CLAUDE_DIR/pk.md"
cp commands/checkpoint.md "$CLAUDE_DIR/checkpoint.md"

# Create Claude Code hooks directory
HOOKS_DIR="$HOME/.claude/hooks"
mkdir -p "$HOOKS_DIR"

# Copy hooks
cp hooks/pre_tool_call.sh "$HOOKS_DIR/pre_tool_call.sh"
cp hooks/post_tool_call.sh "$HOOKS_DIR/post_tool_call.sh"
chmod +x "$HOOKS_DIR/"*.sh 2>/dev/null || true

# Store scripts path in env
SCRIPT_DIR="$(pwd)/scripts"
if [ -f "$HOME/.bashrc" ]; then
    echo "export JUGAADI_CLAUDE_SCRIPTS=\"$SCRIPT_DIR\"" >> "$HOME/.bashrc"
fi
if [ -f "$HOME/.zshrc" ]; then
    echo "export JUGAADI_CLAUDE_SCRIPTS=\"$SCRIPT_DIR\"" >> "$HOME/.zshrc"
fi

echo ""
echo "✅ jugaadi-claude installed successfully!"
echo ""
echo "Commands available in Claude Code:"
echo "  /doctor     — Full health check"
echo "  /pk on      — Activate Pakistan Mode"  
echo "  /pk off     — Deactivate Pakistan Mode"
echo "  /checkpoint — Emergency commit"
echo ""
echo "Theek hai. Kaam shuru karo."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
