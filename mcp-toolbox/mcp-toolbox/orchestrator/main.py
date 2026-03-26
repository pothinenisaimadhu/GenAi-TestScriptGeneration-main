import os
from dotenv import load_dotenv
import argparse
import asyncio
import fitz  # PyMuPDF

# Load environment variables from the .env file in the parent directory
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=dotenv_path)
print(f"INFO: Loading environment from: {dotenv_path}")
print(f"INFO: ChromaDB API Key loaded: {'Yes' if os.getenv('CHROMA_API_KEY') else 'No'}")

import tools
from orchestrator import WorkflowOrchestrator

async def apply_intelligent_analysis(raw_text: str) -> str:
    """Apply intelligent analysis with LLM questions"""
    try:
        # Use intelligent requirement analysis
        analysis_result = tools.intelligent_requirement_analysis(raw_text)
        
        if analysis_result.get('user_responses'):
            enhanced_req = analysis_result['enhanced_requirement']
            print(f"INFO: Enhanced requirement with {len(analysis_result['user_responses'])} user responses")
            return enhanced_req
        else:
            print("INFO: No user responses collected, using original text")
            return raw_text
            
    except Exception as e:
        print(f"ERROR: Intelligent analysis failed: {e}")
        return raw_text

def get_document_content(doc_path: str, upload: bool = False) -> tuple[str, str | None]:
    """
    Extracts text from a document and optionally uploads it to GCS.

    Args:
        doc_path (str): The local path to the document.
        upload (bool): Whether to upload the document to GCS.

    Returns:
        A tuple containing the extracted text and the GCS URI (if uploaded).
    """
    gcs_uri = None
    file_ext = os.path.splitext(doc_path)[1].lower()

    # For plain text, read directly for speed.
    if file_ext == ".txt":
        print(f"INFO: Text file detected ({doc_path}), reading content directly.")
        with open(doc_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(), gcs_uri

    # For PDF files, use local extraction directly
    if file_ext == ".pdf":
        print(f"INFO: PDF file detected ({doc_path}), using local PyMuPDF extraction.")
        try:
            with fitz.open(doc_path) as doc:
                pdf_text = "".join(page.get_text() for page in doc)
            print(f"INFO: Local PDF extraction successful. Extracted {len(pdf_text)} characters.")
            return pdf_text, gcs_uri
        except Exception as e:
            print(f"ERROR: Local PDF extraction failed: {e}")
            return "", gcs_uri

    return "", gcs_uri

async def run_pipeline(requirements_doc_path: str, regulatory_doc_path: str, intelligent_analysis: bool = False):
    """
    Executes the multi-agent RAG test case generation pipeline with orchestration.

    Args:
        requirements_doc_path (str): Path to the requirements document to process.
        regulatory_doc_path (str): Path to the regulatory document for the knowledge base.
    """
    print("=== STARTING MULTI-AGENT RAG PIPELINE WITH ORCHESTRATION ===")
    
    # Initialize orchestrator
    orchestrator = WorkflowOrchestrator()
    
    # Extract document content
    raw_text, _ = get_document_content(requirements_doc_path, upload=False)
    if not raw_text:
        print("❌ No text extracted from document. Exiting.")
        return
    
    print(f"INFO: Extracted {len(raw_text)} characters from requirements document")
    
    # Apply intelligent analysis if enabled
    if intelligent_analysis:
        print("\n=== INTELLIGENT ANALYSIS ENABLED ===")
        enhanced_text = await apply_intelligent_analysis(raw_text)
        if enhanced_text:
            raw_text = enhanced_text
            print("INFO: Requirements enhanced with user input")
    
    # Execute multi-agent workflow
    workflow_results = await orchestrator.execute_workflow(raw_text, regulatory_doc_path)
    
    # Display results
    if workflow_results["success"]:
        print(f"\n=== PIPELINE COMPLETED SUCCESSFULLY ===")
        print(f"Requirements processed: {workflow_results['processed_requirements']}")
        print(f"Test cases generated: {workflow_results['test_cases_generated']}")
        print(f"Feedback entries: {workflow_results['feedback_processed']}")
        print(f"Processing time: {workflow_results.get('processing_time', 0):.2f}s")
        
        # Display performance metrics
        perf_metrics = workflow_results.get('performance_metrics', {})
        if perf_metrics:
            print(f"\n=== PERFORMANCE METRICS ===")
            print(f"   Quality Score: {perf_metrics.get('quality_score', 0):.2f}")
            print(f"   Feedback Rate: {perf_metrics.get('feedback_rate', 0):.2f}")
            print(f"   Retraining Needed: {perf_metrics.get('retraining_needed', False)}")
    else:
        print(f"\n=== PIPELINE FAILED ===")
        for error in workflow_results.get('errors', []):
            print(f"   Error: {error}")
    
    # Get workflow status
    status = orchestrator.get_workflow_status()
    print(f"\n=== AGENT STATUS ===")
    for agent, name in status['agents_status'].items():
        print(f"   {agent}: {name} [OK]")
    
    return workflow_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the multi-agent RAG test case generation pipeline.")
    parser.add_argument(
        "--requirements-doc",
        type=str,
        required=True,
        help="Path to the requirements document (e.g., './requirements_doc.pdf').",
    )
    parser.add_argument(
        "--regulatory-doc",
        type=str,
        required=True,
        help="Path to the regulatory document to ingest into the knowledge base (e.g., './regulatory_doc_IEC_62304.txt').",
    )
    parser.add_argument(
        "--intelligent-analysis",
        action="store_true",
        help="Enable intelligent analysis with LLM-generated questions UI",
    )
    args = parser.parse_args()
    
    # Run async pipeline
    asyncio.run(run_pipeline(
        requirements_doc_path=args.requirements_doc, 
        regulatory_doc_path=args.regulatory_doc,
        intelligent_analysis=args.intelligent_analysis
    ))