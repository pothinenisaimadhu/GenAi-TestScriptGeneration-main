@echo off
echo Stopping any running Streamlit processes...
taskkill /f /im streamlit.exe 2>nul
timeout /t 2 /nobreak >nul

echo Clearing Python cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

echo Starting Streamlit with fresh environment...
streamlit run streamlit_ui.py