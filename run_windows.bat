@echo off
setlocal
cd /d "%~dp0"
if not exist venv (
    echo Creating virtual environment...
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        py -m venv venv
    ) else (
        python -m venv venv
    )
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
python app.py
pause
