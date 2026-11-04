@echo off
if not "%~1"=="run" ( cmd /k "%~f0" run & exit /b )
cd /d "%~dp0"
echo === Copy Claude's update zip into this folder ===
set "ZIP="
rem newest codex-update*.zip in this folder, else newest in Downloads
for /f "delims=" %%Z in ('dir /b /o:d "codex-update*.zip" 2^>nul') do set "ZIP=%CD%\%%Z"
if not defined ZIP for /f "delims=" %%Z in ('dir /b /o:d "%USERPROFILE%\Downloads\codex-update*.zip" 2^>nul') do set "ZIP=%USERPROFILE%\Downloads\%%Z"
if not defined ZIP (
  echo [!] No codex-update*.zip found here or in Downloads.
  echo     Put the zip from Claude next to this file and run again.
  exit /b 1
)
echo Using: %ZIP%
tar -xf "%ZIP%" -C .
if errorlevel 1 ( echo [!] Could not unpack the zip. & exit /b 1 )
rem clean up: stray unzipped copies and the zip itself must not go into the review
for /d %%D in ("codex-update*") do rd /s /q "%%D"
del /q "%ZIP%" >nul 2>&1
del /q "codex-update*.zip" >nul 2>&1
git status --short
echo.
echo Done. Now run 2_SEND_FOR_REVIEW.bat
echo You can close this window.
