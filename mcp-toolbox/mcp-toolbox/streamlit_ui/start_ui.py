#!/usr/bin/env python3
"""
Startup script for the Multi-Agent RAG Test Case Generator UI
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the Streamlit UI"""
    
    # Get the current directory
    current_dir = Path(__file__).parent
    
    # Set environment variables if not already set
    env_vars = {
        'PYTHONPATH': str(current_dir.parent / 'orchestrator'),
        'STREAMLIT_SERVER_PORT': '5000',
        'STREAMLIT_SERVER_ADDRESS': '0.0.0.0'
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
    
    # Change to the UI directory
    os.chdir(current_dir)
    
    # Run Streamlit
    try:
        print("Starting Multi-Agent RAG Test Case Generator UI...")
        print(f"UI will be available at: http://localhost:5000")
        
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port', '5000',
            '--server.address', 'localhost'
        ], check=True)
        
    except KeyboardInterrupt:
        print("\nShutting down UI...")
    except subprocess.CalledProcessError as e:
        print(f"Error starting UI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()