@echo off
cd /d "%~dp0"
title BloodReach BD — Frontend Server (Port 3000)
echo ========================================================
echo   🩸 BloodReach BD — Frontend Server
echo   Running at: http://localhost:3000
echo ========================================================
echo.

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m http.server 3000 --directory frontend
) else if exist "backend\venv\Scripts\python.exe" (
    "backend\venv\Scripts\python.exe" -m http.server 3000 --directory frontend
) else (
    python -m http.server 3000 --directory frontend
)

pause
