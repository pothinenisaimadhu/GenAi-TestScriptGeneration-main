"""
Simple questions display for testing
"""
import json
import os

def show_questions():
    questions_file = "temp_questions.json"
    
    if os.path.exists(questions_file):
        with open(questions_file, 'r') as f:
            questions = json.load(f)
        
        print(f"\n=== {len(questions)} QUESTIONS GENERATED ===")
        
        answers = {}
        for i, q in enumerate(questions, 1):
            print(f"\n{i}. {q['question']}")
            print(f"   Category: {q['category']} | Priority: {q['priority']}")
            print(f"   Reason: {q['reason']}")
            
            answer = input("   Your answer: ").strip()
            if answer:
                answers[f"{q['category']}_{i}"] = {
                    "category": q['category'],
                    "question": q['question'],
                    "answer": answer,
                    "priority": q['priority']
                }
        
        # Save answers
        with open("temp_answers.json", 'w') as f:
            json.dump(answers, f)
        
        print(f"\n✅ Saved {len(answers)} answers")
        return answers
    else:
        print("❌ No questions file found")
        return {}

if __name__ == "__main__":
    show_questions()