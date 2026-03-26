"""
UI Question Handler for intelligent requirement analysis
Integrates with LLM question generator and Streamlit interface
"""
import json
import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add orchestrator to path
sys.path.insert(0, os.path.dirname(__file__))

def generate_ui_questions(requirement_text: str, domain: str = "general") -> List[Dict[str, Any]]:
    """Generate questions for UI display"""
    try:
        from llm_question_generator import llm_question_generator
        
        # Generate LLM-powered questions
        questions = llm_question_generator.generate_questions(requirement_text, domain)
        
        if questions:
            # Convert to UI-friendly format
            ui_questions = []
            for i, (category, question_data) in enumerate(questions.items()):
                ui_question = {
                    'id': category,
                    'question': question_data.get('question', ''),
                    'type': question_data.get('type', 'text'),
                    'options': question_data.get('options', []),
                    'category': category,
                    'priority': question_data.get('priority', 'medium')
                }
                ui_questions.append(ui_question)
            
            # Save questions to temporary file for UI
            save_questions_for_ui(ui_questions)
            return ui_questions
        
    except ImportError:
        print("LLM question generator not available, using fallback questions")
    except Exception as e:
        print(f"Error generating LLM questions: {e}")
    
    # Fallback to basic questions
    return generate_fallback_questions(requirement_text, domain)

def generate_fallback_questions(requirement_text: str, domain: str) -> List[Dict[str, Any]]:
    """Generate fallback questions when LLM is not available"""
    
    # Domain-specific question templates
    domain_questions = {
        "security": [
            {
                'id': 'auth_method',
                'question': 'What authentication method should be used?',
                'type': 'multiple_choice',
                'options': ['Username/Password', 'Multi-factor', 'SSO', 'Certificate-based'],
                'category': 'security'
            },
            {
                'id': 'data_encryption',
                'question': 'What level of data encryption is required?',
                'type': 'multiple_choice',
                'options': ['None', 'Basic (AES-128)', 'Strong (AES-256)', 'End-to-end'],
                'category': 'security'
            }
        ],
        "performance": [
            {
                'id': 'response_time',
                'question': 'What is the maximum acceptable response time?',
                'type': 'text',
                'category': 'performance'
            },
            {
                'id': 'concurrent_users',
                'question': 'How many concurrent users should the system support?',
                'type': 'text',
                'category': 'performance'
            }
        ],
        "compliance": [
            {
                'id': 'regulatory_standard',
                'question': 'Which regulatory standards must be met?',
                'type': 'multiple_choice',
                'options': ['GDPR', 'HIPAA', 'SOX', 'FDA 21 CFR Part 11', 'ISO 27001'],
                'category': 'compliance'
            },
            {
                'id': 'audit_requirements',
                'question': 'What audit trail requirements are needed?',
                'type': 'text',
                'category': 'compliance'
            }
        ],
        "ui": [
            {
                'id': 'user_interface',
                'question': 'What type of user interface is required?',
                'type': 'multiple_choice',
                'options': ['Web-based', 'Desktop application', 'Mobile app', 'API only'],
                'category': 'ui'
            },
            {
                'id': 'accessibility',
                'question': 'What accessibility requirements must be met?',
                'type': 'text',
                'category': 'ui'
            }
        ]
    }
    
    # General questions for any domain
    general_questions = [
        {
            'id': 'test_data',
            'question': 'What specific test data is needed for validation?',
            'type': 'text',
            'category': 'general'
        },
        {
            'id': 'prerequisites',
            'question': 'What are the prerequisites for testing this requirement?',
            'type': 'text',
            'category': 'general'
        },
        {
            'id': 'acceptance_criteria',
            'question': 'What are the specific acceptance criteria?',
            'type': 'text',
            'category': 'general'
        }
    ]
    
    # Select questions based on domain
    questions = domain_questions.get(domain, []) + general_questions
    
    # Add priority and ensure all required fields
    for question in questions:
        question['priority'] = question.get('priority', 'medium')
        if 'options' not in question:
            question['options'] = []
    
    # Save questions for UI
    save_questions_for_ui(questions)
    return questions

