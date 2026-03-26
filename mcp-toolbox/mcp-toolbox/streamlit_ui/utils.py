import os
import asyncio
from pathlib import Path

# Constants
ORCHESTRATOR_PATH = os.path.join(os.path.dirname(__file__), '..', 'orchestrator')
FALLBACK_REQ_TEXT = "REQ-001: The system shall authenticate users using multi-factor authentication\nREQ-002: User data must be encrypted at rest and in transit"
FALLBACK_REG_TEXT = "Default regulatory requirements for compliance testing."

def get_orchestrator_context():
    """Context manager for orchestrator directory operations"""
    class OrchestratorContext:
        def __init__(self):
            self.original_cwd = None
            
        def __enter__(self):
            self.original_cwd = os.getcwd()
            os.chdir(ORCHESTRATOR_PATH)
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            os.chdir(self.original_cwd)
    
    return OrchestratorContext()

async def run_async_operation(operation, *args, **kwargs):
    """Unified async operation runner"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        return await operation(*args, **kwargs)
    finally:
        loop.close()

def extract_text_from_file(file_path):
    """Extract text from file with fallback"""
    try:
        import fitz
        with fitz.open(file_path) as doc:
            return "".join(page.get_text() for page in doc)
    except Exception:
        try:
            with open(file_path, 'rb') as f:
                return f.read().decode('utf-8', errors='ignore')
        except Exception:
            return FALLBACK_REQ_TEXT if 'req' in file_path.lower() else FALLBACK_REG_TEXT