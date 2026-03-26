# Configuration constants
QUALITY_THRESHOLDS = {
    "MEDIUM": 0.7
}

RETRY_CONFIG = {
    "MAX_RETRIES": 3,
    "BACKOFF_FACTOR": 2,
    "TIMEOUT": 30
}

VALIDATION_RULES = {
    "MIN_REQUIREMENT_WORDS": 3,
    "MAX_INPUT_LENGTH": 10000,
    "ALLOWED_CHARS": r'^[a-zA-Z0-9\s\.\,\-\:\;\(\)]+$'
}

CHUNK_CONFIG = {
    "SIZE": 256,
    "OVERLAP": 50
}

EMBEDDING_CONFIG = {
    "DIMENSIONS": 384,
    "CACHE_SIZE": 1000
}

JIRA_CONFIG = {
    "ISSUE_TYPES": ["Idea", "Story", "Task", "Bug"],
    "BATCH_SIZE": 2,
    "TIMEOUT": 15
}

COLLECTION_CONFIG = {
    "NAME": "regulatory_docs_384"
}

OLLAMA_CONFIG = {
    "VECTOR_SIZE": 768,
    "WINDOW": 10,
    "EPOCHS": 20,
    "TIMEOUT": 25,
    "MIN_COUNT": 1,
    "WORKERS": 1,
    "SG": 1
}

FILE_CONFIG = {
    "ALLOWED_EXTENSIONS": [".txt", ".pdf", ".docx"],
    "MAX_FILE_SIZE": 50 * 1024 * 1024,
    "CHUNK_THRESHOLDS": {"MIN": 30, "OPTIMAL_MIN": 50, "OPTIMAL_MAX": 300}
}

CACHE_CONFIG = {
    "TTL_SECONDS": 3600,
    "MAX_QUESTIONS": 4
}