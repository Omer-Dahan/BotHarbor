@echo off
setlocal enabledelayedexpansion

echo ============================================
echo HAMAL Build Script
echo ============================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists, create if not
if not exist ".venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Make sure Python is installed and in PATH
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    exit /b 1
)

REM Install PyInstaller if not present
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller --quiet
)

REM Run PyInstaller
echo.
echo Building HAMAL...
echo.
pyinstaller --noconfirm --clean hamal.spec

REM Check result
if exist "dist\HAMAL\HAMAL.exe" (
    echo.
    echo ============================================
    echo BUILD SUCCESSFUL
    echo ============================================
    echo Output: dist\HAMAL\
    echo.
    echo Next step: Run Inno Setup with installer.iss
    echo to create the Windows installer.
) else (
    echo.
    echo ============================================
    echo BUILD FAILED
    echo ============================================
    exit /b 1
)

endlocal
