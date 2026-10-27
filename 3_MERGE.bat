@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === Accept the current changes (merge into main) ===
for /f "delims=" %%b in ('git branch --show-current') do set "BR=%%b"
if /i "%BR%"=="main" (
  echo You are already on main. Nothing to merge.
  pause & exit /b 0
)
gh pr merge %BR% --squash --delete-branch
git switch main
git pull -q
echo.
echo Merged. This folder is back on main and up to date.
pause
