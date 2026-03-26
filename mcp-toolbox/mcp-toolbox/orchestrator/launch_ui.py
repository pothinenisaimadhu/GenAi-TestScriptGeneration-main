#!/usr/bin/env python3
"""
Simple UI launcher for questions
"""
import os
import sys
import subprocess
import webbrowser
import time

def launch_questions_ui():
    """Launch Streamlit UI for questions"""
    try:
        # Get paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        streamlit_dir = os.path.join(current_dir, "..", "streamlit_ui")
        app_path = os.path.join(streamlit_dir, "app.py")
        
        if not os.path.exists(app_path):
            print("ERROR: Streamlit app not found")
            return False
        
        print("Launching Streamlit UI...")
        
        # Launch Streamlit
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless=true"],
            cwd=streamlit_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Open browser
        webbrowser.open("http://localhost:8501")
        
        print("UI opened at http://localhost:8501")
        print("Please answer the questions in your browser")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to launch UI: {e}")
        return False

if __name__ == "__main__":
    launch_questions_ui()