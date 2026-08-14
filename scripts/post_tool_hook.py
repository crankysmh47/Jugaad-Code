# scripts/post_tool_hook.py
"""
Post-tool execution hook for Claude Code (Cross-platform Python).
Translates known network and packaging errors into plain Roman Urdu.
"""
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

def main():
    if len(sys.argv) < 2:
        return

    # Check arguments / standard input
    output_text = " ".join(sys.argv[1:])
    translated = translate_error(output_text)
    if translated:
        print(f"\n{translated}")

if __name__ == "__main__":
    main()
