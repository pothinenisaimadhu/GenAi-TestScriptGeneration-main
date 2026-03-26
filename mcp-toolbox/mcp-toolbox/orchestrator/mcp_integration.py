"""
MCP Integration Tool for Jira and GitHub APIs with AI Workflows
Extends the test case generation pipeline with intelligent DevOps automation
"""

import os
import re
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class MCPIntegrationTool:
    def __init__(self):
        # Jira configuration
        self.jira_base_url = os.getenv("JIRA_API_URL", "")
        self.jira_user = os.getenv("JIRA_USER", "")
        self.jira_token = os.getenv("JIRA_TOKEN", "")
        self.jira_project_key = os.getenv("JIRA_PROJECT_KEY", "")
        
        # GitHub configuration
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        self.github_repo = os.getenv("GITHUB_REPO", "")  # format: owner/repo
        
        # AI integration
        self.ai_enabled = True
        
    def fetch_jira_issues(self, jql: str = None) -> List[Dict]:
        """Fetch Jira issues using JQL query"""
        if not all([self.jira_base_url, self.jira_user, self.jira_token]):
            logger.warning("Jira credentials not configured")
            return []
            
        try:
            if not jql:
                jql = f"project = {self.jira_project_key} ORDER BY created DESC"
                
            url = f"{self.jira_base_url}/rest/api/3/search"
            auth = (self.jira_user, self.jira_token)
            
            params = {
                "jql": jql,
                "maxResults": 50,
                "fields": "key,summary,description,status,assignee,created,updated"
            }
            
            response = requests.get(url, auth=auth, params=params, timeout=30)
            response.raise_for_status()
            
            issues = response.json().get("issues", [])
            logger.info(f"Fetched {len(issues)} Jira issues")
            return issues
            
        except Exception as e:
            logger.error(f"Failed to fetch Jira issues: {e}")
            return []
    
    def update_jira_issue(self, issue_key: str, update_data: Dict) -> bool:
        """Update Jira issue with AI-generated content"""
        if not all([self.jira_base_url, self.jira_user, self.jira_token]):
            return False
            
        try:
            url = f"{self.jira_base_url}/rest/api/3/issue/{issue_key}"
            auth = (self.jira_user, self.jira_token)
            
            response = requests.put(url, auth=auth, json=update_data, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Updated Jira issue {issue_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update Jira issue {issue_key}: {e}")
            return False
    
    def add_jira_comment(self, issue_key: str, comment: str) -> bool:
        """Add AI-generated comment to Jira issue"""
        if not all([self.jira_base_url, self.jira_user, self.jira_token]):
            return False
            
        try:
            url = f"{self.jira_base_url}/rest/api/3/issue/{issue_key}/comment"
            auth = (self.jira_user, self.jira_token)
            
            payload = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": comment
                                }
                            ]
                        }
                    ]
                }
            }
            
            response = requests.post(url, auth=auth, json=payload, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Added comment to Jira issue {issue_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add comment to {issue_key}: {e}")
            return False
    
    def fetch_github_commits(self, since_days: int = 7) -> List[Dict]:
        """Fetch recent GitHub commits"""
        if not all([self.github_token, self.github_repo]):
            logger.warning("GitHub credentials not configured")
            return []
            
        try:
            url = f"https://api.github.com/repos/{self.github_repo}/commits"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            since_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            since_date = since_date.replace(day=since_date.day - since_days)
            
            params = {
                "since": since_date.isoformat(),
                "per_page": 100
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            commits = response.json()
            logger.info(f"Fetched {len(commits)} GitHub commits")
            return commits
            
        except Exception as e:
            logger.error(f"Failed to fetch GitHub commits: {e}")
            return []
    
    def fetch_github_prs(self, state: str = "all") -> List[Dict]:
        """Fetch GitHub pull requests"""
        if not all([self.github_token, self.github_repo]):
            return []
            
        try:
            url = f"https://api.github.com/repos/{self.github_repo}/pulls"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            params = {
                "state": state,
                "per_page": 50
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            prs = response.json()
            logger.info(f"Fetched {len(prs)} GitHub PRs")
            return prs
            
        except Exception as e:
            logger.error(f"Failed to fetch GitHub PRs: {e}")
            return []
    
    def extract_jira_keys_from_text(self, text: str) -> List[str]:
        """Extract Jira issue keys from text using regex"""
        if not self.jira_project_key:
            return []
            
        pattern = rf"\b{self.jira_project_key}-\d+\b"
        matches = re.findall(pattern, text, re.IGNORECASE)
        return list(set(matches))  # Remove duplicates
    
    def cross_reference_commits_with_jira(self) -> Dict[str, List[Dict]]:
        """Cross-reference GitHub commits with Jira issues"""
        commits = self.fetch_github_commits()
        jira_commit_map = {}
        
        for commit in commits:
            commit_message = commit.get("commit", {}).get("message", "")
            jira_keys = self.extract_jira_keys_from_text(commit_message)
            
            for jira_key in jira_keys:
                if jira_key not in jira_commit_map:
                    jira_commit_map[jira_key] = []
                
                jira_commit_map[jira_key].append({
                    "sha": commit.get("sha", ""),
                    "message": commit_message,
                    "author": commit.get("commit", {}).get("author", {}).get("name", ""),
                    "date": commit.get("commit", {}).get("author", {}).get("date", ""),
                    "url": commit.get("html_url", "")
                })
        
        logger.info(f"Cross-referenced {len(jira_commit_map)} Jira issues with commits")
        return jira_commit_map
    
    def generate_ai_summary(self, jira_issue: Dict, related_commits: List[Dict]) -> str:
        """Generate AI summary of issue progress based on commits"""
        try:
            from tools import get_text_generator, call_ollama
            
            issue_summary = jira_issue.get("fields", {}).get("summary", "")
            issue_description = jira_issue.get("fields", {}).get("description", "")
            
            commit_info = "\n".join([
                f"- {commit['message']} (by {commit['author']})"
                for commit in related_commits[:5]  # Limit to 5 commits
            ])
            
            prompt = f"""
            Analyze the following Jira issue and related commits to generate a progress summary:
            
            Issue: {issue_summary}
            Description: {issue_description}
            
            Related Commits:
            {commit_info}
            
            Generate a concise progress update for this issue based on the commit activity.
            """
            
            text_generator = get_text_generator()
            if text_generator == "ollama":
                summary = call_ollama(prompt)
                if summary:
                    return summary
            
            # Fallback summary
            return f"Found {len(related_commits)} related commits. Latest activity shows ongoing development."
            
        except Exception as e:
            logger.error(f"Failed to generate AI summary: {e}")
            return f"Automated analysis: {len(related_commits)} commits found for this issue."
    
    def auto_update_jira_with_commit_analysis(self) -> Dict[str, Any]:
        """Main workflow: Auto-update Jira issues with commit analysis"""
        results = {
            "updated_issues": 0,
            "failed_updates": 0,
            "processed_issues": []
        }
        
        try:
            # Get cross-reference data
            jira_commit_map = self.cross_reference_commits_with_jira()
            
            if not jira_commit_map:
                logger.info("No Jira-commit cross-references found")
                return results
            
            # Fetch Jira issues for the found keys
            jira_keys = list(jira_commit_map.keys())
            jql = f"key in ({','.join(jira_keys)})"
            issues = self.fetch_jira_issues(jql)
            
            for issue in issues:
                issue_key = issue.get("key", "")
                related_commits = jira_commit_map.get(issue_key, [])
                
                if not related_commits:
                    continue
                
                # Generate AI summary
                ai_summary = self.generate_ai_summary(issue, related_commits)
                
                # Create comment with commit analysis
                import html
                safe_summary = html.escape(ai_summary)
                safe_commits = chr(10).join([f"• [{commit['sha'][:7]}]({html.escape(commit['url'])}) {html.escape(commit['message'])}" for commit in related_commits[:3]])
                comment = f"""🤖 **Automated Commit Analysis**
                
{safe_summary}

**Recent Commits:**
{safe_commits}

*Generated by MCP Integration Tool at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"""
                
                # Add comment to Jira
                if self.add_jira_comment(issue_key, comment):
                    results["updated_issues"] += 1
                else:
                    results["failed_updates"] += 1
                
                results["processed_issues"].append({
                    "key": issue_key,
                    "commits_found": len(related_commits),
                    "summary": issue.get("fields", {}).get("summary", "")
                })
            
            logger.info(f"Updated {results['updated_issues']} Jira issues with commit analysis")
            return results
            
        except Exception as e:
            logger.error(f"Auto-update workflow failed: {e}")
            return results
    
    def check_commits_against_requirements(self, requirements_text: str) -> Dict[str, Any]:
        """Check if recent commits align with requirements"""
        try:
            commits = self.fetch_github_commits(since_days=14)
            
            # Extract key requirements
            req_keywords = []
            for line in requirements_text.lower().split('\n'):
                if 'shall' in line or 'must' in line or 'should' in line:
                    words = re.findall(r'\b\w+\b', line)
                    req_keywords.extend([w for w in words if len(w) > 4])
            
            req_keywords = list(set(req_keywords))[:10]  # Top 10 keywords
            
            matching_commits = []
            for commit in commits:
                message = commit.get("commit", {}).get("message", "").lower()
                matches = [kw for kw in req_keywords if kw in message]
                
                if matches:
                    matching_commits.append({
                        "sha": commit.get("sha", "")[:7],
                        "message": commit.get("commit", {}).get("message", ""),
                        "matched_keywords": matches,
                        "url": commit.get("html_url", "")
                    })
            
            return {
                "total_commits": len(commits),
                "matching_commits": len(matching_commits),
                "matches": matching_commits,
                "requirements_keywords": req_keywords
            }
            
        except Exception as e:
            logger.error(f"Requirements check failed: {e}")
            return {}
    
    def generate_integration_report(self) -> str:
        """Generate comprehensive integration report"""
        try:
            report = []
            report.append("# MCP Integration Report")
            report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            
            # Jira summary
            issues = self.fetch_jira_issues()
            report.append(f"## Jira Summary")
            report.append(f"- Total issues: {len(issues)}")
            
            if issues:
                statuses = {}
                for issue in issues:
                    status = issue.get("fields", {}).get("status", {}).get("name", "Unknown")
                    statuses[status] = statuses.get(status, 0) + 1
                
                for status, count in statuses.items():
                    report.append(f"- {status}: {count}")
            
            report.append("")
            
            # GitHub summary
            commits = self.fetch_github_commits()
            prs = self.fetch_github_prs()
            
            report.append(f"## GitHub Summary")
            report.append(f"- Recent commits (7 days): {len(commits)}")
            report.append(f"- Pull requests: {len(prs)}")
            report.append("")
            
            # Cross-reference analysis
            cross_ref = self.cross_reference_commits_with_jira()
            report.append(f"## Integration Analysis")
            report.append(f"- Issues with linked commits: {len(cross_ref)}")
            
            for jira_key, commits in list(cross_ref.items())[:5]:
                report.append(f"- {jira_key}: {len(commits)} commits")
            
            return "\n".join(report)
            
        except Exception as e:
            return f"Error generating report: {e}"

# Integration with existing pipeline
def integrate_with_pipeline(requirements_text: str = "") -> Dict[str, Any]:
    """Main integration function for the test case generation pipeline"""
    mcp_tool = MCPIntegrationTool()
    
    results = {
        "jira_updates": {},
        "requirements_check": {},
        "integration_report": ""
    }
    
    try:
        logger.info("Starting MCP integration workflow...")
        
        # Auto-update Jira with commit analysis
        results["jira_updates"] = mcp_tool.auto_update_jira_with_commit_analysis()
        
        # Check commits against requirements if provided
        if requirements_text:
            results["requirements_check"] = mcp_tool.check_commits_against_requirements(requirements_text)
        
        # Generate integration report
        results["integration_report"] = mcp_tool.generate_integration_report()
        
        logger.info("MCP integration workflow completed")
        return results
        
    except Exception as e:
        logger.error(f"MCP integration failed: {e}")
        return results

if __name__ == "__main__":
    # Test the integration
    tool = MCPIntegrationTool()
    report = tool.generate_integration_report()
    print(report)