"""Streamlit UI Configuration"""

# UI Settings
UI_CONFIG = {
    "page_title": "Multi-Agent RAG Test Case Generator",
    "page_icon": "🤖",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# File Upload Settings
UPLOAD_CONFIG = {
    "max_file_size": 50 * 1024 * 1024,  # 50MB
    "allowed_types": ["pdf"],
    "temp_dir": "temp"
}

# Processing Settings
PROCESSING_CONFIG = {
    "default_collection": "regulatory_docs_v1",
    "default_chunk_size": 256,
    "default_n_results": 5,
    "progress_steps": {
        "init": 10,
        "read_docs": 20,
        "process": 30,
        "finalize": 90,
        "complete": 100
    }
}

# Display Settings
DISPLAY_CONFIG = {
    "max_text_preview": 200,
    "results_per_page": 10,
    "chart_height": 400
}