import os
import requests
import urllib.parse
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def _validate_url(url: str) -> bool:
    """Validate URL to prevent SSRF attacks."""
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            return False
        if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0', '::1']:
            return False
        # Allow only specific domains for Jira
        if not parsed.hostname or not parsed.hostname.endswith('.atlassian.net'):
            return False
        return True
    except Exception:
        return False

def check_system_health() -> Dict[str, Any]:
    """Check health of all external dependencies"""
    health_status = {
        "overall": "healthy",
        "services": {}
    }
    
    # Check Jira
    try:
        jira_url = os.getenv("JIRA_API_URL")
        if jira_url and _validate_url(jira_url):
            response = requests.get(f"{jira_url}/rest/api/3/myself", 
                                  auth=(os.getenv("JIRA_USER"), os.getenv("JIRA_TOKEN")),
                                  timeout=5)
            health_status["services"]["jira"] = "healthy" if response.status_code == 200 else "unhealthy"
        elif jira_url:
            health_status["services"]["jira"] = "invalid_url"
            logger.warning(f"Invalid Jira URL: {jira_url}")
        else:
            health_status["services"]["jira"] = "not_configured"
    except Exception as e:
        health_status["services"]["jira"] = "unhealthy"
        logger.warning(f"Jira health check failed: {e}")
    
    # Check Ollama (local/offline)
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        health_status["services"]["ollama"] = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception:
        health_status["services"]["ollama"] = "offline (local only)"

    # Check OpenRouter
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            health_status["services"]["openrouter"] = "not_configured"
        else:
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5
            )
            health_status["services"]["openrouter"] = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception as e:
        health_status["services"]["openrouter"] = "unhealthy"
        logger.warning(f"OpenRouter health check failed: {e}")
    
    # Check ChromaDB
    try:
        import chromadb
        client = chromadb.CloudClient(
            api_key=os.getenv("CHROMA_API_KEY"),
            tenant=os.getenv("CHROMA_TENANT"),
            database=os.getenv("CHROMA_DATABASE"),
        )
        client.list_collections()
        health_status["services"]["chromadb"] = "healthy"
    except Exception:
        health_status["services"]["chromadb"] = "unhealthy"
    
    # Set overall status (ollama offline is expected in cloud)
    if any(status == "unhealthy" for k, status in health_status["services"].items() if k != "ollama"):
        health_status["overall"] = "degraded"
    
    return health_status