import asyncio
import logging
import os
import re
from typing import Any, Callable
from config import VALIDATION_RULES, RETRY_CONFIG
from functools import wraps
from collections import OrderedDict

# Setup Google Cloud credentials
gcp_key_path = os.path.join(os.path.dirname(__file__), 'h2stestcase-626c99ca9bd6.json')
if os.path.exists(gcp_key_path):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = gcp_key_path
    print(f"INFO: Google Cloud credentials configured")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LRUCache:
    def __init__(self, capacity: int, ttl_seconds: int = 3600):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.ttl_seconds = ttl_seconds
        self.timestamps = {}
    
    def _is_expired(self, key):
        import time
        return time.time() - self.timestamps.get(key, 0) > self.ttl_seconds
    
    def get(self, key):
        if key in self.cache and not self._is_expired(key):
            self.cache.move_to_end(key)
            return self.cache[key]
        elif key in self.cache:
            del self.cache[key]
            del self.timestamps[key]
        return None
    
    def put(self, key, value):
        import time
        # Cleanup expired entries first
        self._cleanup_expired()
        
        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.capacity:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def _cleanup_expired(self):
        import time
        current_time = time.time()
        expired_keys = [k for k, t in self.timestamps.items() 
                       if current_time - t > self.ttl_seconds]
        for key in expired_keys:
            self.cache.pop(key, None)
            self.timestamps.pop(key, None)

def validate_env_vars():
    """Validate environment variables"""
    project_id = os.getenv('GOOGLE_PROJECT_ID')
    if project_id:
        logger.info(f"Using Google Project: {project_id}")
    else:
        logger.warning("GOOGLE_PROJECT_ID not set")



def validate_file_path(file_path: str) -> bool:
    """Validate file path and extension"""
    from config import FILE_CONFIG
    import os
    
    if not file_path or '..' in file_path:
        return False
    
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in FILE_CONFIG["ALLOWED_EXTENSIONS"]:
        return False
    
    try:
        size = os.path.getsize(file_path)
        return size <= FILE_CONFIG["MAX_FILE_SIZE"]
    except OSError:
        return False

def safe_file_read(file_path: str, max_size: int = None) -> str:
    """Safely read file with size limits and encoding detection"""
    from config import FILE_CONFIG
    import os
    
    if not validate_file_path(file_path):
        raise ValueError(f"Invalid file path: {file_path}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check file size before reading
    file_size = os.path.getsize(file_path)
    max_size = max_size or FILE_CONFIG["MAX_FILE_SIZE"]
    
    if file_size > max_size:
        logger.warning(f"File {file_path} exceeds max size {max_size}, will be truncated")
    
    # Handle PDF files specially
    if file_path.lower().endswith('.pdf'):
        try:
            import fitz
            doc = None
            try:
                doc = fitz.open(file_path)
                content = "".join(page.get_text() for page in doc)
                return content[:max_size] if len(content) > max_size else content
            finally:
                if doc:
                    doc.close()
        except Exception as e:
            logger.error(f"PDF parsing failed: {e}")
            raise ValueError(f"Could not read PDF file: {file_path}")
    
    # Try UTF-8 first, then fallback encodings
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        file_handle = None
        try:
            file_handle = open(file_path, 'r', encoding=encoding)
            content = file_handle.read(max_size)
            if len(content) == max_size:
                logger.warning(f"File truncated at {max_size} bytes")
            return content
        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.error(f"Error reading file with {encoding}: {e}")
            continue
        finally:
            if file_handle:
                file_handle.close()
    
    raise ValueError(f"Could not decode file {file_path} with any encoding")

def validate_input(text: str) -> bool:
    """Validate input text with security checks"""
    if not text or not isinstance(text, str):
        return False
    if len(text) > VALIDATION_RULES["MAX_INPUT_LENGTH"]:
        return False
    # Remove null bytes and control characters
    text = text.replace('\0', '').strip()
    # Check for basic injection patterns
    dangerous_patterns = ['<script', 'javascript:', 'data:', 'vbscript:']
    if any(pattern in text.lower() for pattern in dangerous_patterns):
        return False
    return len(text) >= VALIDATION_RULES["MIN_REQUIREMENT_WORDS"]

def retry_async(max_retries: int = RETRY_CONFIG["MAX_RETRIES"]):
    """Retry decorator for async functions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"{func.__name__} failed after {max_retries} attempts: {e}")
                        raise
                    await asyncio.sleep(RETRY_CONFIG["BACKOFF_FACTOR"] ** attempt)
            return None
        return wrapper
    return decorator

def safe_execute(func: Callable, default: Any = None) -> Any:
    """Safe execution with fallback"""
    try:
        return func()
    except Exception as e:
        logger.warning(f"Safe execution failed: {e}")
        return default