# Multi-Agent RAG Test Case Generation System - Complete Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Agent System](#agent-system)
6. [User Interface](#user-interface)
7. [Configuration](#configuration)
8. [API Integration](#api-integration)
9. [Security](#security)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)

## System Overview

The Multi-Agent RAG Test Case Generation System is a sophisticated AI-powered platform that automatically generates regulatory compliance test cases using Retrieval-Augmented Generation (RAG) with semantic search and intelligent requirement analysis.

### Key Features
- **Multi-Agent Architecture**: 6 specialized agents working in coordination
- **Semantic Search**: 384-dimensional embeddings using sentence-transformers
- **Intelligent Analysis**: LLM-powered requirement analysis with user interaction
- **ChromaDB Integration**: Cloud-based vector storage with local fallback
- **Jira Integration**: Automated test case creation in Jira
- **BigQuery Analytics**: Performance tracking and traceability logging
- **Circuit Breakers**: Fault tolerance for external services
- **Performance Monitoring**: Real-time metrics and automated retraining triggers

## Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                        │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  Streamlit UI   │   CLI Interface │    REST API (Future)       │
└─────────────────┴─────────────────┴─────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATION LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  WorkflowOrchestrator - Coordinates multi-agent workflows      │
│  • Parallel processing                                         │
│  • Error handling and recovery                                 │
│  • Performance monitoring                                      │
│  • State management                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT LAYER                                 │
├─────────────────┬─────────────────┬─────────────────────────────┤
│ DocumentParser  │ TestGenerator   │ ComplianceValidator         │
├─────────────────┼─────────────────┼─────────────────────────────┤
│ FeedbackLoop    │ PerformanceMonitor │ CoordinatorAgent        │
└─────────────────┴─────────────────┴─────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    TOOLS LAYER                                 │
├─────────────────┬─────────────────┬─────────────────────────────┤
│ AI Generation   │ Vector Search   │ Document Processing         │
│ • Gemini        │ • ChromaDB      │ • PDF/DOCX/XML/TXT         │
│ • Ollama        │ • Embeddings    │ • Multi-format support     │
│ • HuggingFace   │ • RAG Retrieval │ • Content extraction       │
└─────────────────┴─────────────────┴─────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                  INTEGRATION LAYER                             │
├─────────────────┬─────────────────┬─────────────────────────────┤
│ Google Cloud    │ Jira API        │ Local Storage               │
│ • BigQuery      │ • Test Cases    │ • File System              │
│ • Cloud Storage │ • Projects      │ • JSON Logs                │
│ • Authentication│ • Issue Types   │ • Feedback Data             │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

### Component Interaction Flow
```
User Input → UI Layer → Orchestrator → Agents → Tools → External APIs
     ↑                                                        │
     └─── Results ← Performance Monitor ← Feedback ←─────────┘
```

## Core Components

### 1. Entry Points

#### main.py
**Purpose**: CLI entry point for the system
**Key Functions**:
- `run_pipeline()`: Main execution function
- `apply_intelligent_analysis()`: Applies LLM-powered requirement analysis
- `get_document_content()`: Multi-format document extraction

**Usage**:
```bash
python main.py --requirements-doc ./req.pdf --regulatory-doc ./reg.pdf --intelligent-analysis
```

#### streamlit_ui.py
**Purpose**: Web-based user interface
**Key Features**:
- Multi-page navigation (Home, Dashboard, Documentation)
- File upload with validation
- Interactive question handling
- Real-time progress tracking
- Comprehensive feedback collection

### 2. Orchestration Layer

#### orchestrator.py - WorkflowOrchestrator
**Purpose**: Coordinates the entire multi-agent workflow

**Key Methods**:
- `execute_workflow()`: Main workflow execution with parallel processing
- `_build_knowledge_base()`: Parallel knowledge base construction
- `_parse_requirements()`: Document parsing coordination
- `_generate_test_case_parallel()`: Parallel test case generation

**Workflow Phases**:
1. **Phase 1**: Parallel Knowledge Base + Document Parsing
2. **Phase 2**: Multi-Agent Processing Pipeline
3. **Phase 3**: Aggregate Results and Feedback Processing
4. **Phase 4**: Performance Monitoring and Results Summary

### 3. Agent System

#### DocumentParserAgent
**Purpose**: Multi-format document parsing and requirement extraction

**Supported Formats**:
- PDF (PyMuPDF)
- DOCX (python-docx)
- XML (ElementTree)
- HTML (BeautifulSoup)
- JSON/YAML
- Markdown
- Plain text

**Key Methods**:
- `parse_document()`: Main parsing entry point
- `_extract_requirements_multi_strategy()`: Multiple extraction strategies
- `_convert_to_test_artifacts()`: Convert to test-ready format

#### TestCaseGeneratorAgent
**Purpose**: Generate test cases with iterative regulatory validation

**Key Features**:
- Iterative compliance validation (max 3 iterations)
- Regulatory enhancement based on missing elements
- Detailed test case structure generation

**Key Methods**:
- `generate_validated_test_case()`: Main generation with validation
- `_enhance_test_case_for_compliance()`: Compliance-based enhancement

#### ComplianceValidationAgent
**Purpose**: Validate requirements and test cases against regulatory standards

**Key Methods**:
- `validate_compliance()`: Requirement validation
- `validate_generated_test_case()`: Test case validation

#### FeedbackLoopAgent
**Purpose**: Process user feedback and generate improvements

**Key Methods**:
- `process_feedback()`: Analyze and process user feedback

#### PerformanceMonitorAgent
**Purpose**: Track system performance and quality metrics

**Key Methods**:
- `track_performance()`: Monitor and analyze performance

#### CoordinatorAgent
**Purpose**: Coordinate workflow and task decomposition

**Key Methods**:
- `coordinate_workflow()`: Break down requirements into tasks
- `generate_test_case()`: Generate comprehensive test cases
- `_generate_functional_test()`: Functional test generation
- `_generate_compliance_test()`: Compliance test generation
- `_generate_security_test()`: Security test generation

### 4. Tools Layer

#### tools.py - Core Functionality
**Purpose**: Provides all core system functionality

**Key Functions**:

**Document Processing**:
- `upload_document()`: GCS document upload
- `chunk_text()`: Text chunking with overlap
- `ocr_extraction()`: OCR processing via Cloud Functions

**AI Generation**:
- `call_ai_generator()`: Multi-provider AI generation (Gemini → Ollama → HuggingFace)
- `create_embeddings()`: Sentence transformer embeddings
- `intelligent_requirement_analysis()`: LLM-powered requirement analysis

**Vector Database**:
- `vector_store()`: ChromaDB storage with cloud/local fallback
- `rag_retrieval()`: Semantic search and retrieval

**Test Case Management**:
- `create_testcase()`: Jira test case creation with fallback
- `compliance_validation_agent()`: Enhanced compliance validation
- `collect_user_feedback()`: Automated feedback collection

**Analytics**:
- `log_traceability()`: BigQuery and local traceability logging
- `log_performance_metrics()`: Performance tracking

### 5. Configuration System

#### config.py
**Purpose**: Centralized configuration management

**Key Configurations**:
```python
QUALITY_THRESHOLDS = {"MEDIUM": 0.7}
VALIDATION_RULES = {"MIN_REQUIREMENT_WORDS": 3}
CHUNK_CONFIG = {"SIZE": 256, "OVERLAP": 50}
EMBEDDING_CONFIG = {"DIMENSIONS": 384, "CACHE_SIZE": 1000}
JIRA_CONFIG = {"ISSUE_TYPES": ["Idea", "Story", "Task", "Bug"]}
```

## Data Flow

### 1. Document Processing Flow
```
Document Upload → Format Detection → Content Extraction → 
Text Chunking → Embedding Generation → Vector Storage
```

### 2. Requirement Analysis Flow
```
Raw Requirement → Domain Detection → Complexity Analysis → 
LLM Question Generation → User Interaction → Enhanced Requirement
```

### 3. Test Case Generation Flow
```
Enhanced Requirement → RAG Retrieval → Multi-Agent Processing → 
Test Case Generation → Compliance Validation → Iterative Enhancement → 
Jira Creation → Feedback Collection
```

### 4. Feedback Loop
```
User Feedback → Analysis → Quality Metrics → Performance Tracking → 
Retraining Triggers → System Improvement
```

## User Interface

### Streamlit Web Interface

#### Main Features
- **File Upload**: Multi-format document support with validation
- **Intelligent Analysis**: Toggle for LLM-powered question generation
- **Interactive Questions**: Domain-specific questions with progress tracking
- **Results Display**: Comprehensive test case results with metrics
- **Feedback Collection**: Multi-dimensional feedback system
- **Dashboard**: System health, performance analytics, recent activity

#### Navigation Structure
```
Home Page
├── Document Upload
├── Processing Options
├── Interactive Questions (conditional)
├── Results Display
└── Feedback Collection

Dashboard Page
├── System Health
├── Performance Analytics
├── Recent Activity
└── Configuration Status

Documentation Page
├── Getting Started
├── Configuration Guide
└── FAQ
```

### CLI Interface

#### Basic Usage
```bash
# Basic execution
python main.py --requirements-doc req.pdf --regulatory-doc reg.pdf

# With intelligent analysis
python main.py --requirements-doc req.pdf --regulatory-doc reg.pdf --intelligent-analysis

# Custom collection
python main.py --requirements-doc req.pdf --regulatory-doc reg.pdf --collection-name custom_collection
```

## Configuration

### Environment Variables

#### Required Variables
```env
# Google Cloud Configuration
GOOGLE_PROJECT_ID="your-project-id"
GCS_BUCKET="your-bucket-name"
BIGQUERY_DATASET="your-dataset"
```

#### Optional Variables
```env
# ChromaDB Cloud
CHROMA_API_KEY="your-chroma-api-key"
CHROMA_TENANT="your-tenant-id"
CHROMA_DATABASE="your-database"

# Jira Integration
JIRA_API_URL="https://your-domain.atlassian.net"
JIRA_USER="your-email@domain.com"
JIRA_TOKEN="your-jira-api-token"
JIRA_PROJECT_KEY="YOUR-PROJECT"

# AI Models
GEMINI_API_KEY="your-gemini-key"
OLLAMA_URL="http://localhost:11434"
OLLAMA_MODEL="llama3.2"
HUGGING_FACE_GENERATION_MODEL="google/flan-t5-small"
```

### Configuration Files

#### .env File Structure
```env
# Core Configuration
GOOGLE_PROJECT_ID=your-project
GCS_BUCKET=your-bucket
BIGQUERY_DATASET=your-dataset

# Vector Database
CHROMA_COLLECTION=regulatory_docs_384
CHROMA_API_KEY=your-key
CHROMA_TENANT=your-tenant
CHROMA_DATABASE=your-db

# ALM Integration
JIRA_API_URL=https://company.atlassian.net
JIRA_USER=user@company.com
JIRA_TOKEN=your-token
JIRA_PROJECT_KEY=PROJ

# AI Services
GEMINI_API_KEY=your-gemini-key
OLLAMA_URL=http://localhost:11434
```

## API Integration

### Google Cloud Services

#### BigQuery Integration
- **Purpose**: Analytics and traceability logging
- **Tables**: `traceability_log` with test case tracking
- **Queries**: Performance metrics, feedback analysis

#### Cloud Storage Integration
- **Purpose**: Document storage and processing
- **Operations**: Upload, download, OCR processing

### Jira Integration

#### Test Case Creation
- **Endpoint**: `/rest/api/3/issue`
- **Issue Types**: Dynamic detection and fallback
- **Project Management**: Automatic project discovery

#### Error Handling
- Multiple issue type attempts
- Project validation
- Local fallback storage

### ChromaDB Integration

#### Cloud Configuration
```python
client = chromadb.CloudClient(
    api_key=os.getenv("CHROMA_API_KEY"),
    tenant=os.getenv("CHROMA_TENANT"),
    database=os.getenv("CHROMA_DATABASE")
)
```

#### Local Fallback
```python
client = chromadb.PersistentClient(path="./chroma")
```

### AI Model Integration

#### Multi-Provider Strategy
1. **Gemini** (Primary): Google's Gemini 1.5 Flash
2. **Ollama** (Secondary): Local LLM deployment
3. **HuggingFace** (Fallback): Transformers pipeline

## Security

### Input Validation
- Path traversal protection
- File type validation
- Content sanitization
- SQL injection prevention

### Authentication
- Environment variable storage
- Service account authentication
- API token management

### Data Protection
- Local data storage by default
- Encrypted API communications
- Secure file handling

## Deployment

### Prerequisites
```bash
# Python 3.8+
python --version

# Required packages
pip install -r requirements.txt

# Optional: Google Cloud SDK
gcloud auth application-default login
```

### Installation Steps

#### 1. Clone and Setup
```bash
git clone <repository-url>
cd mcp-toolbox/orchestrator
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. Configuration
```bash
cp .env.example .env
# Edit .env with your configuration
```

#### 3. Run System
```bash
# Web UI
python run_ui.py
# or
streamlit run streamlit_ui.py

# CLI
python main.py --requirements-doc req.pdf --regulatory-doc reg.pdf
```

### Docker Deployment (Future)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8508
CMD ["streamlit", "run", "streamlit_ui.py"]
```

## Performance Optimization

### Caching Strategy
- Embedding caching (1000 items, 1-hour TTL)
- Question caching for repeated requirements
- Local file caching for processed documents

### Parallel Processing
- Concurrent knowledge base building
- Parallel document parsing
- Asynchronous agent coordination

### Resource Management
- Connection pooling for databases
- Circuit breakers for external services
- Memory-efficient text processing

## Monitoring and Analytics

### Performance Metrics
- Processing time tracking
- Quality score calculation
- Success rate monitoring
- User feedback analysis

### Health Checks
- System component status
- External service connectivity
- Resource utilization monitoring

### Logging
- Structured logging with levels
- Traceability logging for audit
- Performance logging for optimization

## Troubleshooting

### Common Issues

#### 1. ChromaDB Connection Issues
```bash
# Check environment variables
echo $CHROMA_API_KEY
echo $CHROMA_TENANT

# Test local fallback
rm -rf ./chroma
python -c "import chromadb; chromadb.PersistentClient(path='./chroma')"
```

#### 2. Jira Authentication Issues
```bash
# Verify credentials
curl -u user@domain.com:token https://domain.atlassian.net/rest/api/2/myself

# Check project access
curl -u user@domain.com:token https://domain.atlassian.net/rest/api/2/project
```

#### 3. BigQuery Permission Issues
```bash
# Re-authenticate
gcloud auth application-default login

# Test access
bq ls your-project:your-dataset
```

#### 4. AI Model Issues
```bash
# Test Gemini
python -c "import google.generativeai as genai; genai.configure(api_key='your-key')"

# Test Ollama
curl http://localhost:11434/api/tags

# Test HuggingFace
python -c "from transformers import pipeline; pipeline('text2text-generation', model='google/flan-t5-small')"
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py --requirements-doc req.pdf --regulatory-doc reg.pdf
```

### Health Check
```bash
python -c "from health_check import check_system_health; print(check_system_health())"
```

## Future Enhancements

### Planned Features
1. **REST API**: Full API interface for integration
2. **Advanced Analytics**: ML-powered quality prediction
3. **Multi-tenant Support**: Organization-level isolation
4. **Advanced AI Models**: GPT-4, Claude integration
5. **Real-time Collaboration**: Multi-user editing
6. **Advanced Compliance**: Industry-specific validators

### Scalability Improvements
1. **Microservices Architecture**: Service decomposition
2. **Container Orchestration**: Kubernetes deployment
3. **Distributed Processing**: Multi-node processing
4. **Advanced Caching**: Redis integration
5. **Load Balancing**: High availability setup

## Conclusion

The Multi-Agent RAG Test Case Generation System represents a comprehensive solution for automated test case generation with regulatory compliance. Its modular architecture, extensive integration capabilities, and intelligent processing make it suitable for enterprise-scale deployment while maintaining flexibility for various use cases.

The system's strength lies in its multi-agent coordination, intelligent requirement analysis, and robust error handling, making it a reliable tool for quality assurance teams working in regulated industries.