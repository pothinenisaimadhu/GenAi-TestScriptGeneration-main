@echo off
echo Starting Multi-Agent RAG Test Case Generator UI
echo ===============================================

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting UI...
python start_ui.py

pause