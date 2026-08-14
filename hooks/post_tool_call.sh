#!/bin/bash
# hooks/post_tool_call.sh
# Fires after every tool call — translates errors to PK-aware messages

TOOL_NAME=$1
EXIT_CODE=$2
OUTPUT=$3

SCRIPT_DIR="${JUGAADI_CLAUDE_SCRIPTS:-$(cd "$(dirname "$0")/../scripts" && pwd)}"

# Determine python command (python3 or python)
if command -v python3 &>/dev/null; then
    PY="python3"
else
    PY="python"
fi

# If a bash tool failed, diagnose why
if [[ "$TOOL_NAME" == "Bash" || "$TOOL_NAME" == "bash" ]] && [[ "$EXIT_CODE" != "0" ]]; then
    # Check if it looks network related
    if echo "$OUTPUT" | grep -qiE "timeout|ECONNREFUSED|ENOTFOUND|network|npm ERR|pip.*error"; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🇵🇰 [jugaadi-claude] Yeh aapka code nahi hai."
        echo "   Network issue lag raha hai. Diagnose kar raha hoon..."
        
        DIAG=$($PY "$SCRIPT_DIR/net_check.py" 2>/dev/null | \
            $PY -c "import sys,json; d=json.load(sys.stdin); print(d.get('diagnosis','UNKNOWN'))" 2>/dev/null)
        REC=$($PY "$SCRIPT_DIR/net_check.py" 2>/dev/null | \
            $PY -c "import sys,json; d=json.load(sys.stdin); print(d.get('recommendation','Check network.'))" 2>/dev/null)
        
        echo "   Diagnosis: $DIAG"
        echo "   → $REC"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    fi
fi

exit 0
