import streamlit as st
import asyncio
import json
import os
import sys
from pathlib import Path
import time
from typing import Dict, Any, List

# Force reload environment variables
import os
from dotenv import load_dotenv

# Clear any cached environment variables
for key in list(os.environ.keys()):
    if key.startswith('JIRA_'):
        del os.environ[key]

# Force reload from .env file
load_dotenv(override=True)

# Add orchestrator to path
sys.path.insert(0, os.path.dirname(__file__))

# Force reload tools module to get fresh environment
import importlib
import tools
importlib.reload(tools)

from main_ui import run_pipeline_from_ui, process_uploaded_files
from ui_question_handler import generate_ui_questions, load_user_answers, enhance_requirement_with_ui_answers
from ui_dashboard import main_dashboard

# Page config
st.set_page_config(
    page_title="Multi-Agent RAG Test Case Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with Aurora Animation and Dark Background
st.markdown("""
<style>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;800&display=swap");

:root {
    --clr-1: #00c2ff;
    --clr-2: #33ff8c;
    --clr-3: #ffc640;
    --clr-4: #e54cff;
    --blur: 2rem;
}

.stApp {
    background: linear-gradient(
        135deg,
        rgb(0, 0, 0) 0%,
        rgb(13, 13, 27) 25%,
        rgb(17, 11, 34) 50%,
        rgb(18, 9, 40) 75%,
        rgb(0, 0, 0) 100%
    );
    background-attachment: fixed;
}

.main-header {
    font-size: clamp(2rem, 6vw, 3.5rem);
    font-weight: 800;
    text-align: center;
    margin-bottom: 2rem;
    padding: 2rem 1rem;
}

.header-text {
    display: inline-block;
    background: linear-gradient(
        -45deg,
        var(--clr-1),
        var(--clr-2),
        var(--clr-3),
        var(--clr-4),
        var(--clr-1)
    );
    background-size: 400% 400%;
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: aurora-flow 12s ease infinite;
}

@keyframes aurora-flow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Sidebar */
.css-1d391kg {
    background: rgba(0, 51, 102, 0.8) !important;
}

/* Drag and Drop Boxes */
.st-emotion-cache-1erivf3 {
    background: rgba(0, 51, 102, 0.6) !important;
    border: 2px dashed #003366 !important;
}

.st-emotion-cache-19rxjzo {
    background: #003366 !important;
    color: white !important;
}

/* Text Input Fields */
input[type="text"] {
    background: rgba(0, 51, 102, 0.7) !important;
    border: 1px solid #003366 !important;
    color: white !important;
}
</style>

""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'workflow_results' not in st.session_state:
        st.session_state.workflow_results = None
    if 'questions_generated' not in st.session_state:
        st.session_state.questions_generated = False
    if 'current_questions' not in st.session_state:
        st.session_state.current_questions = []
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🏠 Home"
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = {'req': None, 'reg': None}
    if 'continue_processing' not in st.session_state:
        st.session_state.continue_processing = False
    if 'stored_files' not in st.session_state:
        st.session_state.stored_files = {'req': None, 'reg': None}
    if 'stored_intelligent_analysis' not in st.session_state:
        st.session_state.stored_intelligent_analysis = False

def display_header():
    """Display main header with aurora text animation"""
    st.markdown('''
    <div class="main-header">
        <div class="header-text"> Multi-Agent RAG Test Case Generator</div>
    </div>
    ''', unsafe_allow_html=True)

def display_sidebar():
    """Display sidebar with navigation and system info"""
    with st.sidebar:
        # Logo
        logo_path = "img/images-removebg-preview.png"
        if os.path.exists(logo_path):
            st.markdown("""
            <style>
            .logo-container img {
                filter: brightness(1.5) contrast(1.2);
                width: 100% !important;
                max-width: 280px;
            }
            </style>
            """, unsafe_allow_html=True)
            st.markdown('<div class="logo-container">', unsafe_allow_html=True)
            st.image(logo_path, width=280)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("### 🧭 Navigation")
        
        # Navigation menu
        page = st.selectbox(
            "Select Page",
            ["🏠 Home", "📊 Dashboard", "📚 Documentation"],
            key="navigation"
        )
        
        st.session_state.current_page = page
        
        st.markdown("---")
        
        st.markdown("### 🔧 System Status")
        
        # Environment status
        # Force reload environment for status check
        load_dotenv(override=True)
        
        # Debug environment variables
        chroma_key = os.getenv('CHROMA_API_KEY')
        chroma_tenant = os.getenv('CHROMA_TENANT')
        chroma_db = os.getenv('CHROMA_DATABASE')
        
        env_status = {
            "ChromaDB": f"✅ " if chroma_key and chroma_tenant and chroma_db else f"❌ (Key: {'✓' if chroma_key else '✗'}, Tenant: {'✓' if chroma_tenant else '✗'}, DB: {'✓' if chroma_db else '✗'})",
            "BigQuery": "✅" if os.getenv('GOOGLE_PROJECT_ID') and os.getenv('BIGQUERY_DATASET') else "❌",
            "Jira": f"✅ ({os.getenv('JIRA_PROJECT_KEY', 'N/A')})" if os.getenv('JIRA_API_URL') and os.getenv('JIRA_USER') and os.getenv('JIRA_TOKEN') and os.getenv('JIRA_PROJECT_KEY') else "❌"
        }
        
        for service, status in env_status.items():
            st.write(f"{status} {service}")
        
        # st.markdown("---")
        
        # # Debug info
        # st.markdown("### 🔍 Debug Info")
        # current_project = os.getenv('JIRA_PROJECT_KEY', 'Not Set')
        # st.write(f"**Current Jira Project:** {current_project}")
        
        # st.markdown("---")
        
        # Quick metrics
        if st.session_state.workflow_results:
            st.markdown("### 📈 Quick Metrics")
            results = st.session_state.workflow_results
            st.metric("Requirements", results.get('processed_requirements', 0))
            st.metric("Test Cases", results.get('test_cases_generated', 0))
            st.metric("Time", f"{results.get('processing_time', 0):.1f}s")
        
        st.markdown("---")
        
        # Help section
        with st.expander("ℹ️ Quick Help"):
            st.markdown("""
            **Quick Start:**
            1. Upload documents
            2. Enable intelligent analysis
            3. Answer questions
            4. Review results
            5. Provide feedback
            
            **Formats:** PDF, Word, XML, Markup, TXT, MD, RTF
            """)

def load_questions_from_file():
    """Load questions from temporary file if available"""
    questions_file = "temp_questions.json"
    if os.path.exists(questions_file):
        try:
            with open(questions_file, 'r') as f:
                questions_data = json.load(f)
                # Handle both list and dict formats
                if isinstance(questions_data, list):
                    return questions_data
                elif isinstance(questions_data, dict):
                    return questions_data.get('questions', [])
                return []
        except Exception as e:
            st.error(f"Error loading questions: {e}")
    return []

def save_answers_to_file(answers: Dict[str, Any]):
    """Save user answers to temporary file"""
    answers_file = "temp_answers.json"
    try:
        with open(answers_file, 'w') as f:
            json.dump(answers, f, indent=2)
    except Exception as e:
        st.error(f"Error saving answers: {e}")

def display_questions_interface():
    """Display interactive questions interface"""
    st.markdown('<h2 class="section-header">📝 Intelligent Analysis Questions</h2>', unsafe_allow_html=True)
    
    questions = load_questions_from_file()
    if not questions:
        st.info("No questions generated. This may happen if the requirement is clear enough.")
        return False
    
    # Progress indicator
    progress_col1, progress_col2 = st.columns([3, 1])
    with progress_col1:
        st.info(f"Please answer the following {len(questions)} questions to improve test case generation:")
    with progress_col2:
        answered_count = sum(1 for i in range(len(questions)) if st.session_state.get(f"q_{i}"))
        st.metric("Progress", f"{answered_count}/{len(questions)}")
    
    answers = {}
    
    # Group questions by category if available
    categorized_questions = {}
    for i, question_data in enumerate(questions):
        category = question_data.get('category', 'General')
        if category not in categorized_questions:
            categorized_questions[category] = []
        categorized_questions[category].append((i, question_data))
    
    # Display questions by category
    for category, category_questions in categorized_questions.items():
        with st.expander(f"📋 {category.title()} Questions ({len(category_questions)})", expanded=True):
            for i, question_data in category_questions:
                question_id = question_data.get('id', f'q_{i}')
                question_text = question_data.get('question', '')
                question_type = question_data.get('type', 'text')
                priority = question_data.get('priority', 'medium')
                
                # Priority indicator
                priority_icon = "🔴" if priority == 'high' else "🟡" if priority == 'medium' else "🟢"
                
                st.markdown(f"{priority_icon} **Question {i+1}:** {question_text}")
                
                if question_type == 'multiple_choice':
                    options = question_data.get('options', ['Yes', 'No'])
                    answer = st.radio(f"Select answer:", options, key=f"q_{i}", horizontal=True)
                elif question_type == 'text':
                    answer = st.text_area(f"Your answer:", key=f"q_{i}", height=80)
                else:
                    answer = st.text_input(f"Your answer:", key=f"q_{i}")
                
                if answer:
                    answers[question_id] = {
                        'question': question_text,
                        'answer': answer,
                        'type': question_type,
                        'category': category,
                        'priority': priority
                    }
    
    # Submit section
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⏭️ Skip Questions"):
            # Save empty answers file to indicate skipping
            save_answers_to_file({})
            st.session_state.questions_generated = False
            st.session_state.continue_processing = True
            st.success("Questions skipped! Proceeding with test case generation...")
            time.sleep(0.5)  # Brief pause to show message
            return True
    
    with col2:
        if st.button("✅ Submit Answers", type="primary", use_container_width=True):
            if answers:
                save_answers_to_file(answers)
                st.success("Answers saved! Proceeding with test case generation...")
                st.session_state.user_answers = answers
                st.session_state.questions_generated = False
                st.session_state.continue_processing = True
                time.sleep(0.5)  # Brief pause to show message
                return True
            else:
                st.warning("Please provide at least one answer before proceeding.")
    
    with col3:
        if st.button("💾 Save Draft"):
            if answers:
                save_answers_to_file(answers)
                st.success("Draft saved!")
    
    return False

def display_file_upload():
    """Display file upload interface"""
    st.markdown('<h2 class="section-header">📁 Document Upload</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Requirements Document**")
        req_file = st.file_uploader(
            "Upload requirements document",
            type=['pdf', 'txt', 'md', 'rtf', 'doc', 'docx', 'xml', 'html', 'htm'],
            key="req_file",
            help="Upload your requirements document (PDF, Word, XML, Markup, TXT, MD, RTF formats supported)"
        )
    
    with col2:
        st.markdown("**Regulatory Document**")
        reg_file = st.file_uploader(
            "Upload regulatory document",
            type=['pdf', 'txt', 'md', 'rtf', 'doc', 'docx', 'xml', 'html', 'htm'],
            key="reg_file",
            help="Upload regulatory compliance document (PDF, Word, XML, Markup, TXT, MD, RTF formats supported)"
        )
    
    return req_file, reg_file

def display_processing_options():
    """Display processing options"""
    st.markdown('<h2 class="section-header">⚙️ Processing Options</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        intelligent_analysis = st.checkbox(
            "Enable Intelligent Analysis",
            value=True,
            help="Generate smart questions to improve test case quality"
        )
    
    with col2:
        collection_name = st.text_input(
            "Collection Name",
            value=os.getenv("CHROMA_COLLECTION", "regulatory_docs_384"),
            help="ChromaDB collection name for vector storage"
        )
    
    return intelligent_analysis, collection_name

def display_results(results: Dict[str, Any]):
    """Display workflow results"""
    st.markdown('<h2 class="section-header">📊 Results</h2>', unsafe_allow_html=True)
    
    if results.get('success'):
        st.markdown('<div class="status-box success-box">✅ Pipeline completed successfully!</div>', unsafe_allow_html=True)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Requirements", results.get('processed_requirements', 0))
        with col2:
            st.metric("Test Cases", results.get('test_cases_generated', 0))
        with col3:
            st.metric("Processing Time", f"{results.get('processing_time', 0):.2f}s")
        with col4:
            perf_metrics = results.get('performance_metrics', {})
            st.metric("Quality Score", f"{perf_metrics.get('quality_score', 0):.2f}")
        
        # Performance metrics
        if perf_metrics:
            st.markdown("### Performance Metrics")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Success Rate:** {perf_metrics.get('success_rate', 0):.2f}")
                st.write(f"**Feedback Rate:** {perf_metrics.get('feedback_rate', 0):.2f}")
            with col2:
                st.write(f"**Retraining Needed:** {'Yes' if perf_metrics.get('retraining_needed') else 'No'}")
        
        # Test cases details
        successful_results = results.get('successful_results', [])
        if successful_results:
            st.markdown("### Generated Test Cases")
            
            for i, result in enumerate(successful_results, 1):
                with st.expander(f"Test Case {i}: {result.get('testcase_id', 'N/A')}"):
                    st.write(f"**Requirement:** {result.get('requirement', 'N/A')}")
                    
                    test_case = result.get('test_case', {})
                    if isinstance(test_case, dict):
                        st.write(f"**Summary:** {test_case.get('summary', 'N/A')}")
                        st.write(f"**Description:** {test_case.get('description', 'N/A')}")
                        if test_case.get('test_steps'):
                            st.write(f"**Test Steps:** {test_case.get('test_steps')}")
                    else:
                        st.write(f"**Test Case:** {test_case}")
                    
                    # Compliance validation
                    compliance = result.get('compliance_validation', {})
                    if compliance:
                        status = "✅ Passed" if compliance.get('passed') else "❌ Failed"
                        st.write(f"**Compliance Status:** {status}")
                        st.write(f"**Compliance Score:** {compliance.get('score', 0):.2f}")
                        st.write(f"**Iterations:** {compliance.get('iterations', 1)}")
                    
                    # User feedback
                    feedback = result.get('user_feedback', {})
                    if feedback and feedback.get('user_responses'):
                        st.write("**User Feedback:**")
                        responses = feedback['user_responses']
                        if isinstance(responses, dict):
                            for key, value in responses.items():
                                st.write(f"  - {key}: {value}")
    else:
        st.markdown('<div class="status-box error-box">❌ Pipeline failed</div>', unsafe_allow_html=True)
        errors = results.get('errors', [])
        for error in errors:
            st.error(f"Error: {error}")

def display_feedback_interface():
    """Display comprehensive feedback collection interface"""
    if st.session_state.workflow_results and st.session_state.workflow_results.get('success'):
        st.markdown('<h2 class="section-header">💬 Comprehensive Feedback</h2>', unsafe_allow_html=True)
        
        # Check for existing feedback files
        feedback_files = []
        if os.path.exists("user_feedback"):
            import glob
            feedback_files = glob.glob("user_feedback/detailed_feedback_*.json")
            feedback_files.sort(reverse=True)  # Most recent first
        
        if feedback_files:
            st.markdown("### 📊 Recent Feedback Results")
            
            # Display most recent feedback
            try:
                with open(feedback_files[0], 'r') as f:
                    latest_feedback = json.load(f)
                
                st.markdown("**Latest Feedback Summary:**")
                responses = latest_feedback.get('feedback_responses', {})
                
                # Display ratings
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    overall = responses.get('overall_satisfaction_with_gen', 'N/A')
                    st.metric("Overall Satisfaction", overall)
                with col2:
                    quality = responses.get('quality_of_generated_test_c', 'N/A')
                    st.metric("Quality Rating", quality)
                with col3:
                    completeness = responses.get('completeness_of_test_cover', 'N/A')
                    st.metric("Completeness", completeness)
                with col4:
                    efficiency = responses.get('time_efficiency_of_the_pr', 'N/A')
                    st.metric("Time Efficiency", efficiency)
                
                # Display specific feedback
                st.markdown("**Detailed Responses:**")
                for key, value in responses.items():
                    if value and value.strip():
                        clean_key = key.replace('_', ' ').title()
                        st.write(f"**{clean_key}:** {value}")
                
                # Display timestamp
                timestamp = latest_feedback.get('timestamp', 'Unknown')
                st.caption(f"Feedback collected: {timestamp}")
                
            except Exception as e:
                st.error(f"Error loading feedback: {e}")
        
        # Interactive feedback form
        with st.expander("📝 Provide New Feedback", expanded=not feedback_files):
            st.markdown("**Rate the System Performance:**")
            
            col1, col2 = st.columns(2)
            with col1:
                overall_rating = st.slider("Overall Satisfaction", 1, 5, 3)
                quality_rating = st.slider("Test Case Quality", 1, 5, 3)
                completeness_rating = st.slider("Test Coverage", 1, 5, 3)
            
            with col2:
                efficiency_rating = st.slider("Time Efficiency", 1, 5, 3)
                question_quality = st.slider("Question Quality", 1, 5, 3)
                
            st.markdown("**Specific Feedback:**")
            llm_helpful = st.radio("Were LLM questions helpful?", ["Yes", "No", "Partially"])
            interaction_smooth = st.radio("Was interaction smooth?", ["Yes", "No", "Could be better"])
            format_suitable = st.radio("Is test case format suitable?", ["Yes", "No", "Needs improvement"])
            
            missing_features = st.text_area("What features are missing?", height=80)
            improvements = st.text_area("What improvements would you suggest?", height=80)
            recommend = st.radio("Would you recommend this system?", ["Yes", "No", "Maybe"])
            
            additional_comments = st.text_area("Additional Comments", height=100)
            
            if st.button("💾 Submit Comprehensive Feedback", type="primary"):
                feedback_data = {
                    "overall_satisfaction": overall_rating,
                    "quality_rating": quality_rating,
                    "completeness_rating": completeness_rating,
                    "efficiency_rating": efficiency_rating,
                    "question_quality": question_quality,
                    "llm_helpful": llm_helpful,
                    "interaction_smooth": interaction_smooth,
                    "format_suitable": format_suitable,
                    "missing_features": missing_features,
                    "improvements": improvements,
                    "recommend": recommend,
                    "additional_comments": additional_comments,
                    "timestamp": time.time(),
                    "collection_method": "streamlit_ui"
                }
                
                # Save feedback
                try:
                    os.makedirs("user_feedback", exist_ok=True)
                    feedback_file = f"user_feedback/ui_feedback_{int(time.time())}.json"
                    with open(feedback_file, 'w') as f:
                        json.dump(feedback_data, f, indent=2)
                    st.success("✅ Thank you for your comprehensive feedback!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error saving feedback: {e}")

def display_documentation():
    """Display documentation page"""
    st.markdown("# 📚 Documentation")
    
    tab1, tab2, tab3 = st.tabs(["🚀 Getting Started", "🔧 Configuration", "❓ FAQ"])
    
    with tab1:
        st.markdown("""
        ## Getting Started
        
        ### 1. Upload Documents
        - **Requirements Document**: Upload your requirements in PDF or TXT format
        - **Regulatory Document**: Upload regulatory compliance documentation
        
        ### 2. Configure Options
        - **Intelligent Analysis**: Enable AI-powered question generation for better test cases
        - **Collection Name**: Specify ChromaDB collection for vector storage
        
        ### 3. Answer Questions (Optional)
        When intelligent analysis is enabled, the system may generate clarifying questions to improve test case quality.
        
        ### 4. Review Results
        - Generated test cases with compliance validation
        - Performance metrics and quality scores
        - Traceability information
        
        ### 5. Provide Feedback
        Rate the generated test cases to help improve the system.
        """)
    
    with tab2:
        st.markdown("""
        ## Configuration
        
        ### Environment Variables
        
        **Required:**
        - `GOOGLE_PROJECT_ID`: Google Cloud project ID
        - `GCS_BUCKET`: Google Cloud Storage bucket name
        - `BIGQUERY_DATASET`: BigQuery dataset name
        
        **Optional:**
        - `CHROMA_API_KEY`: ChromaDB Cloud API key
        - `CHROMA_TENANT`: ChromaDB tenant ID
        - `CHROMA_DATABASE`: ChromaDB database name
        - `JIRA_API_URL`: Jira instance URL
        - `JIRA_USER`: Jira username
        - `JIRA_TOKEN`: Jira API token
        - `JIRA_PROJECT_KEY`: Jira project key
        
        ### File Structure
        ```
        orchestrator/
        ├── temp/                 # Temporary uploaded files
        ├── user_feedback/        # User feedback data
        ├── generated_testcases/  # Generated test cases
        ├── traceability_logs/    # Traceability information
        └── chroma/              # Local ChromaDB storage
        ```
        """)
    
    with tab3:
        st.markdown("""
        ## Frequently Asked Questions
        
        **Q: What file formats are supported?**
        A: PDF, Word (DOC/DOCX), XML, Markup (HTML/HTM), TXT, MD, and RTF files are supported for both requirements and regulatory documents. The system will attempt to extract text from any uploaded document.
        
        **Q: How does intelligent analysis work?**
        A: The system uses LLM to generate domain-specific questions that help clarify requirements and improve test case quality.
        
        **Q: Can I use the system without cloud services?**
        A: Yes, the system can work with local ChromaDB and simulated services, though some features may be limited.
        
        **Q: How are test cases validated for compliance?**
        A: The system uses iterative validation against regulatory documents with scoring and improvement cycles.
        
        **Q: Where is my data stored?**
        A: Data is stored locally in the orchestrator directory and optionally in configured cloud services.
        """)

def main():
    """Main application"""
    initialize_session_state()
    display_header()
    display_sidebar()
    
    # Route to different pages based on navigation
    current_page = st.session_state.get('current_page', '🏠 Home')
    
    if current_page == '📊 Dashboard':
        main_dashboard()
        return
    elif current_page == '📚 Documentation':
        display_documentation()
        return
    
    # Home page - main functionality
    # Handle questions flow
    if st.session_state.questions_generated:
        if display_questions_interface():
            st.rerun()
        return
    
    # Continue processing after questions are answered
    if st.session_state.continue_processing and st.session_state.stored_files['req'] and st.session_state.stored_files['reg']:
        st.session_state.processing = True
        st.session_state.continue_processing = False
        
        with st.spinner("Processing your answers and generating test cases..."):
            try:
                # Process files with answers
                results = process_uploaded_files(
                    st.session_state.stored_files['req'], 
                    st.session_state.stored_files['reg'], 
                    st.session_state.stored_intelligent_analysis
                )
                
                if not results.get('questions_generated'):
                    st.session_state.workflow_results = results
                    st.success("Test cases generated successfully!")
                    
            except Exception as e:
                st.error(f"Error processing files: {e}")
            finally:
                st.session_state.processing = False
        
        st.rerun()
    
    # Main interface
    req_file, reg_file = display_file_upload()
    intelligent_analysis, collection_name = display_processing_options()
    
    # Process button
    if st.button("🚀 Generate Test Cases", type="primary", disabled=st.session_state.processing):
        if not req_file or not reg_file:
            st.error("Please upload both requirements and regulatory documents.")
            return
        
        # Store files and options for later use
        st.session_state.stored_files['req'] = req_file
        st.session_state.stored_files['reg'] = reg_file
        st.session_state.stored_intelligent_analysis = intelligent_analysis
        
        st.session_state.processing = True
        
        with st.spinner("Processing documents and generating test cases..."):
            try:
                # Process files
                results = process_uploaded_files(req_file, reg_file, intelligent_analysis)
                
                # Check if questions were generated
                if results.get('questions_generated'):
                    st.session_state.questions_generated = True
                    st.session_state.current_questions = load_questions_from_file()
                    st.info("Questions generated! Please answer them to improve test case quality.")
                    st.rerun()
                else:
                    st.session_state.workflow_results = results
                    
            except Exception as e:
                st.error(f"Error processing files: {e}")
            finally:
                st.session_state.processing = False
    
    # Display results if available
    if st.session_state.workflow_results:
        display_results(st.session_state.workflow_results)
        display_feedback_interface()
    
    # Clear results button
    if st.session_state.workflow_results:
        if st.button("🔄 Clear Results"):
            st.session_state.workflow_results = None
            st.session_state.questions_generated = False
            st.session_state.current_questions = []
            st.session_state.user_answers = {}
            st.rerun()

if __name__ == "__main__":
    main()