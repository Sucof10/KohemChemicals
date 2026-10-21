$ErrorActionPreference = 'Stop'

$frontend = Split-Path -Parent $PSScriptRoot
$mvp = Split-Path -Parent $frontend
$python = Join-Path $mvp 'venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $python)) {
  $python = 'python'
}

$backend = $null
$backendAlreadyRunning = $false

try {
  Invoke-RestMethod -Uri 'http://127.0.0.1:8000/' -TimeoutSec 1 | Out-Null
  $backendAlreadyRunning = $true
} catch {
  $backendAlreadyRunning = $false
}

if (-not $backendAlreadyRunning) {
  Write-Host 'Iniciando backend en http://127.0.0.1:8000 ...'
  $backend = Start-Process -FilePath $python -ArgumentList @(
    '-m', 'uvicorn', 'app.presentation.main:app',
    '--reload', '--host', '127.0.0.1', '--port', '8000'
  ) -WorkingDirectory $mvp -PassThru
  Start-Sleep -Seconds 2
} else {
  Write-Host 'Backend ya esta en ejecucion en http://127.0.0.1:8000'
}

try {
  Push-Location $frontend
  npm run dev
} finally {
  Pop-Location
  if ($backend -and -not $backend.HasExited) {
    taskkill /PID $backend.Id /T /F | Out-Null
  }
}
