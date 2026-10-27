@echo off
chcp 65001 >nul
echo ==================================================
echo   LAB GOSSIP - GitHub setup check (one time)
echo ==================================================
echo.
set "NEED_RERUN="

where git >nul 2>&1
if %errorlevel%==0 (
  for /f "delims=" %%v in ('git --version') do echo [OK] %%v
) else (
  echo [..] git is not installed - installing now...
  winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
  set "NEED_RERUN=1"
)

where gh >nul 2>&1
if %errorlevel%==0 (
  for /f "delims=" %%v in ('gh --version ^| findstr /B "gh"') do echo [OK] %%v
) else (
  echo [..] GitHub CLI is not installed - installing now...
  winget install --id GitHub.cli -e --source winget --accept-package-agreements --accept-source-agreements
  set "NEED_RERUN=1"
)

if defined NEED_RERUN (
  echo.
  echo Installed. CLOSE this window and double-click SETUP_GITHUB.bat ONE MORE TIME.
  pause & exit /b 0
)

echo.
gh auth status >nul 2>&1
if %errorlevel% neq 0 (
  echo Logging in to GitHub - a browser window will open.
  echo Sign in with your PERSONAL account ^(angrietta^), then copy the code shown here into the browser.
  gh auth login --hostname github.com --git-protocol https --web
)
gh auth setup-git >nul 2>&1

echo.
for /f "delims=" %%u in ('gh api user --jq .login 2^>nul') do set "GHUSER=%%u"
if defined GHUSER (
  echo [OK] Logged in to GitHub as: %GHUSER%
  if /i not "%GHUSER%"=="angrietta" echo [!] This is not angrietta. Run "gh auth logout" and this file again.
) else (
  echo [!] Not logged in. Run this file again.
)
echo.
echo Send a screenshot of this window to Claude.
pause
