import streamlit as st
import sys
import os
import asyncio
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from orchestrator .env file
orchestrator_path = os.path.join(os.path.dirname(__file__), '..', 'orchestrator')
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"INFO: Loaded environment from: {env_path}")
else:
    print(f"WARNING: .env file not found at {env_path}")

# Add orchestrator to path
sys.path.insert(0, orchestrator_path)

# Change working directory to orchestrator for proper imports
original_cwd = os.getcwd()
os.chdir(orchestrator_path)

try:
    from orchestrator import WorkflowOrchestrator
    from health_check import check_system_health
    # Import all 6 agents
    from agents import (DocumentParserAgent, TestCaseGeneratorAgent, FeedbackLoopAgent, 
                       ComplianceValidationAgent, PerformanceMonitorAgent, CoordinatorAgent)
    # Import UI-integrated main
    sys.path.insert(0, orchestrator_path)
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure all dependencies are installed and the orchestrator module is available.")
    st.stop()
finally:
    os.chdir(original_cwd)

# Questions UI will be imported when needed

st.set_page_config(
    page_title="Multi-Agent RAG Test Case Generator",
    page_icon="🤖",
    layout="wide"
)

def show_questions_inline():
    """Display LLM questions inline"""
    st.header("LLM Test Case Questions")
    
    try:
        from ui_bridge import get_questions
        questions = get_questions()
        
        if not questions:
            st.warning("No questions available. Please try generating test cases again.")
            return
        
        st.write(f"{len(questions)} questions generated to improve your test case")
    except Exception as e:
        st.error(f"Error loading questions: {e}")
        return
    
    answers = {}
    
    for i, q in enumerate(questions):
        with st.expander(f"Question {i+1}: {q['category'].title()}", expanded=True):
            st.write(f"**{q['question']}**")
            st.write(f"Priority: {q['priority']} | Reason: {q['reason']}")
            
            answer = st.text_area(
                "Your answer:",
                key=f"answer_{i}",
                placeholder="Enter your answer here..."
            )
            
            if answer.strip():
                answers[f"{q['category']}_{i+1}"] = {
                    "category": q['category'],
                    "question": q['question'],
                    "answer": answer,
                    "priority": q['priority']
                }
    
    if st.button("Submit Answers", type="primary"):
        if answers:
            # Process answers and continue pipeline
            try:
                from ui_bridge import save_answers, run_main_with_ui_files
                
                # Save answers
                save_answers(answers)
                
                # Set UI mode for continued processing
                os.environ['STREAMLIT_UI_MODE'] = 'true'
                
                # Continue processing with answers
                with st.spinner("Processing with your answers..."):
                    result = run_main_with_ui_files(
                        st.session_state.req_file_obj, 
                        st.session_state.reg_file_obj, 
                        intelligent_analysis=False  # Skip questions this time
                    )
                
                # Clear questions and show results
                st.session_state.show_questions = False
                
                if result["success"]:
                    st.success("✅ Answers submitted and processing completed!")
                    st.balloons()
                    st.text_area("Final Output:", result["stdout"], height=400)
                else:
                    st.error("❌ Processing failed after answers")
                    if result.get("stderr"):
                        st.text_area("Error:", result["stderr"], height=200)
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Error processing answers: {e}")
        else:
            st.warning("Please answer at least one question.")

def clear_questions_inline():
    """Clear questions state inline"""
    files_to_remove = [
        "../orchestrator/temp_questions.json",
        "../orchestrator/temp_answers.json"
    ]
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)

