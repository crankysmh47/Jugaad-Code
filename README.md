# jugaad-code

### Claude Code, raised in Pakistan.

> "Pakistani devs don't have DevOps teams.
> They ARE the DevOps team. On a hotspot. During load-shedding.
> jugaad-code handles the infrastructure chaos so you can just write code."

jugaad-code is a resilience layer for Claude Code built for Pakistani
developer conditions: power cuts, submarine cable faults, flaky ISP
routing, and cryptic error messages. It watches the environment, adapts
your tooling automatically, and protects your work — so you can write
code instead of fighting infrastructure.

---

## Features

| Feature | What it does |
|--------|-------------|
| Bijli Detection | Detects AC vs battery/UPS on Windows (WMI) and Linux/macOS (psutil). The guardian takes an emergency git checkpoint the moment power drops, and the pre-tool hook auto-commits when battery falls under 20% |
| Auto-checkpoint | Silent `[PK-auto]` git commits every 5 minutes while the working tree is dirty |
| Net Diagnosis | Layered DNS → TCP → TTFB checks per endpoint (GitHub, npm, PyPI, Claude API). DNS resolvers (1.1.1.1, 8.8.8.8) are probed with real UDP 53 DNS queries, not fake TCP checks. Classifies the root cause as LOCAL_NETWORK, SUBMARINE_CABLE, or ISP_ROUTING |
| ISP Awareness | Fingerprints your ISP from your public IP and maps known quirks: PTCL, StormFiber, Nayatel, Jazz, Zong, Transworld — each with known issues and recommended mirrors/DNS |
| Mirror Switch | Auto-switches npm → npmmirror and pip → Tsinghua TUNA the moment international routing degrades — and restores whatever registries you had before (official or custom) once the route recovers |
| Guardian Daemon | Background watcher (60s cycles): power checks, auto-checkpoints, network diagnosis, mirror switching, and survival-state tracking. Single-instance, writes its pidfile, log and state cache to `~/.jugaad-code/` |
| Detached Boot | `guardian_boot.py` spawns the guardian as a detached process that survives session exits, and a SessionStart hook auto-boots it every time Claude Code starts — no OS-level startup script needed |
| Survival Mode | Adaptive behavior across four states: NORMAL, NETWORK DEGRADED, POWER UNSTABLE, CRITICAL (details below) |
| PK Theme | A custom "Pakistan Green" Claude Code theme installed at user level, so every project turns green while Pakistan Mode is on. `/pk off` restores whatever theme you had before |
| Desi Statusline | The Claude Code statusline shows `[PK: STATE]` plus a rotating Roman Urdu dev message, fed by the guardian's state cache |
| Hook Flavor | A `jugaad soch raha hai...` spinner replaces the status text while the pre-tool hook runs, and a rotating Roman Urdu line is printed before each shell tool call |
| PK Error Translation | Known errors (`ECONNREFUSED`, `ETIMEDOUT`, npm/pip network failures, DNS misses...) are translated into plain Roman Urdu with an actionable fix |
| Slash Commands | `/doctor` full health check, `/pk on|off|status`, `/checkpoint` emergency commit |

---

## Adaptive Survival Mode

The resilience layer changes how the environment behaves based on
infrastructure state:

```
NORMAL
  ↓
NETWORK DEGRADED
  ↓
POWER UNSTABLE
  ↓
CRITICAL
```

- **NORMAL** — no restrictions.
- **NETWORK DEGRADED** — prefer package caches, avoid large downloads, retry
  transient network commands, switch npm/pip to Asian mirrors, warn before
  expensive network operations.
- **POWER UNSTABLE** — workspace checkpoint on AC loss, warn before long
  builds/downloads, encourage pushing while connectivity is healthy.
- **CRITICAL** — battery under 15% with degraded network: finish the current
  edit, checkpoint now, push when the connection recovers (the guardian
  suggests it — the push itself is manual).

---

## Install

### Windows (PowerShell)

```powershell
git clone https://github.com/crankysmh47/Jugaad-Code
cd Jugaad-Code
.\install.ps1
```

The installer:

- copies `scripts/` and `ui/` to `~/.jugaad-code/`
- copies the slash commands to `~/.claude/commands/`
- sets the `JUGAAD_CODE_SCRIPTS` and `JUGAADI_CLAUDE_SCRIPTS` environment
  variables
- wires the SessionStart guardian boot, the hooks (with the
  `jugaad soch raha hai...` spinner) and the statusline into
  `~/.claude/settings.json` — merging with any existing keys instead of
  overwriting them, and backing up the file first if it isn't valid JSON

### Linux / macOS / WSL

```bash
git clone https://github.com/crankysmh47/Jugaad-Code
cd Jugaad-Code
bash install.sh
```

Same behavior: app files under `~/.jugaad-code/`, commands under
`~/.claude/commands/`, environment variables in your shell rc file, hooks
and statusline wired into `~/.claude/settings.json`.

---

## Usage

In Claude Code:

```bash
/doctor          # Full health check — power, internet, ISP, survival mode
/pk on           # Activate Pakistan Mode (guardian + mirrors + green theme)
/pk off          # Deactivate and restore defaults
/pk status       # Guardian, survival state, theme and mirror status
/checkpoint      # Emergency commit right now
```

