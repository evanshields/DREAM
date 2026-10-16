$ErrorActionPreference = 'Stop'
$checkout = Split-Path $PSScriptRoot -Parent
$pythonExe = 'C:\Users\evana\DREAM\.venv\Scripts\python.exe'
$dependencies = 'C:\Users\evana\DREAM\frontend\node_modules'
if (!(Test-Path -LiteralPath $pythonExe) -or !(Test-Path -LiteralPath $dependencies)) { throw 'Existing DREAM dependencies unavailable; no automatic install.' }
$junction = Join-Path $checkout 'frontend\node_modules'
if (!(Test-Path -LiteralPath $junction)) { New-Item -ItemType Junction -Path $junction -Target $dependencies | Out-Null }
Push-Location (Join-Path $checkout 'frontend')
try {
    & node (Join-Path $dependencies 'typescript\bin\tsc') -p tsconfig.demo.json
    if ($LASTEXITCODE -ne 0) { throw 'Local sample typecheck failed' }
    & node (Join-Path $dependencies 'vite\bin\vite.js') build --config vite.demo.config.mjs --configLoader native
    if ($LASTEXITCODE -ne 0) { throw 'Local static sample build failed' }
} finally { Pop-Location }
Write-Host 'Open http://127.0.0.1:8769/__demo__/ . Synthetic data only; Ctrl+C stops and clears it.'
& $pythonExe (Join-Path $PSScriptRoot 'server.py')
if ($LASTEXITCODE -ne 0) { throw 'Local sample server failed' }
