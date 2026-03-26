"""
Streamlit UI for displaying LLM-generated questions
"""
import streamlit as st
import json
import os
import time
from typing import List, Dict, Any

def display_questions_ui(questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Save questions for UI display"""
    if questions:
        questions_file = "temp_questions.json"
        with open(questions_file, 'w') as f:
            json.dump(questions, f)
        print(f"\nGenerated {len(questions)} questions for UI display")
    return {}

def main():
    """Streamlit app main function"""
    st.title("LLM Test Case Improvement Questions")
    st.write("Please answer the questions below to improve your test case")
    
    # Load questions
    if os.path.exists("temp_questions.json"):
        with open("temp_questions.json", 'r') as f:
            questions = json.load(f)
        
        answers = {}
        
        for i, q in enumerate(questions):
            st.subheader(f"{i+1}. {q['question']}")
            st.write(f"**Category:** {q['category']} | **Priority:** {q['priority']}")
            st.write(f"**Reason:** {q['reason']}")
            
            answer = st.text_area(f"Your answer for question {i+1}:", key=f"answer_{i}")
            
            if answer.strip():
                answers[f"{q['category']}_{i+1}"] = {
                    "category": q['category'],
                    "question": q['question'],
                    "answer": answer,
                    "priority": q['priority']
                }
        
        if st.button("Submit Answers"):
            with open("temp_answers.json", 'w') as f:
                json.dump(answers, f)
            st.success("Answers submitted successfully!")
            st.write("You can close this window now.")
    else:
        st.warning("No questions file found. Please run the main system first.")

if __name__ == "__main__":
    main()