def save_questions_for_ui(questions: List[Dict[str, Any]]):
    """Save questions to temporary file for UI consumption"""
    questions_data = {
        'questions': questions,
        'timestamp': str(os.path.getmtime(__file__) if os.path.exists(__file__) else 0),
        'total_count': len(questions)
    }
    
    try:
        with open('temp_questions.json', 'w') as f:
            json.dump(questions_data, f, indent=2)
        print(f"Saved {len(questions)} questions for UI display")
    except Exception as e:
        print(f"Error saving questions: {e}")

def load_user_answers() -> Dict[str, Any]:
    """Load user answers from temporary file"""
    try:
        if os.path.exists('temp_answers.json'):
            with open('temp_answers.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading user answers: {e}")
    
    return {}

def process_user_answers(answers: Dict[str, Any]) -> Dict[str, Any]:
    """Process and validate user answers"""
    processed_answers = {}
    
    for answer_id, answer_data in answers.items():
        if isinstance(answer_data, dict):
            # Validate answer data
            if answer_data.get('answer') and str(answer_data['answer']).strip():
                processed_answers[answer_id] = {
                    'question': answer_data.get('question', ''),
                    'answer': str(answer_data['answer']).strip(),
                    'type': answer_data.get('type', 'text'),
                    'category': answer_data.get('category', 'general')
                }
    
    return processed_answers

def enhance_requirement_with_ui_answers(original_requirement: str, answers: Dict[str, Any]) -> str:
    """Enhance requirement text with UI-collected answers"""
    if not answers:
        return original_requirement
    
    processed_answers = process_user_answers(answers)
    
    if not processed_answers:
        return original_requirement
    
    # Group answers by category
    categorized_answers = {}
    for answer_id, answer_data in processed_answers.items():
        category = answer_data.get('category', 'general')
        if category not in categorized_answers:
            categorized_answers[category] = []
        categorized_answers[category].append(answer_data)
    
    # Build enhancement text
    enhancement_parts = [original_requirement]
    enhancement_parts.append("\n--- Enhanced Details ---")
    
    for category, category_answers in categorized_answers.items():
        if category_answers:
            enhancement_parts.append(f"\n{category.title()} Requirements:")
            for answer_data in category_answers:
                question = answer_data['question']
                answer = answer_data['answer']
                enhancement_parts.append(f"- {question}: {answer}")
    
    return "\n".join(enhancement_parts)

def cleanup_ui_temp_files():
    """Clean up temporary files created for UI"""
    temp_files = ['temp_questions.json', 'temp_answers.json']
    
    for file_path in temp_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Cleaned up {file_path}")
        except Exception as e:
            print(f"Warning: Could not remove {file_path}: {e}")

def get_question_statistics(answers: Dict[str, Any]) -> Dict[str, Any]:
    """Get statistics about answered questions"""
    if not answers:
        return {
            'total_questions': 0,
            'answered_questions': 0,
            'completion_rate': 0.0,
            'categories': {}
        }
    
    processed_answers = process_user_answers(answers)
    
    # Count by category
    category_stats = {}
    for answer_data in processed_answers.values():
        category = answer_data.get('category', 'general')
        if category not in category_stats:
            category_stats[category] = 0
        category_stats[category] += 1
    
    # Load original questions to get total count
    total_questions = 0
    try:
        if os.path.exists('temp_questions.json'):
            with open('temp_questions.json', 'r') as f:
                questions_data = json.load(f)
                total_questions = len(questions_data.get('questions', []))
    except Exception:
        pass
    
    answered_questions = len(processed_answers)
    completion_rate = (answered_questions / total_questions) if total_questions > 0 else 0.0
    
    return {
        'total_questions': total_questions,
        'answered_questions': answered_questions,
        'completion_rate': completion_rate,
        'categories': category_stats
    }

# Test function for development
def test_question_generation():
    """Test question generation functionality"""
    test_requirement = "The system must authenticate users securely and maintain audit logs for compliance."
    
    print("Testing question generation...")
    questions = generate_ui_questions(test_requirement, "security")
    
    print(f"Generated {len(questions)} questions:")
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q['question']} (Type: {q['type']}, Category: {q['category']})")
    
    return questions

if __name__ == "__main__":
    test_question_generation()