# jugaad-code

### Claude Code, raised in Pakistan.

> "Pakistani devs don't have DevOps teams.
> They ARE the DevOps team. On a hotspot. During load-shedding.
> jugaad-code handles the infrastructure chaos so you can just write code."

---

## The Problem

Pakistani developers lose hours every day to:

- **Bijli** — sudden power cuts killing unsaved work
- **Internet** — submarine cable faults causing mysterious install failures
- **ISP routing** — spending 30 mins debugging code that was never broken
- **No feedback** — cryptic errors with no Pakistani context

---

## The Solution

jugaad-code is a resilience layer for Claude Code that:

| Feature | What it does |
|--------|-------------|
| Bijli Detection | Detects AC power loss, auto-commits immediately |
| Net Diagnosis | Diagnoses DNS/TCP/TTFB per endpoint, classifies root cause |
| ISP Awareness | Knows your ISP's quirks (PTCL, StormFiber, Nayatel, Jazz, Zong...) |
| Mirror Switch | Auto-switches npm/pip to the fastest Asian mirror on degradation |
| Auto-checkpoint | Silent git commits every 5 min when working |
| Survival Mode | Adapts behavior across NORMAL, NETWORK DEGRADED, POWER UNSTABLE, and CRITICAL states |
| PK Errors | Translates ECONNREFUSED into something a human can act on |
| PK Theme | Green/white terminal theme for Claude Code while Pakistan Mode is on |
| Desi Statusline | Survival state + rotating Roman Urdu messages in the status bar |
| Hook Flavor | A desi line and a "jugaadi soch raha hai..." spinner before each tool call |

---

## Adaptive Survival Mode

The four operational states:

```
NORMAL
  ↓
NETWORK DEGRADED
  ↓
POWER UNSTABLE
  ↓
CRITICAL
```

- **NORMAL**: Full operation without restrictions.
- **NETWORK DEGRADED**: Cache preference, avoid large downloads, retry transient network operations, switch npm/pip to Asian mirrors.
- **POWER UNSTABLE**: Trigger workspace checkpoint upon AC power loss, warn before long builds, encourage push when connection is stable.
- **CRITICAL**: Low battery + degraded network → workspace protection, finish current edit, immediate checkpoint.

---

## Install

### Windows (PowerShell):
```powershell
git clone https://github.com/crankysmh47/Jugaad-Code
cd Jugaad-Code
.\install.ps1
```

The installer copies the slash commands and hooks to `~/.claude/`, sets the
`JUGAAD_CODE_SCRIPTS` environment variable, and merges the hook + statusline
config into `~/.claude/settings.json` (existing keys are preserved).

### Linux / macOS / WSL:
```bash
git clone https://github.com/crankysmh47/Jugaad-Code
cd Jugaad-Code
bash install.sh
```

The installer copies the slash commands and hooks to `~/.claude/`, adds
`JUGAAD_CODE_SCRIPTS` to your shell rc file, and merges the hook +
statusline config into `~/.claude/settings.json` (existing keys are
preserved).

---

## Usage

In Claude Code:

```bash
/doctor          # Full health check — power, internet, ISP, survival mode
/pk on           # Activate Pakistan Mode (guardian + mirrors + green theme)
/pk off          # Deactivate
/pk status       # Guardian, survival state, theme and mirror status
/checkpoint      # Emergency commit right now
```

### The PK theme

`/pk on` switches Claude Code to a green/white theme (user-level, so it applies
to all projects) via `scripts/theme_switch.py`. `/pk off` restores whatever
theme you had before. The change reloads live; if the `~/.claude/themes`
folder is created for the first time, restart Claude Code once so the theme
files are picked up.

### Thinking messages

Claude Code's built-in thinking text is not customizable (no setting or hook
exists for it). jugaad-code substitutes the closest supported things:

- the hook spinner text becomes "jugaad soch raha hai..." while the pre-tool
  hook runs (`statusMessage`)
- a rotating Roman Urdu line is printed before each tool call
- the statusline shows the survival state and a rotating desi message

---

## Sample `/doctor` Output

```
══════════════════════════════════════
  jugaad-code Developer Health Report
══════════════════════════════════════
POWER
Status   : On Battery/UPS
Battery  : 34%
Remaining: 52 minutes

SURVIVAL MODE : POWER_UNSTABLE
Protections   : protect_workspace, warn_before_long_operations

INTERNET
GitHub        : SLOW [3800ms]
NPM Registry  : OK [180ms]
Claude API    : OK [210ms]
PyPI          : OK [95ms]

ISP
Detected : PTCL
City     : Karachi
Issues   : GitHub slow after 9pm PKT, Docker Hub inconsistent

DIAGNOSIS
SUBMARINE_CABLE

RECOMMENDATION
Likely SMW4/AAE-1 congestion. Use Asian mirrors.

ACTIONS TAKEN
npm and pip switched to Asian mirrors

Bhai, bijli kam hai aur cable slow hai.
Kaam karo lekin push kar do pehle.
══════════════════════════════════════
```

---

## Architecture & Structure

```
jugaad-code/
├── README.md
├── install.ps1                 # one-command installer (Windows)
├── install.sh                  # one-command installer (Linux / macOS / WSL)
├── plan.md                     # build plan + status
├── .claude/
│   ├── settings.json           # hooks + statusline wiring
│   ├── commands/               # /doctor, /pk, /checkpoint
│   └── hooks/                  # pre_tool_call.sh, post_tool_call.sh
├── scripts/
│   ├── power_check.py          # detects AC vs battery/UPS (WMI + psutil)
│   ├── net_check.py            # diagnoses connectivity layers (DNS, TCP, TTFB)
│   ├── mirror_switch.py        # switches npm/pip to the fastest mirror
│   ├── isp_detect.py           # fingerprints ISP from IP & maps quirks
│   ├── guardian.py             # background watcher daemon (pidfile + state cache)
│   ├── survival_mode.py        # adaptive NORMAL / NETWORK / POWER / CRITICAL engine
│   ├── theme_switch.py         # green/white PK theme on/off (user-level)
│   ├── statusline.py           # Claude Code statusline (state + desi message)
│   ├── cache_reader.py         # fast state reader for hooks
│   └── demo.py                 # interactive demo of all components
└── ui/
    ├── messages.py             # rotating Roman Urdu dev messages
    └── errors.py               # pakistan-aware error translations
```

The guardian writes its pidfile, log and state cache to `~/.jugaad-code/`.
Hooks and the statusline read that cache, so they stay fast and never stall a
tool call on a network probe.

---

## Built for Pakistan. Ready for the world.

Same infrastructure chaos exists in India, Bangladesh, Nigeria, Egypt,
Indonesia. jugaad-code is the proving ground. The product scales globally.

Theek hai.
