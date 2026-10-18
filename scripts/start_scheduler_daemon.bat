@echo off
title PredictApp Background Scheduler Daemon
echo ===================================================
echo Starting PredictApp Match Import Scheduler Daemon
echo ===================================================
echo Schedule:
echo   - 06:30 IST: Morning Results
echo   - 06:35 IST: Morning Fixtures ^& Odds
echo   - 20:30 IST: Evening Results
echo   - 20:35 IST: Evening Fixtures ^& Odds
echo ===================================================

cd /d "%~dp0.."
.venv\Scripts\python.exe manage.py run_scheduler
pause
