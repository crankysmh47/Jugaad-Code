# install.ps1 — Windows PowerShell setup for jugaad-code

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Installing jugaad-code - Pakistan Resilience Layer for Claude Code (Windows)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor DarkGray

# Check Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $pythonCmd) {
    Write-Host "[Error] Python not found in PATH. Install Python 3 first." -ForegroundColor Red
    exit 1
}

# Install Python deps
Write-Host "Installing dependencies..." -ForegroundColor Yellow
& $pythonCmd.Source -m pip install psutil --quiet

# Create Target Directories
$claudeDir = Join-Path $HOME ".claude"
$claudeCommandsDir = Join-Path $claudeDir "commands"
$claudeHooksDir = Join-Path $claudeDir "hooks"
$claudeThemesDir = Join-Path $claudeDir "themes"
$appDir = Join-Path $HOME ".jugaad-code"
$appScriptsDir = Join-Path $appDir "scripts"
$appUiDir = Join-Path $appDir "ui"

New-Item -ItemType Directory -Force -Path $claudeCommandsDir | Out-Null
New-Item -ItemType Directory -Force -Path $claudeHooksDir | Out-Null
New-Item -ItemType Directory -Force -Path $claudeThemesDir | Out-Null
New-Item -ItemType Directory -Force -Path $appScriptsDir | Out-Null
New-Item -ItemType Directory -Force -Path $appUiDir | Out-Null

# Copy scripts & UI to user app directory
if (Test-Path "scripts") {
    Copy-Item -Path "scripts\*" -Destination $appScriptsDir -Recurse -Force
}
if (Test-Path "ui") {
    Copy-Item -Path "ui\*" -Destination $appUiDir -Recurse -Force
}

# Copy slash commands
if (Test-Path ".claude\commands") {
    Copy-Item -Path ".claude\commands\*" -Destination $claudeCommandsDir -Force
}

# Set Environment Variables
[System.Environment]::SetEnvironmentVariable("JUGAAD_CODE_SCRIPTS", $appScriptsDir, [System.EnvironmentVariableTarget]::User)
[System.Environment]::SetEnvironmentVariable("JUGAADI_CLAUDE_SCRIPTS", $appScriptsDir, [System.EnvironmentVariableTarget]::User)
$env:JUGAAD_CODE_SCRIPTS = $appScriptsDir
$env:JUGAADI_CLAUDE_SCRIPTS = $appScriptsDir

# Wire hooks, statusline, and startup into user settings.json (merge, never clobber)
$settingsPath = Join-Path $claudeDir "settings.json"
$settings = @{}
if (Test-Path $settingsPath) {
    try {
        $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json -AsHashtable
    } catch {
        Copy-Item $settingsPath "$settingsPath.bak" -Force
        Write-Host "[Error] ~/.claude/settings.json is not valid JSON." -ForegroundColor Red
        Write-Host "        Backed it up to settings.json.bak — fix it and re-run." -ForegroundColor Red
        exit 1
    }
}

if ($null -eq $settings) { $settings = @{} }

# Bash-style fallback chain; Claude Code runs hook commands through bash even
# on Windows, so these expand. Single-quoted PS strings keep the $ literally.
$scriptsRef = '"${JUGAAD_CODE_SCRIPTS:-${JUGAADI_CLAUDE_SCRIPTS:-$HOME/.jugaad-code/scripts}}"'

function Add-JugaadHook {
    param(
        [hashtable]$Settings,
        [string]$Event,
        [string]$Matcher,
        [string]$Command,
        [int]$Timeout,
        [string]$StatusMessage = ""
    )
    if (-not $Settings.ContainsKey("hooks")) { $Settings["hooks"] = @{} }
    $hooks = $Settings["hooks"]
    if (-not $hooks.ContainsKey($Event)) { $hooks[$Event] = @() }
    $groups = @($hooks[$Event])
    $scriptName = ($Command -split "/")[-1]
    foreach ($group in $groups) {
        foreach ($h in @($group.hooks)) {
            if ($h.command -and $h.command.Contains($scriptName)) { return }
        }
    }
    $hookEntry = @{ type = "command"; command = $Command; timeout = $Timeout }
    if ($StatusMessage) { $hookEntry["statusMessage"] = $StatusMessage }
    $groups += @{ matcher = $Matcher; hooks = @($hookEntry) }
    $hooks[$Event] = $groups
}

Add-JugaadHook -Settings $settings -Event "SessionStart" -Matcher "startup" `
    -Command "python $scriptsRef/guardian_boot.py" -Timeout 10
Add-JugaadHook -Settings $settings -Event "PreToolUse" -Matcher "Bash|PowerShell" `
    -Command "python $scriptsRef/pre_tool_hook.py" -Timeout 15 -StatusMessage "jugaad soch raha hai..."
Add-JugaadHook -Settings $settings -Event "PostToolUse" -Matcher "Bash|PowerShell" `
    -Command "python $scriptsRef/post_tool_hook.py" -Timeout 15

$statuslineCmd = "python $scriptsRef/statusline.py"
$currentStatus = $settings["statusLine"]
if (-not ($currentStatus -is [System.Collections.IDictionary] -and $currentStatus["command"] -match "statusline\.py")) {
    $settings["statusLine"] = @{
        type = "command"
        command = $statuslineCmd
        padding = 1
        refreshInterval = 30
    }
}

$settings | ConvertTo-Json -Depth 20 | Set-Content -Path $settingsPath -Encoding UTF8
Write-Host "[OK] Hooks and statusline wired into $settingsPath" -ForegroundColor Green

Write-Host ""
Write-Host "[OK] jugaad-code installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Commands available in Claude Code:"
Write-Host "  /doctor     - Full health check"
Write-Host "  /pk on      - Activate Pakistan Mode (green theme + guardian)"
Write-Host "  /pk off     - Deactivate Pakistan Mode"
Write-Host "  /pk status  - Show Pakistan Mode state"
Write-Host "  /checkpoint - Emergency commit"
Write-Host ""
Write-Host "Theek hai. Kaam shuru karo." -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor DarkGray
