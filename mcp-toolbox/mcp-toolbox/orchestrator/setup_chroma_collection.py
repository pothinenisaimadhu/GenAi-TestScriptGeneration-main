#!/usr/bin/env python3
"""
Setup ChromaDB collection with 384 dimensions and populate with regulatory documents
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

import tools
from tools import create_embeddings, chunk_text

def setup_collection():
    """Create and populate ChromaDB collection with 384 dimensions"""
    
    print("=== ChromaDB Collection Setup ===")
    
    # Collection name with 384 dimensions
    collection_name = "regulatory_docs_384"
    
    try:
        # Get ChromaDB client
        client = tools.client_config.get_chroma_client()
        
        # Delete existing collection if it exists
        try:
            client.delete_collection(name=collection_name)
            print(f"Deleted existing collection: {collection_name}")
        except:
            pass
        
        # Create new collection
        collection = client.create_collection(name=collection_name)
        print(f"Created new collection: {collection_name}")
        
        # Sample regulatory document text (replace with your actual documents)
        regulatory_texts = [
            """
            GDPR Article 25: Data protection by design and by default
            The controller shall implement appropriate technical and organisational measures 
            to ensure that, by default, only personal data which are necessary for each 
            specific purpose of the processing are processed.
            """,
            """
            HIPAA Security Rule: Administrative Safeguards
            A covered entity must implement administrative safeguards including assigned 
            security responsibility, workforce training, information access management, 
            and security awareness and training programs.
            """,
            """
            SOX Section 404: Management Assessment of Internal Controls
            Management must establish and maintain adequate internal control structure 
            and procedures for financial reporting and assess the effectiveness of 
            such controls annually.
            """,
            """
            ISO 27001: Information Security Management
            Organizations must establish, implement, maintain and continually improve 
            an information security management system within the context of the organization.
            """
        ]
        
        # Process and add documents
        all_chunks = []
        for i, text in enumerate(regulatory_texts):
            chunks = chunk_text(text.strip(), chunk_size=256, chunk_overlap=50)
            all_chunks.extend(chunks)
            print(f"Document {i+1}: Created {len(chunks)} chunks")
        
        if all_chunks:
            # Create embeddings
            print("Creating embeddings...")
            embeddings = create_embeddings(all_chunks)
            
            if embeddings:
                # Store in ChromaDB
                result = tools.vector_store(embeddings, all_chunks, collection_name)
                print(f"Storage result: {result}")
                
                # Test retrieval
                print("\nTesting retrieval...")
                test_query = "data protection requirements"
                retrieval_result = tools.rag_retrieval(test_query, collection_name, n_results=2)
                
                if retrieval_result['chunks']:
                    print(f"Retrieved {len(retrieval_result['chunks'])} chunks for test query")
                    print(f"Sample chunk: {retrieval_result['chunks'][0][:100]}...")
                else:
                    print("No chunks retrieved - check collection setup")
            else:
                print("Failed to create embeddings")
        else:
            print("No text chunks to process")
            
    except Exception as e:
        print(f"Error setting up collection: {e}")
        return False
    
    print(f"\n✅ Collection '{collection_name}' setup complete!")
    print(f"Update your .env file: CHROMA_COLLECTION=\"{collection_name}\"")
    return True

if __name__ == "__main__":
    success = setup_collection()
    if success:
        print("\nNext steps:")
        print("1. Update CHROMA_COLLECTION in .env to 'regulatory_docs_384'")
        print("2. Add your actual regulatory documents to the script")
        print("3. Run the main system")
    else:
        print("\nSetup failed. Check your ChromaDB configuration.")