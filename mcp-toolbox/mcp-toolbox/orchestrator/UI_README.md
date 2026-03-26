# Multi-Agent RAG Test Case Generator - Interactive UI

A comprehensive web-based interface for the Multi-Agent RAG Test Case Generation System, built with Streamlit.

## 🌟 Features

### Core Functionality
- **📁 Document Upload**: Support for PDF and TXT files
- **🤖 Intelligent Analysis**: AI-powered question generation for requirement clarification
- **📊 Real-time Dashboard**: System health, performance metrics, and analytics
- **💬 Interactive Questions**: Domain-specific questions with smart categorization
- **📋 Test Case Generation**: Multi-agent workflow with compliance validation
- **🔄 Feedback Loop**: User feedback collection and system improvement

### User Interface
- **🎨 Modern Design**: Clean, responsive interface with custom styling
- **📱 Multi-page Navigation**: Home, Dashboard, and Documentation pages
- **📈 Visual Analytics**: Charts and metrics using Plotly
- **⚡ Real-time Updates**: Live progress tracking and status updates
- **🔧 Configuration Management**: Environment status and system health monitoring

## 🚀 Quick Start

### Option 1: Windows Batch Script (Recommended)
```bash
# Simply double-click or run:
start_ui.bat
```

### Option 2: Python Script
```bash
python run_ui.py
```

### Option 3: Direct Streamlit
```bash
pip install -r requirements_ui.txt
streamlit run streamlit_ui.py
```

## 📋 Prerequisites

### Required Software
- Python 3.8 or higher
- pip (Python package manager)

### Required Python Packages
```bash
pip install -r requirements_ui.txt
```

Key packages include:
- `streamlit>=1.28.0` - Web interface framework
- `PyMuPDF>=1.23.0` - PDF processing
- `sentence-transformers>=2.2.2` - AI embeddings
- `chromadb>=0.4.15` - Vector database
- `google-cloud-storage>=2.10.0` - Cloud storage
- `plotly>=5.17.0` - Interactive charts

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the orchestrator directory:

```env
# Required - Google Cloud Configuration
GOOGLE_PROJECT_ID="your-project-id"
GCS_BUCKET="your-bucket-name"
BIGQUERY_DATASET="your-dataset"

# Optional - ChromaDB Cloud
CHROMA_API_KEY="your-chroma-api-key"
CHROMA_TENANT="your-tenant-id"
CHROMA_DATABASE="your-database"

# Optional - Jira Integration
JIRA_API_URL="https://your-domain.atlassian.net"
JIRA_USER="your-email@domain.com"
JIRA_TOKEN="your-jira-api-token"
JIRA_PROJECT_KEY="YOUR-PROJECT"
```

### Directory Structure
```
orchestrator/
├── streamlit_ui.py          # Main UI application
├── ui_dashboard.py          # Dashboard components
├── ui_question_handler.py   # Question generation and handling
├── main_ui.py              # Backend integration
├── run_ui.py               # Launcher script
├── start_ui.bat            # Windows batch launcher
├── requirements_ui.txt     # UI-specific dependencies
├── temp/                   # Temporary uploaded files
├── user_feedback/          # User feedback storage
├── generated_testcases/    # Generated test cases
├── traceability_logs/      # Traceability information
└── chroma/                 # Local ChromaDB storage
```

## 🎯 How to Use

### 1. Upload Documents
- **Requirements Document**: Upload your requirements in PDF or TXT format
- **Regulatory Document**: Upload regulatory compliance documentation

### 2. Configure Options
- **Enable Intelligent Analysis**: Turn on AI-powered question generation
- **Collection Name**: Specify ChromaDB collection name (default: "regulatory_docs")

### 3. Answer Questions (Optional)
When intelligent analysis is enabled:
- Questions are categorized by domain (Security, Performance, Compliance, UI, General)
- Priority indicators show question importance (🔴 High, 🟡 Medium, 🟢 Low)
- Progress tracking shows completion status
- Save draft functionality for partial completion

### 4. Review Results
- **Test Cases**: Generated with compliance validation
- **Performance Metrics**: Quality scores, processing time, success rates
- **Traceability**: Links between requirements and regulatory documents
- **Compliance Status**: Validation results with scoring

### 5. Provide Feedback
- Rate overall quality, completeness, and clarity
- Add comments for improvement
- Feedback is stored for system learning

## 📊 Dashboard Features

