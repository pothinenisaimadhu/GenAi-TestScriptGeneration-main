#!/usr/bin/env python3

import os
import requests
from requests.auth import HTTPBasicAuth
import json
from dotenv import load_dotenv

def create_test_project():
    """Create a simple test project in Jira"""
    
    load_dotenv()
    
    jira_url = os.getenv("JIRA_API_URL")
    jira_user = os.getenv("JIRA_USER")
    jira_token = os.getenv("JIRA_TOKEN")
    
    print(f"Creating test project in Jira")
    print(f"Jira URL: {jira_url}")
    print(f"User: {jira_user}")
    
    # Test basic auth first
    try:
        response = requests.get(
            f"{jira_url}/rest/api/2/myself",
            auth=HTTPBasicAuth(jira_user, jira_token),
            headers={"Accept": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"Authentication successful!")
            print(f"   User: {user_info.get('displayName', 'Unknown')}")
            print(f"   Account ID: {user_info.get('accountId', 'Unknown')}")
        else:
            print(f"Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error testing authentication: {e}")
        return False
    
    # Create a simple project
    try:
        project_data = {
            "key": "TC",
            "name": "Test Cases",
            "projectTypeKey": "software",
            "projectTemplateKey": "com.pyxis.greenhopper.jira:gh-simplified-agility-kanban",
            "description": "Test case management project",
            "lead": jira_user,
            "assigneeType": "PROJECT_LEAD"
        }
        
        response = requests.post(
            f"{jira_url}/rest/api/2/project",
            auth=HTTPBasicAuth(jira_user, jira_token),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            data=json.dumps(project_data),
            timeout=30
        )
        
        if response.status_code == 201:
            project_info = response.json()
            print(f"Project created successfully!")
            print(f"   Key: {project_info.get('key', 'TC')}")
            print(f"   Name: {project_info.get('name', 'Test Cases')}")
            return True
        else:
            print(f"Failed to create project: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error creating project: {e}")
        return False

if __name__ == "__main__":
    success = create_test_project()
    if success:
        print("\nProject creation successful!")
    else:
        print("\nProject creation failed.")