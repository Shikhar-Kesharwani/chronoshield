@echo off
REM ============================================================
REM  start_frontend.bat — Install deps and launch the React app
REM ============================================================
title AnomalyWatch Frontend

echo.
echo  ⚡  AnomalyWatch — Starting Frontend
echo  ─────────────────────────────────────
echo.

cd /d "%~dp0frontend"

REM Check for Node
node --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Node.js not found. Install Node.js 18+ from https://nodejs.org
    pause & exit /b 1
)

REM Install if node_modules missing
if not exist "node_modules" (
    echo  [INFO] Installing npm packages...
    npm install
)

echo  [INFO] Starting Vite dev server on http://localhost:5173
echo  [INFO] Press Ctrl+C to stop.
echo.
npm run dev
