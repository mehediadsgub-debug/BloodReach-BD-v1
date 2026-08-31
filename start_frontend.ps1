# BloodReach BD — Start Frontend Server
Write-Host "========================================================" -ForegroundColor Red
Write-Host "  🩸 BloodReach BD — Frontend Server" -ForegroundColor Yellow
Write-Host "  Running at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Red

$pythonPath = if (Test-Path ".\.venv\Scripts\python.exe") { ".\.venv\Scripts\python.exe" } elseif (Test-Path "backend\venv\Scripts\python.exe") { "backend\venv\Scripts\python.exe" } else { "python" }

& $pythonPath -m http.server 3000 --directory frontend
