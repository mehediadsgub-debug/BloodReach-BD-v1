@echo off
cd /d "%~dp0"
title BloodReach BD — Complete System Launcher
echo ========================================================
echo   🩸 BloodReach BD — Launching Everything
echo   Website  : http://localhost:8000
echo   API Docs : http://localhost:8000/docs
echo ========================================================
echo.

start "BloodReach Server" cmd /k "cd /d "%~dp0" && start_backend.bat"
timeout /t 3 /nobreak >nul
start http://localhost:8000

echo Server is active!
echo Browser opened at http://localhost:8000
timeout /t 3 >nul
