import os
from contextlib import contextmanager
from typing import Generator, Any
import chromadb
from google.cloud import bigquery
import logging

logger = logging.getLogger(__name__)

@contextmanager
def get_chroma_client() -> Generator[chromadb.Client, None, None]:
    """Context manager for ChromaDB client"""
    client = None
    try:
        try:
            client = chromadb.CloudClient(
                api_key=os.getenv("CHROMA_API_KEY"),
                tenant=os.getenv("CHROMA_TENANT"),
                database=os.getenv("CHROMA_DATABASE"),
            )
        except Exception as e:
            logger.warning(f"ChromaDB Cloud failed, using local: {e}")
            client = chromadb.Client()
        
        yield client
    finally:
        if client and hasattr(client, 'close'):
            try:
                client.close()
            except Exception as e:
                logger.error(f"Failed to close ChromaDB client: {e}")

@contextmanager
def get_bigquery_client() -> Generator[bigquery.Client, None, None]:
    """Context manager for BigQuery client"""
    client = None
    try:
        client = bigquery.Client(project=os.getenv("GOOGLE_PROJECT_ID"))
        yield client
    finally:
        if hasattr(client, 'close'):
            client.close()

