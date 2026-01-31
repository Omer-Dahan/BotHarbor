@echo off
echo Starting HAMAL...
cd /d "%~dp0"
call .venv\Scripts\activate.bat
cd src
python -m hamal.main
pause
