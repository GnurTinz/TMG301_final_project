@echo off
setlocal
cd /d "%~dp0web_app\frontend"
where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js is not on PATH. Install Node 22.12+ or 24 LTS.
    exit /b 1
)
if not exist "node_modules\vite\bin\vite.js" (
    echo Installing frontend dependencies...
    call npm.cmd install
    if errorlevel 1 exit /b 1
)
echo Open http://127.0.0.1:5173 after the server is ready.
call npm.cmd run dev
exit /b %errorlevel%
