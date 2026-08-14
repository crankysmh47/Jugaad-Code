---
description: Toggle Pakistan Mode — resilience layer for Pakistani dev conditions
model: claude-sonnet-4-6
allowed-tools: Bash, PowerShell
---

Toggle Pakistan Mode on or off.

If argument is "on" or no argument provided:
1. If the guardian is not already running (check `~/.jugaadi-claude/guardian.pid` exists and `~/.jugaadi-claude/state.json` is fresh), start it in the background: `python scripts/guardian.py`.
2. Apply the green/white Jugaadi PK theme (all projects, user-level): `python scripts/theme_switch.py on`.
3. Switch npm to Asian mirror: `python scripts/mirror_switch.py npm https://registry.npmmirror.com/`
4. Switch pip to Asian mirror: `python scripts/mirror_switch.py pip https://pypi.tuna.tsinghua.edu.cn/simple/`
5. Print:

```
Pakistan Mode: ACTIVE
━━━━━━━━━━━━━━━━━━━━━━━━━
Guardian daemon running
NPM -> Asian mirror
PIP -> Asian mirror
Theme -> green/white (Jugaadi PK)
Auto-checkpoint: every 5 min
Bijli detection: ON

Theek hai. Kaam karo.
━━━━━━━━━━━━━━━━━━━━━━━━━
```

Note: the theme applies to all projects and reloads live. If the
`~/.claude/themes` folder was just created for the first time, one
Claude Code restart is needed for theme files to be picked up.

If argument is "off":
1. Kill the guardian using its pidfile: read `~/.jugaadi-claude/guardian.pid` and stop that process (Windows: `taskkill /F /PID <pid>`, otherwise `kill <pid>`).
2. Restore the previous theme: `python scripts/theme_switch.py off`
3. Reset npm: `python scripts/mirror_switch.py npm https://registry.npmjs.org/`
4. Reset pip: `python scripts/mirror_switch.py pip https://pypi.org/simple/`
5. Print: `Pakistan Mode: OFF. Default settings restored.`

If argument is "status":
- Guardian running? (pidfile exists and the process is alive)
- Current survival state from `~/.jugaadi-claude/state.json` if fresh (< 90s)
- Theme active? (user settings `theme` equals `custom:jugaadi-pk`)
- Current npm registry and pip index-url
