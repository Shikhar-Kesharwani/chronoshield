@echo off
REM ============================================================
REM  run_tests.bat — Run backend unit tests
REM ============================================================
title AnomalyWatch Tests

cd /d "%~dp0backend"

if not exist ".venv" (
    echo  [ERROR] Run start_backend.bat first to set up the environment.
    pause & exit /b 1
)

call .venv\Scripts\activate.bat

echo.
echo  ⚡  Running Unit Tests
echo  ─────────────────────
python -m pytest tests/ -v --tb=short
echo.
pause
