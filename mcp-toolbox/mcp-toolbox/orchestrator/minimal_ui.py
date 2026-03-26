import streamlit as st
import os
import sys
import asyncio
from pathlib import Path

# Add orchestrator to path
sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(page_title="Test Case Generator", layout="wide")

st.title("🤖 Multi-Agent RAG Test Case Generator")

# File upload
req_file = st.file_uploader("Requirements Document", type=['pdf', 'txt'])
reg_file = st.file_uploader("Regulatory Document", type=['pdf', 'txt'])

if st.button("Generate Test Cases", type="primary"):
    if req_file and reg_file:
        with st.spinner("Processing..."):
            try:
                # Save files
                temp_dir = Path("temp")
                temp_dir.mkdir(exist_ok=True)
                
                req_path = temp_dir / req_file.name
                reg_path = temp_dir / reg_file.name
                
                with open(req_path, "wb") as f:
                    f.write(req_file.getbuffer())
                with open(reg_path, "wb") as f:
                    f.write(reg_file.getbuffer())
                
                st.success("Files uploaded successfully!")
                st.info("Full processing requires additional dependencies. Use main UI for complete functionality.")
                
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.error("Please upload both files")