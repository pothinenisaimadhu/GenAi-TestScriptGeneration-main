#!/usr/bin/env python3

import os
import requests
from requests.auth import HTTPBasicAuth
import json
from dotenv import load_dotenv

def test_tc_project():
    load_dotenv()
    
    jira_url = os.getenv("JIRA_API_URL")
    jira_user = os.getenv("JIRA_USER")
    jira_token = os.getenv("JIRA_TOKEN")
    
    print("Testing TC project specifically...")
    
    # Test TC project
    try:
        response = requests.get(
            f"{jira_url}/rest/api/2/project/TC",
            auth=HTTPBasicAuth(jira_user, jira_token),
            headers={"Accept": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            project_data = response.json()
            issue_types = project_data.get('issueTypes', [])
            print(f"TC Project Issue Types:")
            for it in issue_types:
                if not it.get('subtask', False):
                    print(f"   - {it['name']}")
            
            # Try to create test case in TC project
            if issue_types:
                first_type = next((it['name'] for it in issue_types if not it.get('subtask', False)), "Task")
                
                test_issue = {
                    "fields": {
                        "project": {"key": "TC"},
                        "summary": "Test Case - TC Project Test",
                        "description": {
                            "type": "doc",
                            "version": 1,
                            "content": [{
                                "type": "paragraph",
                                "content": [{"type": "text", "text": "Testing TC project integration"}]
                            }]
                        },
                        "issuetype": {"name": first_type}
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
                    print(f"\nTC Test issue created!")
                    print(f"   Issue Key: {issue_data['key']}")
                    print(f"   Issue Type: {first_type}")
                    return True
                else:
                    print(f"\nFailed to create TC issue: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
        else:
            print(f"TC Project Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_tc_project()
    if success:
        print("\nTC project integration working!")
    else:
        print("\nTC project needs attention.")