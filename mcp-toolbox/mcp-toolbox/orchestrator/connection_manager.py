import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Centralized connection management with pooling"""
    
    def __init__(self):
        self._pools: Dict[str, Any] = {}
        self._loop = None
    
    @asynccontextmanager
    async def get_connection(self, service: str):
        """Get managed connection with automatic cleanup"""
        connection = None
        try:
            if service == "bigquery":
                from google.cloud import bigquery
                connection = bigquery.Client()
            elif service == "chroma":
                import chromadb
                connection = chromadb.Client()
            
            yield connection
        except Exception as e:
            logger.error(f"Connection error for {service}: {e}")
            raise
        finally:
            if connection and hasattr(connection, 'close'):
                try:
                    connection.close()
                except:
                    pass
    
    async def cleanup(self):
        """Cleanup all connections"""
        for pool in self._pools.values():
            if hasattr(pool, 'close'):
                await pool.close()
        self._pools.clear()

# Global connection manager
connection_manager = ConnectionManager()