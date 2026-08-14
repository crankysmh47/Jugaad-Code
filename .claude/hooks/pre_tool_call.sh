#!/bin/bash
# .claude/hooks/pre_tool_call.sh
# Before every Bash/PowerShell tool call: warn on degraded states,
# auto-checkpoint on low battery, and drop one rotating desi line.
SCRIPT_DIR="${JUGAAD_CODE_SCRIPTS:-${JUGAADI_CLAUDE_SCRIPTS:-$(cd "$(dirname "$0")/../../scripts" && pwd)}}"

if command -v python3 &>/dev/null; then
    PY="python3"
else
    PY="python"
fi

# Cache-first state read; power-only fallback when the cache is stale.
# cache_reader.py prints JSON — flatten it to "STATE ON_AC PCT" here.
LINE=$("$PY" "$SCRIPT_DIR/cache_reader.py" 2>/dev/null | "$PY" -c "import json,sys; d=json.loads(sys.stdin.read()); p=d.get('power',{}); print(d.get('state','NONE'), str(p.get('on_ac',True)).lower(), p.get('battery_percent',100))" 2>/dev/null)
read -r STATE ON_AC PCT <<< "$LINE"
if [[ -z "$STATE" ]]; then
    STATE="NONE"; ON_AC="true"; PCT="100"
fi

if [[ "$STATE" == "CRITICAL" ]]; then
    echo "[jugaad-code] Critical state: checkpoint your work and avoid long operations."
elif [[ "$STATE" == "POWER_UNSTABLE" ]]; then
    echo "[jugaad-code] Power unstable: workspace protection active."
elif [[ "$STATE" == "NETWORK_DEGRADED" ]]; then
    echo "[jugaad-code] Network degraded: cache, mirrors and retries active."
fi

if [[ "$ON_AC" == "false" && "$PCT" -lt 20 ]]; then
    echo "[jugaad-code] Battery at ${PCT}%. Power is out. Taking an auto-checkpoint."
    cd "${CLAUDE_PROJECT_DIR:-$(pwd)}" && \
        git add -A 2>/dev/null && \
        git commit -m "chore: [PK-checkpoint] low-battery @ $(date '+%H:%M')" 2>/dev/null
fi

# Rotating desi flavor line while Claude works
"$PY" "$SCRIPT_DIR/../ui/messages.py" 2>/dev/null

exit 0
