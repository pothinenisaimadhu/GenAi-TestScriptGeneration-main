import streamlit as st
import json
import os
from typing import List, Dict, Any

def show_questions_ui():
    """Display LLM questions in Streamlit UI"""
    st.header("🤖 LLM Test Case Questions")
    
    questions_file = "../orchestrator/temp_questions.json"
    
    if not os.path.exists(questions_file):
        st.warning("No questions available. Run the orchestrator first.")
        return
    
    with open(questions_file, 'r') as f:
        questions = json.load(f)
    
    st.write(f"📝 {len(questions)} questions generated to improve your test case")
    
    answers = {}
    
    for i, q in enumerate(questions):
        with st.expander(f"Question {i+1}: {q['category'].title()}", expanded=True):
            st.write(f"**{q['question']}**")
            st.write(f"Priority: {q['priority']} | Reason: {q['reason']}")
            
            answer = st.text_area(
                "Your answer:",
                key=f"answer_{i}",
                placeholder="Enter your answer here..."
            )
            
            if answer.strip():
                answers[f"{q['category']}_{i+1}"] = {
                    "category": q['category'],
                    "question": q['question'],
                    "answer": answer,
                    "priority": q['priority']
                }
    
    if st.button("Submit Answers", type="primary"):
        if answers:
            answers_file = "../orchestrator/temp_answers.json"
            with open(answers_file, 'w') as f:
                json.dump(answers, f)
            st.success("✅ Answers submitted successfully!")
            st.balloons()
        else:
            st.warning("Please answer at least one question.")

def clear_questions_state():
    """Clear questions state"""
    files_to_remove = [
        "../orchestrator/temp_questions.json",
        "../orchestrator/temp_answers.json"
    ]
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)