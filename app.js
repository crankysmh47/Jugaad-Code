// app.js — Interactive Terminal and UI Engine for jugaad-code

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const installCommand = document.getElementById('installCommand');
  const btnCopyInstall = document.getElementById('btnCopyInstall');
  const osTabs = document.querySelectorAll('.os-tab');
  const terminalScreen = document.getElementById('terminalScreen');
  const cmdButtons = document.querySelectorAll('.cmd-btn');
  const badgeStateText = document.getElementById('badgeStateText');
  const terminalStatusline = document.getElementById('terminalStatusline');

  // Simulator Buttons
  const simPowerCut = document.getElementById('simPowerCut');
  const simCableCongestion = document.getElementById('simCableCongestion');
  const simCritical = document.getElementById('simCritical');
  const simNormal = document.getElementById('simNormal');

  // Command Snippets
  const COMMANDS = {
    win: 'irm https://raw.githubusercontent.com/yourhandle/jugaad-code/main/install.ps1 | iex',
    nix: 'curl -fsSL https://raw.githubusercontent.com/yourhandle/jugaad-code/main/install.sh | bash'
  };

  // State
  let currentOS = 'win';
  let currentState = 'NORMAL';

  // OS Tab Switching
  osTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      osTabs.forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');

      currentOS = tab.dataset.os;
      installCommand.textContent = COMMANDS[currentOS];
    });
  });

  // Copy Install Command
  btnCopyInstall.addEventListener('click', () => {
    const textToCopy = installCommand.textContent;
    navigator.clipboard.writeText(textToCopy).then(() => {
      const copyText = btnCopyInstall.querySelector('.copy-text');
      const originalText = copyText.textContent;
      copyText.textContent = 'Copied! ✓';
      btnCopyInstall.style.background = 'var(--pk-green-mint)';
      btnCopyInstall.style.color = '#000';

      setTimeout(() => {
        copyText.textContent = originalText;
        btnCopyInstall.style.background = '';
        btnCopyInstall.style.color = '';
      }, 2200);
    });
  });

  // Terminal Output Templates
  const TERMINAL_OUTPUTS = {
    doctor: `\x3cspan style="color:#00E676;">$ claude\x3c/span>
> <span style="color:#FFFFFF; font-weight:bold;">/doctor</span>

<span style="color:#00E676;">══════════════════════════════════════════════════════</span>
  <span style="color:#FFFFFF; font-weight:bold;">🇵🇰 jugaad-code Developer Health Report</span>
<span style="color:#00E676;">══════════════════════════════════════════════════════</span>

⚡ <span style="color:#FFD600; font-weight:bold;">POWER</span>
Status   : <span style="color:#00E676;">AC Connected (Bijli mojood hai)</span>
Battery  : 100%
Remaining: N/A

🛡️ <span style="color:#00B4D8; font-weight:bold;">SURVIVAL MODE</span> : <span style="color:#00E676; font-weight:bold;">NORMAL</span>
Protections   : normal_operation, background_guardian_active

🌐 <span style="color:#00E676; font-weight:bold;">INTERNET & GATEWAYS</span>
GitHub        : <span style="color:#00E676;">✓ OK</span> (118ms) [SMW4/AAE-1]
NPM Registry  : <span style="color:#00E676;">✓ OK</span> (182ms) [SMW4]
Claude API    : <span style="color:#00E676;">✓ OK</span> (210ms) [SMW4/AAE-1]
PyPI          : <span style="color:#00E676;">✓ OK</span> (145ms) [SMW4]

📡 <span style="color:#FFD600; font-weight:bold;">ISP DETECTED</span>
Provider : <span style="color:#FFFFFF; font-weight:bold;">PTCL Broadband</span> (Islamabad, Pakistan)
Quirks   : Heavy SMW4 dependence, GitHub slow after 9pm PKT

🩺 <span style="color:#00E676; font-weight:bold;">DIAGNOSIS</span>
<span style="color:#00E676; font-weight:bold;">ALL_OK</span> — Local gateway & international routes look healthy.

💊 <span style="color:#00B4D8; font-weight:bold;">RECOMMENDATION</span>
Submarine cables are clear. If package installs fail, check your code.

💬 <span style="color:#A3F9C9; font-style:italic;">"Barkat hai, submarine cable theek hai aaj. Kaam karo."</span>
<span style="color:#00E676;">══════════════════════════════════════════════════════</span>`,

    pkon: `\x3cspan style="color:#00E676;">$ claude\x3c/span>
> <span style="color:#FFFFFF; font-weight:bold;">/pk on</span>

<span style="color:#00E676;">🇵🇰 Pakistan Mode: ACTIVE</span>
<span style="color:#00E676;">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>
✓ Guardian daemon running in background (PID: 4920)
✓ NPM registry  → <span style="color:#A3F9C9;">https://registry.npmmirror.com/</span>
✓ PIP index     → <span style="color:#A3F9C9;">https://pypi.tuna.tsinghua.edu.cn/simple/</span>
✓ Theme         → <span style="color:#00E676;">Pakistan Green & White (Jugaad PK)</span>
✓ Auto-checkpoint: every 5 min on dirty repo
✓ Bijli / Power loss detector: ON

<span style="color:#FFFFFF; font-weight:bold;">Theek hai. Kaam karo.</span>
<span style="color:#00E676;">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>`,

    checkpoint: `\x3cspan style="color:#00E676;">$ claude\x3c/span>
> <span style="color:#FFFFFF; font-weight:bold;">/checkpoint</span>

<span style="color:#FFD600;">[jugaad-code] Scanning workspace for uncommitted changes...</span>
✓ Found 3 modified files (scripts/guardian.py, src/index.ts, .env)
✓ Staged all files (git add -A)
✓ Committed: <span style="color:#00E676;">"chore: [PK-checkpoint] manual @ 2026-08-14 22:30"</span>

<span style="color:#A3F9C9;">Sab safe hai. Emergency checkpoint complete.</span>`,

    error: `\x3cspan style="color:#00E676;">$ claude\x3c/span>
> <span style="color:#FFFFFF;">npm install @anthropic-ai/sdk</span>

<span style="color:#FF5252;">npm ERR! code ECONNREFUSED</span>
<span style="color:#FF5252;">npm ERR! syscall connect 104.16.27.34:443 - Connection refused</span>

<span style="color:#00E676;">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>
<span style="color:#00E676;">🇵🇰 [jugaad-code] Yeh aapka code nahi hai.</span>
   Network issue lag raha hai. Diagnose kar raha hoon...
   
   <span style="color:#FFD600;">Diagnosis:</span> SUBMARINE_CABLE_CONGESTION (SMW4)
   <span style="color:#00E676;">→ Switching NPM to Asian mirror:</span> registry.npmmirror.com
   <span style="color:#A3F9C9;">→ Rerunning install automatically... Success!</span>
<span style="color:#00E676;">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>`
  };

  // Render Terminal Screen
  function renderTerminal(content) {
    terminalScreen.innerHTML = `<pre>${content}</pre>`;
  }

  // Update Status Badge & Statusline
  function updateStatus(state, msg) {
    currentState = state;
    badgeStateText.textContent = `SURVIVAL: ${state}`;
    
    let tag = `[PK: ${state} ✓]`;
    if (state === 'POWER_UNSTABLE') tag = `[PK: POWER UNSTABLE ⚡]`;
    if (state === 'NETWORK_DEGRADED') tag = `[PK: NET DEGRADED 🌐]`;
    if (state === 'CRITICAL') tag = `[PK: CRITICAL 🚨]`;

    terminalStatusline.innerHTML = `
      <span class="status-tag">${tag}</span>
      <span class="status-msg">"${msg}"</span>
    `;
  }

  // Command Button Clicks
  cmdButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      cmdButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const cmd = btn.dataset.cmd;
      if (TERMINAL_OUTPUTS[cmd]) {
        renderTerminal(TERMINAL_OUTPUTS[cmd]);
      }
    });
  });

  // Simulator Triggers
  simPowerCut.addEventListener('click', () => {
    updateStatus('POWER_UNSTABLE', 'UPS pe ho? Auto-checkpoint committed.');
    renderTerminal(`\x3cspan style="color:#FFBD2E; font-weight:bold;">⚡ [jugaad-code] BIJLI GONE! AC Power Disconnected.</span\x3e
[jugaad-code] Switched to Battery / UPS. Battery: 84%.
[jugaad-code] Triggering Emergency Git Checkpoint...
✓ Staged all dirty files (git add -A)
✓ Committed: <span style="color:#00E676;">"chore: [PK-checkpoint] bijli-cut @ 22:34"</span>
🛡️ <span style="color:#FFBD2E;">Adaptive Survival Mode: POWER_UNSTABLE active.</span>
   • Workspace protection enabled
   • Blocking long builds to conserve battery`);
  });

  simCableCongestion.addEventListener('click', () => {
    updateStatus('NETWORK_DEGRADED', 'SMW4 cable slow. Switched to Asian mirror.');
    renderTerminal(`\x3cspan style="color:#00B4D8; font-weight:bold;">🌊 [jugaad-code] Submarine Cable Degradation Detected.</span\x3e
[net_check] Ping to US/EU endpoints exceeding 3500ms (SMW4/AAE-1 bottleneck).
[guardian] Switching package managers to Asian mirror routes:
  ✓ npm -> https://registry.npmmirror.com/
  ✓ pip -> https://pypi.tuna.tsinghua.edu.cn/simple/
🛡️ <span style="color:#00B4D8;">Adaptive Survival Mode: NETWORK_DEGRADED active.</span>
   • Preferring local cache
   • Rerouting international requests`);
  });

  simCritical.addEventListener('click', () => {
    updateStatus('CRITICAL', '🚨 Battery 12% + No Net! Finish current edit now.');
    renderTerminal(`\x3cspan style="color:#FF5252; font-weight:bold;">🚨 [jugaad-code] CRITICAL SURVIVAL MODE ENGAGED.</span\x3e
⚠ Battery at 12% (approx 9 mins left)
⚠ International Gateway degraded

Recommended Actions:
  1. Finish current file edit
  2. Workspace checkpoint locked & committed
  3. Defer background builds until AC power restores.`);
  });

  simNormal.addEventListener('click', () => {
    updateStatus('NORMAL', 'Kaam karo. Guardian jaag raha hai.');
    renderTerminal(TERMINAL_OUTPUTS.doctor);
  });

  // Initial Render
  renderTerminal(TERMINAL_OUTPUTS.doctor);
});
