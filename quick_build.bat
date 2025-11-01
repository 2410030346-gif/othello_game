@echo off
REM Quick Build Script for Othello Game
REM This script builds the standalone executable

echo ========================================
echo OTHELLO GAME - QUICK BUILD SCRIPT
echo ========================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller!
        pause
        exit /b 1
    )
)

echo Building executable...
echo.

REM Build the executable
pyinstaller --name=Othello --onefile --windowed --clean main.py

if errorlevel 1 (
    echo.
    echo Build FAILED!
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD COMPLETE!
echo ========================================
echo.
echo Executable location: dist\Othello.exe
echo.
echo Next steps:
echo 1. Test the executable in dist\Othello.exe
echo 2. Create distribution package
echo 3. Share your game!
echo.

pause
