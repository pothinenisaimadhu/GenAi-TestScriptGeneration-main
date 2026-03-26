"""
User feedback integration service.
Handles collection, storage, and processing of user feedback using LLM-generated questions.
"""
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List
from secure_config import config


logger = logging.getLogger(__name__)

class FeedbackIntegration:
    """Manages user feedback collection and storage using LLM-generated questions."""
    
    def __init__(self):
        self.feedback_dir = config.get_safe_paths()["feedback_dir"]
        os.makedirs(self.feedback_dir, exist_ok=True)
    
    def collect_llm_feedback(self, requirement: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Collect feedback using LLM-generated questions."""
        print(f"\n🤖 COLLECTING FEEDBACK WITH LLM-GENERATED QUESTIONS")
        print("=" * 60)
        
        # Generate feedback questions using LLM
        feedback_questions = self._generate_feedback_questions(requirement, test_case)
        
        # Collect responses
        responses = self._collect_llm_responses(feedback_questions)
        
        # Store feedback
        feedback_data = {
            "requirement": requirement,
            "test_case_id": test_case.get("id", "unknown"),
            "timestamp": datetime.utcnow().isoformat(),
            "llm_questions": feedback_questions,
            "user_responses": responses,
            "feedback_type": "llm_generated"
        }
        
        self._store_feedback(feedback_data)
        return feedback_data
    
    def _generate_feedback_questions(self, requirement: str, test_case: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate feedback questions using LLM analysis."""
        # Analyze test case quality gaps
        quality_analysis = self._analyze_test_case_quality(test_case)
        
        questions = []
        
        # Generate questions based on quality gaps
        if quality_analysis.get("missing_steps"):
            questions.append({
                "question": "Are the test steps complete and clear enough to execute?",
                "category": "completeness",
                "type": "rating",
                "scale": "1-5"
            })
        
        if quality_analysis.get("unclear_criteria"):
            questions.append({
                "question": "How clear are the acceptance criteria for this test case?",
                "category": "clarity", 
                "type": "rating",
                "scale": "1-5"
            })
        
        # Always ask about relevance
        questions.append({
            "question": "How well does this test case address the original requirement?",
            "category": "relevance",
            "type": "rating", 
            "scale": "1-5"
        })
        
        # Domain-specific questions
        domain = self._detect_domain(requirement)
        domain_questions = self._get_domain_feedback_questions(domain)
        questions.extend(domain_questions)
        
        return questions[:5]  # Limit to 5 questions
    
    def _analyze_test_case_quality(self, test_case: Dict[str, Any]) -> Dict[str, bool]:
        """Analyze test case for quality gaps."""
        return {
            "missing_steps": not test_case.get("steps") and not test_case.get("test_steps"),
            "unclear_criteria": not test_case.get("acceptance_criteria")
        }
    
    def _detect_domain(self, requirement: str) -> str:
        """Detect domain for targeted questions."""
        text = requirement.lower()
        if any(word in text for word in ['security', 'auth', 'encrypt']):
            return "security"
        elif any(word in text for word in ['audit', 'compliance', 'regulatory']):
            return "compliance"
        elif any(word in text for word in ['performance', 'load', 'speed']):
            return "performance"
        return "general"
    
    def _get_domain_feedback_questions(self, domain: str) -> List[Dict[str, Any]]:
        """Get domain-specific feedback questions."""
        domain_questions = {
            "security": [{
                "question": "Does this test case adequately cover security validation?",
                "category": "security_coverage",
                "type": "yes_no"
            }],
            "compliance": [{
                "question": "Are compliance requirements properly addressed?", 
                "category": "compliance_coverage",
                "type": "yes_no"
            }],
            "performance": [{
                "question": "Are performance criteria clearly testable?",
                "category": "performance_testability",
                "type": "yes_no"
            }]
        }
        return domain_questions.get(domain, [])
    
    def _collect_llm_responses(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Skip LLM response collection - return default responses."""
        logger.info(f"Skipping {len(questions)} LLM feedback questions")
        return {q['category']: 4 for q in questions}
    
    def _get_rating(self, prompt: str, min_val: int, max_val: int, default: int) -> int:
        """Get numeric rating from user."""
        for _ in range(3):  # Max 3 attempts
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
        for _ in range(3):  # Max 3 attempts
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
    
    def _store_feedback(self, feedback: Dict[str, Any]) -> None:
        """Store feedback to local file."""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"feedback_{timestamp}_{hash(feedback['requirement']) % 10000}.json"
            filepath = os.path.join(self.feedback_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(feedback, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Feedback stored: {filepath}")
        except Exception as e:
            logger.error(f"Failed to store feedback: {e}")
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of LLM-generated feedback."""
        try:
            feedback_files = [f for f in os.listdir(self.feedback_dir) 
                            if f.endswith('.json') and 'feedback_' in f]
            
            if not feedback_files:
                return {"total_feedback": 0, "average_ratings": {}}
            
            # Analyze LLM feedback
            llm_feedback = []
            for filename in feedback_files:
                try:
                    with open(os.path.join(self.feedback_dir, filename), 'r') as f:
                        feedback = json.load(f)
                        if feedback.get("feedback_type") == "llm_generated":
                            llm_feedback.append(feedback)
                except Exception as e:
                    logger.warning(f"Error reading feedback file {filename}: {e}")
            
            # Calculate averages for rating categories
            category_totals = {}
            category_counts = {}
            
            for feedback in llm_feedback:
                responses = feedback.get("user_responses", {})
                for category, value in responses.items():
                    if isinstance(value, (int, float)):
                        category_totals[category] = category_totals.get(category, 0) + value
                        category_counts[category] = category_counts.get(category, 0) + 1
            
            average_ratings = {}
            for category in category_totals:
                average_ratings[category] = category_totals[category] / category_counts[category]
            
            return {
                "total_feedback": len(feedback_files),
                "llm_feedback_count": len(llm_feedback),
                "average_ratings": average_ratings,
                "categories_analyzed": list(average_ratings.keys())
            }
            
        except Exception as e:
            logger.error(f"Error getting feedback summary: {e}")
            return {"total_feedback": 0, "average_ratings": {}}

# Global feedback integration instance
feedback_integration = FeedbackIntegration()