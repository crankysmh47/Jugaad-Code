---
description: Full Pakistan-aware developer environment health check
model: claude-sonnet-4-6
allowed-tools: Bash, PowerShell
---

Run a full environment health check for Pakistani developer conditions.

Steps:
1. Run `python scripts/power_check.py` and parse the JSON output.
2. Run `python scripts/isp_detect.py` and parse the JSON output.
3. Run `python scripts/net_check.py` and parse the JSON output.
4. Run `python scripts/survival_mode.py --json` to get current state and adaptive protections.
5. Based on results, produce a formatted report like this:

```
══════════════════════════════════════
  jugaadi-claude Developer Health Report
══════════════════════════════════════
POWER
Status   : [AC Connected / On Battery/UPS]
Battery  : [X]%
Remaining: [X] minutes

SURVIVAL MODE : [NORMAL / NETWORK DEGRADED / POWER UNSTABLE / CRITICAL]
Protections   : [Current adaptive protections]

INTERNET
GitHub        : [OK / SLOW / DOWN] [Xms]
NPM Registry  : [OK / SLOW / DOWN] [Xms]
Claude API    : [OK / SLOW / DOWN] [Xms]
PyPI          : [OK / SLOW / DOWN] [Xms]

ISP
Detected : [ISP Name]
City     : [City]
Issues   : [Known issues for this ISP]

DIAGNOSIS
[SUBMARINE_CABLE / ISP_ROUTING / LOCAL_NETWORK / ALL_OK]

RECOMMENDATION
[Specific actionable recommendation]

ACTIONS TAKEN
[List any mirrors switched, commits made, etc.]
══════════════════════════════════════
```

6. Automatically apply the recommended mirror switch if network is degraded.
7. If on battery under 20%, trigger a git checkpoint commit.
8. End with one line in Roman Urdu summarizing the situation.
