#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

def test_streamlit_environment():
    """Test environment loading as Streamlit would do it"""
    
    print("=== Streamlit Environment Test ===")
    
    # Clear any cached Jira variables
    for key in list(os.environ.keys()):
        if key.startswith('JIRA_'):
            del os.environ[key]
            print(f"Cleared cached: {key}")
    
    # Force reload from .env file
    load_dotenv(override=True)
    print("Environment reloaded with override=True")
    
    # Test the specific variables
    jira_project = os.getenv("JIRA_PROJECT_KEY")
    jira_url = os.getenv("JIRA_API_URL")
    
    print(f"JIRA_PROJECT_KEY: '{jira_project}'")
    print(f"JIRA_API_URL: '{jira_url}'")
    
    # Test tools import
    print("\n=== Testing Tools Import ===")
    sys.path.insert(0, os.path.dirname(__file__))
    
    try:
        import tools
        print("Tools imported successfully")
        
        # Test create_testcase function
        test_payload = {
            "summary": "Streamlit Environment Test",
            "description": "Testing environment loading from Streamlit context"
        }
        
        result = tools.create_testcase(test_payload)
        print(f"Test case creation result: {result}")
        
        if result.startswith("TC-"):
            print("SUCCESS: Using correct TC project!")
        elif result.startswith("TC-"):
            print("ERROR: Still using old TC project!")
        else:
            print(f"INFO: Local storage used: {result}")
            
    except Exception as e:
        print(f"Error testing tools: {e}")

if __name__ == "__main__":
    test_streamlit_environment()