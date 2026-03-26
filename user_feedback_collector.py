#!/usr/bin/env python3

import json
import os
import time
from typing import Dict, List, Any

def collect_user_feedback(testcase_id: str, test_case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Collect user feedback to improve test case generation"""
    
    print(f"\n=== FEEDBACK FOR TEST CASE: {testcase_id} ===")
    print(f"Summary: {test_case_data.get('summary', 'N/A')}")
    print(f"Description: {test_case_data.get('description', 'N/A')[:100]}...")
    print("=" * 50)
    
    feedback = {
        "testcase_id": testcase_id,
        "timestamp": time.time(),
        "improvements": {},
        "ratings": {},
        "suggestions": {}
    }
    
    # Quality ratings (1-5 scale)
    print("\n📊 RATE THE QUALITY (1=Poor, 5=Excellent):")
    
    ratings = [
        ("clarity", "How clear and understandable is the test case?"),
        ("completeness", "How complete are the test steps?"),
        ("relevance", "How relevant is it to the requirement?"),
        ("compliance", "How well does it address compliance needs?")
    ]
    
    for key, question in ratings:
        while True:
            try:
                rating = input(f"{question} (1-5): ").strip()
                if rating in ['1', '2', '3', '4', '5']:
                    feedback["ratings"][key] = int(rating)
                    break
                else:
                    print("Please enter a number between 1 and 5")
            except KeyboardInterrupt:
                print("\nFeedback collection cancelled")
                return feedback
    
    # Specific improvement areas
    print("\n🔧 IMPROVEMENT AREAS (y/n):")
    
    improvements = [
        ("test_steps", "Do the test steps need improvement?"),
        ("expected_results", "Do the expected results need clarification?"),
        ("prerequisites", "Are the prerequisites missing or unclear?"),
        ("test_data", "Is the test data insufficient?"),
        ("acceptance_criteria", "Are acceptance criteria missing?")
    ]
    
    for key, question in improvements:
        try:
            answer = input(f"{question} (y/n): ").strip().lower()
            if answer in ['y', 'yes']:
                suggestion = input(f"  What should be improved in {key}? ").strip()
                if suggestion:
                    feedback["improvements"][key] = suggestion
        except KeyboardInterrupt:
            print("\nFeedback collection cancelled")
            return feedback
    
    # Overall suggestions
    print("\n💡 GENERAL SUGGESTIONS:")
    try:
        general_feedback = input("Any other suggestions for improvement? ").strip()
        if general_feedback:
            feedback["suggestions"]["general"] = general_feedback
        
        missing_elements = input("What important elements are missing? ").strip()
        if missing_elements:
            feedback["suggestions"]["missing_elements"] = missing_elements
        
        # Domain-specific questions
        domain = _detect_domain(test_case_data)
        if domain == "security":
            security_feedback = input("Are security validation steps adequate? ").strip()
            if security_feedback:
                feedback["suggestions"]["security"] = security_feedback
        elif domain == "audit":
            audit_feedback = input("Are audit trail requirements covered? ").strip()
            if audit_feedback:
                feedback["suggestions"]["audit"] = audit_feedback
        
    except KeyboardInterrupt:
        print("\nFeedback collection cancelled")
    
    # Calculate overall score
    if feedback["ratings"]:
        avg_rating = sum(feedback["ratings"].values()) / len(feedback["ratings"])
        feedback["overall_score"] = avg_rating
        
        if avg_rating < 3:
            feedback["priority"] = "high"
        elif avg_rating < 4:
            feedback["priority"] = "medium"
        else:
            feedback["priority"] = "low"
    
    # Save feedback
    _save_feedback(feedback)
    
    print(f"\n✅ Feedback collected! Overall score: {feedback.get('overall_score', 0):.1f}/5")
    return feedback

def _detect_domain(test_case_data: Dict[str, Any]) -> str:
    """Detect the domain of the test case"""
    text = str(test_case_data).lower()
    
    if any(word in text for word in ['security', 'encrypt', 'auth', 'password']):
        return "security"
    elif any(word in text for word in ['audit', 'log', 'trail', 'compliance']):
        return "audit"
    elif any(word in text for word in ['data', 'database', 'storage']):
        return "data"
    else:
        return "general"

def _save_feedback(feedback: Dict[str, Any]) -> None:
    """Save feedback to local file and prepare for BigQuery"""
    try:
        # Save to local feedback directory
        feedback_dir = "user_feedback"
        os.makedirs(feedback_dir, exist_ok=True)
        
        feedback_file = os.path.join(feedback_dir, f"feedback_{feedback['testcase_id']}_{int(time.time())}.json")
        
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedback, f, indent=2, default=str)
        
        print(f"Feedback saved to: {feedback_file}")
        
        # Also update BigQuery if possible
        _update_bigquery_with_feedback(feedback)
        
    except Exception as e:
        print(f"Warning: Could not save feedback: {e}")

def _update_bigquery_with_feedback(feedback: Dict[str, Any]) -> None:
    """Update BigQuery with user feedback"""
    try:
        from google.cloud import bigquery
        
        client = bigquery.Client(project=os.getenv("GOOGLE_PROJECT_ID"))
        dataset_id = os.getenv("BIGQUERY_DATASET")
        
        if not dataset_id:
            return
        
        # Update traceability table with feedback metrics
        overall_score = feedback.get("overall_score", 0)
        quality_score = overall_score / 5.0  # Convert to 0-1 scale
        
        query = f"""
        UPDATE `{os.getenv('GOOGLE_PROJECT_ID')}.{dataset_id}.traceability_log`
        SET 
            feedback_count = COALESCE(feedback_count, 0) + 1,
            last_feedback_at = CURRENT_TIMESTAMP(),
            quality_score = {quality_score}
        WHERE test_case_id = '{feedback['testcase_id']}'
        """
        
        job = client.query(query)
        job.result()  # Wait for completion
        
        print("✅ BigQuery updated with feedback")
        
    except Exception as e:
        print(f"Warning: Could not update BigQuery: {e}")

def batch_feedback_collection(testcase_ids: List[str]) -> Dict[str, Dict]:
    """Collect feedback for multiple test cases"""
    all_feedback = {}
    
    print(f"\n🔄 COLLECTING FEEDBACK FOR {len(testcase_ids)} TEST CASES")
    
    for i, testcase_id in enumerate(testcase_ids, 1):
        print(f"\n--- Test Case {i}/{len(testcase_ids)} ---")
        
        # Try to load test case data
        test_case_data = _load_test_case_data(testcase_id)
        
        try:
            feedback = collect_user_feedback(testcase_id, test_case_data)
            all_feedback[testcase_id] = feedback
            
            # Ask if user wants to continue
            if i < len(testcase_ids):
                continue_feedback = input(f"\nContinue with next test case? (y/n): ").strip().lower()
                if continue_feedback not in ['y', 'yes']:
                    break
                    
        except KeyboardInterrupt:
            print(f"\nFeedback collection stopped at test case {i}")
            break
    
    # Generate summary report
    _generate_feedback_summary(all_feedback)
    
    return all_feedback

def _load_test_case_data(testcase_id: str) -> Dict[str, Any]:
    """Load test case data from local files"""
    try:
        # Try to load from complete_testcases directory
        complete_file = f"complete_testcases/{testcase_id}_complete.json"
        if os.path.exists(complete_file):
            with open(complete_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Try generated_testcases directory
        generated_file = f"generated_testcases/{testcase_id}.json"
        if os.path.exists(generated_file):
            with open(generated_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {"summary": f"Test case {testcase_id}", "description": "No data available"}
        
    except Exception as e:
        print(f"Warning: Could not load test case data: {e}")
        return {"summary": f"Test case {testcase_id}", "description": "No data available"}

def _generate_feedback_summary(all_feedback: Dict[str, Dict]) -> None:
    """Generate a summary report of all feedback"""
    if not all_feedback:
        return
    
    print(f"\n📋 FEEDBACK SUMMARY REPORT")
    print("=" * 40)
    
    # Calculate averages
    total_scores = [f.get("overall_score", 0) for f in all_feedback.values() if f.get("overall_score")]
    avg_score = sum(total_scores) / len(total_scores) if total_scores else 0
    
    print(f"Total test cases reviewed: {len(all_feedback)}")
    print(f"Average quality score: {avg_score:.1f}/5")
    
    # Common improvement areas
    improvement_counts = {}
    for feedback in all_feedback.values():
        for area in feedback.get("improvements", {}):
            improvement_counts[area] = improvement_counts.get(area, 0) + 1
    
    if improvement_counts:
        print(f"\nMost common improvement areas:")
        for area, count in sorted(improvement_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {area}: {count} mentions")
    
    # Priority distribution
    priorities = [f.get("priority", "unknown") for f in all_feedback.values()]
    priority_counts = {p: priorities.count(p) for p in set(priorities)}
    
    print(f"\nPriority distribution:")
    for priority, count in priority_counts.items():
        print(f"  {priority}: {count} test cases")
    
    # Save summary
    summary_file = f"user_feedback/feedback_summary_{int(time.time())}.json"
    summary_data = {
        "timestamp": time.time(),
        "total_reviewed": len(all_feedback),
        "average_score": avg_score,
        "improvement_areas": improvement_counts,
        "priority_distribution": priority_counts,
        "detailed_feedback": all_feedback
    }
    
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, default=str)
        print(f"\n📄 Summary saved to: {summary_file}")
    except Exception as e:
        print(f"Warning: Could not save summary: {e}")

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        testcase_ids = sys.argv[1:]
        batch_feedback_collection(testcase_ids)
    else:
        print("Usage: python user_feedback_collector.py <testcase_id1> [testcase_id2] ...")
        print("Example: python user_feedback_collector.py MDP-64 MDP-65 MDP-66")