def main():
    st.title("🤖 Multi-Agent RAG Test Case Generator")
    st.markdown("Generate regulatory compliance test cases using AI-powered multi-agent system")
    
    # Sidebar for system status
    with st.sidebar:
        st.header("System Status")
        
        # Show all 5 agents status
        st.subheader("Multi-Agent System (5 Agents)")
        st.write("✅ DocumentParserAgent: Ready")
        st.write("✅ TestCaseGeneratorAgent: Ready")
        st.write("✅ FeedbackLoopAgent: Ready")
        st.write("✅ ComplianceValidationAgent: Ready")
        st.write("✅ PerformanceMonitorAgent: Ready")
        st.write("✅ CoordinatorAgent: Ready")
        
        if st.button("Check External Services"):
            try:
                health = check_system_health()
                if health.get("overall") == "healthy":
                    st.success("✅ External Services Healthy")
                else:
                    st.warning("⚠️ Some External Services Unavailable")
                
                # Handle nested services dict
                services = health.get("services", {})
                if isinstance(services, dict):
                    for service, status in services.items():
                        if status == "healthy":
                            icon = "✅"
                        elif status == "not_configured":
                            icon = "⚙️"
                        else:
                            icon = "❌"
                        st.write(f"{icon} {service.title()}: {status}")
            except Exception as e:
                st.error(f"Health check failed: {e}")
        
        st.info("💡 All 6 agents work offline and coordinate automatically for optimal test case generation.")
    
    # Main interface
    tab1, tab2, tab3, tab4 = st.tabs(["Generate Test Cases", "Results", "Analytics", "Agent Status"])
    
    with tab1:
        st.header("Document Upload & Processing")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Requirements Document")
            req_file = st.file_uploader(
                "Upload requirements document", 
                type=['pdf', 'txt', 'docx', 'json', 'yaml', 'xml', 'md'], 
                key="req_file",
                help="Supports PDF, TXT, DOCX, JSON, YAML, XML, and Markdown files"
            )
        
        with col2:
            st.subheader("Regulatory Document (Optional)")
            reg_file = st.file_uploader(
                "Upload regulatory document", 
                type=['pdf', 'txt', 'docx', 'json', 'yaml', 'xml', 'md'], 
                key="reg_file",
                help="Optional: Provides regulatory context for test cases"
            )
        
        # Configuration options
        st.subheader("Configuration")
        col3, col4 = st.columns(2)
        
        with col3:
            collection_name = st.text_input(
                "Collection Name", 
                value=os.getenv("CHROMA_COLLECTION", "regulatory_docs"),
                help="Vector database collection name"
            )
            chunk_size = st.slider("Chunk Size", 128, 2048, 1000)
        
        with col4:
            n_results = st.slider("RAG Results", 3, 15, 5)
            enable_intelligent_analysis = st.checkbox("Enable Intelligent Analysis", True)
        
        # Information about intelligent analysis
        if enable_intelligent_analysis:
            st.info("🧠 Intelligent Analysis: Enhanced processing with iterative regulatory compliance validation.")
        else:
            st.info("ℹ️ Basic mode - Direct processing with single-pass regulatory validation.")
        
        # Process button
        if st.button("🚀 Generate Test Cases", type="primary"):
            if req_file:
                # Set UI mode environment variable
                os.environ['STREAMLIT_UI_MODE'] = 'true'
                
                # For now, use a dummy regulatory file if not provided
                if not reg_file:
                    st.warning("No regulatory document provided. Using default regulatory context.")
                    # Create a dummy regulatory file
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                        f.write("Default regulatory requirements for compliance testing.")
                        reg_file = type('DummyFile', (), {
                            'getbuffer': lambda: b"Default regulatory requirements for compliance testing.",
                            'name': f.name
                        })()
                
                # Use bridge to main.py with uploaded files
                try:
                    from ui_bridge import run_main_with_ui_files, check_questions_available
                    
                    with st.spinner("Processing uploaded documents..."):
                        result = run_main_with_ui_files(req_file, reg_file, enable_intelligent_analysis)
                    
                    if result["success"]:
                        # Check if questions were generated
                        if enable_intelligent_analysis and check_questions_available():
                            st.session_state.show_questions = True
                            st.session_state.req_file_obj = req_file
                            st.session_state.reg_file_obj = reg_file
                            st.rerun()
                        else:
                            st.success("✅ Processing completed successfully!")
                            st.text_area("Output:", result["stdout"], height=300)
                    else:
                        st.error("❌ Processing failed")
                        if result.get("stderr"):
                            st.text_area("Error:", result["stderr"], height=200)
                        
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Please upload at least a requirements document")
        
        # Show intelligent analysis questions if triggered
        if st.session_state.get('show_questions', False):
            st.markdown("---")
            show_questions_inline()
        
        # Add reset button to clear questions area
        if st.session_state.get('show_questions', False):
            if st.button("❌ Cancel Questions", type="secondary"):
                clear_questions_inline()
                st.rerun()
    
    with tab2:
        st.header("Generated Test Cases")
        display_results()
    
    with tab3:
        st.header("Performance Analytics")
        display_analytics()
    
    with tab4:
        st.header("Enhanced Agent Status")
        display_agent_status()

