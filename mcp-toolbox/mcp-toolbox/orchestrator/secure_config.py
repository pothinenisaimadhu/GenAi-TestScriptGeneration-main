"""
Secure configuration management for the orchestrator.
Centralizes all hardcoded values and provides validation.
"""
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SecureConfig:
    """Centralized configuration with validation."""
    
    # Default values
    DEFAULTS = {
        "CHUNK_SIZE": 1000,
        "CHUNK_OVERLAP": 50,
        "MAX_RETRIES": 3,
        "REQUEST_TIMEOUT": 30,
        "FEEDBACK_NORMALIZATION_FACTOR": 10.0,
        "MIN_QUALITY_THRESHOLD": 0.6,
        "COMPLEXITY_WORD_THRESHOLD": 20,
        "HIGH_COMPLEXITY_THRESHOLD": 50,
        "DEFAULT_CLARITY_SCORE": 0.8,
        "JIRA_ISSUE_TYPE_ID": "10001",
        "MAX_SUMMARY_LENGTH": 255
    }
    
    # Allowed URL schemes
    ALLOWED_SCHEMES = ["http", "https"]
    
    # Blocked hostnames for security
    BLOCKED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "::1", "169.254.169.254"]
    
    # Domain keywords for classification
    DOMAIN_KEYWORDS = {
        "security": ["security", "authentication", "authorization", "encryption", "access"],
        "performance": ["performance", "speed", "latency", "throughput", "response time"],
        "compliance": ["compliance", "regulation", "audit", "gdpr", "hipaa", "fda"],
        "ui": ["interface", "user", "display", "screen", "button", "form"]
    }
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback to defaults."""
        env_value = os.getenv(key)
        if env_value is not None:
            return env_value
        return cls.DEFAULTS.get(key, default)
    
    @classmethod
    def get_int(cls, key: str, default: int = 0) -> int:
        """Get integer configuration value."""
        try:
            return int(cls.get(key, default))
        except (ValueError, TypeError):
            logger.warning(f"Invalid integer value for {key}, using default: {default}")
            return default
    
    @classmethod
    def get_float(cls, key: str, default: float = 0.0) -> float:
        """Get float configuration value."""
        try:
            return float(cls.get(key, default))
        except (ValueError, TypeError):
            logger.warning(f"Invalid float value for {key}, using default: {default}")
            return default
    
    @classmethod
    def validate_required_env_vars(cls) -> None:
        """Validate that required environment variables are set."""
        required_vars = [
            "JIRA_API_URL", "JIRA_USER", "JIRA_TOKEN", "JIRA_PROJECT_KEY"
        ]
        optional_vars = [
            "CHROMA_API_KEY", "CHROMA_TENANT", "CHROMA_DATABASE",
            "GOOGLE_PROJECT_ID", "GCS_BUCKET", "BIGQUERY_DATASET"
        ]
        
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            logger.warning(f"Missing optional environment variables: {missing}")
            # Don't fail, just warn for optional vars
        
        missing_optional = [var for var in optional_vars if not os.getenv(var)]
        if missing_optional:
            logger.info(f"Optional services disabled: {missing_optional}")
    
    @classmethod
    def get_safe_paths(cls) -> Dict[str, str]:
        """Get safe file paths for operations."""
        base_dir = os.path.abspath(".")
        return {
            "feedback_dir": os.path.join(base_dir, "user_feedback"),
            "temp_dir": os.path.join(base_dir, "temp"),
            "logs_dir": os.path.join(base_dir, "logs")
        }

# Global configuration instance
config = SecureConfig()