#!/bin/bash
# .claude/hooks/pre_tool_call.sh
TOOL_NAME=$1
SCRIPT_DIR="${JUGAADI_CLAUDE_SCRIPTS:-$(cd "$(dirname "$0")/../../scripts" && pwd)}"

if command -v python3 &>/dev/null; then
    PY="python3"
else
    PY="python"
fi

if [[ "$TOOL_NAME" == "Bash" || "$TOOL_NAME" == "bash" ]]; then
    POWER=$($PY "$SCRIPT_DIR/power_check.py" 2>/dev/null)
    ON_AC=$(echo "$POWER" | $PY -c "import sys,json; d=json.load(sys.stdin); print(d.get('on_ac','true'))" 2>/dev/null)
    PCT=$(echo "$POWER" | $PY -c "import sys,json; d=json.load(sys.stdin); print(d.get('battery_percent',100))" 2>/dev/null)

    SURVIVAL=$($PY "$SCRIPT_DIR/survival_mode.py" --json 2>/dev/null || echo '{}')
    STATE=$(echo "$SURVIVAL" | $PY -c "import sys,json; d=json.load(sys.stdin); print(d.get('state','NORMAL'))" 2>/dev/null)

    if [[ "$STATE" == "CRITICAL" ]]; then
        echo "🚨 [jugaadi-claude] CRITICAL mode: protect workspace before long operations."
    elif [[ "$STATE" == "POWER_UNSTABLE" ]]; then
        echo "⚡ [jugaadi-claude] Power unstable: workspace protection active."
    elif [[ "$STATE" == "NETWORK_DEGRADED" ]]; then
        echo "🌐 [jugaadi-claude] Network degraded: resilience behavior active."
    fi

    if [[ "$ON_AC" == "False" && "$PCT" -lt 20 ]]; then
        echo "⚠️  [jugaadi-claude] Battery at ${PCT}%. Bijli nahi hai. Auto-checkpoint triggered."
        cd "${CLAUDE_PROJECT_DIR:-$(pwd)}" && \
            git add -A 2>/dev/null && \
            git commit -m "chore: [PK-checkpoint] low-battery @ $(date '+%H:%M')" 2>/dev/null
    fi
fi

exit 0
