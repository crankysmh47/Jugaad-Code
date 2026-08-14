# jugaadi-claude 🇵🇰
### Claude Code, raised in Pakistan.

> "Pakistani devs don't have DevOps teams.  
> They ARE the DevOps team. On a hotspot. During load-shedding.  
> jugaadi-claude handles the infrastructure chaos so you can just write code."

---

## The Problem

Pakistani developers lose hours every day to:
- **Bijli** — sudden power cuts killing unsaved work
- **Internet** — submarine cable faults causing mysterious install failures  
- **ISP routing** — spending 30 mins debugging code that was never broken
- **No feedback** — cryptic errors with no Pakistani context

---

## The Solution

jugaadi-claude is a silent resilience layer for Claude Code that:

| Feature | What it does |
|--------|-------------|
| ⚡ **Bijli Detection** | Detects AC power loss, auto-commits immediately |
| 🌐 **Net Diagnosis** | Diagnoses DNS/TCP/TTFB per endpoint, classifies root cause |
| 📡 **ISP Awareness** | Knows your ISP's quirks (PTCL, StormFiber, Nayatel, Jazz, Zong...) |
| 🔄 **Mirror Switch** | Auto-switches npm/pip to fastest Asian mirror on degradation |
| 💾 **Auto-checkpoint** | Silent git commits every 5 min when working |
| 🛡️ **Survival Mode** | Adapts behavior across NORMAL, NETWORK DEGRADED, POWER UNSTABLE, and CRITICAL states |
| 💬 **PK Errors** | Translates ECONNREFUSED into something a human can act on |

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

### Linux / macOS / WSL:
```bash
git clone https://github.com/yourhandle/jugaadi-claude
cd jugaadi-claude
bash install.sh
```

### Windows (PowerShell):
```powershell
git clone https://github.com/yourhandle/jugaadi-claude
cd jugaadi-claude
.\install.ps1
```

---

## Usage

In Claude Code:

```bash
/doctor          # Full health check — power, internet, ISP, survival mode
/pk on           # Activate Pakistan Mode
/pk off          # Deactivate
/checkpoint      # Emergency commit right now
```

---

## Sample `/doctor` Output

```
══════════════════════════════════════
  🇵🇰 jugaadi-claude Developer Health Report
══════════════════════════════════════
⚡ POWER        : On Battery — 34% — ~52 mins
🛡️ SURVIVAL    : POWER_UNSTABLE — workspace protection active
🌐 GitHub       : ✗ SLOW (3800ms TTFB)
🌐 NPM Registry : ✓ OK (180ms)
🌐 Claude API   : ✓ OK (210ms)
📡 ISP          : PTCL, Karachi
🩺 DIAGNOSIS    : SUBMARINE_CABLE
💊 FIX          : npm switched to Asian mirror
⚙️  COMMITTED   : 3 files (WIP auto-checkpoint)

Bhai, bijli kam hai aur cable slow hai.
Kaam karo lekin push kar do pehle.
══════════════════════════════════════
```

---

## Architecture & Structure

```
jugaadi-claude/
├── README.md
├── install.sh                  # one-command installer (Bash)
├── install.ps1                 # one-command installer (PowerShell)
├── scripts/
│   ├── power_check.py          # detects AC vs battery/UPS (WMI + psutil)
│   ├── net_check.py            # diagnoses connectivity layers (DNS, TCP, TTFB)
│   ├── mirror_switch.py        # switches npm/pip to fastest mirror
│   ├── isp_detect.py           # fingerprints ISP from IP & maps quirks
│   ├── guardian.py             # background watcher daemon
│   └── survival_mode.py        # adaptive NORMAL / NETWORK / POWER / CRITICAL state engine
├── hooks/
│   ├── pre_tool_call.sh        # claude code hook: before every tool
│   └── post_tool_call.sh       # claude code hook: after every tool
├── commands/
│   ├── doctor.md               # /doctor slash command
│   ├── pk.md                   # /pk slash command
│   └── checkpoint.md           # /checkpoint slash command
└── ui/
    ├── messages.py             # rotating status bar messages
    └── errors.py               # pakistan-aware error translations
```

---

## Built for Pakistan. Ready for the world.

Same infrastructure chaos exists in India, Bangladesh, Nigeria, Egypt, Indonesia. jugaadi-claude is the proving ground. The product scales globally.

Theek hai.
