---
description: Toggle Pakistan Mode — resilience layer for Pakistani dev conditions
model: claude-sonnet-4-6
allowed-tools: Bash, PowerShell
---

Toggle Pakistan Mode on or off.

First resolve the scripts directory `<SCRIPTS>`: use `$env:JUGAAD_CODE_SCRIPTS`
(PowerShell) or `$JUGAAD_CODE_SCRIPTS` (bash) if set; otherwise
`~/.jugaad-code/scripts`; otherwise the repo's local `scripts/` folder.

If argument is "on" or no argument provided:
1. Start the guardian if it isn't already running:
   `python <SCRIPTS>/guardian_boot.py` — it is idempotent (checks
   `~/.jugaad-code/guardian.pid` and exits if the daemon is already alive) and
   spawns a detached daemon that survives the session. Do NOT run guardian.py
   directly — it runs forever in the foreground.
2. Apply the green/white Jugaadi PK theme (all projects, user-level): `python <SCRIPTS>/theme_switch.py on`.
3. Switch npm to Asian mirror: `python <SCRIPTS>/mirror_switch.py npm https://registry.npmmirror.com/`
4. Switch pip to Asian mirror: `python <SCRIPTS>/mirror_switch.py pip https://pypi.tuna.tsinghua.edu.cn/simple/`
5. Print:

```
Pakistan Mode: ACTIVE
━━━━━━━━━━━━━━━━━━━━━━━━━
Guardian daemon running
NPM -> Asian mirror
PIP -> Asian mirror
Theme -> green/white (Jugaad PK)
Auto-checkpoint: every 5 min
Bijli detection: ON

Theek hai. Kaam karo.
━━━━━━━━━━━━━━━━━━━━━━━━━
```

Note: the theme writes to your user settings and applies to all projects.
Custom themes cannot be set via /config (built-in themes only). To switch
colors instantly, type /theme and pick "Pakistan Green" — it applies
immediately. Otherwise the change applies on the next restart.

If argument is "off":
1. Kill the guardian using its pidfile: read `~/.jugaad-code/guardian.pid` and stop that process (Windows: `taskkill /F /PID <pid>`, otherwise `kill <pid>`).
2. Restore the previous theme: `python <SCRIPTS>/theme_switch.py off`
3. Reset npm and pip registries to whatever they were before Pakistan Mode
   switched them (falls back to the official registries):
   `python <SCRIPTS>/mirror_switch.py reset all`
4. Print: `Pakistan Mode: OFF. Default settings restored.`

If argument is "status":
- Guardian running? (pidfile exists and the process is alive)
- Current survival state from `~/.jugaad-code/state.json` if fresh (< 90s)
- Theme active? (user settings `theme` equals `custom:pk`)
- Current npm registry and pip index-url
