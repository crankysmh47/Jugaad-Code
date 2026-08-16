# ui/errors.py
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ERROR_MAP = {
    "ECONNREFUSED": {
        "en": "Connection refused",
        "pk": "Server ne mana kar diya. Check karo service chal rahi hai ya nahi."
    },
    "ENOTFOUND": {
        "en": "DNS not found",
        "pk": "Domain nahi mila. DNS theek hai? 1.1.1.1 try karo."
    },
    "ETIMEDOUT": {
        "en": "Connection timed out",
        "pk": "Time out ho gaya. Submarine cable issue ho sakta hai. /doctor chalao."
    },
    "timeout": {
        "en": "Operation timed out",
        "pk": "Time out ho gaya. Submarine cable issue ho sakta hai. /doctor chalao."
    },
    "npm ERR! code E404": {
        "en": "Package not found",
        "pk": "Package nahi mila. Naam theek likha hai? ya mirror pe nahi hai."
    },
    "npm ERR! network": {
        "en": "NPM network error",
        "pk": "NPM ka network kharab hai. /pk on karo — Asian mirror pe switch kar deta hoon."
    },
    "pip._internal.exceptions": {
        "en": "pip install failed",
        "pk": "pip install fail hua. Mirror switch karo: /pk on"
    },
    "Permission denied": {
        "en": "Permission denied",
        "pk": "Permission nahi hai. sudo lagao ya admin se poocho."
    },
    "git: command not found": {
        "en": "git not installed",
        "pk": "Git install nahi hai. pehle git install karo bhai."
    }
}

def translate_error(error_text):
    for key, val in ERROR_MAP.items():
        if key.lower() in error_text.lower():
            return f"[jugaad-code] {val['pk']}"
    return None

if __name__ == "__main__":
    error = " ".join(sys.argv[1:])
    result = translate_error(error)
    if result:
        print(result)
        sys.exit(0)
    # No known pattern: stay silent so callers (hooks) can stay quiet too
    sys.exit(1)