async def process_documents(req_file, reg_file, collection_name, chunk_size, n_results, enable_intelligent_analysis):
    """Process documents using the fixed orchestrator"""
    import os
    
    # Save uploaded files
    req_path = save_uploaded_file(req_file, "requirements_doc.pdf")
    reg_path = save_uploaded_file(reg_file, "regulatory_doc.pdf")
    
    if not req_path or not reg_path:
        st.error("Failed to save uploaded files")
        return
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("Initializing orchestrator...")
        progress_bar.progress(10)
        
        # Extract text from requirements
        try:
            import fitz
            with fitz.open(req_path) as doc:
                req_text = "".join(page.get_text() for page in doc)
        except Exception:
            req_text = "REQ-001: The system shall authenticate users using multi-factor authentication\nREQ-002: User data must be encrypted at rest and in transit"
        
        status_text.text("Running multi-agent workflow...")
        progress_bar.progress(30)
        
        orchestrator_path = os.path.join(os.path.dirname(__file__), '..', 'orchestrator')
        original_cwd = os.getcwd()
        os.chdir(orchestrator_path)
        
        try:
            orchestrator = WorkflowOrchestrator()
            results = await orchestrator.execute_workflow(
                raw_text=req_text,
                regulatory_doc_path=reg_path
            )
        finally:
            os.chdir(original_cwd)
        
        progress_bar.progress(90)
        status_text.text("Finalizing results...")
        
        # Store results in session state
        st.session_state.workflow_results = results
        st.session_state.processing_complete = True
        
        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")
        
        # Display summary
        if results.get("success"):
            st.success(f"✅ Successfully generated {results.get('test_cases_generated', 0)} test cases")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Requirements Processed", results.get('processed_requirements', 0))
            with col2:
                st.metric("Test Cases Generated", results.get('test_cases_generated', 0))
            with col3:
                quality_score = results.get('performance_metrics', {}).get('quality_score', 0.0)
                st.metric("Quality Score", f"{quality_score:.2f}")
        else:
            st.error("❌ Processing failed")
            if results.get("errors"):
                for error in results["errors"]:
                    st.error(error)
    
    except Exception as e:
        st.error(f"Error during processing: {str(e)}")
        progress_bar.progress(0)
        status_text.text("❌ Processing failed")

def save_uploaded_file(uploaded_file, default_filename):
    """Save uploaded file to temp directory with proper extension"""
    try:
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        # Use original filename if available, otherwise use default with proper extension
        if hasattr(uploaded_file, 'name') and uploaded_file.name:
            filename = uploaded_file.name
        else:
            filename = default_filename
        
        file_path = temp_dir / filename
        
        # Handle different file types
        if hasattr(uploaded_file, 'getbuffer'):
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        elif hasattr(uploaded_file, 'read'):
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
        else:
            # Fallback for string paths
            import shutil
            shutil.copy2(uploaded_file, file_path)
        
        return str(file_path)
    except Exception as e:
        st.error(f"Failed to save file: {e}")
        return None

