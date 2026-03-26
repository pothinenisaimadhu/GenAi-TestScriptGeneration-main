#!/usr/bin/env python3
"""
Launcher script for the Multi-Agent RAG Test Case Generator UI
"""
import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit',
        'asyncio',
        'chromadb',
        'sentence-transformers',
        'google-cloud-storage',
        'google-cloud-bigquery',
        'PyMuPDF',
        'requests'
    ]
    
    missing_packages = []
    
    import_mapping = {
        'google-cloud-storage': 'google.cloud.storage',
        'google-cloud-bigquery': 'google.cloud.bigquery',
        'PyMuPDF': 'fitz'
    }
    
    for package in required_packages:
        try:
            import_name = import_mapping.get(package, package.replace('-', '_'))
            __import__(import_name)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_environment():
    """Check environment configuration"""
    required_env_vars = [
        'GOOGLE_PROJECT_ID',
        'GCS_BUCKET',
        'BIGQUERY_DATASET'
    ]
    
    optional_env_vars = [
        'CHROMA_API_KEY',
        'CHROMA_TENANT', 
        'CHROMA_DATABASE',
        'JIRA_API_URL',
        'JIRA_USER',
        'JIRA_TOKEN',
        'JIRA_PROJECT_KEY'
    ]
    
    print("🔧 Environment Configuration:")
    
    # Check required variables
    missing_required = []
    for var in required_env_vars:
        if os.getenv(var):
            print(f"   ✅ {var}")
        else:
            print(f"   ❌ {var} (required)")
            missing_required.append(var)
    
    # Check optional variables
    for var in optional_env_vars:
        if os.getenv(var):
            print(f"   ✅ {var}")
        else:
            print(f"   ⚠️  {var} (optional)")
    
    if missing_required:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_required)}")
        print("Please configure these in your .env file")
        return False
    
    return True

def setup_directories():
    """Create necessary directories"""
    directories = [
        'temp',
        'user_feedback',
        'generated_testcases',
        'traceability_logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("📁 Created necessary directories")

def main():
    """Main launcher function"""
    print("🚀 Multi-Agent RAG Test Case Generator")
    print("=" * 50)
    
    # Change to orchestrator directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        print("\n⚠️  Some environment variables are missing.")
        print("The system will work with limited functionality.")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    print("\n🌐 Starting Streamlit UI...")
    print("The application will open in your default web browser")
    print("If it doesn't open automatically, go to: http://0.0.0.0:8508")
    print("\nPress Ctrl+C to stop the application")
    print("=" * 50)
    
    try:
        # Launch Streamlit (foreground process)
        process = subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', 
            'streamlit_ui.py',
            '--server.port=8508',
            '--server.address=0.0.0.0',
            '--browser.gatherUsageStats=false'
        ])
        
        # Wait for process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()