"""Mock tools module for testing agents"""
from config import CHUNK_CONFIG
from typing import List, Dict, Any
from config import OLLAMA_CONFIG
import hashlib



def get_text_generator():
    """Mock text generator availability check"""
    return False  # Simulate no AI generator available


def call_ai_generator(prompt, max_tokens):
    """Mock AI generator call"""
    return f"Generated test case for: {prompt[:50]}..."

def retrain_worker_model(feedback_uri):
    """Mock model retraining"""
    import time
    return f"model_v{int(time.time())}"

def chunk_text(text: str) -> List[str]:
    """Splits text into overlapping chunks."""
    chunk_size = CHUNK_CONFIG.get("SIZE", 256)
    chunk_overlap = CHUNK_CONFIG.get("OVERLAP", 50)






    
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks


def intelligent_requirement_analysis(requirement_text: str) -> Dict[str, Any]:
    """
    Analyzes a requirement using the IntelligentQuestioner.
    This is a simplified wrapper for the functionality in intelligent_questioner.py
    """
    # In a real scenario, this would call the LLM-powered analysis.
    # For this mock, we return a simplified structure.
    return {
        "enhanced_requirement": requirement_text,
        "analysis": {"domain": "general", "complexity": "moderate"},
        "user_responses": {}
    }


def create_embeddings(text_chunks: List[str]) -> List[List[float]]:
    """Generates mock embeddings for text chunks."""
    print(f"INFO: Generating mock embeddings for {len(text_chunks)} chunks")
    return [[0.0] * 384 for _ in text_chunks]



def coordinator_agent(requirement_text: str) -> List[str]:
    """Orchestrates request decomposition using a local Hugging Face model."""
    print("INFO: Coordinator agent is decomposing requirements...")
    prompt = f"""
    Given the following software requirement, break it down into a list of specific,
    verifiable tasks or questions that need to be checked for regulatory compliance.
    Return the output as a simple list of strings, one task per line.

    Requirement:
    ---
    {requirement_text}
    ---
    """
    tasks = [f"Simulated task 1 for '{requirement_text[:30]}...'"]
    print(f"INFO: Coordinator identified tasks via simulation: {tasks}")
    return tasks

def compliance_validation_agent(requirement: str, retrieved_chunks: List[str], intelligent_result: Dict) -> str:
     """Generates a compliant test case using mock logic."""
     print("INFO: Compliance agent is generating test case...")
     return f"TEST CASE: {requirement[:60]}... \n STEPS: 1. Verify compliance"

def vector_store(vectors: List[List[float]], text_chunks: List[str]) -> str:
     """Stores or updates embeddings and text in ChromaDB."""
     print(f"INFO: Storing vectors in mock vector DB")
     
def rag_retrieval(query: str) -> Dict[str, List]:
    print(f"INFO: Mock RAG retrieval for query: '{query}'")
    return {"ids": ["mock_id_1", "mock_id_2"], "chunks": ["Mock chunk 1", "Mock chunk 2"]}

     return "Stored in mock vector DB"