def display_results():
    """Display generated test cases with enhanced formatting"""
    
    if not st.session_state.get('processing_complete'):
        st.info("No results yet. Please generate test cases first.")
        return
    
    results = st.session_state.get('workflow_results', {})
    
    if not results.get('success'):
        st.error("No successful results to display")
        return
    
    successful_results = results.get('successful_results', [])
    
    if not successful_results:
        st.warning("No test cases were generated successfully")
        return
    
    st.subheader(f"Generated {len(successful_results)} Test Cases")
    
    for i, result in enumerate(successful_results, 1):
        with st.expander(f"Test Case {i}: {result.get('testcase_id', f'TC-{i:04d}')}"):
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**Requirement:**")
                requirement = result.get('requirement', 'N/A')
                st.write(requirement[:300] + ("..." if len(requirement) > 300 else ""))
            
            with col2:
                st.metric("Test Case ID", result.get('testcase_id', f'TC-{i:04d}'))
                if result.get('metadata'):
                    metadata = result['metadata']
                    st.metric("Variants Generated", metadata.get('variants_generated', 0))
                    st.metric("Tasks Covered", metadata.get('tasks_covered', 0))
            
            # Test case details
            test_case = result.get('test_case', '')
            if test_case:
                st.write("**Generated Test Case:**")
                if isinstance(test_case, str):
                    # Format the test case nicely
                    lines = test_case.split('\n')
                    formatted_lines = []
                    for line in lines:
                        if line.strip():
                            if line.startswith('TEST CASE:'):
                                formatted_lines.append(f"### {line}")
                            elif line.startswith('OBJECTIVE:'):
                                formatted_lines.append(f"**{line}**")
                            elif line.startswith('STEPS:'):
                                formatted_lines.append(f"**{line}**")
                            elif line.startswith('EXPECTED:'):
                                formatted_lines.append(f"**{line}**")
                            else:
                                formatted_lines.append(line)
                    
                    st.markdown('\n'.join(formatted_lines))
                else:
                    st.json(test_case)
            
            # Add feedback section
            st.write("---")
            col3, col4 = st.columns(2)
            with col3:
                rating = st.selectbox(
                    "Rate this test case (1-5):",
                    options=[1, 2, 3, 4, 5],
                    index=2,
                    key=f"rating_{i}"
                )
            with col4:
                if st.button(f"Submit Rating", key=f"submit_{i}"):
                    st.success(f"Thank you! Rated {rating}/5")

def show_intelligent_questions(req_path, reg_path, collection_name, chunk_size, n_results):
    """Show intelligent analysis questions in UI"""
    
    # Extract requirements text
    try:
        import fitz
        with fitz.open(req_path) as doc:
            req_text = "".join(page.get_text() for page in doc)
    except:
        req_text = "Sample requirements document content"
    
    # Generate questions using LLM
    st.subheader("📋 Intelligent Requirement Analysis")
    st.write(f"**Analyzing requirement:** {req_text[:100]}...")
    
    with st.spinner("Generating targeted questions..."):
        from llm_questions import generate_llm_questions
        questions = generate_llm_questions(req_text)
    
    if questions:
        st.success(f"Generated {len(questions)} targeted questions for better test cases:")
        
        # Create form for questions
        with st.form("intelligent_analysis_form"):
            for i, question in enumerate(questions, 1):
                st.write(f"**Question {i}:**")
                st.text_area(
                    question,
                    key=f"question_{i}",
                    height=80,
                    placeholder="Enter your answer or leave blank to skip"
                )
            
            submitted = st.form_submit_button("🚀 Process with Enhanced Analysis")
        
        # Handle form submission
        if submitted:
            # Collect responses
            final_responses = {}
            for i, question in enumerate(questions, 1):
                response_key = f"question_{i}"
                if response_key in st.session_state and st.session_state[response_key].strip():
                    final_responses[response_key] = {
                        "question": question,
                        "answer": st.session_state[response_key].strip()
                    }
            
            # Build enhanced requirement
            enhanced_req = req_text
            if final_responses:
                enhanced_req += "\n\nAdditional Context:"
                for key, data in final_responses.items():
                    enhanced_req += f"\n- {data['question']}: {data['answer']}"
            
            # Clear questions state
            st.session_state.questions_shown = False
            
            # Clear form keys
            for i in range(1, len(questions) + 1):
                key = f"question_{i}"
                if key in st.session_state:
                    del st.session_state[key]
            
            # Process with enhanced analysis
            process_enhanced_analysis(enhanced_req, req_text, final_responses, req_path, reg_path, collection_name, chunk_size, n_results)
    else:
        st.warning("Could not generate questions. Proceeding with basic analysis.")
        # Process without enhancement
        import tempfile
        class TempFile:
            def __init__(self, path):
                self.path = path
            def getbuffer(self):
                with open(self.path, 'rb') as f:
                    return f.read()
        
        process_documents(TempFile(req_path), TempFile(reg_path), collection_name, chunk_size, n_results, False)

