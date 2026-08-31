@echo off
cd /d "%~dp0"
title BloodReach BD — Server (Port 8000)

echo ========================================================
echo   🩸 BloodReach BD — Starting Server
echo   Running at: http://localhost:8000
echo   API Docs  : http://localhost:8000/docs
echo ========================================================
echo.

if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0run_backend.py"
) else if exist "%~dp0backend\venv\Scripts\python.exe" (
    "%~dp0backend\venv\Scripts\python.exe" "%~dp0run_backend.py"
) else (
    python "%~dp0run_backend.py"
)

pause
