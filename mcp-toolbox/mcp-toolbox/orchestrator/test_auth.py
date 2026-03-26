#!/usr/bin/env python3

import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

def test_auth():
    load_dotenv()
    
    jira_url = os.getenv("JIRA_API_URL")
    jira_user = os.getenv("JIRA_USER")
    jira_token = os.getenv("JIRA_TOKEN")
    
    print(f"Testing basic authentication")
    print(f"URL: {jira_url}")
    print(f"User: {jira_user}")
    print(f"Token: {jira_token[:20]}...")
    
    # Test basic auth
    try:
        response = requests.get(
            f"{jira_url}/rest/api/2/myself",
            auth=HTTPBasicAuth(jira_user, jira_token),
            headers={"Accept": "application/json"},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_auth()