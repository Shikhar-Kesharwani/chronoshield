@echo off
REM ============================================================
REM  start_backend.bat — Install deps and launch the API server
REM ============================================================
title AnomalyWatch Backend

echo.
echo  ⚡  AnomalyWatch — Starting Backend
echo  ─────────────────────────────────────
echo.

cd /d "%~dp0backend"

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Install Python 3.10+ and add it to PATH.
    pause & exit /b 1
)

REM Create venv if needed
if not exist ".venv" (
    echo  [INFO] Creating virtual environment...
    python -m venv .venv
)

REM Activate venv
call .venv\Scripts\activate.bat

REM Install / upgrade dependencies
echo  [INFO] Installing dependencies...
pip install -r requirements.txt -q

REM Launch API (also starts generator + worker as background threads)
echo.
echo  [INFO] Starting FastAPI server on http://localhost:8000
echo  [INFO] Press Ctrl+C to stop.
echo.
python api.py
