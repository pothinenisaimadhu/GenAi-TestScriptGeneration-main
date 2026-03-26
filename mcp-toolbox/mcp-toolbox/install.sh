#!/bin/bash

echo "Multi-Agent RAG Test Case Generation System - Linux/Mac Installation"
echo "=================================================================="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
if [[ $(echo "$python_version >= 3.8" | bc -l) -eq 0 ]]; then
    echo "ERROR: Python 3.8+ required. Current version: $python_version"
    exit 1
fi

echo
echo "Step 1: Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo
echo "Step 2: Activating virtual environment..."
source venv/bin/activate

echo
echo "Step 3: Upgrading pip..."
python -m pip install --upgrade pip

echo
echo "Step 4: Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo
echo "Step 5: Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from template. Please edit it with your credentials."
else
    echo ".env file already exists."
fi

echo
echo "Step 6: Testing installation..."
python -c "import chromadb, sentence_transformers, google.cloud.bigquery; print('All core dependencies installed successfully!')"
if [ $? -ne 0 ]; then
    echo "WARNING: Some dependencies may not be properly installed."
fi

echo
echo "=================================================================="
echo "Installation completed!"
echo
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Place your PDF documents in this directory"
echo "3. Run: python main.py --requirements-doc requirements_doc.pdf --regulatory-doc regulatory_doc.pdf"
echo
echo "For detailed setup instructions, see SETUP.md"
echo "=================================================================="