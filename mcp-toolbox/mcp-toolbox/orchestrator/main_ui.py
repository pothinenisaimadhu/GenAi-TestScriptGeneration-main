"""
UI-integrated main script that works with Streamlit
"""
import os
import sys
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add orchestrator to path
sys.path.insert(0, os.path.dirname(__file__))

import tools
from orchestrator import WorkflowOrchestrator

async def run_pipeline_from_ui(requirements_text: str, regulatory_doc_path: str, intelligent_analysis: bool = False):
    """
    Run pipeline with text input from UI instead of file paths
    """
    print("=== STARTING UI-INTEGRATED PIPELINE ===")
    
    try:
        # Initialize orchestrator with error handling
        orchestrator = WorkflowOrchestrator()
        
        # Apply intelligent analysis if enabled
        if intelligent_analysis:
            print("\n=== INTELLIGENT ANALYSIS ENABLED ===")
            enhanced_text = await apply_intelligent_analysis(requirements_text)
            if enhanced_text == "QUESTIONS_GENERATED":
                print("INFO: Questions generated - UI will display them")
                return {"success": True, "questions_generated": True, "original_text": requirements_text}
            elif enhanced_text:
                requirements_text = enhanced_text
                print("INFO: Requirements enhanced with user input")
        
        # Execute multi-agent workflow
        workflow_results = await orchestrator.execute_workflow(requirements_text, regulatory_doc_path)
        
        return workflow_results
        
    except Exception as e:
        print(f"ERROR: Pipeline execution failed: {e}")
        # Return a basic result for UI display
        return {
            "success": False,
            "error": str(e),
            "processed_requirements": 0,
            "test_cases_generated": 0,
            "message": "Pipeline failed due to configuration issues. Please check your environment setup."
        }

async def apply_intelligent_analysis(raw_text: str) -> str:
    """Apply intelligent analysis with LLM questions"""
    try:
        # Check if user answers already exist
        answers_file = "temp_answers.json"
        if os.path.exists(answers_file):
            print("INFO: Using existing user answers")
            with open(answers_file, 'r') as f:
                user_answers = json.load(f)
            
            # Enhance requirement with user answers
            enhanced_req = enhance_requirement_with_answers(raw_text, user_answers)
            
            # Clean up temp files
            cleanup_temp_files()
            return enhanced_req
        
        # Generate fallback questions
        questions = generate_fallback_questions(raw_text)
        
        if questions:
            # Save questions for UI
            questions_file = "temp_questions.json"
            with open(questions_file, 'w') as f:
                json.dump(questions, f, indent=2)
            
            print(f"INFO: Generated {len(questions)} questions for UI display")
            return "QUESTIONS_GENERATED"
        else:
            print("INFO: No questions generated, using original text")
            return raw_text
            
    except Exception as e:
        print(f"ERROR: Intelligent analysis failed: {e}")
        return raw_text

def enhance_requirement_with_answers(original_text: str, user_answers: dict) -> str:
    """Enhance requirement text with user answers"""
    enhancements = []
    
    for answer_id, answer_data in user_answers.items():
        if isinstance(answer_data, dict) and answer_data.get('answer'):
            question = answer_data.get('question', answer_id)
            answer = answer_data.get('answer')
            enhancements.append(f"{question}: {answer}")
    
    if enhancements:
        enhanced_text = f"{original_text}\n\nAdditional Details:\n" + "\n".join(enhancements)
        return enhanced_text
    
    return original_text

def generate_fallback_questions(requirement_text: str) -> list:
    """Generate simple fallback questions based on requirement content"""
    text_lower = requirement_text.lower()
    questions = []
    
    # Domain detection
    if any(word in text_lower for word in ['security', 'auth', 'encrypt', 'access']):
        questions.extend([
            {
                "id": "security_1",
                "question": "What specific security measures need to be tested?",
                "type": "text",
                "category": "Security",
                "priority": "high"
            },
            {
                "id": "security_2",
                "question": "Are there any authentication requirements?",
                "type": "multiple_choice",
                "options": ["Yes", "No", "Not specified"],
                "category": "Security",
                "priority": "medium"
            }
        ])
    
    if any(word in text_lower for word in ['performance', 'speed', 'load', 'time']):
        questions.append({
            "id": "performance_1",
            "question": "What are the expected performance criteria?",
            "type": "text",
            "category": "Performance",
            "priority": "high"
        })
    
    if any(word in text_lower for word in ['ui', 'interface', 'user', 'display']):
        questions.append({
            "id": "ui_1",
            "question": "What user interface elements need validation?",
            "type": "text",
            "category": "UI",
            "priority": "medium"
        })
    
    # Always add general questions
    questions.extend([
        {
            "id": "general_1",
            "question": "Are there any edge cases or error conditions to consider?",
            "type": "text",
            "category": "General",
            "priority": "medium"
        },
        {
            "id": "general_2",
            "question": "What test data or scenarios are needed?",
            "type": "text",
            "category": "General",
            "priority": "low"
        }
    ])
    
    return questions[:4]  # Limit to 4 questions

def cleanup_temp_files():
    """Clean up temporary files"""
    temp_files = ["temp_questions.json", "temp_answers.json"]
    for file in temp_files:
        try:
            if os.path.exists(file):
                os.remove(file)
        except Exception as e:
            print(f"Warning: Could not remove {file}: {e}")

def process_uploaded_files(req_file, reg_file, intelligent_analysis=False):
    """Process files uploaded through Streamlit UI"""
    
    # Save uploaded files temporarily
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    # Determine file extensions
    req_name = getattr(req_file, 'name', 'requirements_doc.pdf')
    reg_name = getattr(reg_file, 'name', 'regulatory_doc.pdf')
    
    req_path = temp_dir / req_name
    reg_path = temp_dir / reg_name
    
    # Save requirement file
    if hasattr(req_file, 'getbuffer'):
        with open(req_path, "wb") as f:
            f.write(req_file.getbuffer())
    
    # Save regulatory file
    if hasattr(reg_file, 'getbuffer'):
        with open(reg_path, "wb") as f:
            f.write(reg_file.getbuffer())
    
    # Extract text from requirements based on file type
    req_text = extract_text_from_file(req_path)
    
    if not req_text or len(req_text.strip()) < 10:
        req_text = "Sample requirements text for testing"
    
    # Run pipeline
    return asyncio.run(run_pipeline_from_ui(req_text, str(reg_path), intelligent_analysis))

def extract_text_from_file(file_path: Path) -> str:
    """Extract text from uploaded file based on extension"""
    try:
        file_ext = file_path.suffix.lower()
        
        if file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        
        elif file_ext == '.pdf':
            import fitz
            with fitz.open(file_path) as doc:
                return "".join(page.get_text() for page in doc)
        
        else:
            # Try to read as text file
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
                
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return ""