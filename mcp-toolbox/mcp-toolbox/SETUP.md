# Quick Setup Guide

## 1. System Requirements

- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 2GB free space
- **Internet**: Required for ChromaDB Cloud, Jira, and BigQuery

## 2. Installation Steps

### Step 1: Clone and Setup Environment
```bash
# Navigate to project directory
cd mcp-toolbox/orchestrator

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
# Use any text editor to fill in the required values
```

### Step 3: Google Cloud Setup
```bash
# Install Google Cloud SDK (if not already installed)
# Download from: https://cloud.google.com/sdk/docs/install

# Authenticate with Google Cloud
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
```

### Step 4: Prepare Documents
```bash
# Place your documents in the orchestrator directory:
# - requirements_doc.pdf (your requirements document)
# - regulatory_doc.pdf (regulatory compliance document)
```

### Step 5: Test Installation
```bash
# Run health check
python -c "from health_check import check_system_health; print(check_system_health())"

# Run the system
python main.py --requirements-doc requirements_doc.pdf --regulatory-doc regulatory_doc.pdf
```

## 3. Required Credentials

### Google Cloud Project
1. Create project at https://console.cloud.google.com
2. Enable BigQuery and Storage APIs
3. Create service account or use application default credentials

### Jira API Token
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Create new token
3. Use your email as JIRA_USER and token as JIRA_TOKEN

### ChromaDB Cloud (Optional)
1. Sign up at https://www.trychroma.com
2. Create database and get API credentials
3. If not configured, system uses local ChromaDB

## 4. Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip list` shows required packages)
- [ ] .env file configured with your credentials
- [ ] Google Cloud authentication working
- [ ] Documents (requirements_doc.pdf, regulatory_doc.pdf) in place
- [ ] Health check passes
- [ ] System runs without errors

## 5. Common Setup Issues

### Issue: "No module named 'sentence_transformers'"
**Solution**: `pip install sentence-transformers`

### Issue: "Google Cloud authentication error"
**Solution**: Run `gcloud auth application-default login`

### Issue: "ChromaDB connection failed"
**Solution**: Check CHROMA_* variables in .env or let system use local ChromaDB

### Issue: "Jira authentication failed"
**Solution**: Verify JIRA_TOKEN is API token (not password) and JIRA_PROJECT_KEY exists

### Issue: "Permission denied for BigQuery"
**Solution**: Ensure BigQuery API is enabled and you have proper permissions

## 6. Next Steps

After successful setup:
1. Run the system with your documents
2. Review generated test cases in Jira
3. Provide feedback to improve quality
4. Monitor performance metrics
5. Customize configuration as needed

## 7. Support

If you encounter issues:
1. Check the troubleshooting section in README.md
2. Review console output for error messages
3. Run health check to identify specific problems
4. Ensure all credentials are correctly configured