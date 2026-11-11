@echo off
title JobShield AI - Intelligent Recruitment Safety Engine
color 0B
cls
echo ====================================================================
echo        JobShield AI - Intelligent Recruitment Safety Engine
echo              HackNova: Harsh, Shivam, Mahi, Priyanshi
echo ====================================================================
echo.
cd /d "%~dp0"

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in PATH!
    echo Please install Python 3.10+ and check 'Add Python to PATH'.
    pause
    exit /b 1
)

echo [2/3] Verifying dependencies...
pip install -r requirements.txt --quiet --disable-pip-version-check

echo [3/3] Starting JobShield AI Web Server...
echo.
echo Server will run at: http://127.0.0.1:5000
echo Opening browser in 3 seconds...
echo Press CTRL+C in this window to stop the server.
echo.

start "" powershell -NoProfile -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:5000'"

python app.py
pause
