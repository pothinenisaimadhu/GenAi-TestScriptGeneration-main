#!/bin/bash

echo "Starting Multi-Agent RAG Test Case Generator UI"
echo "==============================================="

echo "Installing Streamlit dependencies..."
pip install -r requirements.txt

echo
echo "Starting Streamlit app..."
streamlit run app.py --server.port 5000 --server.address localhost