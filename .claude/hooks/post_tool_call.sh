#!/bin/bash
# .claude/hooks/post_tool_call.sh
# After a failed Bash/PowerShell tool call, translate known network
# and packaging errors into something a Pakistani dev can act on.
TOOL_NAME=$1
EXIT_CODE=$2
OUTPUT=$3

SCRIPT_DIR="${JUGAADI_CLAUDE_SCRIPTS:-$(cd "$(dirname "$0")/../../scripts" && pwd)}"

if command -v python3 &>/dev/null; then
    PY="python3"
else
    PY="python"
fi

case "$TOOL_NAME" in
    Bash|bash|PowerShell|powershell) ;;
    *) exit 0 ;;
esac

if [[ "$EXIT_CODE" != "0" ]]; then
    # errors.py prints a translated line only for known patterns and
    # stays silent otherwise
    TRANSLATED=$("$PY" "$SCRIPT_DIR/../ui/errors.py" "$OUTPUT" 2>/dev/null)
    if [[ -n "$TRANSLATED" ]]; then
        echo ""
        echo "$TRANSLATED"
    fi
fi

exit 0
