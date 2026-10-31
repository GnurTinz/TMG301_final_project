@echo off
title Retrain Support Ticket Router Models (TMG301)

REM Chuyen thu muc lam viec ve dung thu muc chua file bat nay
cd /d "%~dp0"

echo ======================================================================
echo   HUAN LUYEN ^& DANH GIA MO HINH SUPPORT TICKET ROUTER (TMG301)
echo   Dataset: processed_datasets/combined_dataset.csv (39,955 mau)
echo ======================================================================
echo.

set PYTHON_EXEC=D:\InstalledApps\MiniConda\envs\tmg_project\python.exe

if not exist "%PYTHON_EXEC%" (
    echo [ERROR] Khong tim thay Python tai: %PYTHON_EXEC%
    echo Thu dung python mac dinh trong he thong...
    set PYTHON_EXEC=python
)

echo [*] Python duoc su dung: "%PYTHON_EXEC%"
echo [*] Bat dau qua trinh huan luyen va danh gia mo hinh...
echo.

"%PYTHON_EXEC%" model\train_ticket_router.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Qua trinh huan luyen gap loi (Exit code: %errorlevel%).
) else (
    echo.
    echo ======================================================================
    echo [*] Qua trinh huan luyen va xuat do thi da HOAN TAT thanh cong!
    echo [*] Bieu do da luu tai thu muc: model\plots\
    echo [*] Mo hinh tot nhat da luu tai: model\saved_models\
    echo ======================================================================
)

echo.
echo Nhan phim bat ky de thoat...
pause > nul
