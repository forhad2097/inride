<#
  inride test runner.

    .\run.ps1 demo        HEADED full suite + slow motion + long highlight  <- client demo
    .\run.ps1 quick       HEADED smoke only (faster demo)
    .\run.ps1             full suite, headless (no browser window)
    .\run.ps1 login       login page validations only
    .\run.ps1 menus       menu / page access validations only
    .\run.ps1 report      open the reports without running anything
#>
param([string]$Mode = "all")

$py = ".\.venv\Scripts\python.exe"
$assertionReport = "reports\assertion_report.html"
$pytestReport = "reports\report.html"

# remember the shell's original settings so a demo run does not leak into the next one
$original = @{
    HEADLESS      = $env:HEADLESS
    SLOW_MO       = $env:SLOW_MO
    HIGHLIGHT_MS  = $env:HIGHLIGHT_MS
}

function Set-DemoMode {
    $env:HEADLESS = "false"     # <- the browser window opens
    $env:SLOW_MO = "250"        # <- every action is slowed down so it is watchable
    $env:HIGHLIGHT_MS = "700"   # <- the yellow highlight stays on screen longer
}

function Restore-Env {
    foreach ($key in $original.Keys) {
        if ($null -eq $original[$key]) {
            Remove-Item "env:$key" -ErrorAction SilentlyContinue
        } else {
            Set-Item "env:$key" $original[$key]
        }
    }
}

function Show-Reports {
    Write-Host ""
    Write-Host "  Assertion report : $(Resolve-Path $assertionReport)" -ForegroundColor Cyan
    Write-Host "  pytest report    : $(Resolve-Path $pytestReport)" -ForegroundColor Cyan
    Write-Host ""
    Start-Process (Resolve-Path $assertionReport)
}

try {
    switch ($Mode) {
        "demo" {
            Set-DemoMode
            Write-Host "`n  DEMO MODE - a Chromium window will open. Full suite, ~10 minutes.`n" -ForegroundColor Yellow
            & $py -m pytest
            Show-Reports
        }
        "quick" {
            Set-DemoMode
            Write-Host "`n  QUICK DEMO - a Chromium window will open. Smoke suite, ~5 minutes.`n" -ForegroundColor Yellow
            & $py -m pytest -m smoke
            Show-Reports
        }
        "login"  { & $py -m pytest -m login;  Show-Reports }
        "menus"  { & $py -m pytest -m menu;   Show-Reports }
        "report" { Show-Reports; Start-Process (Resolve-Path $pytestReport) }
        default  { & $py -m pytest;           Show-Reports }
    }
}
finally {
    Restore-Env
}
