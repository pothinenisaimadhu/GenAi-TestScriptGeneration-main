import asyncio
import json
import time
import logging
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
try:
    from . import tools
except ImportError:
    import tools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentResult:
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None

class DocumentParserAgent:
    """Multi-format document parser with intelligent requirement extraction"""
    
    def __init__(self):
        self.name = "DocumentParserAgent"
        self.supported_formats = [".pdf", ".txt", ".docx", ".xml", ".md", ".html", ".json", ".yaml", ".yml"]
    
    async def parse_document(self, raw_text: str = None, document_path: str = None) -> AgentResult:
        """Parse multi-format documents and convert to test cases and datasets"""
        try:
            if not raw_text and not document_path:
                return AgentResult(success=False, data=[], error="No input provided")
            
            # Multi-format parsing
            if document_path:
                raw_text = await self._parse_by_format(document_path)
            
            if not raw_text or not raw_text.strip():
                return AgentResult(success=False, data=[], error="No content extracted")
            
            # Validate content length
            if len(raw_text.strip()) < 10:
                return AgentResult(success=False, data=[], error="Content too short to process")
            
            # Extract requirements
            requirements = await self._extract_requirements_multi_strategy(raw_text)
            
            if not requirements:
                return AgentResult(success=False, data=[], error="No requirements extracted")
            
            # Convert to test artifacts
            test_artifacts = await self._convert_to_test_artifacts(requirements)
            
            logger.info(f"Successfully processed document: {len(requirements)} requirements, {len(test_artifacts.get('test_cases', []))} test cases")
            
            return AgentResult(
                success=True,
                data=test_artifacts,
                metadata={
                    "total_requirements": len(requirements),
                    "test_cases_generated": len(test_artifacts.get('test_cases', [])),
                    "datasets_created": len(test_artifacts.get('datasets', []))
                }
            )
        except Exception as e:
            logger.error(f"Document parsing failed: {e}")
            return AgentResult(success=False, data=[], error=str(e))
    
    async def _parse_by_format(self, file_path: str) -> str:
        """Parse document based on file format"""
        if not file_path or not isinstance(file_path, str):
            raise ValueError("Invalid file path")
        
        # Validate and sanitize file path to prevent path traversal
        file_path = self._validate_file_path(file_path)
        
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Additional security check after resolution
        if not self._is_safe_path(file_path):
            raise ValueError(f"Unsafe file path detected: {file_path}")
        
        file_ext = file_path.suffix.lower()
        
        # Run parsing in executor to avoid blocking
        loop = asyncio.get_event_loop()
        
        try:
            if file_ext == ".pdf":
                return await loop.run_in_executor(None, self._parse_pdf, str(file_path))
            elif file_ext == ".docx":
                return await loop.run_in_executor(None, self._parse_docx, str(file_path))
            elif file_ext == ".xml":
                return await loop.run_in_executor(None, self._parse_xml, str(file_path))
            elif file_ext in [".md", ".markdown"]:
                return await loop.run_in_executor(None, self._parse_markdown, str(file_path))
            elif file_ext in [".html", ".htm"]:
                return await loop.run_in_executor(None, self._parse_html, str(file_path))
            elif file_ext == ".json":
                return await loop.run_in_executor(None, self._parse_json, str(file_path))
            elif file_ext in [".yaml", ".yml"]:
                return await loop.run_in_executor(None, self._parse_yaml, str(file_path))
            else:
                return await loop.run_in_executor(None, self._parse_text, str(file_path))
        except Exception as e:
            logger.error(f"Document parsing failed for {file_path}: {e}")
            raise
    
    def _parse_pdf(self, file_path: str) -> str:
        try:
            import fitz
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            with fitz.open(file_path) as doc:
                return "".join(page.get_text() for page in doc)
        except ImportError:
            logger.error("PyMuPDF not installed. Install with: pip install PyMuPDF")
            raise
        except Exception as e:
            logger.error(f"PDF parsing failed: {e}")
            raise
    
    def _parse_docx(self, file_path: str) -> str:
        try:
            from docx import Document
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except ImportError:
            logger.error("python-docx not installed. Install with: pip install python-docx")
            raise
        except Exception as e:
            logger.error(f"DOCX parsing failed: {e}")
            raise
    
    def _parse_xml(self, file_path: str) -> str:
        try:
            import xml.etree.ElementTree as ET
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            tree = ET.parse(file_path)
            return "\n".join([elem.text for elem in tree.iter() if elem.text and elem.text.strip()])
        except ET.ParseError as e:
            logger.error(f"XML parsing failed: {e}")
            raise
        except Exception as e:
            logger.error(f"XML processing failed: {e}")
            raise
    
    def _parse_markdown(self, file_path: str) -> str:
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            import re
            content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
            content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
            return content
        except Exception as e:
            logger.error(f"Markdown parsing failed: {e}")
            raise
    
    def _parse_html(self, file_path: str) -> str:
        try:
            from bs4 import BeautifulSoup
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            return soup.get_text(separator='\n', strip=True)
        except ImportError:
            logger.error("BeautifulSoup not installed. Install with: pip install beautifulsoup4")
            raise
        except Exception as e:
            logger.error(f"HTML parsing failed: {e}")
            raise
    
    def _parse_json(self, file_path: str) -> str:
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self._extract_text_from_json(data)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            raise
        except Exception as e:
            logger.error(f"JSON processing failed: {e}")
            raise
    
    def _parse_yaml(self, file_path: str) -> str:
        try:
            import yaml
            # Validate file path before opening
            safe_path = Path(file_path).resolve()
            if not self._is_safe_path(safe_path):
                raise ValueError(f"Unsafe file path: {file_path}")
            with open(safe_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return self._extract_text_from_json(data)
        except ImportError:
            logger.error("PyYAML not installed. Install with: pip install PyYAML")
            raise
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing failed: {e}")
            raise
        except Exception as e:
            logger.error(f"YAML processing failed: {e}")
            raise
    
    def _parse_text(self, file_path: str) -> str:
        try:
            # Validate file path before opening
            safe_path = Path(file_path).resolve()
            if not self._is_safe_path(safe_path):
                raise ValueError(f"Unsafe file path: {file_path}")
            with open(safe_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Text file parsing failed: {e}")
            raise
    
    ALLOWED_DIRS = ['temp', 'documents', 'orchestrator']
    
    def _validate_file_path(self, file_path: str) -> str:
        """Validate and sanitize file path to prevent path traversal."""
        # Remove null bytes and normalize path separators
        file_path = file_path.replace('\0', '').replace('\\', '/').strip()
        
        # Check for path traversal patterns
        if '..' in file_path or file_path.startswith('/'):
            raise ValueError("Path traversal detected in file path")
        
        # Only allow relative paths in current directory or subdirectories
        if os.path.isabs(file_path):
            # For absolute paths, ensure they're in allowed directories
            cwd = Path.cwd()
            allowed_dirs = [cwd] + [cwd / dirname for dirname in self.ALLOWED_DIRS]
            if not any(file_path.startswith(str(allowed_dir)) for allowed_dir in allowed_dirs):
                raise ValueError("Absolute path not in allowed directories")
        
        return file_path
    
    def _is_safe_path(self, resolved_path: Path) -> bool:
        """Check if resolved path is safe after resolution."""
        try:
            # Get current working directory
            cwd = Path.cwd().resolve()
            
            # Ensure the resolved path is within allowed directories
            allowed_dirs = [cwd] + [cwd / dirname for dirname in self.ALLOWED_DIRS]
            
            return any(resolved_path.is_relative_to(allowed_dir) for allowed_dir in allowed_dirs)
        except (OSError, ValueError):
            return False
    
    def _extract_text_from_json(self, data, prefix="") -> str:
        text_parts = []
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    text_parts.append(f"{key}: {value}")
                elif isinstance(value, (dict, list)):
                    text_parts.append(self._extract_text_from_json(value, f"{key}."))
        elif isinstance(data, list):
            for item in data:
                text_parts.append(self._extract_text_from_json(item))
        else:
            text_parts.append(str(data))
        return "\n".join(filter(None, text_parts))
    
    async def _extract_requirements_multi_strategy(self, raw_text: str) -> List[Dict]:
        """Extract requirements using multiple strategies"""
        lines = [line.strip() for line in raw_text.strip().split('\n') if line.strip()]
        doc_type = self._detect_document_type(raw_text)
        
        if doc_type == "csv":
            return self._parse_csv_format(lines)
        elif doc_type == "structured":
            return self._parse_structured_format(lines)
        else:
            return self._parse_free_text(raw_text)
    
    async def _convert_to_test_artifacts(self, requirements: List[Dict]) -> Dict[str, Any]:
        """Convert requirements to test cases and datasets"""
        return {
            "requirements": requirements,
            "test_cases": [],
            "datasets": []
        }
    

    
    def _detect_document_type(self, text: str) -> str:
        if "requirement" in text.lower() and ("," in text or "|" in text):
            return "csv"
        elif any(marker in text for marker in ["REQ-", "R-", "1.", "2."]):
            return "structured"
        return "free_text"
    
    def _parse_csv_format(self, lines: List[str]) -> List[Dict]:
        import csv
        import io
        
        header_idx = next((i for i, line in enumerate(lines) 
                          if "requirement" in line.lower()), 0)
        
        csv_data = '\n'.join(lines[header_idx:])
        reader = csv.DictReader(io.StringIO(csv_data))
        return [row for row in reader if row.get("Requirement")]
    
    def _parse_structured_format(self, lines: List[str]) -> List[Dict]:
        requirements = []
        current_req = ""
        
        for line in lines:
            if any(line.startswith(prefix) for prefix in ["REQ-", "R-"]) or \
               (line and line[0].isdigit() and "." in line[:5]):
                if current_req:
                    requirements.append({"Requirement": current_req.strip()})
                current_req = line
            else:
                current_req += " " + line
        
        if current_req:
            requirements.append({"Requirement": current_req.strip()})
        
        return requirements
    
    def _parse_free_text(self, text: str) -> List[Dict]:
        # Split by sentences and filter meaningful requirements
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        return [{"Requirement": sent} for sent in sentences[:5]]

class TestCaseGeneratorAgent:
    """Dedicated agent for test case generation with regulatory validation"""
    
    def __init__(self):
        self.name = "TestCaseGeneratorAgent"
        from regulatory_validator import RegulatoryValidator
        self.validator = RegulatoryValidator()
    
    async def generate_validated_test_case(self, requirement: str, regulatory_context: List[str]) -> AgentResult:
        """Generate test case and iteratively improve based on regulatory validation"""
        try:
            max_iterations = 3
            iteration = 0
            
            # Generate initial test case
            test_case = self._generate_basic_test_case(requirement)
            
            while iteration < max_iterations:
                iteration += 1
                logger.info(f"Validation iteration {iteration}/{max_iterations}")
                
                # Validate against regulatory requirements
                compliance_check = await self.validator.validate_test_case_compliance(
                    test_case=test_case,
                    requirement=requirement,
                    regulatory_context=regulatory_context
                )
                
                logger.info(f"Iteration {iteration}: Score={compliance_check.compliance_score:.2f}, Passed={compliance_check.validation_passed}")
                
                # If validation passes, return success
                if compliance_check.validation_passed:
                    logger.info(f"Compliance validation passed on iteration {iteration}")
                    return AgentResult(
                        success=True,
                        data={
                            'test_case': test_case,
                            'compliance_validation': {
                                'passed': True,
                                'score': compliance_check.compliance_score,
                                'missing_elements': compliance_check.missing_elements,
                                'regulatory_section': compliance_check.regulatory_section,
                                'iterations': iteration
                            }
                        },
                        metadata={'compliance_validated': True, 'iterations': iteration}
                    )
                
                # If max iterations reached, return with failure
                if iteration >= max_iterations:
                    logger.warning(f"Max iterations ({max_iterations}) reached, compliance still failing")
                    return AgentResult(
                        success=True,
                        data={
                            'test_case': test_case,
                            'compliance_validation': {
                                'passed': False,
                                'score': compliance_check.compliance_score,
                                'missing_elements': compliance_check.missing_elements,
                                'regulatory_section': compliance_check.regulatory_section,
                                'iterations': iteration
                            }
                        },
                        metadata={'compliance_validated': True, 'max_iterations_reached': True}
                    )
                
                # Enhance test case for next iteration with detailed feedback
                logger.info(f"ITERATION {iteration} ENHANCEMENT:")
                logger.info(f"  Current Score: {compliance_check.compliance_score:.2f}")
                logger.info(f"  Missing Elements: {compliance_check.missing_elements}")
                logger.info(f"  Regulatory Section: {compliance_check.regulatory_section}")
                
                test_case = self._enhance_test_case_for_compliance(
                    test_case, compliance_check.missing_elements
                )
                
                logger.info(f"  Enhancement Applied: Added {len(compliance_check.missing_elements)} compliance areas")
            
            # Fallback return (should not reach here)
            return AgentResult(
                success=False,
                error="Unexpected end of validation loop"
            )
        except Exception as e:
            logger.error(f"Validated test case generation failed: {e}")
            return AgentResult(success=False, error=str(e))
    
    def _generate_basic_test_case(self, requirement: str) -> str:
        """Generate test case using LLM"""
        prompt = f"""Generate a comprehensive test case for this requirement:

Requirement: {requirement}

Generate a structured test case with:
- Clear test case title
- Specific objective
- Detailed step-by-step procedures
- Expected results
- Validation criteria

Format as a professional test case."""
        
        try:
            import tools
            if hasattr(tools, 'call_ai_generator'):
                result = tools.call_ai_generator(prompt, 600)
                if result and len(result.strip()) > 50:
                    return result
        except Exception as e:
            logger.warning(f"LLM test case generation failed: {e}")
        
        # Fallback template
        return f"""TEST CASE: {requirement[:50]}...
OBJECTIVE: Verify requirement compliance
STEPS:
1. Setup test environment
2. Execute requirement validation
3. Verify expected outcomes
EXPECTED: Requirement satisfied"""
    
    def _enhance_test_case_for_compliance(self, test_case: str, missing_elements: List[str]) -> str:
        """Enhance test case using LLM based on missing compliance elements"""
        if not missing_elements:
            return test_case
        
        logger.info(f"ENHANCEMENT FEEDBACK: Missing compliance elements: {missing_elements}")
        
        prompt = f"""Enhance this test case to address missing regulatory compliance elements:

Current Test Case:
{test_case}

Missing Compliance Elements:
{', '.join(missing_elements)}

Enhance the test case by:
1. Adding specific test steps for each missing compliance element
2. Including validation criteria for regulatory requirements
3. Maintaining the original test structure
4. Adding compliance verification steps

Generate the enhanced test case:"""
        
        try:
            import tools
            if hasattr(tools, 'call_ai_generator'):
                result = tools.call_ai_generator(prompt, 800)
                if result and len(result.strip()) > len(test_case):
                    return result
        except Exception as e:
            logger.warning(f"LLM enhancement failed: {e}")
        
        # Fallback to template enhancement
        return self._template_enhance_test_case(test_case, missing_elements)
    
    def _template_enhance_test_case(self, test_case: str, missing_elements: List[str]) -> str:
        """Template-based enhancement as fallback"""
        enhancements = []
        for element in missing_elements:
            if 'audit' in element:
                enhancements.append("- Verify audit trail generation and logging")
            elif 'retention' in element:
                enhancements.append("- Validate data retention and deletion policies")
            elif 'access' in element:
                enhancements.append("- Test access control and authorization")
            elif 'encrypt' in element:
                enhancements.append("- Verify data encryption requirements")
        
        if enhancements:
            enhanced_steps = '\n'.join(enhancements)
            return f"{test_case}\n\nCOMPLIANCE STEPS:\n{enhanced_steps}"
        return test_case

class FeedbackLoopAgent:
    """Agent for processing user feedback and improving quality"""
    
    def __init__(self):
        self.name = "FeedbackLoopAgent"
    
    async def process_feedback(self, testcase_id: str, feedback_data: Dict[str, Any]) -> AgentResult:
        """Process user feedback using LLM analysis"""
        try:
            prompt = f"""Analyze this user feedback and generate improvement recommendations:

Test Case ID: {testcase_id}
User Rating: {feedback_data.get('rating', 'Not provided')}
User Comments: {feedback_data.get('improvement', 'No comments')}
Feedback Data: {feedback_data}

Generate:
1. Quality assessment
2. Specific improvement areas
3. Actionable recommendations

Provide structured analysis:"""
            
            try:
                import tools
                if hasattr(tools, 'call_ai_generator'):
                    analysis = tools.call_ai_generator(prompt, 400)
                    if analysis:
                        return AgentResult(
                            success=True,
                            data={'llm_analysis': analysis, 'rating': feedback_data.get('rating', 3)},
                            metadata={'processed': True, 'method': 'llm'}
                        )
            except Exception as e:
                logger.warning(f"LLM feedback analysis failed: {e}")
            
            # Fallback analysis
            corrections = {}
            rating = feedback_data.get('rating', 3)
            if rating < 3:
                corrections['quality_issue'] = 'Low rating detected'
            if feedback_data.get('improvement'):
                corrections['user_suggestion'] = feedback_data['improvement']
            
            return AgentResult(
                success=True,
                data=corrections,
                metadata={'rating': rating, 'processed': True, 'method': 'template'}
            )
        except Exception as e:
            return AgentResult(success=False, error=str(e))

class ComplianceValidationAgent:
    """Agent for regulatory compliance validation"""
    
    def __init__(self):
        self.name = "ComplianceValidationAgent"
        from regulatory_validator import RegulatoryValidator
        self.validator = RegulatoryValidator()
    
    async def validate_compliance(self, requirement: str, regulatory_context: List[str]) -> AgentResult:
        """Validate requirement against regulatory standards"""
        try:
            # Use dedicated regulatory validator
            compliance_check = await self.validator.validate_test_case_compliance(
                test_case="",  # Will be filled during test case generation
                requirement=requirement,
                regulatory_context=regulatory_context
            )
            
            validation_result = {
                'compliance_score': compliance_check.compliance_score,
                'regulatory_section': compliance_check.regulatory_section,
                'missing_elements': compliance_check.missing_elements,
                'validation_passed': compliance_check.validation_passed,
                'regulatory_context': regulatory_context[:2],
                'validated': True
            }
            
            return AgentResult(
                success=True,
                data=validation_result,
                metadata={'score': compliance_check.compliance_score, 'passed': compliance_check.validation_passed}
            )
        except Exception as e:
            logger.error(f"Compliance validation failed: {e}")
            return AgentResult(success=False, error=str(e))
    
    async def validate_generated_test_case(self, test_case: str, requirement: str, 
                                         regulatory_context: List[str]) -> AgentResult:
        """Validate generated test case against regulatory requirements"""
        try:
            compliance_check = await self.validator.validate_test_case_compliance(
                test_case=test_case,
                requirement=requirement,
                regulatory_context=regulatory_context
            )
            
            return AgentResult(
                success=True,
                data={
                    'compliance_passed': compliance_check.validation_passed,
                    'compliance_score': compliance_check.compliance_score,
                    'missing_elements': compliance_check.missing_elements,
                    'regulatory_section': compliance_check.regulatory_section,
                    'requirement_id': compliance_check.requirement_id
                },
                metadata={'validation_complete': True}
            )
        except Exception as e:
            logger.error(f"Test case compliance validation failed: {e}")
            return AgentResult(success=False, error=str(e))

class PerformanceMonitorAgent:
    """Agent for monitoring system performance and quality metrics"""
    
    def __init__(self):
        self.name = "PerformanceMonitorAgent"
        self.metrics = {'total_processed': 0, 'success_count': 0}
    
    async def track_performance(self, operation_result: Dict[str, Any]) -> AgentResult:
        """Track and analyze performance metrics"""
        try:
            self.metrics['total_processed'] += 1
            if operation_result.get('success'):
                self.metrics['success_count'] += 1
            
            success_rate = self.metrics['success_count'] / self.metrics['total_processed']
            quality_score = operation_result.get('quality_score', success_rate)
            
            performance_data = {
                'success_rate': success_rate,
                'quality_score': quality_score,
                'total_processed': self.metrics['total_processed'],
                'retraining_needed': quality_score < 0.7
            }
            
            return AgentResult(
                success=True,
                data=performance_data,
                metadata=self.metrics
            )
        except Exception as e:
            return AgentResult(success=False, error=str(e))

class CoordinatorAgent:
    """Agent for coordinating workflow and task decomposition"""
    
    def __init__(self):
        self.name = "CoordinatorAgent"
    
    async def coordinate_workflow(self, requirement: str) -> AgentResult:
        """Break down requirements into coordinated tasks"""
        try:
            tasks = []
            req_lower = requirement.lower()
            
            # Basic task decomposition
            tasks.append('parse_requirement')
            tasks.append('generate_test_case')
            
            if 'security' in req_lower:
                tasks.append('security_validation')
            if 'compliance' in req_lower:
                tasks.append('compliance_check')
            if 'performance' in req_lower:
                tasks.append('performance_test')
            
            tasks.append('quality_review')
            
            coordination_result = {
                'tasks': tasks,
                'priority': 'high' if len(tasks) > 4 else 'medium',
                'estimated_time': len(tasks) * 30,
                'coordinated': True
            }
            
            return AgentResult(
                success=True,
                data=coordination_result,
                metadata={'task_count': len(tasks)}
            )
        except Exception as e:
            return AgentResult(success=False, error=str(e))
    
    async def generate_test_case(self, requirement: str, context: List[str], 
                               tasks: List[str]) -> AgentResult:
        """Generate comprehensive test case with multiple approaches"""
        try:
            # Generate multiple test case variants
            variants = await asyncio.gather(
                self._generate_functional_test(requirement, context),
                self._generate_compliance_test(requirement, context),
                self._generate_security_test(requirement, context)
            )
            
            # Select best variant or combine
            best_test = self._select_best_test_case(variants, tasks)
            
            # Validate against regulatory requirements
            from regulatory_validator import RegulatoryValidator
            validator = RegulatoryValidator()
            compliance_check = await validator.validate_test_case_compliance(
                test_case=best_test,
                requirement=requirement,
                regulatory_context=context
            )
            
            # Add compliance validation results
            test_result = {
                'test_case': best_test,
                'compliance_validation': {
                    'passed': compliance_check.validation_passed,
                    'score': compliance_check.compliance_score,
                    'missing_elements': compliance_check.missing_elements,
                    'regulatory_section': compliance_check.regulatory_section
                }
            }
            
            return AgentResult(
                success=True,
                data=test_result,
                metadata={
                    "variants_generated": len(variants), 
                    "tasks_covered": len(tasks),
                    "compliance_validated": True,
                    "compliance_passed": compliance_check.validation_passed
                }
            )
        except Exception as e:
            logger.error(f"Test case generation with validation failed: {e}")
            return AgentResult(success=False, data="", error=str(e))
    
    async def _generate_functional_test(self, requirement: str, context: List[str]) -> str:
        prompt = f"""Generate functional test case for: {requirement}
Context: {' '.join(context[:2])}
Focus on: functionality, user scenarios, expected behavior"""
        
        return await self._call_ai_generator(prompt, "functional")
    
    async def _generate_compliance_test(self, requirement: str, context: List[str]) -> str:
        prompt = f"""Generate compliance test case for: {requirement}
Regulatory context: {' '.join(context)}
Focus on: regulatory compliance, standards adherence, audit trails"""
        
        return await self._call_ai_generator(prompt, "compliance")
    
    async def _generate_security_test(self, requirement: str, context: List[str]) -> str:
        prompt = f"""Generate security test case for: {requirement}
Context: {' '.join(context[:2])}
Focus on: security controls, data protection, access validation"""
        
        return await self._call_ai_generator(prompt, "security")
    
    async def _call_ai_generator(self, prompt: str, test_type: str) -> str:
        """Call AI generator with proper error handling and fallback"""
        if not prompt or not prompt.strip():
            logger.warning(f"Empty prompt for {test_type}, using fallback")
            return self._generate_fallback_test(prompt, test_type)
        
        loop = asyncio.get_event_loop()
        
        try:
            if hasattr(tools, 'get_text_generator') and tools.get_text_generator():
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, tools.call_ai_generator, prompt, 300),
                    timeout=30.0
                )
                if result and len(result.strip()) > 10:
                    logger.info(f"AI generation successful for {test_type}")
                    return result
                else:
                    logger.warning(f"AI generation returned insufficient content for {test_type}")
            else:
                logger.warning(f"AI generator not available for {test_type}")
        except asyncio.TimeoutError:
            logger.warning(f"AI generation timed out for {test_type}, using fallback")
        except Exception as e:
            logger.error(f"AI generation failed for {test_type}: {e}")
        
        return self._generate_fallback_test(prompt, test_type)
    
    def _generate_fallback_test(self, prompt: str, test_type: str) -> str:
        """Generate fallback test using LLM with simplified prompt"""
        req_text = prompt.split("for: ")[1].split("\n")[0] if "for: " in prompt else "requirement"
        
        fallback_prompt = f"""Generate a {test_type} test case for: {req_text}

Include:
- Test objective
- Step-by-step procedures
- Expected results

Keep it concise and professional."""
        
        try:
            import tools
            if hasattr(tools, 'call_ai_generator'):
                result = tools.call_ai_generator(fallback_prompt, 300)
                if result and len(result.strip()) > 50:
                    return result
        except Exception as e:
            logger.warning(f"Fallback LLM generation failed: {e}")
        
        # Final template fallback
        return f"""TEST CASE: {test_type.title()} - {req_text[:50]}
OBJECTIVE: Verify {test_type} requirements
STEPS:
1. Setup test environment
2. Execute {test_type} validation
3. Verify expected outcomes
EXPECTED: {test_type.title()} requirements satisfied"""
    
    def _select_best_test_case(self, variants: List[str], tasks: List[str]) -> str:
        """Select best test case variant with improved scoring"""
        if not variants:
            return "No test case variants generated"
        
        # Filter out empty variants
        valid_variants = [v for v in variants if v and v.strip()]
        if not valid_variants:
            return "No valid test case variants"
        
        scored_variants = []
        
        for variant in valid_variants:
            score = 0
            
            # Quality indicators
            if "STEPS:" in variant:
                score += 50
            if "EXPECTED:" in variant:
                score += 30
            if "OBJECTIVE:" in variant:
                score += 20
            
            # Length bonus (but cap it)
            score += min(len(variant) // 10, 100)
            
            # Task coverage bonus
            for task in tasks:
                task_words = task.lower().split()[:3]
                if any(word in variant.lower() for word in task_words if len(word) > 2):
                    score += 75
            
            scored_variants.append((score, variant))
        
        # Return highest scoring variant
        best_variant = max(scored_variants, key=lambda x: x[0])[1]
        logger.info(f"Selected test case variant with score: {max(scored_variants, key=lambda x: x[0])[0]}")
        return best_variant

