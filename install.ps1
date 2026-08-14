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

# Wire hooks, statusline, and startup into user settings.json
$settingsPath = Join-Path $claudeDir "settings.json"
$settings = @{}
if (Test-Path $settingsPath) {
    try {
        $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json -AsHashtable
    } catch {
        $settings = @{}
    }
}

if ($null -eq $settings) { $settings = @{} }

$settings["hooks"] = @{
    PreToolUse = @(
        @{
            matcher = "Bash|PowerShell"
            hooks = @(
                @{
                    type = "command"
                    command = 'python "${JUGAAD_CODE_SCRIPTS}/pre_tool_hook.py"'
                    timeout = 15
                    statusMessage = "jugaad soch raha hai..."
                }
            )
        }
    )
    PostToolUse = @(
        @{
            matcher = "Bash|PowerShell"
            hooks = @(
                @{
                    type = "command"
                    command = 'python "${JUGAAD_CODE_SCRIPTS}/post_tool_hook.py"'
                    timeout = 15
                }
            )
        }
    )
}

$settings["statusLine"] = @{
    type = "command"
    command = 'python "${JUGAAD_CODE_SCRIPTS}/statusline.py"'
    padding = 1
    refreshInterval = 30
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
