@echo off
echo Multi-Agent RAG Test Case Generation System - Windows Installation
echo ================================================================

echo.
echo Step 1: Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment. Please ensure Python 3.8+ is installed.
    pause
    exit /b 1
)

echo.
echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 3: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Step 4: Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies. Check your internet connection.
    pause
    exit /b 1
)

echo.
echo Step 5: Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo Created .env file from template. Please edit it with your credentials.
) else (
    echo .env file already exists.
)

echo.
echo Step 6: Testing installation...
python -c "import chromadb, sentence_transformers, google.cloud.bigquery; print('All core dependencies installed successfully!')"
if errorlevel 1 (
    echo WARNING: Some dependencies may not be properly installed.
)

echo.
echo ================================================================
echo Installation completed!
echo.
echo Next steps:
echo 1. Edit .env file with your credentials
echo 2. Place your PDF documents in this directory
echo 3. Run: python main.py --requirements-doc requirements_doc.pdf --regulatory-doc regulatory_doc.pdf
echo.
echo For detailed setup instructions, see SETUP.md
echo ================================================================
pause