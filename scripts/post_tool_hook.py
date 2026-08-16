# scripts/post_tool_hook.py
"""
Post-tool execution hook for Claude Code (Cross-platform Python).
Translates known network and packaging errors into plain Roman Urdu.

Claude Code delivers hook input as JSON on stdin (fields like tool_name,
tool_input and tool_response). Fall back to argv for manual runs.
"""
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(SCRIPT_DIR))

try:
    from ui.errors import translate_error
except ImportError:
    def translate_error(t):
        return None


def _extract_text(payload):
    """Pull searchable text out of a Claude Code hook payload."""
    parts = []

    def flatten(value):
        if isinstance(value, dict):
            for v in value.values():
                flatten(v)
        elif isinstance(value, list):
            for v in value:
                flatten(v)
        elif isinstance(value, str):
            parts.append(value)

    flatten(payload)
    return "\n".join(parts)


def read_hook_input():
    """Read and parse the hook JSON from stdin; return a dict or None."""
    try:
        raw = sys.stdin.read()
    except Exception:
        raw = ""
    if not raw.strip():
        return None
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def main():
    payload = read_hook_input()
    if payload is not None:
        output_text = _extract_text(payload)
    else:
        # Manual invocation fallback: treat argv as the output text
        output_text = " ".join(sys.argv[1:])

    if not output_text.strip():
        return

    translated = translate_error(output_text)
    if translated:
        print(f"\n{translated}")


if __name__ == "__main__":
    main()