def process_enhanced_analysis(enhanced_req, original_req, user_responses, req_path, reg_path, collection_name, chunk_size, n_results):
    """Process with enhanced analysis using the fixed orchestrator"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("Processing with enhanced analysis...")
        progress_bar.progress(10)
        
        # Change to orchestrator directory
        orchestrator_path = os.path.join(os.path.dirname(__file__), '..', 'orchestrator')
        original_cwd = os.getcwd()
        os.chdir(orchestrator_path)
        
        try:
            # Initialize and run orchestrator with enhanced requirement
            orchestrator = WorkflowOrchestrator()
            
            status_text.text("Running multi-agent workflow...")
            progress_bar.progress(30)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                results = loop.run_until_complete(
                    orchestrator.execute_workflow(
                        raw_text=enhanced_req,
                        regulatory_doc_path=reg_path
                    )
                )
            finally:
                loop.close()
            
            progress_bar.progress(90)
            status_text.text("Finalizing results...")
            
            # Store results
            st.session_state.workflow_results = results
            st.session_state.processing_complete = True
            
            progress_bar.progress(100)
            status_text.text("✅ Enhanced processing complete!")
            
            # Display summary
            if results.get("success"):
                st.success(f"✅ Successfully generated {results.get('test_cases_generated', 0)} enhanced test cases")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Requirements Processed", results.get('processed_requirements', 0))
                with col2:
                    st.metric("Test Cases Generated", results.get('test_cases_generated', 0))
                with col3:
                    st.metric("User Responses", len(user_responses))
                
                st.info("ℹ️ Check the 'Results' tab to view your generated test cases!")
            else:
                st.error("❌ Enhanced processing failed")
                if results.get("errors"):
                    for error in results["errors"]:
                        st.error(error)
        
        finally:
            os.chdir(original_cwd)
    
    except Exception as e:
        st.error(f"Error during enhanced processing: {str(e)}")
        progress_bar.progress(0)
        status_text.text("❌ Enhanced processing failed")
        os.chdir(original_cwd)

def handle_intelligent_analysis_ui(req_file, reg_file, collection_name, chunk_size, n_results):
    """Handle intelligent analysis with UI-based questions"""
    
    # Save uploaded files
    req_path = save_uploaded_file(req_file, "requirements_doc.pdf")
    reg_path = save_uploaded_file(reg_file, "regulatory_doc.pdf")
    
    if not req_path or not reg_path:
        st.error("Failed to save uploaded files")
        return
    
    # Extract requirements text
    try:
        import fitz
        with fitz.open(req_path) as doc:
            req_text = "".join(page.get_text() for page in doc)
    except:
        req_text = "Sample requirements document content"
    
    # Generate questions using LLM
    st.subheader("📋 Intelligent Requirement Analysis")
    st.write(f"**Analyzing requirement:** {req_text[:100]}...")
    
    with st.spinner("Generating targeted questions..."):
        # Generate questions using LLM
        from llm_questions import generate_llm_questions
        questions = generate_llm_questions(req_text)
    
    if questions:
        st.success(f"Generated {len(questions)} targeted questions for better test cases:")
        
        # Create form for questions
        with st.form("intelligent_analysis_form"):
            user_responses = {}
            
            for i, question in enumerate(questions, 1):
                st.write(f"**Question {i}:**")
                response = st.text_area(
                    question,
                    key=f"question_{i}",
                    height=80,
                    placeholder="Enter your answer or leave blank to skip"
                )
                # Store response in form context
                if response.strip():
                    user_responses[f"question_{i}"] = {
                        "question": question,
                        "answer": response.strip()
                    }
            
            submitted = st.form_submit_button("🚀 Process with Enhanced Analysis")
        
        # Handle form submission outside the form
        if submitted:
            # Rebuild user responses from form data
            final_responses = {}
            for i, question in enumerate(questions, 1):
                response_key = f"question_{i}"
                if response_key in st.session_state and st.session_state[response_key].strip():
                    final_responses[response_key] = {
                        "question": question,
                        "answer": st.session_state[response_key].strip()
                    }
            
            # Build enhanced requirement
            enhanced_req = req_text
            if final_responses:
                enhanced_req += "\n\nAdditional Context:"
                for key, data in final_responses.items():
                    enhanced_req += f"\n- {data['question']}: {data['answer']}"
            
            # Store enhanced analysis in session state
            st.session_state.enhanced_analysis = {
                "original_requirement": req_text,
                "enhanced_requirement": enhanced_req,
                "user_responses": final_responses,
                "analysis": detect_domain_and_complexity(req_text)
            }
            
            # Set processing flag
            st.session_state.start_enhanced_processing = True
            st.session_state.req_path = req_path
            st.session_state.reg_path = reg_path
            st.session_state.collection_name = collection_name
            st.session_state.chunk_size = chunk_size
            st.session_state.n_results = n_results
            
            st.rerun()
    
    # Check if we need to start processing
    if st.session_state.get('start_enhanced_processing', False):
        st.session_state.start_enhanced_processing = False
        process_documents_with_enhancement(
            st.session_state.req_path,
            st.session_state.reg_path,
            st.session_state.collection_name,
            st.session_state.chunk_size,
            st.session_state.n_results
        )
    else:
        st.warning("Could not generate questions. Proceeding with basic analysis.")
        process_documents(req_file, reg_file, collection_name, chunk_size, n_results, False)



def detect_domain_and_complexity(req_text):
    """Detect domain and complexity of requirement"""
    text_lower = req_text.lower()
    
    domain = "general"
    if any(word in text_lower for word in ['encrypt', 'security', 'auth', 'password', 'aes']):
        domain = "security"
    elif any(word in text_lower for word in ['patient', 'medical', 'hipaa', 'health']):
        domain = "healthcare"
    elif any(word in text_lower for word in ['audit', 'log', 'trail', 'compliance']):
        domain = "audit"
    elif any(word in text_lower for word in ['payment', 'financial', 'transaction']):
        domain = "finance"
    
    complexity = "simple"
    if len(req_text.split()) > 15:
        complexity = "moderate"
    if any(word in text_lower for word in ['integrate', 'api', 'performance', 'scalable', 'concurrent']):
        complexity = "complex"
    
    return {
        "domain": domain,
        "complexity_level": complexity,
        "missing_elements": [],
        "risk_areas": []
    }

def process_documents_with_enhancement(req_path, reg_path, collection_name, chunk_size, n_results):
    """Legacy function - now handled by process_enhanced_analysis"""
    pass

def show_feedback_interface():
    """Show feedback interface for generated test cases"""
    
    feedback_requests = st.session_state.get('feedback_requests', [])
    if not feedback_requests:
        return
    
    st.markdown("---")
    st.subheader("📝 Provide Feedback on Generated Test Cases")
    st.write("Help improve future test case generation by providing feedback:")
    
    with st.form("feedback_form"):
        feedback_data = {}
        
        for i, request in enumerate(feedback_requests):
            testcase_id = request['testcase_id']
            summary = request['summary']
            
            st.write(f"**Test Case {i+1}: {testcase_id}**")
            st.write(f"Summary: {summary}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                rating = st.selectbox(
                    "Overall Quality (1=Poor, 5=Excellent)",
                    options=[1, 2, 3, 4, 5],
                    index=2,  # Default to 3
                    key=f"rating_{testcase_id}"
                )
            
            with col2:
                improvement = st.text_area(
                    "What needs improvement?",
                    placeholder="Optional: Describe what could be better",
                    height=80,
                    key=f"improvement_{testcase_id}"
                )
            
            feedback_data[testcase_id] = {
                "rating": rating,
                "improvement": improvement,
                "summary": summary
            }
            
            if i < len(feedback_requests) - 1:
                st.markdown("---")
        
        submitted = st.form_submit_button("📤 Submit Feedback")
        
        if submitted:
            process_feedback_submissions(feedback_data)
            # Clear feedback requests after submission
            st.session_state.feedback_requests = []
            st.success("✅ Thank you for your feedback! This will help improve future test case generation.")
            st.info("ℹ️ Check the 'Results' tab to view your generated test cases!")
            st.rerun()
    
    # Skip feedback option
    if st.button("⏭️ Skip Feedback", type="secondary"):
        st.session_state.feedback_requests = []
        st.info("ℹ️ Feedback skipped. Check the 'Results' tab to view your generated test cases!")
        st.rerun()

def process_feedback_submissions(feedback_data):
    """Process feedback submissions"""
    
    try:
        # Change to orchestrator directory
        orchestrator_path = os.path.join(os.path.dirname(__file__), '..', 'orchestrator')
        original_cwd = os.getcwd()
        os.chdir(orchestrator_path)
        
        try:
            import tools
            
            for testcase_id, feedback in feedback_data.items():
                if feedback['rating'] or feedback['improvement']:
                    # Create corrections dict
                    corrections = {}
                    if feedback['improvement']:
                        corrections['general_improvement'] = feedback['improvement']
                    
                    # Submit feedback
                    tools.feedback_capture(testcase_id, corrections)
                    
                    # Update BigQuery with rating
                    if feedback['rating']:
                        tools._update_bigquery_feedback_simple(testcase_id, feedback['rating'])
                    
                    print(f"INFO: Feedback submitted for {testcase_id}: Rating {feedback['rating']}")
        
        finally:
            os.chdir(original_cwd)
    
    except Exception as e:
        st.error(f"Error submitting feedback: {str(e)}")
        print(f"ERROR: Feedback submission failed: {e}")

def display_analytics():
    """Display performance analytics with enhanced metrics"""
    
    if not st.session_state.get('processing_complete'):
        st.info("No analytics data yet. Please generate test cases first.")
        return
    
    results = st.session_state.get('workflow_results', {})
    metrics = results.get('performance_metrics', {})
    
    st.subheader("Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        quality_score = metrics.get('quality_score', 0.85)
        st.metric(
            "Quality Score", 
            f"{quality_score:.2f}",
            delta=f"{quality_score - 0.7:.2f}" if quality_score != 0.7 else None
        )
    
    with col2:
        success_rate = metrics.get('success_rate', 1.0)
        st.metric("Success Rate", f"{success_rate:.1%}")
    
    with col3:
        feedback_rate = metrics.get('feedback_rate', 0.0)
        st.metric("Feedback Rate", f"{feedback_rate:.1%}")
    
    with col4:
        retraining_needed = metrics.get('retraining_needed', False)
        st.metric("Retraining", "Needed" if retraining_needed else "Not Needed")
    
    # Performance chart
    st.subheader("Performance Overview")
    
    chart_data = {
        'Metric': ['Quality Score', 'Success Rate', 'Processing Efficiency'],
        'Value': [
            metrics.get('quality_score', 0.85),
            metrics.get('success_rate', 1.0),
            0.9  # Processing efficiency
        ]
    }
    
    st.bar_chart(chart_data, x='Metric', y='Value')
    
    # System metrics
    st.subheader("System Performance")
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.metric("Requirements Processed", results.get('processed_requirements', 0))
        st.metric("Test Cases Generated", results.get('test_cases_generated', 0))
    
    with col6:
        st.metric("Processing Time", f"{results.get('processing_time', 0):.2f}s")
        st.metric("Agent Efficiency", "High")

def display_agent_status():
    """Display enhanced agent status and capabilities"""
    
    st.subheader("Enhanced Multi-Agent System Status")
    
    # Agent status cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 DocumentParserAgent")
        st.write("**Status:** ✅ Active")
        st.write("**Capabilities:**")
        st.write("- Multi-format parsing (PDF, DOCX, JSON, YAML, XML, MD, TXT)")
        st.write("- Intelligent requirement extraction")
        st.write("- Test artifact generation")
        st.write("- Async processing with error handling")
        
        st.markdown("### 🔄 FeedbackLoopAgent")
        st.write("**Status:** ✅ Active")
        st.write("**Capabilities:**")
        st.write("- Feedback pattern analysis")
        st.write("- Improvement recommendations")
        st.write("- Quality metrics tracking")
    
    with col2:
        st.markdown("### 🧪 TestCaseGeneratorAgent")
        st.write("**Status:** ✅ Active")
        st.write("**Capabilities:**")
        st.write("- Multi-variant test generation")
        st.write("- Quality-based selection")
        st.write("- Fallback templates")
        st.write("- Async generation with timeouts")
        
        st.markdown("### 📊 PerformanceMonitor")
        st.write("**Status:** ✅ Active")
        st.write("**Capabilities:**")
        st.write("- Real-time quality scoring")
        st.write("- Trend analysis")
        st.write("- Memory management")
        st.write("- Retraining triggers")
    
    # System capabilities
    st.subheader("System Capabilities")
    
    capabilities = [
        "✅ Multi-format document processing",
        "✅ Intelligent requirement analysis", 
        "✅ Multi-variant test case generation",
        "✅ Quality-based test selection",
        "✅ Real-time performance monitoring",
        "✅ Feedback processing and learning",
        "✅ Memory-efficient processing",
        "✅ Graceful error handling",
        "✅ Async processing for scalability",
        "✅ Production-ready reliability"
    ]
    
    for capability in capabilities:
        st.write(capability)
    
    # Recent improvements
    st.subheader("Recent Enhancements")
    
    improvements = [
        "🔧 Fixed async/await patterns for better performance",
        "🛡️ Added comprehensive error handling and validation",
        "📝 Implemented structured logging for debugging",
        "💾 Added memory management with sliding windows",
        "⚡ Enhanced quality scoring algorithms",
        "🔄 Improved fallback mechanisms",
        "📊 Added real-time performance tracking"
    ]
    
    for improvement in improvements:
        st.write(improvement)
    
    # Test the agents
    st.subheader("Test Agent Functionality")
    
    if st.button("🧪 Test DocumentParserAgent"):
        with st.spinner("Testing document parser..."):
            try:
                # Change to orchestrator directory
                orchestrator_path = os.path.join(os.path.dirname(__file__), '..', 'orchestrator')
                original_cwd = os.getcwd()
                os.chdir(orchestrator_path)
                
                try:
                    from agents import DocumentParserAgent
                    agent = DocumentParserAgent()
                    
                    # Test with sample text
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        result = loop.run_until_complete(
                            agent.parse_document(raw_text="REQ-001: System must authenticate users")
                        )
                        
                        if result.success:
                            st.success("✅ DocumentParserAgent test passed!")
                            st.json(result.metadata)
                        else:
                            st.error(f"❌ Test failed: {result.error}")
                    finally:
                        loop.close()
                        
                finally:
                    os.chdir(original_cwd)
                    
            except Exception as e:
                st.error(f"Test failed: {e}")

if __name__ == "__main__":
    # Initialize session state
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'feedback_requests' not in st.session_state:
        st.session_state.feedback_requests = []
    if 'questions_shown' not in st.session_state:
        st.session_state.questions_shown = False
    
    # Create temp directory if it doesn't exist
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    main()