### `/pk on` — what happens

1. Boots the guardian daemon if it isn't running (detached, survives sessions)
2. Switches npm → `https://registry.npmmirror.com/`
3. Switches pip → `https://pypi.tuna.tsinghua.edu.cn/simple/`
4. Applies the Pakistan Green theme (user-level, all projects)

### `/pk off` — what happens

1. Kills the guardian via its pidfile
2. Restores your previous theme (or removes the theme key so Claude Code
   falls back to its default colors)
3. Resets npm and pip to their official registries

### The PK theme

The theme lives at `~/.claude/themes/pk.json` ("Pakistan Green" — dark
base with green accents) and is activated by setting `theme: "custom:pk"`
in `~/.claude/settings.json`. Notes:

- Custom themes cannot be set via `/config` (built-in themes only). To
  switch colors instantly, type `/theme` and pick "Pakistan Green".
- Otherwise theme changes apply on the next Claude Code restart.
- `/pk off` restores the exact theme you had before turning pk on.

### Thinking messages — an honest note

Claude Code's built-in thinking text ("Thinking…") is hardcoded and cannot
be changed by any setting or hook. jugaad-code substitutes the closest
supported things:

- the hook spinner becomes `jugaad soch raha hai...` while the pre-tool
  hook runs (`statusMessage`)
- a rotating Roman Urdu line is printed before each tool call
- the statusline permanently shows the survival state plus a desi message

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

## How it fits together

```
SessionStart hook ──► guardian_boot.py ──► guardian.py (detached daemon)
                                                 │ 60s cycle
                                                 ├─ power check (bijli) ──► emergency checkpoint
                                                 ├─ auto-checkpoint every 5 min if dirty
                                                 ├─ net_check every 5 cycles ──► auto mirror switch
                                                 │    └─ auto-restore registries when net recovers
                                                 └─ writes ~/.jugaad-code/state.json

PreToolUse hook ──► pre_tool_hook.py   (state warnings, low-battery
                  │                     checkpoint, desi flavor line)
PostToolUse hook ─► post_tool_hook.py  (Roman Urdu error translations)
statusLine ───────► statusline.py      ([PK: STATE] + rotating message,
                                         reads the same state cache)
```

The guardian writes its pidfile, log, and state cache to `~/.jugaad-code/`.
Git checkpoints target the project it was spawned from
(`CLAUDE_PROJECT_DIR` at boot), so it never commits to the wrong repo.
Hooks and the statusline read that cache (freshness window of ~2 minutes)
instead of running network probes on every tool call, so they never stall
your work.

---

## Project Structure

```
jugaad-code/
├── README.md
├── install.ps1                 # one-command installer (Windows)
├── install.sh                  # one-command installer (Linux / macOS / WSL)
├── .claude/
│   ├── settings.json           # SessionStart + Pre/PostToolUse + statusline wiring
│   ├── commands/               # /doctor, /pk, /checkpoint
│   └── hooks/                  # pre_tool_call.sh, post_tool_call.sh (shell variants)
├── scripts/
│   ├── power_check.py          # AC vs battery/UPS detection (WMI + psutil)
│   ├── net_check.py            # layered DNS/TCP/TTFB diagnosis + DNS resolver probes
│   ├── mirror_switch.py        # npm/pip mirror switching
│   ├── isp_detect.py           # ISP fingerprinting + Pakistani ISP quirks
│   ├── guardian.py             # background watcher daemon (pidfile + state cache)
│   ├── guardian_boot.py        # detached, idempotent guardian starter
│   ├── survival_mode.py        # NORMAL / NETWORK / POWER / CRITICAL state engine
│   ├── theme_switch.py         # Pakistan Green theme on/off (user-level)
│   ├── statusline.py           # statusline: survival state + desi message
│   ├── cache_reader.py         # fast cached state reader for hooks and statusline
│   ├── pre_tool_hook.py        # python pre-tool hook (state + battery + flavor)
│   ├── post_tool_hook.py       # python post-tool hook (error translation)
│   └── demo.py                 # interactive demo of all components
└── ui/
    ├── messages.py             # rotating Roman Urdu dev messages
    └── errors.py               # pakistan-aware error translations
```

---

## License

jugaad-code is released under the [Noncommercial Source License v1.0](LICENSE).

- **Non-commercial use** — personal, hobby, educational, academic,
  research, and non-profit use: free, including free redistribution.
- **Commercial use** — use by a business or any revenue-generating
  organization (even internally), or any use that generates revenue,
  requires **prior written permission** from the author, with fair
  compensation for the author (a license fee or a share of revenue).
  Contact [crankysmh47](mailto:annankhan741@gmail.com) for a commercial
  license.

The license text is generic — reuse it in other projects by updating the
copyright line in `LICENSE` to your name and year.

---

## Built for Pakistan. Ready for the world.

The same infrastructure chaos exists in India, Bangladesh, Nigeria, Egypt,
and Indonesia. jugaad-code is the proving ground — the resilience layer
scales anywhere the network and the power grid fight back.

Theek hai.
