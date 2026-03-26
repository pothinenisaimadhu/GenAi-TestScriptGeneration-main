# Streamlit UI for Multi-Agent RAG Test Case Generator

A user-friendly web interface for the Multi-Agent RAG Test Case Generation System.

## Features

- **Document Upload**: Drag-and-drop PDF upload for requirements and regulatory documents
- **Real-time Processing**: Live progress tracking during test case generation
- **System Health**: Monitor system status and component health
- **Results Visualization**: View generated test cases with detailed information
- **Performance Analytics**: Track quality scores, success rates, and system metrics
- **Interactive Configuration**: Adjust processing parameters through the UI

## Quick Start

### Prerequisites
- Main orchestrator system must be set up (see ../README.md)
- Python environment with orchestrator dependencies

### Installation

```bash
# Navigate to UI directory
cd streamlit_ui

# Install UI dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

Or use the provided scripts:
- **Windows**: `run.bat`
- **Linux/Mac**: `chmod +x run.sh && ./run.sh`

### Access
Open your browser and go to: http://localhost:5000

## Usage

### 1. Upload Documents
- **Requirements Document**: Upload your requirements PDF
- **Regulatory Document**: Upload regulatory compliance PDF

### 2. Configure Processing
- **Collection Name**: ChromaDB collection name
- **Chunk Size**: Text chunking size (128-512)
- **RAG Results**: Number of retrieval results (3-10)
- **Intelligent Analysis**: Enable/disable LLM-powered analysis

### 3. Generate Test Cases
- Click "🚀 Generate Test Cases"
- Monitor real-time progress
- View processing metrics

### 4. Review Results
- **Results Tab**: View generated test cases with Jira IDs
- **Analytics Tab**: Monitor performance metrics and system health

## Interface Overview

### Main Tabs

1. **Generate Test Cases**
   - Document upload interface
   - Configuration options
   - Processing controls

2. **Results**
   - Generated test case details
   - Jira integration status
   - Requirement traceability

3. **Analytics**
   - Quality scores and success rates
   - Performance metrics
   - System operation statistics

### Sidebar
- **System Health Check**: Real-time status of all components
- **Service Status**: ChromaDB, BigQuery, Jira connectivity

## Configuration Options

### Processing Parameters
- **Collection Name**: Vector database collection identifier
- **Chunk Size**: Text segmentation size for better processing
- **RAG Results**: Number of relevant chunks to retrieve
- **Intelligent Analysis**: Enable interactive requirement analysis

### System Integration
- Connects to orchestrator system automatically
- Uses same .env configuration as main system
- Shares ChromaDB collections and BigQuery datasets

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure orchestrator dependencies are installed
   - Check Python path configuration

2. **File upload failures**
   - Verify PDF files are valid and not corrupted
   - Check available disk space

3. **Processing errors**
   - Review system health in sidebar
   - Check orchestrator system configuration
   - Verify all required services are running

4. **No results displayed**
   - Ensure processing completed successfully
   - Check for errors in the Results tab
   - Verify Jira integration is working

### Performance Tips

- **Large Documents**: Increase chunk size for better processing
- **Slow Processing**: Reduce RAG results count
- **Memory Issues**: Process smaller documents or restart the UI

## Development

### Adding New Features

1. **New Metrics**: Add to `display_analytics()` function
2. **UI Components**: Use Streamlit components in main tabs
3. **Data Visualization**: Add charts using Plotly or built-in Streamlit charts

### Customization

- **Styling**: Modify `st.set_page_config()` for theme changes
- **Layout**: Adjust column layouts and tab organization
- **Metrics**: Add custom performance indicators

## Security

- **File Handling**: Uploaded files are stored temporarily and cleaned up
- **Credentials**: Uses same secure credential management as orchestrator
- **Access Control**: Runs on localhost by default

## Integration

### With Main System
- Imports orchestrator modules directly
- Shares configuration and credentials
- Uses same database connections

### External Services
- **Jira**: Displays created test case IDs and links
- **ChromaDB**: Shows collection status and metrics
- **BigQuery**: Retrieves performance analytics

## Support

For UI-specific issues:
1. Check browser console for JavaScript errors
2. Review Streamlit logs in terminal
3. Verify orchestrator system is properly configured
4. Test individual components using system health check

For system integration issues, refer to the main README.md file.