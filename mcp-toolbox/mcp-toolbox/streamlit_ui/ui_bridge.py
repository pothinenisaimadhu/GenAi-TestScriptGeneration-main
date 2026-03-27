"""
Bridge between Streamlit UI and orchestrator main.py
"""
import os
import sys
import asyncio
import subprocess
from pathlib import Path

# Add orchestrator to path
orchestrator_path = os.path.join(os.path.dirname(__file__), '..', 'orchestrator')
sys.path.insert(0, orchestrator_path)

print(f"INFO: UI Bridge - Using orchestrator path: {orchestrator_path}")

def run_main_with_ui_files(req_file, reg_file, intelligent_analysis=False):
    """Run main.py with uploaded files from UI"""
    
    # Save uploaded files to orchestrator's temp directory (where main.py runs)
    temp_dir = Path(orchestrator_path) / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    # Use original filenames if available
    req_filename = getattr(req_file, 'name', 'requirements_doc.pdf')
    reg_filename = getattr(reg_file, 'name', 'regulatory_doc.pdf')
    
    req_path = temp_dir / req_filename
    reg_path = temp_dir / reg_filename
    
    # Save uploaded files
    if hasattr(req_file, 'getbuffer'):
        with open(req_path, "wb") as f:
            f.write(req_file.getbuffer())
    elif hasattr(req_file, 'read'):
        with open(req_path, "wb") as f:
            f.write(req_file.read())
    
    if hasattr(reg_file, 'getbuffer'):
        with open(reg_path, "wb") as f:
            f.write(reg_file.getbuffer())
    elif hasattr(reg_file, 'read'):
        with open(reg_path, "wb") as f:
            f.write(reg_file.read())
    
    # Set environment variable for UI mode
    env = os.environ.copy()
    env['STREAMLIT_UI_MODE'] = 'true'
    
    # Build command to run main.py with uploaded files
    cmd = [
        sys.executable, 
        os.path.join(orchestrator_path, "main.py"),
        "--requirements-doc", str(req_path),
        "--regulatory-doc", str(reg_path)
    ]
    
    if intelligent_analysis:
        cmd.append("--intelligent-analysis")
    
    # Run command with UI environment
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=orchestrator_path, env=env)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def check_questions_available():
    """Check if questions are available for display"""
    questions_file = os.path.join(orchestrator_path, "temp_questions.json")
    return os.path.exists(questions_file)

def get_questions():
    """Get questions from orchestrator"""
    import json
    questions_file = os.path.join(orchestrator_path, "temp_questions.json")
    
    if os.path.exists(questions_file):
        with open(questions_file, 'r') as f:
            return json.load(f)
    return []

def save_answers(answers):
    """Save answers to orchestrator"""
    import json
    answers_file = os.path.join(orchestrator_path, "temp_answers.json")
    
    with open(answers_file, 'w') as f:
        json.dump(answers, f)
    
    return True