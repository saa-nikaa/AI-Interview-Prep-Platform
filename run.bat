@echo off
echo ===================================================
echo 🚀 Launching AI Interview Helper...
echo ===================================================

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment 'venv' not found!
    echo Please follow the setup instructions in README.md
    pause
    exit /b
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting Streamlit App...
streamlit run app.py

pause
