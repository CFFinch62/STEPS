@echo off
setlocal enabledelayedexpansion

REM Define project root
set "PROJECT_ROOT=%CD%"
set "DIST_DIR=%PROJECT_ROOT%\dist\windows"
set "BUILD_DIR=%PROJECT_ROOT%\build\windows"

echo ========================================
echo Steps IDE Windows Build Script
echo ========================================
echo.

echo [1/3] Cleaning previous builds...
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
if exist "*.spec" del /q "*.spec"

echo [2/3] Installing build dependencies...
pip install pyinstaller PyQt6-WebEngine pywinpty

echo [3/4] Building Steps IDE...
REM Create the executable
REM --noconsole: Don't show a terminal window
REM --name: Name of the executable
REM --add-data: Include the Quick Reference file
REM --hidden-import: Ensure all needed modules are found (PyQt6-WebEngine might need this)
REM --clean: Clean PyInstaller cache
REM --noconfirm: Don't ask to overwrite
pyinstaller --name="StepsIDE" ^
            --windowed ^
            --noconsole ^
            --clean ^
            --noconfirm ^
            --distpath "%DIST_DIR%" ^
            --workpath "%BUILD_DIR%" ^
            --add-data "src\steps\stdlib;steps\stdlib" ^
            --add-data "docs\QUICK-REFERENCE.md;docs" ^
            --add-data "images;images" ^
            --hidden-import "PyQt6.QtWebEngineCore" ^
            --hidden-import "PyQt6.QtWebEngineWidgets" ^
            --hidden-import "winpty" ^
            --hidden-import "serial" ^
            src\steps_ide\main.py

echo.
echo [4/4] Building Steps Interpreter...
pyinstaller --name="steps" ^
            --onefile ^
            --console ^
            --clean ^
            --noconfirm ^
            --distpath "%DIST_DIR%" ^
            --workpath "%BUILD_DIR%" ^
            --paths "src" ^
            --add-data "src\steps\stdlib;steps\stdlib" ^
            --hidden-import "steps_repl" ^
            --hidden-import "steps_repl.repl" ^
            --hidden-import "steps_repl.commands" ^
            --hidden-import "steps_repl.environment" ^
            --hidden-import "serial" ^
            src\steps\main.py

echo.
echo ========================================
echo Build complete!
echo ========================================
echo Executable is located at: dist\windows\StepsIDE\StepsIDE.exe
echo (using directory mode for faster startup)
echo.

REM Optional: Create a simple run script in dist for convenience
if not exist "%DIST_DIR%\StepsIDE" mkdir "%DIST_DIR%\StepsIDE"
echo @echo off > "%DIST_DIR%\StepsIDE\run.bat"
echo cd /d "%%~dp0" >> "%DIST_DIR%\StepsIDE\run.bat"
echo start "" "StepsIDE.exe" >> "%DIST_DIR%\StepsIDE\run.bat"

echo Ready to test!
echo.
endlocal
