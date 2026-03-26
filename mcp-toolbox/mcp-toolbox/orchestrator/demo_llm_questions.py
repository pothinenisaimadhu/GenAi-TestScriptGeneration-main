#!/usr/bin/env python3
"""
Demo script showing LLM-powered question generation for requirement analysis.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_question_generator import llm_question_generator
import json

def demo_question_generation():
    """Demonstrate LLM question generation with sample requirements."""
    
    sample_requirements = [
        {
            "text": "The system must authenticate users securely",
            "domain": "security"
        },
        {
            "text": "All user data must be encrypted and comply with GDPR regulations for data protection",
            "domain": "compliance"
        },
        {
            "text": "The application should respond to user requests within reasonable time",
            "domain": "performance"
        },
        {
            "text": "Create a comprehensive audit trail system that logs all user activities and system changes for regulatory compliance, ensuring data integrity and providing detailed reporting capabilities for compliance officers",
            "domain": "compliance"
        }
    ]
    
    print("🤖 LLM-POWERED QUESTION GENERATION DEMO")
    print("=" * 50)
    
    for i, req in enumerate(sample_requirements, 1):
        print(f"\n📋 REQUIREMENT {i}:")
        print(f"Text: {req['text']}")
        print(f"Domain: {req['domain']}")
        print("-" * 40)
        
        # Generate questions
        questions = llm_question_generator.generate_questions(req['text'], req['domain'])
        
        print(f"Generated {len(questions)} questions:")
        for j, q in enumerate(questions, 1):
            print(f"\n  {j}. {q['question']}")
            print(f"     Category: {q['category']} | Priority: {q['priority']}")
            print(f"     Reason: {q['reason']}")
        
        # Simulate answers for demo
        print(f"\n🎯 SIMULATED ANSWERS:")
        sample_answers = _generate_sample_answers(questions)
        
        for category, answer_data in sample_answers.items():
            print(f"  {category}: {answer_data['answer']}")
        
        # Show how test case would be updated
        original_test_case = {
            "summary": f"Test case for: {req['text'][:50]}...",
            "description": f"Basic test case for requirement: {req['text']}"
        }
        
        updated_test_case = llm_question_generator.update_test_case(original_test_case, sample_answers)
        
        print(f"\n📝 ENHANCED TEST CASE:")
        print(json.dumps(updated_test_case, indent=2))
        
        if i < len(sample_requirements):
            input("\nPress Enter to continue to next requirement...")

def _generate_sample_answers(questions):
    """Generate sample answers for demo purposes."""
    sample_answers = {}
    
    for q in questions[:3]:  # Answer first 3 questions
        category = q['category']
        
        if category == "test_steps":
            sample_answers[category] = {
                "question": q['question'],
                "answer": "1. Setup test environment 2. Execute validation 3. Verify results",
                "priority": q['priority']
            }
        elif category == "acceptance":
            sample_answers[category] = {
                "question": q['question'],
                "answer": "Test passes when all validation criteria are met and no errors occur",
                "priority": q['priority']
            }
        elif category == "test_data":
            sample_answers[category] = {
                "question": q['question'],
                "answer": "Valid user credentials, test datasets, and edge case scenarios",
                "priority": q['priority']
            }
        elif category == "clarification":
            sample_answers[category] = {
                "question": q['question'],
                "answer": "Specific measurable criteria defined with clear thresholds",
                "priority": q['priority']
            }
        elif category == "prerequisites":
            sample_answers[category] = {
                "question": q['question'],
                "answer": "Test environment setup, required permissions, and test data preparation",
                "priority": q['priority']
            }
    
    return sample_answers

def interactive_demo():
    """Interactive demo where user can input their own requirement."""
    print("\n🎮 INTERACTIVE DEMO")
    print("=" * 30)
    
    try:
        requirement = input("Enter your requirement: ").strip()
        if not requirement:
            print("No requirement entered. Using default.")
            requirement = "The system must validate user input and provide appropriate error messages"
        
        domain = input("Enter domain (security/compliance/performance/ui/general): ").strip().lower()
        if domain not in ['security', 'compliance', 'performance', 'ui', 'general']:
            domain = 'general'
        
        print(f"\n🔍 Analyzing requirement...")
        questions = llm_question_generator.generate_questions(requirement, domain)
        
        if questions:
            print(f"\n✅ Generated {len(questions)} questions!")
            answers = llm_question_generator.collect_answers(questions)
            
            if answers:
                print(f"\n📊 Collected {len(answers)} answers!")
                
                # Create and update test case
                original_test_case = {
                    "summary": f"Test case for: {requirement[:50]}...",
                    "description": f"Test case for requirement: {requirement}"
                }
                
                updated_test_case = llm_question_generator.update_test_case(original_test_case, answers)
                
                print(f"\n🎯 FINAL ENHANCED TEST CASE:")
                print(json.dumps(updated_test_case, indent=2))
            else:
                print("No answers collected.")
        else:
            print("No questions generated.")
            
    except KeyboardInterrupt:
        print("\nDemo cancelled.")
    except Exception as e:
        print(f"Error in interactive demo: {e}")

if __name__ == "__main__":
    print("Choose demo mode:")
    print("1. Automated demo with sample requirements")
    print("2. Interactive demo with your requirement")
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            demo_question_generation()
        elif choice == "2":
            interactive_demo()
        else:
            print("Invalid choice. Running automated demo.")
            demo_question_generation()
            
    except KeyboardInterrupt:
        print("\nDemo cancelled.")
    except Exception as e:
        print(f"Demo error: {e}")