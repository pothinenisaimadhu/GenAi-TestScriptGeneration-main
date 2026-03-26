import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import tools

logger = logging.getLogger(__name__)

@dataclass
class ComplianceCheck:
    requirement_id: str
    regulatory_section: str
    compliance_score: float
    missing_elements: List[str]
    validation_passed: bool

class RegulatoryValidator:
    """Validates test cases against regulatory PDF requirements"""
    
    def __init__(self):
        self.name = "RegulatoryValidator"
        self.compliance_threshold = 0.7
    
    async def validate_test_case_compliance(self, test_case: str, requirement: str, 
                                          regulatory_context: List[str]) -> ComplianceCheck:
        """Validate if test case covers regulatory requirements"""
        try:
            # Extract regulatory requirements from context
            regulatory_requirements = self._extract_regulatory_requirements(regulatory_context)
            
            # Check test case coverage
            coverage_score = await self._calculate_coverage_score(test_case, regulatory_requirements)
            
            # Identify missing elements
            missing_elements = self._identify_missing_elements(test_case, regulatory_requirements)
            
            # Validate specific compliance areas
            compliance_areas = await self._validate_compliance_areas(test_case, regulatory_context)
            
            # Calculate final compliance score with better weighting
            final_score = (coverage_score * 0.4) + (compliance_areas['score'] * 0.6)
            
            # Boost score if test case has good structure
            if 'steps:' in test_case.lower() and 'expected:' in test_case.lower():
                final_score += 0.1
            
            final_score = min(final_score, 1.0)
            
            return ComplianceCheck(
                requirement_id=f"REQ-{hash(requirement) % 10000}",
                regulatory_section=self._identify_regulatory_section(regulatory_context),
                compliance_score=final_score,
                missing_elements=missing_elements,
                validation_passed=final_score >= self.compliance_threshold
            )
            
        except Exception as e:
            logger.error(f"Compliance validation failed: {e}")
            return ComplianceCheck(
                requirement_id="UNKNOWN",
                regulatory_section="UNKNOWN",
                compliance_score=0.0,
                missing_elements=["Validation failed"],
                validation_passed=False
            )
    
    def _extract_regulatory_requirements(self, regulatory_context: List[str]) -> List[str]:
        """Extract specific regulatory requirements from context"""
        requirements = []
        for context in regulatory_context:
            # Look for regulatory patterns
            lines = context.split('\n')
            for line in lines:
                line = line.strip()
                if any(keyword in line.lower() for keyword in 
                      ['must', 'shall', 'required', 'mandatory', 'compliance']):
                    if len(line) > 20:  # Filter out short lines
                        requirements.append(line)
        return requirements[:10]  # Limit to top 10
    
    async def _calculate_coverage_score(self, test_case: str, regulatory_reqs: List[str]) -> float:
        """Calculate how well test case covers regulatory requirements"""
        if not regulatory_reqs:
            return 0.5  # Default score if no regulatory context
        
        test_case_lower = test_case.lower()
        covered_count = 0
        
        for req in regulatory_reqs:
            req_keywords = self._extract_keywords(req)
            if any(keyword in test_case_lower for keyword in req_keywords):
                covered_count += 1
        
        return covered_count / len(regulatory_reqs) if regulatory_reqs else 0.0
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key compliance keywords from text"""
        import re
        # Remove common words and extract meaningful terms
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        stop_words = {'must', 'shall', 'will', 'should', 'required', 'the', 'and', 'or', 'but'}
        return [word for word in words if word not in stop_words][:5]
    
    def _identify_missing_elements(self, test_case: str, regulatory_reqs: List[str]) -> List[str]:
        """Identify regulatory elements missing from test case"""
        missing = []
        test_case_lower = test_case.lower()
        
        # Enhanced compliance elements with more keywords
        compliance_elements = {
            'audit trail': ['audit', 'trail', 'log', 'record', 'trace'],
            'data retention': ['retention', 'archive', 'delete', 'purge', 'lifecycle'],
            'access control': ['access', 'permission', 'authorize', 'authenticate', 'role'],
            'encryption': ['encrypt', 'secure', 'protect', 'cipher', 'crypto'],
            'logging': ['log', 'monitor', 'track', 'event', 'activity'],
            'validation': ['valid', 'verify', 'check', 'confirm', 'ensure']
        }
        
        # Only add to missing if:
        # 1. Test case doesn't have the element
        # 2. Regulatory requirements mention it
        # 3. Element is actually relevant to compliance
        
        for element, keywords in compliance_elements.items():
            # Check if test case has this element (need at least 2 keyword matches for confidence)
            test_matches = sum(1 for keyword in keywords if keyword in test_case_lower)
            has_element = test_matches >= 2
            
            if not has_element:
                # Check if regulatory requirements mention this element
                reg_mentions = 0
                for req in regulatory_reqs:
                    if req and len(req.strip()) > 10:
                        req_lower = req.lower()
                        reg_mentions += sum(1 for keyword in keywords if keyword in req_lower)
                
                # Only add as missing if regulatory requirements actually mention it
                if reg_mentions >= 1:
                    missing.append(element)
        
        # If no specific missing elements but score is low, add generic compliance
        if not missing and len(regulatory_reqs) > 0:
            # Check for basic compliance structure
            if 'compliance' not in test_case_lower and 'regulatory' not in test_case_lower:
                missing.append('regulatory compliance verification')
        
        return missing[:4]  # Limit to top 4 missing elements
    
    async def _validate_compliance_areas(self, test_case: str, regulatory_context: List[str]) -> Dict[str, Any]:
        """Validate specific compliance areas"""
        areas = {
            'data_protection': self._check_data_protection(test_case),
            'audit_requirements': self._check_audit_requirements(test_case),
            'access_controls': self._check_access_controls(test_case),
            'retention_policies': self._check_retention_policies(test_case)
        }
        
        # Calculate overall compliance area score
        scores = [score for score in areas.values() if isinstance(score, (int, float))]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        return {'areas': areas, 'score': avg_score}
    
    def _check_data_protection(self, test_case: str) -> float:
        """Check data protection compliance"""
        keywords = ['encrypt', 'privacy', 'personal', 'sensitive', 'protect', 'gdpr']
        test_lower = test_case.lower()
        matches = sum(1 for keyword in keywords if keyword in test_lower)
        return min(matches / 3, 1.0)  # Normalize to 0-1
    
    def _check_audit_requirements(self, test_case: str) -> float:
        """Check audit trail requirements"""
        keywords = ['audit', 'log', 'track', 'record', 'trace', 'monitor']
        test_lower = test_case.lower()
        matches = sum(1 for keyword in keywords if keyword in test_lower)
        return min(matches / 3, 1.0)
    
    def _check_access_controls(self, test_case: str) -> float:
        """Check access control requirements"""
        keywords = ['access', 'permission', 'authorize', 'authenticate', 'role', 'user']
        test_lower = test_case.lower()
        matches = sum(1 for keyword in keywords if keyword in test_lower)
        return min(matches / 3, 1.0)
    
    def _check_retention_policies(self, test_case: str) -> float:
        """Check data retention requirements"""
        keywords = ['retention', 'delete', 'archive', 'expire', 'purge', 'lifecycle']
        test_lower = test_case.lower()
        matches = sum(1 for keyword in keywords if keyword in test_lower)
        return min(matches / 2, 1.0)
    
    def _identify_regulatory_section(self, regulatory_context: List[str]) -> str:
        """Identify which regulatory section applies"""
        if not regulatory_context:
            return "No regulatory context provided"
        
        # Look for section identifiers with better parsing
        for context in regulatory_context:
            if not context or len(context.strip()) < 5:
                continue
                
            # Look for section patterns
            lines = context.split('\n')
            for line in lines:
                line = line.strip()
                if len(line) < 5:
                    continue
                    
                # Check for section patterns
                if any(pattern in line.lower() for pattern in ['section', 'article', 'clause', 'requirement']):
                    # Clean and return meaningful section
                    clean_line = ' '.join(line.split()[:10])  # First 10 words
                    if len(clean_line) > 10:
                        return clean_line
        
        # Fallback to first meaningful content
        for context in regulatory_context:
            if context and len(context.strip()) > 20:
                # Get first sentence or meaningful chunk
                sentences = context.strip().split('.')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if len(sentence) > 20 and len(sentence) < 100:
                        return sentence
        
        return "Regulatory compliance requirements"