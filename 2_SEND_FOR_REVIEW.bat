@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === Send Claude's changes to Codex for review ===
for /f "delims=" %%t in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmm"') do set "TS=%%t"
set "BR=review-%TS%"
git switch -c %BR% >nul 2>&1
git add -A
git diff --cached --quiet
if %errorlevel%==0 (
  echo Nothing changed since the last review. Copy Claude's new files into this folder first.
  pause & exit /b 0
)
git commit -q -m "Kit update %TS%"
git push -q -u origin %BR%
gh pr create --base main --head %BR% --title "Kit update %TS%" --body "Changes made by Claude. Codex: please review using the Code Review Rules in AGENTS.md."
gh pr comment %BR% --body "@codex review"
echo.
echo Sent. Codex usually answers in a few minutes.
echo Then just tell Claude: "리뷰 봐줘"
pause
