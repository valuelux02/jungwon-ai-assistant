@echo off
setlocal
cd /d "%~dp0"
echo ========================================================
echo  Jungwon AI Assistant - GitHub Repository Push
echo ========================================================
echo.

set "GIT_CMD=C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\Git\cmd\git.exe"

if not exist "%GIT_CMD%" (
    set "GIT_CMD=git"
)

echo [1/3] Setting Git config...
"%GIT_CMD%" config http.sslVerify true
"%GIT_CMD%" config http.sslBackend schannel

echo [2/3] Setting remote repository origin...
"%GIT_CMD%" remote remove origin 2>nul
"%GIT_CMD%" remote add origin https://github.com/valuelux02/jungwon-ai-assistant.git
"%GIT_CMD%" branch -M main

echo [3/3] Pushing to GitHub...
echo (A browser window or login prompt will appear if authentication is needed)
"%GIT_CMD%" push -u origin main

echo.
echo ========================================================
echo  Completed! Check https://github.com/valuelux02/jungwon-ai-assistant
echo ========================================================
pause
