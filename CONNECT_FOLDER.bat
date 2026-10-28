@echo off
rem keep this window open even if something fails
if not "%~1"=="run" (
  cmd /k ""%~f0" run"
  exit /b
)
setlocal
cd /d "%~dp0"
echo === Connect this folder to github.com/angrietta/labgossip-kits ===
echo Folder: %CD%

rem 1) Windows "dubious ownership" block
git status 2>&1 | findstr /C:"dubious ownership" >nul
if not errorlevel 1 (
  echo Fixing a Windows folder-ownership check...
  git config --global --add safe.directory "%CD:\=/%"
)

rem 2) already connected?
git rev-parse --is-inside-work-tree >nul 2>&1
if not errorlevel 1 (
  echo [OK] This folder is already connected.
  git status --short --branch
  goto END
)

rem 3) not a repo yet: attach it to GitHub, keep the files that are here now
echo This folder has no repo yet - connecting it now...
git init -q -b main
git remote add origin https://github.com/angrietta/labgossip-kits.git
git fetch -q origin
if errorlevel 1 (
  echo [!] Could not reach GitHub. Run 0_SETUP_GITHUB.bat, then this file again.
  goto END
)
for /f "delims=" %%u in ('gh api user --jq .login 2^>nul') do set "GHUSER=%%u"
git config user.name "%GHUSER%"
git config user.email "%GHUSER%@users.noreply.github.com"
set "BR="
for /f "delims=" %%b in ('gh pr list -R angrietta/labgossip-kits --state open --json headRefName --jq ".[0].headRefName" 2^>nul') do set "BR=%%b"
if defined BR (
  echo Open review found: %BR%
  git switch -q -c %BR%
  git reset -q origin/%BR%
  git branch -q -u origin/%BR%
) else (
  git reset -q origin/main
  git branch -q -u origin/main
)
echo.
echo [OK] Connected. Files that differ from GitHub (these are Claude's updates):
git status --short
echo.
echo Next: run 2_SEND_FOR_REVIEW.bat

:END
echo.
echo You can close this window.
