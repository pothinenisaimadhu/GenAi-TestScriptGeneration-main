#!/usr/bin/env python3

import os
import requests
from requests.auth import HTTPBasicAuth
import json
from dotenv import load_dotenv

def test_jira_connection():
    """Test connection to Jira and discover available projects"""
    
    # Load environment variables from .env file
    load_dotenv()
    
    jira_url = os.getenv("JIRA_API_URL")
    jira_user = os.getenv("JIRA_USER")
    jira_token = os.getenv("JIRA_TOKEN")
    project_key = os.getenv("JIRA_PROJECT_KEY")
    
    print(f"Testing connection to Jira")
    print(f"Jira URL: {jira_url}")
    print(f"User: {jira_user}")
    
    # Test 0: Discover available projects
    try:
        response = requests.get(
            f"{jira_url}/rest/api/2/project",
            auth=HTTPBasicAuth(jira_user, jira_token),
            headers={"Accept": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            projects = response.json()
            print(f"\nAvailable projects:")
            for project in projects:
                print(f"   - {project['key']}: {project['name']}")
            
            if projects:
                # Use TC project if available, otherwise first project
                test_project = "TC" if any(p['key'] == 'TC' for p in projects) else projects[0]['key']
                print(f"\nUsing project '{test_project}' for testing...")
            else:
                print("No projects found!")
                return False
        else:
            print(f"Failed to get projects: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error connecting to Jira: {e}")
        return False
    
    # Test 1: Get project info for the test project
    try:
        response = requests.get(
            f"{jira_url}/rest/api/3/project/{test_project}",
            auth=HTTPBasicAuth(jira_user, jira_token),
            headers={"Accept": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            project_info = response.json()
            print(f"\nProject details:")
            print(f"   Name: {project_info['name']}")
            print(f"   Key: {project_info['key']}")
            print(f"   ID: {project_info['id']}")
        else:
            print(f"Failed to get project info: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error getting project info: {e}")
        return False
    
    # Test 2: Get available issue types
    try:
        response = requests.get(
            f"{jira_url}/rest/api/2/project/{test_project}",
            auth=HTTPBasicAuth(jira_user, jira_token),
            headers={"Accept": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            project_data = response.json()
            issue_types = project_data.get('issueTypes', [])
            print(f"\nAvailable issue types:")
            for issue_type in issue_types:
                if not issue_type.get('subtask', False):
                    print(f"   - {issue_type['name']}")
        else:
            print(f"Could not get issue types: {response.status_code}")
            
    except Exception as e:
        print(f"Error getting issue types: {e}")
    
    # Test 3: Create a test issue
    try:
        # Use Atlassian Document Format (ADF) for description
        adf_description = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "This is a test issue created to verify Jira integration with the new TC project."
                        }
                    ]
                }
            ]
        }
        
        # Get the first available issue type
        first_issue_type = None
        if 'issue_types' in locals():
            for it in issue_types:
                if not it.get('subtask', False):
                    first_issue_type = it['name']
                    break
        
        if not first_issue_type:
            first_issue_type = "Task"  # fallback
        
        test_issue = {
            "fields": {
                "project": {"key": test_project},
                "summary": "Test Case - Connection Test",
                "description": adf_description,
                "issuetype": {"name": first_issue_type}
            }
        }
        
        response = requests.post(
            f"{jira_url}/rest/api/3/issue",
            auth=HTTPBasicAuth(jira_user, jira_token),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            data=json.dumps(test_issue),
            timeout=15
        )
        
        if response.status_code == 201:
            issue_data = response.json()
            print(f"\nTest issue created successfully!")
            print(f"   Issue Key: {issue_data['key']}")
            print(f"   Issue URL: {jira_url}/browse/{issue_data['key']}")
            print(f"   Issue Type: {first_issue_type}")
            return True
        else:
            print(f"\nFailed to create test issue: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error creating test issue: {e}")
        return False

if __name__ == "__main__":
    success = test_jira_connection()
    if success:
        print("\nJira integration is working correctly!")
    else:
        print("\nJira integration needs attention.")