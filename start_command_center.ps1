<#
    Brings up the whole Marino 007 command center:
      1. WhatsApp bridge   (port 3010)
      2. Dashboard         (port 3003, production build)
      3. Cloudflare tunnel (public URL for the team)

    Usage:
      powershell -ExecutionPolicy Bypass -File start_command_center.ps1
      powershell -ExecutionPolicy Bypass -File start_command_center.ps1 -SkipTunnel

    Each service runs in its own window so you can watch it and close it
    deliberately. Closing a window stops that service.
#>

param(
    [switch]$SkipTunnel,
    [switch]$SkipBuild
)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$dash = Join-Path $root 'shopify-affiliates'

function Test-Port($port) {
    $null -ne (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue)
}

Write-Host ''
Write-Host '  MARINO 007 COMMAND CENTER' -ForegroundColor Yellow
Write-Host '  =========================' -ForegroundColor DarkYellow
Write-Host ''

# --- 1. WhatsApp bridge ---------------------------------------------------
if (Test-Port 3010) {
    Write-Host '  [=] WhatsApp bridge already running on 3010' -ForegroundColor DarkGray
} else {
    Write-Host '  [>] Starting WhatsApp bridge on 3010...' -ForegroundColor Cyan
    Start-Process -FilePath 'cmd.exe' `
        -ArgumentList '/k', 'node whatsapp_server.js' `
        -WorkingDirectory $root
    # Baileys needs ~8s to reach WhatsApp before Express binds reliably.
    Start-Sleep -Seconds 12
    if (Test-Port 3010) {
        Write-Host '  [OK] WhatsApp bridge up' -ForegroundColor Green
    } else {
        Write-Host '  [!!] Bridge did not come up - check its window' -ForegroundColor Red
    }
}

# --- 2. Dashboard ---------------------------------------------------------
if (Test-Port 3003) {
    Write-Host '  [=] Dashboard already running on 3003' -ForegroundColor DarkGray
} else {
    if (-not $SkipBuild) {
        Write-Host '  [>] Building dashboard (production)...' -ForegroundColor Cyan
        Push-Location $dash
        & npm run build 2>&1 | Select-Object -Last 3
        Pop-Location
    }

    Write-Host '  [>] Starting dashboard on 3003...' -ForegroundColor Cyan
    Start-Process -FilePath 'cmd.exe' `
        -ArgumentList '/k', 'set PORT=3003 && npm start' `
        -WorkingDirectory $dash
    Start-Sleep -Seconds 12
    if (Test-Port 3003) {
        Write-Host '  [OK] Dashboard up -> http://localhost:3003' -ForegroundColor Green
    } else {
        Write-Host '  [!!] Dashboard did not come up - check its window' -ForegroundColor Red
    }
}

# --- 3. Public tunnel -----------------------------------------------------
if ($SkipTunnel) {
    Write-Host '  [-] Tunnel skipped (local only)' -ForegroundColor DarkGray
} else {
    Write-Host '  [>] Opening Cloudflare tunnel...' -ForegroundColor Cyan
    $log = Join-Path $root 'tunnel.log'
    if (Test-Path $log) { Remove-Item $log -Force }

    Start-Process -FilePath 'cmd.exe' `
        -ArgumentList '/k', "cloudflared tunnel --url http://localhost:3003 --no-autoupdate --logfile `"$log`"" `
        -WorkingDirectory $root
    Start-Sleep -Seconds 15

    $url = $null
    if (Test-Path $log) {
        $url = (Select-String -Path $log -Pattern 'https://[a-z0-9-]+\.trycloudflare\.com' |
                Select-Object -First 1).Matches.Value
    }

    if ($url) {
        Write-Host ''
        Write-Host "  [OK] PUBLIC URL: $url" -ForegroundColor Green
        Write-Host '       (changes every restart - a named tunnel would fix that)' -ForegroundColor DarkGray
    } else {
        Write-Host '  [!!] Tunnel URL not found yet - check the tunnel window' -ForegroundColor Yellow
    }
}

Write-Host ''
Write-Host '  Password is in shopify-affiliates\.env.local (DASHBOARD_PASSWORD)' -ForegroundColor DarkGray
Write-Host ''
