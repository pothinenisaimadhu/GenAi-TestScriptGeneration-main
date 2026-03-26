# Multi-Agent RAG Test Case Generation System

A sophisticated multi-agent system that generates regulatory compliance test cases using RAG (Retrieval-Augmented Generation) with semantic search and intelligent requirement analysis.

## Features

- **Multi-Agent Architecture**: Coordinated agents for document parsing, test generation, and feedback processing
- **Semantic Search**: 384-dimensional embeddings using sentence-transformers (all-MiniLM-L6-v2)
- **Intelligent Analysis**: LLM-powered requirement analysis with user interaction
- **ChromaDB Integration**: Cloud-based vector storage with fallback to local
- **Jira Integration**: Automated test case creation in Jira
- **BigQuery Analytics**: Performance tracking and traceability logging
- **Circuit Breakers**: Fault tolerance for external services
- **Performance Monitoring**: Real-time metrics and automated retraining triggers

## Quick Start

### 1. Prerequisites

- Python 3.8+
- Google Cloud Project with BigQuery and Storage APIs enabled
- ChromaDB Cloud account (optional - falls back to local)
- Jira account with API access
- Ollama (optional - for local LLM)

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd mcp-toolbox/orchestrator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

**Required Environment Variables:**

```env
# GCP Configuration
GOOGLE_PROJECT_ID="your-project-id"
GCS_BUCKET="your-bucket-name"
BIGQUERY_DATASET="your-dataset"

# ChromaDB Cloud (optional)
CHROMA_API_KEY="your-chroma-api-key"
CHROMA_TENANT="your-tenant-id"
CHROMA_DATABASE="your-database"

# Jira Integration
JIRA_API_URL="https://your-domain.atlassian.net"
JIRA_USER="your-email@domain.com"
JIRA_TOKEN="your-jira-api-token"
JIRA_PROJECT_KEY="YOUR-PROJECT"
```

### 4. Setup Google Cloud

```bash
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

### 5. Run the System

```bash
# Basic usage
python main.py --requirements-doc ./requirements_doc.pdf --regulatory-doc ./regulatory_doc.pdf

# With custom collection
python main.py --requirements-doc ./requirements_doc.pdf --regulatory-doc ./regulatory_doc.pdf --collection-name custom_collection
```

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Document Parser │    │ Test Generator  │    │ Feedback Agent  │
│     Agent       │    │     Agent       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Orchestrator  │
                    │                 │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    ChromaDB     │    │    BigQuery     │    │      Jira       │
│  Vector Store   │    │   Analytics     │    │   Test Cases    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Key Components

### Core Files

- `main.py` - Entry point and CLI interface
- `orchestrator.py` - Multi-agent workflow coordination
- `tools.py` - Core functionality (embeddings, RAG, test generation)
- `agents.py` - Individual agent implementations
- `config.py` - Configuration constants
- `resource_manager.py` - Database connection management

### Supporting Files

- `utils.py` - Utility functions and caching
- `health_check.py` - System health monitoring
- `circuit_breaker.py` - Fault tolerance
- `performance_optimizer.py` - Performance tracking

## Configuration Options

### Embedding Configuration
```python
EMBEDDING_CONFIG = {
    "DIMENSIONS": 384,  # sentence-transformers all-MiniLM-L6-v2
    "CACHE_SIZE": 1000
}
```

### Quality Thresholds
```python
QUALITY_THRESHOLDS = {
    "MEDIUM": 0.7  # Retraining trigger threshold
}
```

### Jira Configuration
```python
JIRA_CONFIG = {
    "ISSUE_TYPES": ["Idea", "Story", "Task", "Bug"],
    "BATCH_SIZE": 2,
    "TIMEOUT": 15
}
```

## Usage Examples

### Basic Test Case Generation
```bash
python main.py --requirements-doc requirements.pdf --regulatory-doc regulations.pdf
```

### With Custom Parameters
```bash
python main.py \
  --requirements-doc requirements.pdf \
  --regulatory-doc regulations.pdf \
  --collection-name my_collection \
  --chunk-size 512 \
  --n-results 10
```

### Health Check
```bash
python -c "from health_check import check_system_health; print(check_system_health())"
```

## Troubleshooting

### Common Issues

1. **ChromaDB Connection Error**
   - Check CHROMA_API_KEY, CHROMA_TENANT, CHROMA_DATABASE
   - System falls back to local ChromaDB automatically

2. **BigQuery Permission Error**
   - Run `gcloud auth application-default login`
   - Ensure BigQuery API is enabled in GCP

3. **Jira Authentication Error**
   - Verify JIRA_TOKEN is valid API token (not password)
   - Check JIRA_PROJECT_KEY exists and is accessible

4. **Embedding Dimension Mismatch**
   - Delete existing ChromaDB collection to re-ingest with 384 dimensions
   - Or use `--collection-name new_collection_name`

### Performance Optimization

- **Memory**: Adjust `CACHE_CONFIG["TTL_SECONDS"]` to manage memory usage
- **Speed**: Use local Ollama for faster LLM responses
- **Quality**: Increase `CHUNK_CONFIG["SIZE"]` for better context

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Adding New Agents
1. Inherit from base agent class in `agents.py`
2. Implement required methods
3. Register in orchestrator

### Custom Tools
Add new tools in `tools.py` following existing patterns:
- Use circuit breakers for external calls
- Implement proper error handling
- Add performance monitoring

## Monitoring

### Performance Metrics
- Quality Score: Based on success rate and user feedback
- Feedback Rate: Percentage of test cases with user feedback
- Retraining Trigger: Automatic when quality drops below threshold

### BigQuery Tables
- `traceability_log`: Test case traceability and metrics
- Custom analytics queries available

## Security

- API keys stored in environment variables
- SQL injection protection with parameterized queries
- Input validation and sanitization
- Circuit breakers prevent cascade failures

## License

[Your License Here]

## Support

For issues and questions:
1. Check troubleshooting section
2. Review logs in console output
3. Check system health with health_check.py