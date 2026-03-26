@echo off
echo ========================================
echo Multi-Agent RAG Test Case Generator UI
echo ========================================
echo.

REM Change to the orchestrator directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)




REM Install/upgrade requirements
echo Installing UI requirements...
echo This may take a few minutes, please wait...
pip install streamlit PyMuPDF requests python-dotenv --no-cache-dir
if errorlevel 1 (
    echo WARNING: Some packages failed to install, trying basic setup...
    pip install streamlit --no-cache-dir
)



REM Start the UI
echo.
echo Starting Streamlit UI...
echo The application will open in your browser at http://localhost:5000
echo Press Ctrl+C to stop the application
echo.

python run_ui.py

echo.
echo Application stopped.
pause