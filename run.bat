@echo off
echo Starting BotHarbor...
cd /d "%~dp0"
call .venv\Scripts\activate.bat
cd src
python -m botharbor.main
pause
