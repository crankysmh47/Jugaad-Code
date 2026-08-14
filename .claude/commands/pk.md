---
description: Toggle Pakistan Mode — resilience layer for Pakistani dev conditions
model: claude-sonnet-4-6
allowed-tools: Bash
---

Toggle Pakistan Mode on or off.

If argument is "on" or no argument provided:
1. Start the guardian daemon: `python scripts/guardian.py &`
2. Enable adaptive survival mode through the guardian: NORMAL / NETWORK DEGRADED / POWER UNSTABLE / CRITICAL.
3. Switch npm to Asian mirror: `python scripts/mirror_switch.py npm https://registry.npmmirror.com/`
4. Switch pip to Asian mirror: `python scripts/mirror_switch.py pip https://pypi.tuna.tsinghua.edu.cn/simple/`
5. Print:

```
🇵🇰 Pakistan Mode: ACTIVE
━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Guardian daemon started
✓ NPM → Asian mirror
✓ PIP → Asian mirror
✓ Auto-checkpoint: every 5 min
✓ Bijli detection: ON

Theek hai. Kaam karo.
━━━━━━━━━━━━━━━━━━━━━━━━━
```

If argument is "off":
1. Kill guardian: `pkill -f guardian.py` (or taskkill on Windows)
2. Reset npm: `python scripts/mirror_switch.py npm https://registry.npmjs.org/`
3. Reset pip: `python scripts/mirror_switch.py pip https://pypi.org/simple/`
4. Print: `Pakistan Mode: OFF. Default settings restored.`
