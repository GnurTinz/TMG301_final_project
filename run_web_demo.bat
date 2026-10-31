@echo off
title CRM Support Ticket Router - Web Demo (TMG301)

REM Chuyen thu muc lam viec ve dung thu muc chua file bat nay
cd /d "%~dp0"

echo ======================================================================
echo   CRM SUPPORT TICKET ROUTER - MULTI-CLASS TEXT CLASSIFICATION
echo   Mon hoc: TMG301 ^| Conda Env: tmg_project
echo ======================================================================
echo.

set PYTHON_EXEC=D:\InstalledApps\MiniConda\envs\tmg_project\python.exe

if not exist "%PYTHON_EXEC%" (
    echo [ERROR] Khong tim thay Python tai: %PYTHON_EXEC%
    echo Thu dung python mac dinh trong he thong...
    set PYTHON_EXEC=python
)

echo [*] Python duoc su dung: "%PYTHON_EXEC%"
echo [*] Dang khoi dong Web Server tren cong 5050...
echo.
echo ======================================================================
echo   * Local Ticket Router:       http://127.0.0.1:5050/
echo   * Local Model Dashboard:     http://127.0.0.1:5050/dashboard
echo   * Online 24/7 Public Domain: https://gnurtinz-tmg301-crm-router.hf.space
echo ======================================================================
echo.
echo [*] Tu dong mo trinh duyet sau 2 giay...
start "" "http://127.0.0.1:5050"

REM Khoi chay server Flask
"%PYTHON_EXEC%" web_app\app.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Server bi dung hoac xay ra loi (Exit code: %errorlevel%).
)

echo.
echo Nhan phim bat ky de thoat...
pause > nul
