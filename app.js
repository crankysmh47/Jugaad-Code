// app.js — Minimal interactions for jugaad-code

document.addEventListener('DOMContentLoaded', () => {
  const cmdText = document.getElementById('cmdText');
  const copyBtn = document.getElementById('copyBtn');
  const tabBtns = document.querySelectorAll('.tab-btn');

  const COMMANDS = {
    win: 'irm https://raw.githubusercontent.com/crankysmh47/Jugaad-Code/main/install.ps1 | iex',
    nix: 'curl -fsSL https://raw.githubusercontent.com/crankysmh47/Jugaad-Code/main/install.sh | bash'
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
});
