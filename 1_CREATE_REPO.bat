@echo off
rem keep this window open even if something fails
if not "%~1"=="run" (
  cmd /k ""%~f0" run"
  exit /b
)
cd /d "%~dp0"
echo === Create the GitHub repo "labgossip-kits" (one time) ===
for /f "delims=" %%u in ('gh api user --jq .login 2^>nul') do set "GHUSER=%%u"
if not defined GHUSER (
  echo [!] Not logged in to GitHub. Run SETUP_GITHUB.bat first.
  exit /b 1
)
echo GitHub account: %GHUSER%
if /i not "%GHUSER%"=="angrietta" (
  echo [!] This is not angrietta. Stop here and tell Claude.
  exit /b 1
)
if exist .git (
  echo [!] This folder is already a repo. Nothing to do.
  exit /b 0
)
git init -b main
git config user.name "%GHUSER%"
git config user.email "%GHUSER%@users.noreply.github.com"
rem only the review setup goes to main first; the kit code goes in the first PR so Codex reviews all of it
git add README.md AGENTS.md .gitignore .github *.bat
git commit -q -m "Review setup"
gh repo create labgossip-kits --public --source . --remote origin --push
echo.
echo Done: https://github.com/%GHUSER%/labgossip-kits
echo Next: connect this repo in ChatGPT Codex, then run 2_SEND_FOR_REVIEW.bat
