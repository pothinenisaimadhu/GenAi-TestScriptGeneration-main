import asyncio
from typing import Dict, Any
import chromadb
from google.cloud import bigquery
import os

class ConnectionPool:
    def __init__(self):
        self._chroma_client = None
        self._bigquery_client = None
        self._lock = asyncio.Lock()
    
    async def get_chroma_client(self):
        if not self._chroma_client:
            async with self._lock:
                if not self._chroma_client:
                    try:
                        self._chroma_client = chromadb.CloudClient(
                            api_key=os.getenv("CHROMA_API_KEY"),
                            tenant=os.getenv("CHROMA_TENANT"),
                            database=os.getenv("CHROMA_DATABASE"),
                        )
                    except Exception:
                        self._chroma_client = chromadb.Client()
        return self._chroma_client
    
    async def get_bigquery_client(self):
        if not self._bigquery_client:
            async with self._lock:
                if not self._bigquery_client:
                    self._bigquery_client = bigquery.Client(project=os.getenv("GOOGLE_PROJECT_ID"))
        return self._bigquery_client

# Global connection pool
connection_pool = ConnectionPool()