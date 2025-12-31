@echo off
title BotHarbor
cd /d "%~dp0"

echo Starting BotHarbor...
call .venv\Scripts\activate
python -m botharbor.main

if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit...
    pause >nul
)
