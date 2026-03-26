"""
LLM-powered question generation for requirement analysis and test case improvement.
"""
import logging
import json
from typing import Dict, List, Any, Optional
from secure_config import config

logger = logging.getLogger(__name__)

class LLMQuestionGenerator:
    """Generates intelligent questions using LLM to improve test cases."""
    
    def __init__(self):
        pass
    
    def generate_questions(self, requirement: str, domain: str = "general") -> List[Dict[str, Any]]:
        """Generate targeted questions based on requirement analysis."""
        logger.info(f"Generating questions for {domain} requirement")
        
        # Analyze requirement complexity and gaps
        analysis = self._analyze_requirement(requirement)
        
        # Generate LLM-powered questions
        llm_questions = self._generate_llm_questions(requirement, analysis)
        
        # Add domain-specific questions
        domain_questions = self._get_domain_questions(domain, requirement)
        
        # Combine questions
        all_questions = llm_questions + domain_questions
        
        return all_questions[:8]  # Limit to 8 most important questions
    
    def _analyze_requirement(self, requirement: str) -> Dict[str, Any]:
        """Analyze requirement to identify gaps and complexity."""
        words = requirement.lower().split()
        
        analysis = {
            "length": len(words),
            "complexity": "high" if len(words) > 50 else "medium" if len(words) > 20 else "low",
            "missing_elements": [],
            "ambiguous_terms": [],
            "technical_depth": "low"
        }
        
        # Check for missing elements
        if not any(word in words for word in ["test", "verify", "validate", "check"]):
            analysis["missing_elements"].append("test_actions")
        
        if not any(word in words for word in ["should", "must", "shall", "expected"]):
            analysis["missing_elements"].append("acceptance_criteria")
        
        if not any(word in words for word in ["data", "input", "output", "result"]):
            analysis["missing_elements"].append("test_data")
        
        # Check for ambiguous terms
        ambiguous_words = ["appropriate", "reasonable", "adequate", "sufficient", "proper"]
        analysis["ambiguous_terms"] = [word for word in ambiguous_words if word in words]
        
        # Assess technical depth
        technical_terms = ["api", "database", "algorithm", "protocol", "encryption", "authentication"]
        if any(term in words for term in technical_terms):
            analysis["technical_depth"] = "high"
        
        return analysis
    
    def _generate_llm_questions(self, requirement: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate context-specific questions based on requirement content."""
        questions = []
        req_lower = requirement.lower()
        
        # Extract key entities and actions from requirement
        entities = self._extract_entities(requirement)
        actions = self._extract_actions(requirement)
        
        # Generate specific questions based on requirement content only
        if entities and actions:
            questions.append({
                "question": f"How should we verify that {actions[0]} works correctly with {entities[0]}?",
                "category": "functional_validation",
                "priority": "high",
                "reason": f"Requirement involves {actions[0]} action on {entities[0]}"
            })
        
        if len(entities) > 1:
            questions.append({
                "question": f"What happens when {entities[0]} interacts with {entities[1]}?",
                "category": "integration_testing",
                "priority": "medium",
                "reason": f"Multiple entities detected: {', '.join(entities[:2])}"
            })
        
        # Generate questions based on missing elements from analysis
        if "test_actions" in analysis.get("missing_elements", []) and entities:
            questions.append({
                "question": f"How should we test the {entities[0]} functionality described in this requirement?",
                "category": "test_actions",
                "priority": "high",
                "reason": f"Testing approach needed for {entities[0]}"
            })
        
        if "acceptance_criteria" in analysis.get("missing_elements", []) and actions:
            questions.append({
                "question": f"What should happen after {actions[0]} is successfully completed?",
                "category": "acceptance_criteria",
                "priority": "high",
                "reason": f"Success criteria needed for {actions[0]} action"
            })
        
        if "test_data" in analysis.get("missing_elements", []) and (entities or actions):
            focus = entities[0] if entities else actions[0]
            questions.append({
                "question": f"What sample data should be used when testing {focus}?",
                "category": "test_data",
                "priority": "medium",
                "reason": f"Test data needed for {focus} validation"
            })
        
        # Handle ambiguous terms
        if analysis.get("ambiguous_terms"):
            ambiguous = analysis["ambiguous_terms"][0]
            questions.append({
                "question": f"What does '{ambiguous}' mean in the context of this requirement?",
                "category": "clarification",
                "priority": "high",
                "reason": f"Ambiguous term '{ambiguous}' needs clarification"
            })
        
        return questions[:5]  # Limit to 5 most relevant questions
    
    def _extract_entities(self, requirement: str) -> List[str]:
        """Extract key entities from requirement text."""
        import re
        # Simple entity extraction - look for capitalized words and common nouns
        entities = []
        words = requirement.split()
        
        for word in words:
            # Capitalized words (potential entities)
            if word[0].isupper() and len(word) > 2 and word.isalpha():
                entities.append(word)
            # Common entity patterns
            elif word.lower() in ['user', 'system', 'database', 'file', 'record', 'account', 'profile']:
                entities.append(word.lower())
        
        return list(set(entities))[:5]  # Return unique entities, max 5
    
    def _extract_actions(self, requirement: str) -> List[str]:
        """Extract key actions from requirement text."""
        action_words = ['create', 'update', 'delete', 'validate', 'verify', 'process', 'generate', 
                       'authenticate', 'authorize', 'login', 'logout', 'save', 'load', 'send', 'receive']
        
        req_lower = requirement.lower()
        actions = [action for action in action_words if action in req_lower]
        
        return actions[:3]  # Return max 3 actions
    
    def _get_domain_questions(self, domain: str, requirement: str) -> List[Dict[str, Any]]:
        """Get contextual domain-specific questions based on requirement content."""
        questions = []
        req_lower = requirement.lower()
        
        # Generate domain questions only if requirement content relates to that domain
        entities = self._extract_entities(requirement)
        
        if domain == "security" and any(word in req_lower for word in ['secure', 'auth', 'encrypt', 'permission', 'access']) and entities:
            questions.append({
                "question": f"How should {entities[0]} be secured in this implementation?",
                "category": "security",
                "priority": "high",
                "reason": f"Security considerations for {entities[0]}"
            })
        
        elif domain == "performance" and any(word in req_lower for word in ['fast', 'speed', 'time', 'load', 'response']) and entities:
            questions.append({
                "question": f"What performance expectations exist for {entities[0]}?",
                "category": "performance",
                "priority": "high",
                "reason": f"Performance requirements for {entities[0]}"
            })
        
        elif domain == "compliance" and any(word in req_lower for word in ['comply', 'standard', 'regulation', 'audit']) and entities:
            questions.append({
                "question": f"What compliance rules apply to {entities[0]}?",
                "category": "compliance",
                "priority": "high",
                "reason": f"Compliance requirements for {entities[0]}"
            })
        
        return questions
    

    
    def collect_answers(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Always use UI mode for question collection."""
        try:
            from question_ui import display_questions_ui
            return display_questions_ui(questions)
        except ImportError:
            return self._collect_answers_console(questions)
    
    def _collect_answers_console(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Skip console collection - return empty answers."""
        logger.info(f"Skipping {len(questions)} console questions")
        return {}
    
    def update_test_case(self, original_test_case: Dict[str, Any], answers: Dict[str, Any]) -> Dict[str, Any]:
        """Update test case based on collected answers."""
        updated_test_case = original_test_case.copy()
        
        # Update based on answers (handle new key structure)
        for key, answer_data in answers.items():
            category = answer_data.get("category", key.split("_")[0])
            answer = answer_data.get("answer", "")
            
            if category == "test_steps" and answer:
                if "steps" in updated_test_case:
                    updated_test_case["steps"] += f"\nAdditional steps: {answer}"
                else:
                    updated_test_case["test_steps"] = answer
            
            elif category == "acceptance" and answer:
                updated_test_case["acceptance_criteria"] = answer
            
            elif category == "test_data" and answer:
                updated_test_case["test_data"] = answer
            
            elif category == "prerequisites" and answer:
                updated_test_case["prerequisites"] = answer
        
        # Update description with clarifications
        clarifications = [a.get("answer", "") for a in answers.values() if a.get("answer")]
        if clarifications:
            clarification_text = " ".join(clarifications)
            if "description" in updated_test_case:
                updated_test_case["description"] += f"\n\nClarifications: {clarification_text}"
            else:
                updated_test_case["description"] = f"Clarifications: {clarification_text}"
        
        # Add metadata about improvements
        updated_test_case["llm_enhanced"] = True
        updated_test_case["enhancement_timestamp"] = str(config.get("timestamp", "unknown"))
        updated_test_case["questions_answered"] = len(answers)
        
        return updated_test_case

# Global instance
llm_question_generator = LLMQuestionGenerator()