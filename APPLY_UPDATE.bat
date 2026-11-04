@echo off
if not "%~1"=="run" ( cmd /k "%~f0" run & exit /b )
cd /d "%~dp0"
echo === Copy Claude's update zip into this folder ===
set "ZIP="
for %%Z in ("%~dp0codex-update*.zip") do set "ZIP=%%~fZ"
if not defined ZIP for %%Z in ("%USERPROFILE%\Downloads\codex-update*.zip") do set "ZIP=%%~fZ"
if not defined ZIP (
  echo [!] No codex-update*.zip found here or in Downloads.
  echo     Put the zip from Claude next to this file and run again.
  exit /b 1
)
echo Using: %ZIP%
tar -xf "%ZIP%" -C .
if errorlevel 1 ( echo [!] Could not unpack the zip. & exit /b 1 )
git status --short
echo.
echo Done. Now run 2_SEND_FOR_REVIEW.bat
echo You can close this window.
