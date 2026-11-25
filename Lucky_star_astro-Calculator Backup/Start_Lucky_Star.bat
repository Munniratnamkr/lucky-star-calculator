
@echo off
title Lucky Star App - Auto Update & Run
cd /d "%~dp0"

echo Checking latest updates from GitHub...
git pull origin main

if exist requirements.txt (
    echo Installing/updating required packages...
    pip install -r requirements.txt --quiet
)

echo Starting app.py...
python app.py

pause