// app.js — Minimal interactions for jugaad-code

document.addEventListener('DOMContentLoaded', () => {
  const cmdText = document.getElementById('cmdText');
  const copyBtn = document.getElementById('copyBtn');
  const tabBtns = document.querySelectorAll('.tab-btn');
  const terminalOutput = document.getElementById('terminalOutput');
  const tTabs = document.querySelectorAll('.t-tab');

  const COMMANDS = {
    win: 'irm https://raw.githubusercontent.com/yourhandle/jugaad-code/main/install.ps1 | iex',
    nix: 'curl -fsSL https://raw.githubusercontent.com/yourhandle/jugaad-code/main/install.sh | bash'
  };

  const TERMINAL_VIEWS = {
    doctor: `══════════════════════════════════════
  jugaad-code Developer Health Report
══════════════════════════════════════
POWER
Status   : AC Connected (Bijli mojood hai)
Battery  : 100%
Remaining: N/A

SURVIVAL MODE : NORMAL
Protections   : normal_operation, background_guardian_active

INTERNET
GitHub        : OK [118ms] (SMW4/AAE-1)
NPM Registry  : OK [182ms] (SMW4)
Claude API    : OK [210ms] (SMW4/AAE-1)
PyPI          : OK [145ms] (SMW4)

ISP
Detected : PTCL Broadband (Islamabad, Pakistan)
Quirks   : Heavy SMW4 dependence, GitHub slow after 9pm PKT

DIAGNOSIS
ALL_OK — Local gateway and international routes are healthy.

RECOMMENDATION
Submarine cables are clear. If package installs fail, check your code.

"Barkat hai, submarine cable theek hai aaj. Kaam karo."
══════════════════════════════════════`,

    pk: `Pakistan Mode: ACTIVE
━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Guardian daemon running in background (PID: 4920)
✓ NPM registry  → https://registry.npmmirror.com/
✓ PIP index     → https://pypi.tuna.tsinghua.edu.cn/simple/
✓ Theme         → Pakistan Green (Jugaad PK)
✓ Auto-checkpoint: every 5 min on dirty repo
✓ Bijli / Power loss detector: ON

Theek hai. Kaam karo.
━━━━━━━━━━━━━━━━━━━━━━━━━`,

    checkpoint: `[jugaad-code] Scanning workspace for uncommitted changes...
✓ Staged 3 files
✓ Committed: "chore: [PK-checkpoint] manual @ 2026-08-14 22:30"

Sab theek hai. Emergency checkpoint complete.`
  };

  // OS Tab Switch
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const os = btn.dataset.os;
      if (COMMANDS[os]) {
        cmdText.textContent = COMMANDS[os];
      }
    });
  });

  // Copy Install Command
  copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(cmdText.textContent).then(() => {
      copyBtn.textContent = 'Copied';
      setTimeout(() => {
        copyBtn.textContent = 'Copy';
      }, 1800);
    });
  });

  // Terminal Tab Switch
  tTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const view = tab.dataset.view;
      if (TERMINAL_VIEWS[view]) {
        terminalOutput.textContent = TERMINAL_VIEWS[view];
      }
    });
  });
});
