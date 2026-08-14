# install.ps1 — Windows PowerShell setup for jugaadi-claude

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Installing jugaadi-claude - Pakistan Resilience Layer for Claude Code (Windows)" -ForegroundColor Cyan
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

# Create Claude Code directories
$claudeCommandsDir = Join-Path $HOME ".claude\commands"
$claudeHooksDir = Join-Path $HOME ".claude\hooks"

New-Item -ItemType Directory -Force -Path $claudeCommandsDir | Out-Null
New-Item -ItemType Directory -Force -Path $claudeHooksDir | Out-Null

# Copy slash commands and hooks (single source of truth: .claude/)
Copy-Item -Path ".claude\commands\doctor.md" -Destination (Join-Path $claudeCommandsDir "doctor.md") -Force
Copy-Item -Path ".claude\commands\pk.md" -Destination (Join-Path $claudeCommandsDir "pk.md") -Force
Copy-Item -Path ".claude\commands\checkpoint.md" -Destination (Join-Path $claudeCommandsDir "checkpoint.md") -Force

Copy-Item -Path ".claude\hooks\pre_tool_call.sh" -Destination (Join-Path $claudeHooksDir "pre_tool_call.sh") -Force
Copy-Item -Path ".claude\hooks\post_tool_call.sh" -Destination (Join-Path $claudeHooksDir "post_tool_call.sh") -Force

# Set Environment Variable for session / user
$scriptsPath = (Join-Path (Get-Location) "scripts")
[System.Environment]::SetEnvironmentVariable("JUGAADI_CLAUDE_SCRIPTS", $scriptsPath, [System.EnvironmentVariableTarget]::User)
$env:JUGAADI_CLAUDE_SCRIPTS = $scriptsPath

# Wire hooks and statusline into the user settings (preserving existing keys)
$settingsPath = Join-Path $HOME ".claude\settings.json"
$settings = @{}
if (Test-Path $settingsPath) {
    try {
        $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json -AsHashtable
    } catch {
        Write-Host "[Warning] Existing settings.json could not be parsed - hook wiring skipped." -ForegroundColor Yellow
        $settings = $null
    }
}

if ($null -ne $settings) {
    $settings["hooks"] = @{
        PreToolUse = @(
            @{
                matcher = "Bash|PowerShell"
                hooks = @(
                    @{
                        type = "command"
                        command = 'bash "$HOME/.claude/hooks/pre_tool_call.sh"'
                        timeout = 15
                        statusMessage = "jugaadi soch raha hai..."
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
                        command = 'bash "$HOME/.claude/hooks/post_tool_call.sh"'
                        timeout = 15
                    }
                )
            }
        )
    }
    $settings["statusLine"] = @{
        type = "command"
        command = 'python "${JUGAADI_CLAUDE_SCRIPTS}/statusline.py"'
        padding = 1
        refreshInterval = 30
    }
    $settings | ConvertTo-Json -Depth 20 | Set-Content -Path $settingsPath -Encoding UTF8
    Write-Host "[OK] Hooks and statusline wired into $settingsPath" -ForegroundColor Green
}

Write-Host ""
Write-Host "[OK] jugaadi-claude installed successfully!" -ForegroundColor Green
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
