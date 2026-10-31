@echo off
setlocal
cd /d "%~dp0"
if not defined PYTHON_EXEC set "PYTHON_EXEC=D:\InstalledApps\MiniConda\envs\pyenv\python.exe"
if not exist "%PYTHON_EXEC%" (
    echo [ERROR] Python not found: "%PYTHON_EXEC%"
    echo Set PYTHON_EXEC to your existing Python environment.
    exit /b 1
)
if not defined HOST set "HOST=127.0.0.1"
if not defined PORT set "PORT=5050"
set "PYTHONIOENCODING=utf-8"
echo Starting the existing Flask inference API at http://%HOST%:%PORT%
"%PYTHON_EXEC%" web_app\app.py
exit /b %errorlevel%
