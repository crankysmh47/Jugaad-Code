# install.ps1 — Windows PowerShell setup for jugaadi-claude

Write-Host "🇵🇰 Installing jugaadi-claude — Pakistan Resilience Layer for Claude Code (Windows)" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

# Check Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $pythonCmd) {
    Write-Host "❌ Python not found in PATH. Install Python 3 first." -ForegroundColor Red
    exit 1
}

# Install Python deps
Write-Host "Installing dependencies..." -ForegroundColor Yellow
& $pythonCmd.Source -m pip install psutil --quiet

# Create Claude Code directories
$claudeCommandsDir = Join-Path $HOME ".claude\commands"
$claudeHooksDir = Join-Path $HOME ".claude\hooks"

New-Item -ItemType Directory -Force -Path $claudeCommandsDir | Out-Null
New-Item -ItemType Directory -Force -Path $claudeHooksDir | Out-Null

# Copy slash commands
Copy-Item -Path "commands\doctor.md" -Destination (Join-Path $claudeCommandsDir "doctor.md") -Force
Copy-Item -Path "commands\pk.md" -Destination (Join-Path $claudeCommandsDir "pk.md") -Force
Copy-Item -Path "commands\checkpoint.md" -Destination (Join-Path $claudeCommandsDir "checkpoint.md") -Force

# Copy hooks
Copy-Item -Path "hooks\pre_tool_call.sh" -Destination (Join-Path $claudeHooksDir "pre_tool_call.sh") -Force
Copy-Item -Path "hooks\post_tool_call.sh" -Destination (Join-Path $claudeHooksDir "post_tool_call.sh") -Force

# Set Environment Variable for session / user
$scriptsPath = (Join-Path (Get-Location) "scripts")
[System.Environment]::SetEnvironmentVariable("JUGAADI_CLAUDE_SCRIPTS", $scriptsPath, [System.EnvironmentVariableTarget]::User)
$env:JUGAADI_CLAUDE_SCRIPTS = $scriptsPath

Write-Host ""
Write-Host "✅ jugaadi-claude installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Commands available in Claude Code:"
Write-Host "  /doctor     — Full health check"
Write-Host "  /pk on      — Activate Pakistan Mode"
Write-Host "  /pk off     — Deactivate Pakistan Mode"
Write-Host "  /checkpoint — Emergency commit"
Write-Host ""
Write-Host "Theek hai. Kaam shuru karo." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
