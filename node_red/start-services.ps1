$ErrorActionPreference = 'Stop'
$projectDirectory = Split-Path $PSScriptRoot -Parent
$pythonExecutable = Join-Path (Split-Path $projectDirectory -Parent) 'Scripts/python.exe'
$nodeExecutable = Join-Path $env:LOCALAPPDATA 'Programs/NodeJS/node-v24.21.0-win-x64/node.exe'
$redScript = Join-Path $env:APPDATA 'npm/node_modules/node-red/red.js'
$runtimeDirectory = Join-Path $env:LOCALAPPDATA 'NodeRED/analysis-automation'
New-Item -ItemType Directory -Path $runtimeDirectory -Force | Out-Null
$env:TZ = 'Europe/Budapest'
$env:Path = (Split-Path $nodeExecutable -Parent) + ';' + (Join-Path $env:APPDATA 'npm') + ';' + $env:Path
if (-not (Get-NetTCPConnection -LocalPort 1880 -State Listen -ErrorAction SilentlyContinue)) {
    $redArguments = '"' + $redScript + '" --userDir "' + $runtimeDirectory + '" --settings "' + (Join-Path $PSScriptRoot 'settings.js') + '"'
    Start-Process -FilePath $nodeExecutable -ArgumentList $redArguments -WorkingDirectory $projectDirectory -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeDirectory 'node-red.log') -RedirectStandardError (Join-Path $runtimeDirectory 'node-red-error.log')
}
if (-not (Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue)) {
    $dashboardArguments = '-B -m streamlit run "' + (Join-Path $projectDirectory 'streamlit_app.py') + '" --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false'
    Start-Process -FilePath $pythonExecutable -ArgumentList $dashboardArguments -WorkingDirectory $projectDirectory -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeDirectory 'dashboard.log') -RedirectStandardError (Join-Path $runtimeDirectory 'dashboard-error.log')
}
