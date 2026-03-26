@echo off
echo Starting UI with minimal setup...

REM Install only essential packages
pip install streamlit --quiet

REM Start directly with streamlit
echo Opening UI at http://localhost:8508
streamlit run streamlit_ui.py --server.port=8508 --browser.gatherUsageStats=false

pause