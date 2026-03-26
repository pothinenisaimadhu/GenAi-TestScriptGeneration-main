#!/usr/bin/env python3

import os
from dotenv import load_dotenv

def test_environment_variables():
    """Test that environment variables are loaded correctly"""
    
    # Load environment variables
    load_dotenv()
    
    print("=== Environment Variables Test ===")
    
    # Test key variables
    test_vars = [
        "JIRA_API_URL",
        "JIRA_USER", 
        "JIRA_TOKEN",
        "JIRA_PROJECT_KEY",
        "GOOGLE_PROJECT_ID",
        "CHROMA_COLLECTION"
    ]
    
    for var in test_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "TOKEN" in var or "KEY" in var:
                masked_value = value[:10] + "..." if len(value) > 10 else "***"
                print(f"OK {var}: {masked_value}")
            else:
                print(f"OK {var}: {value}")
        else:
            print(f"MISSING {var}: Not set")
    
    # Specific test for Jira project key
    jira_project = os.getenv("JIRA_PROJECT_KEY")
    print(f"\n=== Jira Project Key Test ===")
    print(f"Current JIRA_PROJECT_KEY: '{jira_project}'")
    
    if jira_project == "TC":
        print("OK Correct project key (TC) is loaded")
    elif jira_project == "TC":
        print("ERROR Old project key (TC) is still loaded - environment not refreshed")
    else:
        print(f"WARNING Unexpected project key: {jira_project}")

if __name__ == "__main__":
    test_environment_variables()