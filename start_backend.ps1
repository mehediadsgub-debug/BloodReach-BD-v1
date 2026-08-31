# BloodReach BD — Start Backend Server
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $scriptDir

$pythonPath = if (Test-Path "$scriptDir\.venv\Scripts\python.exe") { 
    "$scriptDir\.venv\Scripts\python.exe" 
} elseif (Test-Path "$scriptDir\backend\venv\Scripts\python.exe") { 
    "$scriptDir\backend\venv\Scripts\python.exe" 
} else { 
    "python" 
}

Write-Host "========================================================" -ForegroundColor Red
Write-Host "  🩸 BloodReach BD — Starting Full-Stack Server" -ForegroundColor Yellow
Write-Host "  Website  : http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs : http://localhost:8000/docs" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Red

& $pythonPath "$scriptDir\run_backend.py"
