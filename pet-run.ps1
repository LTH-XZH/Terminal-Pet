# pet-run.ps1 - TerminalPet build wrapper (PowerShell version)
# Usage: .\pet-run.ps1 -- gcc main.c -o main
#        or  .\pet-run.ps1 npm run build
$ErrorActionPreference = "Continue"

$py = $null
foreach ($cand in @("python", "py")) {
    $cmd = Get-Command $cand -ErrorAction SilentlyContinue
    if ($cmd) { $py = $cmd.Source; break }
}
if (-not $py) {
    Write-Host "[TerminalPet] Python 3 not found. Install it from https://www.python.org" -ForegroundColor Red
    exit 1
}

& $py "$PSScriptRoot\pet-run.py" -- @args
exit $LASTEXITCODE
