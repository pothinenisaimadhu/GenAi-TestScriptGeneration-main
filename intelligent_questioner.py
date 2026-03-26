#!/usr/bin/env python3

import json
import os
import time
import requests
from typing import Dict, List, Any, Optional

class IntelligentQuestioner:
    """LLM-powered intelligent questioner that analyzes data and asks contextual questions"""
    
    def __init__(self):
        self.conversation_history = []
        self.context_analysis = {}
        
    def analyze_and_question(self, data: Dict[str, Any], data_type: str = "requirement") -> Dict[str, Any]:
        """Analyze submitted data and generate intelligent questions"""
        
        print(f"\n🤖 ANALYZING {data_type.upper()} DATA...")
        
        # Analyze the context
        analysis = self._analyze_context(data, data_type)
        self.context_analysis = analysis
        
        # Generate intelligent questions based on analysis
        questions = self._generate_contextual_questions(analysis, data_type)
        
        # Ask questions interactively
        responses = self._ask_questions_interactively(questions, data)
        
        # Generate improvement suggestions
        improvements = self._generate_improvements(analysis, responses)
        
        return {
            "analysis": analysis,
            "questions_asked": questions,
            "user_responses": responses,
            "improvements": improvements,
            "timestamp": time.time()
        }
    
    def _analyze_context(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """Analyze the context of submitted data using LLM"""
        
        # Prepare context for LLM analysis
        context_prompt = self._build_analysis_prompt(data, data_type)
        
        # Get LLM analysis
        llm_analysis = self._call_llm_for_analysis(context_prompt)
        
        # Parse and structure the analysis
        analysis = {
            "data_type": data_type,
            "complexity_level": self._assess_complexity(data),
            "domain": self._detect_domain(data),
            "missing_elements": self._identify_missing_elements(data, data_type),
            "clarity_issues": self._identify_clarity_issues(data),
            "llm_insights": llm_analysis,
            "risk_areas": self._identify_risk_areas(data)
        }
        
        return analysis
    
    def _build_analysis_prompt(self, data: Dict[str, Any], data_type: str) -> str:
        """Build prompt for LLM analysis"""
        
        data_text = json.dumps(data, indent=2)[:1000]  # Limit size
        
        prompt = f"""
Analyze this {data_type} data and provide insights:

DATA:
{data_text}

Please analyze and identify:
1. Domain/Industry (security, healthcare, finance, etc.)
2. Complexity level (simple, moderate, complex)
3. Missing critical information
4. Unclear or ambiguous parts
5. Potential compliance requirements
6. Risk areas that need attention

Provide a structured analysis in JSON format with these keys:
- domain
- complexity
- missing_info
- unclear_parts
- compliance_needs
- risk_areas
"""
        return prompt
    
    def _call_llm_for_analysis(self, prompt: str) -> Dict[str, Any]:
        """Call LLM for intelligent analysis"""
        try:
            # Try Ollama first
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code == 200:
                models = response.json().get("models", [])
                if models:
                    model_name = models[0]["name"]
                    
                    llm_response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": model_name,
                            "prompt": prompt,
                            "stream": False,
                            "options": {"temperature": 0.3, "num_predict": 500}
                        },
                        timeout=30
                    )
                    
                    if llm_response.status_code == 200:
                        result = llm_response.json().get("response", "")
                        return self._parse_llm_response(result)
        
        except Exception as e:
            print(f"LLM analysis failed: {e}")
        
        # Fallback to rule-based analysis
        return self._fallback_analysis()
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response and extract structured data"""
        try:
            # Try to extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback parsing
        return {
            "domain": "general",
            "complexity": "moderate",
            "missing_info": ["More details needed"],
            "unclear_parts": ["Some ambiguity detected"],
            "compliance_needs": ["Standard compliance"],
            "risk_areas": ["General risks"]
        }
    
    def _generate_contextual_questions(self, analysis: Dict[str, Any], data_type: str) -> List[Dict[str, str]]:
        """Generate intelligent questions based on analysis"""
        
        questions = []
        domain = analysis.get("domain", "general")
        complexity = analysis.get("complexity_level", "moderate")
        missing = analysis.get("missing_elements", [])
        
        # Domain-specific questions
        if domain == "security":
            questions.extend([
                {"type": "security", "question": "What security standards must this comply with (ISO 27001, NIST, etc.)?"},
                {"type": "security", "question": "What are the authentication and authorization requirements?"},
                {"type": "security", "question": "Are there specific encryption or data protection needs?"}
            ])
        elif domain == "healthcare":
            questions.extend([
                {"type": "compliance", "question": "Does this need to comply with HIPAA or other healthcare regulations?"},
                {"type": "data", "question": "What patient data will be handled and how should it be protected?"}
            ])
        elif domain == "finance":
            questions.extend([
                {"type": "compliance", "question": "What financial regulations apply (SOX, PCI-DSS, etc.)?"},
                {"type": "audit", "question": "What audit trail requirements are needed?"}
            ])
        
        # Complexity-based questions
        if complexity == "complex":
            questions.extend([
                {"type": "integration", "question": "What systems or services will this integrate with?"},
                {"type": "performance", "question": "What are the performance and scalability requirements?"},
                {"type": "error_handling", "question": "How should errors and edge cases be handled?"}
            ])
        
        # Missing elements questions
        if "user_roles" in missing:
            questions.append({"type": "users", "question": "Who are the different types of users and what are their roles?"})
        
        if "business_rules" in missing:
            questions.append({"type": "business", "question": "What are the key business rules and constraints?"})
        
        # General improvement questions
        questions.extend([
            {"type": "context", "question": "What is the main business goal this requirement addresses?"},
            {"type": "priority", "question": "What is the priority level of this requirement (High/Medium/Low)?"},
            {"type": "timeline", "question": "What is the expected timeline for implementation?"},
            {"type": "success", "question": "How will you measure success for this requirement?"}
        ])
        
        return questions[:8]  # Limit to 8 questions to avoid fatigue
    
    def _ask_questions_interactively(self, questions: List[Dict[str, str]], original_data: Dict[str, Any]) -> Dict[str, str]:
        """Ask questions interactively and collect responses"""
        
        responses = {}
        
        print(f"\n💬 I have {len(questions)} questions to better understand your needs:")
        print("(You can type 'skip' to skip a question or 'done' to finish early)\n")
        
        for i, q in enumerate(questions, 1):
            try:
                print(f"[{i}/{len(questions)}] {q['question']}")
                
                response = input("Your answer: ").strip()
                
                if response.lower() == 'done':
                    print("Finishing questions early...")
                    break
                elif response.lower() == 'skip':
                    responses[q['type']] = "skipped"
                elif response:
                    responses[q['type']] = response
                    
                    # Ask follow-up questions based on response
                    followup = self._generate_followup_question(q, response, original_data)
                    if followup:
                        print(f"  Follow-up: {followup}")
                        followup_response = input("  Answer: ").strip()
                        if followup_response:
                            responses[f"{q['type']}_followup"] = followup_response
                
                print()  # Empty line for readability
                
            except KeyboardInterrupt:
                print("\nQuestioning session cancelled")
                break
        
        return responses
    
    def _generate_followup_question(self, original_q: Dict[str, str], response: str, data: Dict[str, Any]) -> Optional[str]:
        """Generate intelligent follow-up questions"""
        
        q_type = original_q['type']
        response_lower = response.lower()
        
        followups = {
            "security": {
                "encrypt": "What type of encryption is required (AES-256, RSA, etc.)?",
                "auth": "Will you use single sign-on (SSO) or multi-factor authentication?",
                "compliance": "Are there specific security certifications required?"
            },
            "performance": {
                "fast": "What response time is acceptable (milliseconds, seconds)?",
                "scale": "How many concurrent users should the system support?",
                "load": "What is the expected data volume or transaction rate?"
            },
            "integration": {
                "api": "What API format is preferred (REST, GraphQL, SOAP)?",
                "database": "What database systems need to be supported?",
                "system": "Are there specific integration patterns or protocols required?"
            }
        }
        
        if q_type in followups:
            for keyword, followup in followups[q_type].items():
                if keyword in response_lower:
                    return followup
        
        return None
    
    def _generate_improvements(self, analysis: Dict[str, Any], responses: Dict[str, str]) -> Dict[str, Any]:
        """Generate improvement suggestions based on analysis and responses"""
        
        improvements = {
            "enhanced_requirements": {},
            "test_case_improvements": {},
            "compliance_additions": {},
            "risk_mitigations": {}
        }
        
        # Enhance requirements based on responses
        for response_type, response in responses.items():
            if response == "skipped":
                continue
                
            if response_type == "security":
                improvements["enhanced_requirements"]["security"] = f"Security requirement: {response}"
                improvements["test_case_improvements"]["security_tests"] = "Add security validation test cases"
            
            elif response_type == "performance":
                improvements["enhanced_requirements"]["performance"] = f"Performance requirement: {response}"
                improvements["test_case_improvements"]["performance_tests"] = "Add performance and load test cases"
            
            elif response_type == "compliance":
                improvements["compliance_additions"]["standards"] = f"Compliance standards: {response}"
                improvements["test_case_improvements"]["compliance_tests"] = "Add compliance validation test cases"
        
        # Add risk mitigations
        risk_areas = analysis.get("risk_areas", [])
        for risk in risk_areas:
            improvements["risk_mitigations"][risk] = f"Mitigation strategy needed for: {risk}"
        
        return improvements
    
    # Helper methods for analysis
    def _assess_complexity(self, data: Dict[str, Any]) -> str:
        """Assess complexity level of the data"""
        text = str(data).lower()
        
        complex_indicators = ['integration', 'api', 'database', 'security', 'performance', 'scalability']
        moderate_indicators = ['user', 'interface', 'validation', 'business rule']
        
        complex_count = sum(1 for indicator in complex_indicators if indicator in text)
        moderate_count = sum(1 for indicator in moderate_indicators if indicator in text)
        
        if complex_count >= 2:
            return "complex"
        elif moderate_count >= 1 or complex_count >= 1:
            return "moderate"
        else:
            return "simple"
    
    def _detect_domain(self, data: Dict[str, Any]) -> str:
        """Detect the domain/industry"""
        text = str(data).lower()
        
        domains = {
            "security": ["security", "encrypt", "auth", "password", "token", "certificate"],
            "healthcare": ["patient", "medical", "hipaa", "health", "clinical"],
            "finance": ["payment", "transaction", "financial", "banking", "sox", "pci"],
            "audit": ["audit", "compliance", "regulation", "trail", "log"],
            "data": ["database", "storage", "backup", "data", "information"]
        }
        
        for domain, keywords in domains.items():
            if any(keyword in text for keyword in keywords):
                return domain
        
        return "general"
    
    def _identify_missing_elements(self, data: Dict[str, Any], data_type: str) -> List[str]:
        """Identify missing critical elements"""
        missing = []
        text = str(data).lower()
        
        critical_elements = {
            "user_roles": ["user", "role", "permission", "access"],
            "business_rules": ["rule", "constraint", "condition", "validation"],
            "error_handling": ["error", "exception", "failure", "fallback"],
            "performance": ["performance", "speed", "response", "load"],
            "security": ["security", "authentication", "authorization", "encryption"]
        }
        
        for element, keywords in critical_elements.items():
            if not any(keyword in text for keyword in keywords):
                missing.append(element)
        
        return missing
    
    def _identify_clarity_issues(self, data: Dict[str, Any]) -> List[str]:
        """Identify clarity and ambiguity issues"""
        issues = []
        text = str(data)
        
        # Check for vague terms
        vague_terms = ["should", "might", "could", "maybe", "probably", "some", "various"]
        if any(term in text.lower() for term in vague_terms):
            issues.append("Contains vague or ambiguous language")
        
        # Check for missing specifics
        if len(text.split()) < 20:
            issues.append("Requirement appears too brief or lacks detail")
        
        return issues
    
    def _identify_risk_areas(self, data: Dict[str, Any]) -> List[str]:
        """Identify potential risk areas"""
        risks = []
        text = str(data).lower()
        
        risk_indicators = {
            "data_privacy": ["personal", "sensitive", "confidential", "private"],
            "integration_complexity": ["integrate", "connect", "interface", "api"],
            "performance_risk": ["real-time", "high-volume", "concurrent", "scalable"],
            "security_risk": ["external", "public", "internet", "third-party"]
        }
        
        for risk, indicators in risk_indicators.items():
            if any(indicator in text for indicator in indicators):
                risks.append(risk)
        
        return risks
    
    def _fallback_analysis(self) -> Dict[str, Any]:
        """Fallback analysis when LLM is not available"""
        return {
            "domain": "general",
            "complexity": "moderate",
            "missing_info": ["Additional context needed"],
            "unclear_parts": ["Some areas need clarification"],
            "compliance_needs": ["Standard compliance requirements"],
            "risk_areas": ["General implementation risks"]
        }

def integrate_with_requirement_processing(requirement_text: str) -> Dict[str, Any]:
    """Integrate intelligent questioning with requirement processing"""
    
    questioner = IntelligentQuestioner()
    
    # Prepare requirement data
    req_data = {
        "requirement": requirement_text,
        "source": "user_input",
        "timestamp": time.time()
    }
    
    # Analyze and question
    result = questioner.analyze_and_question(req_data, "requirement")
    
    # Save the enhanced understanding
    _save_enhanced_understanding(result)
    
    return result

def _save_enhanced_understanding(result: Dict[str, Any]) -> None:
    """Save the enhanced understanding for future use"""
    try:
        understanding_dir = "enhanced_understanding"
        os.makedirs(understanding_dir, exist_ok=True)
        
        filename = f"understanding_{int(time.time())}.json"
        filepath = os.path.join(understanding_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"📚 Enhanced understanding saved to: {filepath}")
        
    except Exception as e:
        print(f"Warning: Could not save enhanced understanding: {e}")

if __name__ == "__main__":
    # Example usage
    sample_requirement = "The system should handle user authentication securely"
    
    print("🤖 INTELLIGENT REQUIREMENT ANALYSIS")
    print("=" * 50)
    
    result = integrate_with_requirement_processing(sample_requirement)
    
    print(f"\n📊 ANALYSIS COMPLETE")
    print(f"Domain detected: {result['analysis']['domain']}")
    print(f"Complexity: {result['analysis']['complexity_level']}")
    print(f"Questions asked: {len(result['questions_asked'])}")
    print(f"Responses collected: {len(result['user_responses'])}")