@echo off
rem keep this window open even if something fails
if not "%~1"=="run" (
  cmd /k ""%~f0" run"
  exit /b
)
setlocal
cd /d "%~dp0"
echo === Send Claude's changes to Codex for review (max 3 rounds per PR) ===
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
  echo [!] This folder is not the labgossip-kits repo. Run this file from the labgossip-kits folder.
  goto END
)
set "CUR="
for /f "delims=" %%b in ('git branch --show-current') do set "CUR=%%b"
echo Current branch: %CUR%
set "STATE="
if /i "%CUR:~0,7%"=="review-" for /f "delims=" %%s in ('gh pr view %CUR% --json state --jq .state 2^>nul') do set "STATE=%%s"
if /i "%STATE%"=="OPEN" goto CONTINUE_PR

:NEW_PR
for /f "delims=" %%t in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmm"') do set "TS=%%t"
set "BR=review-%TS%"
set "ROUND=1"
git switch -c %BR%
call :COMMIT
if errorlevel 1 goto END
git push -u origin %BR%
gh pr create --base main --head %BR% --title "Kit update %TS%" --body "Changes made by Claude. Codex: please review using the Code Review Rules and Review rounds in AGENTS.md."
goto REQUEST

:CONTINUE_PR
set "BR=%CUR%"
set "ROUND=0"
if exist .review_round set /p ROUND=<.review_round
set /a ROUND+=1
if %ROUND% GTR 3 goto TOO_MANY
call :COMMIT
if errorlevel 1 goto CHECK_AHEAD
goto PUSH
:CHECK_AHEAD
rem nothing new to commit, but an earlier run may have committed without pushing
set "AHEAD=0"
for /f %%n in ('git rev-list --count origin/%BR%..HEAD') do set "AHEAD=%%n"
if "%AHEAD%"=="0" goto END
echo Found %AHEAD% commit^(s^) not sent yet - sending them now.
:PUSH
git push origin %BR%

:REQUEST
> .review_round echo %ROUND%
gh pr comment %BR% --body "@codex review - round %ROUND%/3 (see Review rounds in AGENTS.md)"
echo.
echo Sent: round %ROUND%/3. Codex usually answers in a few minutes.
echo Then tell Claude to read the review.
goto END

:TOO_MANY
echo.
echo This pull request already had 3 review rounds.
echo Run 3_MERGE.bat to accept it, or ask Claude to sum up what is still disputed.
goto END

:COMMIT
git add -A
git diff --cached --quiet
if errorlevel 1 goto DO_COMMIT
echo.
echo Nothing changed. Copy Claude's new files into this folder first.
exit /b 1
:DO_COMMIT
git commit -q -m "Kit update"
exit /b 0

:END
echo.
echo You can close this window.