### System Health
- **Component Status**: Database, Vector Store, LLM Service, Jira Integration
- **Overall Health Score**: Percentage-based system health indicator
- **Storage Usage**: File counts and disk usage by category

### Performance Analytics
- **Trend Charts**: Test case generation over time
- **Quality Metrics**: Distribution of quality ratings
- **Performance Charts**: Processing time analysis
- **Success Rates**: System performance tracking

### Recent Activity
- **Activity Log**: Recent test case generations and feedback
- **Timestamp Tracking**: When activities occurred
- **Status Indicators**: Success/failure status

### Configuration Status
- **Environment Variables**: Current configuration status
- **Service Connectivity**: Connection status to external services
- **Storage Information**: Local storage usage statistics

## 🔧 Advanced Features

### Intelligent Question Generation
- **Domain Detection**: Automatic detection of requirement domain
- **LLM Integration**: Uses language models for smart question generation
- **Fallback Questions**: Domain-specific templates when LLM unavailable
- **Question Categorization**: Organized by functional areas

### Multi-Agent Integration
- **Document Parser Agent**: Extracts and processes requirements
- **Test Generator Agent**: Creates comprehensive test cases
- **Compliance Validator**: Validates against regulatory requirements
- **Feedback Loop Agent**: Processes user feedback for improvement
- **Performance Monitor**: Tracks system performance metrics

### Data Management
- **Temporary Files**: Automatic cleanup of temporary files
- **User Feedback**: Persistent storage of user feedback
- **Traceability Logs**: Detailed logging for audit purposes
- **Performance Data**: Historical performance tracking

## 🛠️ Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip install -r requirements_ui.txt
   ```

2. **Streamlit not starting**
   ```bash
   # Check if port 8508 is available
   netstat -an | findstr 8508
   
   # Use different port
   streamlit run streamlit_ui.py --server.port 8502
   ```

3. **File upload errors**
   - Ensure `temp/` directory exists and is writable
   - Check file size limits (default: 200MB)
   - Verify file format (PDF/TXT only)

4. **Environment configuration**
   - Copy `.env.example` to `.env`
   - Configure required Google Cloud variables
   - Check service account permissions

5. **ChromaDB connection issues**
   - System falls back to local ChromaDB automatically
   - Check CHROMA_API_KEY if using cloud version
   - Ensure `chroma/` directory is writable

### Performance Optimization

- **Memory Usage**: Adjust caching settings in configuration
- **Processing Speed**: Use local LLM models for faster response
- **File Size**: Compress large PDF files before upload
- **Concurrent Users**: Single-user application by default

## 🔒 Security Considerations

- **File Validation**: Input validation for uploaded files
- **Path Traversal**: Protection against directory traversal attacks
- **Environment Variables**: Sensitive data stored in environment variables
- **Local Storage**: All data stored locally by default
- **API Security**: Secure handling of external API credentials

## 📈 Performance Metrics

The system tracks various performance metrics:

- **Processing Time**: Time taken for complete workflow
- **Quality Score**: Based on success rate and user feedback
- **Feedback Rate**: Percentage of test cases with user feedback
- **Success Rate**: Percentage of successful test case generations
- **Compliance Score**: Regulatory compliance validation results

## 🤝 Contributing

To contribute to the UI development:

1. **Setup Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements_ui.txt
   ```

2. **Run in Development Mode**
   ```bash
   streamlit run streamlit_ui.py --server.runOnSave true
   ```

3. **Code Style**
   - Follow PEP 8 guidelines
   - Use type hints where possible
   - Add docstrings for functions
   - Include error handling

## 📞 Support

For issues and questions:

1. **Check Logs**: Console output provides detailed error information
2. **System Health**: Use dashboard to check component status
3. **Documentation**: Review built-in documentation page
4. **Configuration**: Verify environment variables and file permissions

## 🔄 Updates and Maintenance

### Regular Maintenance
- **Clean Temporary Files**: Automatic cleanup on restart
- **Update Dependencies**: Regular package updates
- **Monitor Storage**: Check disk usage in dashboard
- **Review Feedback**: Analyze user feedback for improvements

### Version Updates
- **Backup Data**: Before updating, backup user_feedback/ and generated_testcases/
- **Update Packages**: `pip install -r requirements_ui.txt --upgrade`
- **Test Configuration**: Verify all features work after update

---

## 📄 License

This UI component is part of the Multi-Agent RAG Test Case Generator system. See main project license for details.