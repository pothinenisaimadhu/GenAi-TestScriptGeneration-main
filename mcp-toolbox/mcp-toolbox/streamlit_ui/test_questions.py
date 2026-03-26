import streamlit as st
import json
import os

st.title("Test Questions Display")

questions_file = "../orchestrator/temp_questions.json"

if os.path.exists(questions_file):
    st.success("Questions file found!")
    
    with open(questions_file, 'r') as f:
        questions = json.load(f)
    
    st.write(f"Found {len(questions)} questions:")
    
    for i, q in enumerate(questions):
        with st.expander(f"Question {i+1}: {q['category']}", expanded=True):
            st.write(f"**{q['question']}**")
            st.write(f"Priority: {q['priority']} | Reason: {q['reason']}")
            
            answer = st.text_area(f"Answer {i+1}:", key=f"answer_{i}")
else:
    st.error("Questions file not found")
    st.write(f"Looking for: {questions_file}")
    st.write(f"Current directory: {os.getcwd()}")
    st.write(f"Files in orchestrator: {os.listdir('../orchestrator') if os.path.exists('../orchestrator') else 'Directory not found'}")