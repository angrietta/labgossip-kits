@echo off
rem keep this window open even if something fails
if not "%~1"=="run" (
  cmd /k ""%~f0" run"
  exit /b
)
setlocal
cd /d "%~dp0"
echo === Accept the current changes (merge into main) ===
for /f "delims=" %%b in ('git branch --show-current') do set "BR=%%b"
if /i "%BR%"=="main" (
  echo You are already on main. Nothing to merge.
  exit /b 0
)
gh pr merge %BR% --squash --delete-branch
git switch main
git pull -q
if exist .review_round del .review_round
echo.
echo Merged. This folder is back on main and up to date.
