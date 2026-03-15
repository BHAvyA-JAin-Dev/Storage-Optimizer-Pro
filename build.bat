@echo off
echo.
echo ============================================================
echo   Storage Optimizer Pro - EXE Builder
echo ============================================================
echo.

:: Check for PyInstaller
python -m PyInstaller --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] PyInstaller not found. Installing dependencies...
    pip install -r requirements.txt
)

echo [*] Building standalone executable...
echo [*] This may take a few minutes...
echo.

:: Run PyInstaller
:: --onefile: Create a single executable
:: --windowed: Don't show console window
:: --name: Name of the output file
:: --clean: Clean cache before build
python -m PyInstaller --onefile --windowed --name "Storage Optimizer Pro" --clean main.py

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo [SUCCESS] Build complete! 
    echo [INFO] You can find your app in the "dist" folder.
    echo ============================================================
) else (
    echo.
    echo [ERROR] Build failed. Please check the logs above.
)

pause
