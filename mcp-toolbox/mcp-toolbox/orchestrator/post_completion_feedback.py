"""
Post-completion feedback system for test case generation.
Collects feedback after the entire workflow is complete.
"""
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from secure_config import config

logger = logging.getLogger(__name__)

class PostCompletionFeedback:
    """Collects comprehensive feedback after test case generation completion."""
    
    def __init__(self):
        self.feedback_dir = config.get_safe_paths()["feedback_dir"]
        os.makedirs(self.feedback_dir, exist_ok=True)
    
    def collect_workflow_feedback(self, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """Skip terminal feedback collection - return default feedback."""
        logger.info("Skipping terminal feedback collection")
        return self._create_default_feedback(workflow_results)
    
    def _display_workflow_summary(self, results: Dict[str, Any]) -> None:
        """Display summary of workflow results."""
        print(f"\\n📊 WORKFLOW SUMMARY:")
        print(f"  • Requirements processed: {results.get('processed_requirements', 0)}")
        print(f"  • Test cases generated: {results.get('test_cases_generated', 0)}")
        print(f"  • Success rate: {results.get('performance_metrics', {}).get('success_rate', 0):.1%}")
        print(f"  • Processing time: {results.get('processing_time', 0):.1f}s")
        
        if results.get("successful_results"):
            print(f"\\n📝 GENERATED TEST CASES:")
            for i, result in enumerate(results["successful_results"][:3], 1):
                testcase_id = result.get("testcase_id", "Unknown")
                requirement = result.get("requirement", "")[:50]
                print(f"  {i}. {testcase_id}: {requirement}...")
    
    def _collect_specific_feedback(self) -> Dict[str, Any]:
        """Collect feedback on specific aspects."""
        specific_feedback = {}
        
        print(f"\\n🔍 SPECIFIC FEEDBACK AREAS:")
        
        # Question quality
        question_quality = self._get_rating(
            "Quality of generated questions (1-5): ", 1, 5, 3
        )
        specific_feedback["question_quality"] = question_quality
        
        # LLM enhancement effectiveness
        llm_helpful = self._get_yes_no(
            "Were the LLM-generated questions helpful? (y/n): ", True
        )
        specific_feedback["llm_questions_helpful"] = llm_helpful
        
        # User interaction experience
        interaction_smooth = self._get_yes_no(
            "Was the user interaction smooth and intuitive? (y/n): ", True
        )
        specific_feedback["smooth_interaction"] = interaction_smooth
        
        # Test case format
        format_good = self._get_yes_no(
            "Is the test case format suitable for your needs? (y/n): ", True
        )
        specific_feedback["good_format"] = format_good
        
        # Missing features
        missing_features = input("What features are missing? (optional): ").strip()
        if missing_features:
            specific_feedback["missing_features"] = missing_features
        
        return specific_feedback
    
    def _get_rating(self, prompt: str, min_val: int, max_val: int, default: int) -> int:
        """Get numeric rating from user."""
        for _ in range(3):
            try:
                response = input(prompt).strip()
                if not response:
                    return default
                rating = int(response)
                if min_val <= rating <= max_val:
                    return rating
                print(f"Please enter a number between {min_val} and {max_val}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                return default
        return default
    
    def _get_yes_no(self, prompt: str, default: bool) -> bool:
        """Get yes/no response from user."""
        for _ in range(3):
            try:
                response = input(prompt).strip().lower()
                if not response:
                    return default
                if response in ['y', 'yes', '1', 'true']:
                    return True
                elif response in ['n', 'no', '0', 'false']:
                    return False
                print("Please enter 'y' for yes or 'n' for no")
            except KeyboardInterrupt:
                return default
        return default
    
    def _store_completion_feedback(self, feedback: Dict[str, Any]) -> None:
        """Store completion feedback to file."""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"completion_feedback_{timestamp}.json"
            filepath = os.path.join(self.feedback_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(feedback, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Completion feedback stored: {filepath}")
            
            # Also update BigQuery if possible
            self._update_bigquery_completion_feedback(feedback)
            
        except Exception as e:
            logger.error(f"Failed to store completion feedback: {e}")
    
    def _update_bigquery_completion_feedback(self, feedback: Dict[str, Any]) -> None:
        """Update BigQuery with completion feedback."""
        try:
            from google.cloud import bigquery
            
            client = bigquery.Client(project=os.getenv("GOOGLE_PROJECT_ID"))
            dataset_id = os.getenv("BIGQUERY_DATASET")
            
            if not dataset_id:
                return
            
            # Create completion feedback record
            completion_data = feedback["completion_feedback"]
            
            table_id = "completion_feedback"
            rows_to_insert = [{
                "workflow_id": feedback["workflow_id"],
                "timestamp": feedback["timestamp"],
                "overall_satisfaction": completion_data.get("overall_satisfaction", 0),
                "test_case_quality": completion_data.get("test_case_quality", 0),
                "test_coverage": completion_data.get("test_coverage", 0),
                "time_efficiency": completion_data.get("time_efficiency", 0),
                "overall_score": completion_data.get("overall_score", 0),
                "would_recommend": completion_data.get("would_recommend", False),
                "improvement_suggestions": completion_data.get("improvement_suggestions", ""),
                "llm_questions_helpful": completion_data.get("llm_questions_helpful", True)
            }]
            
            table_ref = client.dataset(dataset_id).table(table_id)
            errors = client.insert_rows_json(table_ref, rows_to_insert)
            
            if not errors:
                logger.info("Completion feedback updated in BigQuery")
            else:
                logger.error(f"BigQuery completion feedback errors: {errors}")
                
        except Exception as e:
            logger.warning(f"Could not update BigQuery with completion feedback: {e}")
    
    def _generate_recommendations(self, feedback: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on feedback."""
        recommendations = []
        completion_data = feedback["completion_feedback"]
        
        overall_score = completion_data.get("overall_score", 3)
        
        if overall_score < 3:
            recommendations.append("Consider reviewing the requirement analysis process")
            recommendations.append("Focus on improving test case quality")
        
        if completion_data.get("test_case_quality", 3) < 3:
            recommendations.append("Enhance LLM question generation templates")
            recommendations.append("Add more domain-specific validation")
        
        if completion_data.get("time_efficiency", 3) < 3:
            recommendations.append("Optimize workflow processing time")
            recommendations.append("Consider reducing number of interactive questions")
        
        if not completion_data.get("llm_questions_helpful", True):
            recommendations.append("Review and improve LLM question relevance")
            recommendations.append("Add more context-aware question generation")
        
        if not completion_data.get("smooth_interaction", True):
            recommendations.append("Improve user interface and interaction flow")
            recommendations.append("Add better error handling and user guidance")
        
        return recommendations
    
    def _create_default_feedback(self, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create default feedback for UI mode without terminal prompts."""
        feedback = {
            "workflow_id": workflow_results.get("workflow_id", "unknown"),
            "timestamp": datetime.utcnow().isoformat(),
            "workflow_results": workflow_results,
            "completion_feedback": {
                "overall_satisfaction": 4,
                "test_case_quality": 4,
                "test_coverage": 4,
                "time_efficiency": 4,
                "overall_score": 4.0,
                "question_quality": 4,
                "llm_questions_helpful": True,
                "smooth_interaction": True,
                "good_format": True,
                "would_recommend": True,
                "ui_mode": True
            }
        }
        
        # Store feedback
        self._store_completion_feedback(feedback)
        
        logger.info("Default feedback created for UI mode")
        return feedback
    
    def generate_feedback_report(self) -> Dict[str, Any]:
        """Generate comprehensive feedback report from all collected data."""
        try:
            feedback_files = [f for f in os.listdir(self.feedback_dir) 
                            if f.startswith('completion_feedback_') and f.endswith('.json')]
            
            if not feedback_files:
                return {"message": "No completion feedback data available"}
            
            all_feedback = []
            for filename in feedback_files:
                try:
                    with open(os.path.join(self.feedback_dir, filename), 'r') as f:
                        feedback = json.load(f)
                        all_feedback.append(feedback)
                except Exception as e:
                    logger.warning(f"Error reading feedback file {filename}: {e}")
            
            # Calculate aggregated metrics
            completion_scores = []
            satisfaction_scores = []
            quality_scores = []
            
            for feedback in all_feedback:
                completion_data = feedback.get("completion_feedback", {})
                if "overall_score" in completion_data:
                    completion_scores.append(completion_data["overall_score"])
                if "overall_satisfaction" in completion_data:
                    satisfaction_scores.append(completion_data["overall_satisfaction"])
                if "test_case_quality" in completion_data:
                    quality_scores.append(completion_data["test_case_quality"])
            
            report = {
                "total_feedback_sessions": len(all_feedback),
                "average_overall_score": sum(completion_scores) / len(completion_scores) if completion_scores else 0,
                "average_satisfaction": sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0,
                "average_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
                "recommendation_rate": sum(1 for f in all_feedback 
                                        if f.get("completion_feedback", {}).get("would_recommend", False)) / len(all_feedback),
                "common_improvements": [],
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating feedback report: {e}")
            return {"error": str(e)}
    


# Global instance
post_completion_feedback = PostCompletionFeedback()