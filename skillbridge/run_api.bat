@echo off
REM Windows batch script to run SkillBridge API

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Run the API
echo Starting SkillBridge API...
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
