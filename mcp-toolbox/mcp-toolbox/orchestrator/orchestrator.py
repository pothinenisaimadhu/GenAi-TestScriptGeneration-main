import asyncio
import os
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from agents import (
    DocumentParserAgent, TestCaseGeneratorAgent, FeedbackLoopAgent, 
    ComplianceValidationAgent, PerformanceMonitorAgent, CoordinatorAgent, AgentResult
)
import tools
from performance_optimizer import performance_optimizer, resource_manager, circuit_breaker
from config import QUALITY_THRESHOLDS, VALIDATION_RULES
from utils import validate_input, retry_async, safe_execute, logger, validate_env_vars, safe_file_read
from health_check import check_system_health

@dataclass
class WorkflowState:
    """Maintains state across workflow execution"""
    requirements: Optional[List[Dict]] = None
    current_requirement: Optional[Dict] = None
    rag_context: Optional[List[str]] = None
    test_case: Optional[str] = None
    feedback_metrics: Optional[Dict] = None
    performance_data: Optional[Dict] = None

class WorkflowOrchestrator:
    """Complex multi-agent workflow orchestrator with parallel processing"""
    
    def __init__(self):
        # Validate environment first
        validate_env_vars()
        
        # Check system health
        health = check_system_health()
        if health["overall"] == "unhealthy":
            logger.warning(f"System health degraded: {health}")
        
        # Initialize all 5 agents
        self.document_parser = DocumentParserAgent()
        self.test_generator = TestCaseGeneratorAgent()
        self.feedback_loop = FeedbackLoopAgent()
        self.compliance_validator = ComplianceValidationAgent()
        self.performance_monitor = PerformanceMonitorAgent()
        self.coordinator = CoordinatorAgent()
        
        # Workflow state
        self.state = WorkflowState()
        
        # Performance tracking
        self.workflow_metrics = {
            "total_processed": 0,
            "success_rate": 0.0,
            "avg_processing_time": 0.0
        }
    
    async def execute_workflow(self, raw_text: str, regulatory_doc_path: str) -> Dict[str, Any]:
        """Execute complete multi-agent workflow with performance optimization"""
        workflow_id = performance_optimizer.start_operation("complete_workflow")
        workflow_results = {
            "success": False,
            "processed_requirements": 0,
            "test_cases_generated": 0,
            "feedback_processed": 0,
            "performance_metrics": {},
            "errors": []
        }
        
        try:
            workflow_start_time = time.time()
            print("=== Starting Multi-Agent Workflow Orchestration ===")
            
            # Phase 1: Parallel Knowledge Base + Document Parsing
            kb_task = asyncio.create_task(self._build_knowledge_base(regulatory_doc_path))
            parse_task = asyncio.create_task(self._parse_requirements(raw_text))
            
            kb_result, parse_result = await asyncio.gather(kb_task, parse_task)
            
            if not parse_result.success:
                workflow_results["errors"].append(f"Document parsing failed: {parse_result.error}")
                return workflow_results
            
            self.state.requirements = parse_result.data
            print(f"INFO: Parsed {len(self.state.requirements)} requirements")
            
            # Phase 2: Multi-Agent Processing Pipeline
            processed_results = []
            
            # Step 2a: Coordinator agent breaks down workflow
            enhanced_requirements = []
            for i, req_data in enumerate(self.state.requirements, 1):
                print(f"INFO: Processing requirement {i}/{len(self.state.requirements)} with 5-agent pipeline")
                # Handle both string and dict types
                if isinstance(req_data, str):
                    requirement_text = req_data
                    req_data = {"Requirement": req_data}
                else:
                    requirement_text = req_data.get("Requirement", "")
                
                if len(requirement_text.split()) >= VALIDATION_RULES["MIN_REQUIREMENT_WORDS"] and validate_input(requirement_text):
                    # Multi-agent processing pipeline with error handling
                    try:
                        coord_result = await self.coordinator.coordinate_workflow(requirement_text)
                        intelligent_result = await self._async_intelligent_analysis(requirement_text)
                        compliance_result = await self.compliance_validator.validate_compliance(requirement_text, [])
                        
                        enhanced_requirements.append({
                            "original_data": req_data,
                            "intelligent_result": intelligent_result,
                            "coordination": coord_result.data if coord_result.success else {},
                            "compliance": compliance_result.data if compliance_result.success else {}
                        })
                    except Exception as e:
                        logger.error(f"Agent processing failed for requirement {i}: {e}")
                        enhanced_requirements.append({
                            "original_data": req_data,
                            "intelligent_result": {"enhanced_requirement": requirement_text, "analysis": {}},
                            "coordination": {},
                            "compliance": {}
                        })
                else:
                    enhanced_requirements.append({
                        "original_data": req_data,
                        "intelligent_result": {"enhanced_requirement": requirement_text, "analysis": {}},
                        "coordination": {},
                        "compliance": {}
                    })
            
            # Step 2b: Sequential test case generation (after all questioning is complete)
            if enhanced_requirements:
                print(f"INFO: Starting test case generation for {len(enhanced_requirements)} requirements")
                
                for i, enhanced_req in enumerate(enhanced_requirements, 1):
                    print(f"INFO: Generating test case {i}/{len(enhanced_requirements)}")
                    try:
                        result = await self._generate_test_case_parallel(enhanced_req)
                        processed_results.append(result)
                    except Exception as e:
                        print(f"WARNING: Test case generation {i} failed: {e}")
                        processed_results.append({"success": False, "error": str(e)})
            
            # Phase 3: Aggregate Results and Feedback Processing
            successful_results = [r for r in processed_results if isinstance(r, dict) and r.get("success")]
            workflow_results["processed_requirements"] = len(enhanced_requirements)
            workflow_results["test_cases_generated"] = len(successful_results)
            workflow_results["successful_results"] = successful_results
            
            # Phase 4: Performance Monitoring and Results Summary
            # Use performance monitor agent
            perf_result = await self.performance_monitor.track_performance({
                'success': True,
                'quality_score': len(successful_results) / len(enhanced_requirements) if enhanced_requirements else 0
            })
            
            perf_data = perf_result.data if perf_result.success else {}
            perf_summary = performance_optimizer.get_performance_summary()
            
            # Calculate real performance metrics
            total_requirements = len(enhanced_requirements)
            success_rate = len(successful_results) / total_requirements if total_requirements > 0 else 0
            
            # Real quality score based on actual success rate and user responses
            user_response_quality = sum(1 for r in successful_results if r.get("user_responses")) / len(successful_results) if successful_results else 0
            quality_score = (success_rate * 0.7) + (user_response_quality * 0.3)
            
            workflow_results["performance_metrics"] = {
                "quality_score": round(quality_score, 2),
                "success_rate": round(success_rate, 2),
                "feedback_rate": round(user_response_quality, 2),
                "retraining_needed": quality_score < QUALITY_THRESHOLDS["MEDIUM"],
                **perf_summary
            }
            
            processing_time = perf_summary.get("total_duration", 0)
            if processing_time == 0:
                processing_time = time.time() - workflow_start_time
            
            self._update_workflow_metrics(len(successful_results), processing_time)
            
            workflow_results["success"] = True
            workflow_results["processing_time"] = processing_time
            workflow_results["workflow_id"] = workflow_id
            
            performance_optimizer.end_operation(workflow_id, success=True)
            print(f"SUCCESS: Workflow completed successfully in {processing_time:.2f}s")
            print(f"INFO: Operations: {perf_summary.get('total_operations', 0)} total, {perf_summary.get('success_rate', 0):.1%} success rate")
            
            # Collect post-completion feedback
            try:
                from post_completion_feedback import post_completion_feedback
                print(f"\n🎯 COLLECTING POST-COMPLETION FEEDBACK...")
                completion_feedback = post_completion_feedback.collect_workflow_feedback(workflow_results)
                workflow_results["completion_feedback"] = completion_feedback
            except ImportError:
                logger.warning("Post-completion feedback not available")
            except Exception as e:
                logger.error(f"Error collecting post-completion feedback: {e}")
                workflow_results["feedback_error"] = str(e)
            
        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            workflow_results["errors"].append(error_msg)
            performance_optimizer.end_operation(workflow_id, success=False, error=str(e))
            logger.error(error_msg, exc_info=True)
        
        return workflow_results
    
    async def _build_knowledge_base(self, regulatory_doc_path: str) -> AgentResult:
        """Build knowledge base in parallel"""
        try:
            print("INFO: Building knowledge base...")
            
            # Read and process regulatory document
            try:
                reg_text = safe_file_read(regulatory_doc_path)
            except Exception as e:
                logger.warning(f"Could not read regulatory document: {e}")
                # Use fallback regulatory content
                reg_text = self._get_fallback_regulatory_content()
            
            logger.info(f"Processing {len(reg_text)} characters of regulatory content")
            
            # Parallel chunking and embedding
            chunk_task = asyncio.create_task(self._async_chunk_text(reg_text))
            chunks = await chunk_task
            
            logger.info(f"Created {len(chunks)} text chunks")
            
            if chunks:
                embed_task = asyncio.create_task(self._async_create_embeddings(chunks))
                vectors = await embed_task
                
                logger.info(f"Generated {len(vectors)} embedding vectors")
                
                if vectors:
                    store_task = asyncio.create_task(self._async_vector_store(vectors, chunks))
                    result = await store_task
                    logger.info(f"Vector storage result: {result}")
                else:
                    logger.warning("No vectors generated")
            else:
                logger.warning("No chunks created")
            
            return AgentResult(success=True, data="Knowledge base built successfully")
        except Exception as e:
            logger.error(f"Knowledge base building failed: {e}", exc_info=True)
            return AgentResult(success=False, error=str(e))
    
    def _get_fallback_regulatory_content(self) -> str:
        """Read regulatory content from PDF file"""
        try:
            import fitz  # PyMuPDF
            with fitz.open("regulatory_doc.pdf") as doc:
                text = "".join(page.get_text() for page in doc)
            return text if text.strip() else "No regulatory content available"
        except Exception:
            return "No regulatory content available"
    
    async def _parse_requirements(self, raw_text: str) -> AgentResult:
        """Parse requirements using dedicated agent"""
        return await self.document_parser.parse_document(raw_text)
    

    

    
    # Generic async wrapper to reduce code duplication
    async def _async_execute(self, func, *args, **kwargs):
        """Generic async wrapper for synchronous functions."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            return await loop.run_in_executor(None, func, *args, **kwargs)
        except Exception as e:
            logger.error(f"Async execution failed for {func.__name__}: {e}")
            raise
    
    # Async wrapper methods for existing tools
    async def _async_chunk_text(self, text: str) -> List[str]:
        return await self._async_execute(tools.chunk_text, text, 1000)
    
    async def _async_create_embeddings(self, chunks: List[str]) -> List[List[float]]:
        return await self._async_execute(tools.create_embeddings, chunks)
    
    async def _async_vector_store(self, vectors: List[List[float]], chunks: List[str]) -> str:
        collection_name = os.getenv("CHROMA_COLLECTION", "regulatory_docs")
        return await self._async_execute(tools.vector_store, vectors, chunks, collection_name)
    
    async def _async_intelligent_analysis(self, requirement: str) -> Dict[str, Any]:
        return await self._async_execute(tools.intelligent_requirement_analysis, requirement)
    
    @retry_async()
    async def _generate_test_case_parallel(self, enhanced_req_data: Dict) -> Dict[str, Any]:
        """Generate test case after questioning is complete"""
        try:
            req_data = enhanced_req_data["original_data"]
            intelligent_result = enhanced_req_data["intelligent_result"]
            
            requirement_text = req_data.get("Requirement", "")
            enhanced_req = intelligent_result.get("enhanced_requirement", requirement_text)
            
            print(f"INFO: Processing requirement: {requirement_text[:50]}...")
            
            # Get coordinator tasks and RAG context
            coord_task = asyncio.create_task(self._async_coordinator(enhanced_req))
            rag_task = asyncio.create_task(self._async_rag_retrieval(enhanced_req))
            
            tasks, rag_result = await asyncio.gather(coord_task, rag_task)
            
            # Generate test case with iterative regulatory validation
            print(f"INFO: Generating test case with {len(rag_result.get('chunks', []))} context chunks")
            test_case_result = await self.test_generator.generate_validated_test_case(
                enhanced_req, rag_result.get("chunks", [])
            )
            
            if not test_case_result.success:
                return {"success": False, "error": f"Test case generation failed: {test_case_result.error}"}
            
            test_case_data = test_case_result.data
            compliance_validation = test_case_data.get('compliance_validation', {})
            iterations = compliance_validation.get('iterations', 1)
            
            # Log detailed iterative compliance validation results
            if not compliance_validation.get('passed', False):
                print(f"⚠️  COMPLIANCE VALIDATION FAILED after {iterations} iterations")
                print(f"   Final Score: {compliance_validation.get('score', 0):.2f}/1.0")
                print(f"   Still Missing: {compliance_validation.get('missing_elements', [])}")
                print(f"   Regulatory Section: {compliance_validation.get('regulatory_section', 'Unknown')}")
                print(f"   ❌ Test case needs manual review for regulatory compliance")
            else:
                print(f"✅ COMPLIANCE VALIDATION PASSED after {iterations} iterations")
                print(f"   Final Score: {compliance_validation.get('score', 0):.2f}/1.0")
                print(f"   Regulatory Section: {compliance_validation.get('regulatory_section', 'Unknown')}")
                print(f"   ✓ Test case meets all regulatory requirements")
            
            if not test_case_data:
                return {"success": False, "error": "Test case generation failed"}
            
            # Create test case in ALM first
            print(f"INFO: Creating test case in Jira...")
            testcase_id = await self._async_create_testcase(test_case_data, requirement_text)
            
            # Collect user feedback on generated test case
            print(f"INFO: Collecting user feedback...")
            try:
                user_feedback = await self._async_execute(tools.collect_user_feedback, requirement_text, str(test_case_data))
                
                # Process feedback through feedback agent
                if user_feedback and isinstance(user_feedback, dict):
                    feedback_result = await self.feedback_loop.process_feedback(testcase_id or f"TC-{hash(requirement_text) % 1000}", user_feedback)
                    if feedback_result.success:
                        user_feedback.update(feedback_result.data)
            except Exception as e:
                logger.error(f"Feedback collection failed: {e}")
                user_feedback = {"error": str(e), "collected": False}
            
            # Traceability logging
            if testcase_id and not testcase_id.startswith("TC-FAILED"):
                await self._async_log_traceability(testcase_id, rag_result.get("ids", []))
            
            return {
                "success": True,
                "requirement": requirement_text,
                "enhanced_requirement": enhanced_req,
                "intelligent_analysis": intelligent_result.get("analysis", {}),
                "user_responses": intelligent_result.get("user_responses", {}),
                "user_feedback": user_feedback,
                "test_case": test_case_data.get('test_case', test_case_data),
                "compliance_validation": compliance_validation,
                "regulatory_compliance_passed": compliance_validation.get('passed', False),
                "compliance_iterations": compliance_validation.get('iterations', 1),
                "final_compliance_score": compliance_validation.get('score', 0.0),
                "remaining_missing_elements": compliance_validation.get('missing_elements', []),
                "regulatory_section_validated": compliance_validation.get('regulatory_section', 'Unknown'),
                "testcase_id": testcase_id,
                "tasks": tasks,
                "rag_chunks": len(rag_result.get("chunks", []))
            }
            
        except Exception as e:
            print(f"ERROR: Test case generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _async_coordinator(self, requirement: str) -> List[str]:
        return await self._async_execute(tools.coordinator_agent, requirement)
    
    async def _async_rag_retrieval(self, query: str) -> Dict[str, List]:
        collection_name = os.getenv("CHROMA_COLLECTION", "regulatory_docs")
        return await self._async_execute(tools.rag_retrieval, query, collection_name)
    
    async def _async_create_testcase(self, test_case_data, requirement: str) -> str:
        # Handle both string and dict test case data
        if isinstance(test_case_data, dict):
            payload = test_case_data.copy()
            if "summary" not in payload:
                payload["summary"] = f"Auto-generated TC for: {requirement[:60]}..."
        else:
            payload = {
                "summary": f"Auto-generated TC for: {requirement[:60]}...",
                "description": str(test_case_data),
                "requirement_ref": requirement
            }
        
        return await self._async_execute(tools.create_testcase, payload)
    
    async def _async_log_traceability(self, testcase_id: str, chunk_ids: List[str]) -> str:
        return await self._async_execute(tools.log_traceability, testcase_id, chunk_ids)
    
    async def _async_compliance_validation(self, requirement: str, chunks: List[str], intelligent_result: Dict) -> Dict[str, Any]:
        return await self._async_execute(tools.compliance_validation_agent, requirement, chunks, intelligent_result)
    

    
    async def _get_bigquery_feedback_data(self) -> Dict[str, Dict]:
        """Get feedback data from BigQuery"""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._query_bigquery_feedback)
        except Exception as e:
            print(f"WARNING: Could not get BigQuery feedback data: {e}")
            return {}
    
    async def _get_bigquery_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from BigQuery"""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._query_bigquery_metrics)
        except Exception as e:
            print(f"WARNING: Could not get BigQuery metrics: {e}")
            return {"total_test_cases": 0, "avg_quality_score": 0.8, "feedback_rate": 0.0}
    
    def _query_bigquery_feedback(self) -> Dict[str, Dict]:
        """Query BigQuery for feedback data"""
        try:
            from google.cloud import bigquery
            from resource_manager import get_bigquery_client
            import os
            
            dataset_id = os.getenv("BIGQUERY_DATASET")
            
            with get_bigquery_client() as client:
            
                query = f"""
                SELECT test_case_id, feedback_count, quality_score
                FROM `{os.getenv('GOOGLE_PROJECT_ID')}.{dataset_id}.traceability_log`
                WHERE feedback_count > 0
                ORDER BY created_at DESC
                LIMIT 10
                """
                
                results = client.query(query)
                feedback_data = {}
                
                for row in results:
                    feedback_data[row.test_case_id] = {
                        "quality_issues": "Low quality score detected" if row.quality_score < 0.6 else "Good quality",
                        "feedback_count": row.feedback_count
                    }
                
                return feedback_data
        except Exception as e:
            print(f"ERROR: BigQuery feedback query failed: {e}")
            return {}
    
    def _query_bigquery_metrics(self) -> Dict[str, Any]:
        """Query BigQuery for performance metrics"""
        try:
            from google.cloud import bigquery
            from google.cloud.bigquery import ScalarQueryParameter
            from resource_manager import get_bigquery_client
            import os
            
            dataset_id = os.getenv("BIGQUERY_DATASET")
            
            with get_bigquery_client() as client:
            
                if not dataset_id:
                    logger.warning("BIGQUERY_DATASET not configured")
                    return {"total_test_cases": 0, "avg_quality_score": 0.8, "feedback_rate": 0.0}
                
                project_id = os.getenv('GOOGLE_PROJECT_ID')
                if not project_id:
                    logger.warning("GOOGLE_PROJECT_ID not configured")
                    return {"total_test_cases": 0, "avg_quality_score": 0.8, "feedback_rate": 0.0}
                
                query = """
                SELECT 
                    COUNT(DISTINCT test_case_id) as total_test_cases,
                    AVG(COALESCE(quality_score, 0.8)) as avg_quality_score,
                    AVG(COALESCE(feedback_count, 0)) as avg_feedback_count,
                    COUNT(CASE WHEN feedback_count > 0 THEN 1 END) / COUNT(*) as feedback_rate
                FROM `{}.{}.traceability_log`
                WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @hours HOUR)
                """.format(project_id, dataset_id)
                
                job_config = bigquery.QueryJobConfig(
                    query_parameters=[ScalarQueryParameter("hours", "INT64", 24)]
                )
                
                results = client.query(query, job_config=job_config)
                
                for row in results:
                    return {
                        "total_test_cases": int(row.total_test_cases or 0),
                        "avg_quality_score": float(row.avg_quality_score or 0.8),
                        "feedback_rate": float(row.feedback_rate or 0.0),
                        "avg_feedback_count": float(row.avg_feedback_count or 0.0)
                    }
                
                return {"total_test_cases": 0, "avg_quality_score": 0.8, "feedback_rate": 0.0}
        except Exception as e:
            logger.error(f"BigQuery metrics query failed: {e}", exc_info=True)
            return {"total_test_cases": 0, "avg_quality_score": 0.8, "feedback_rate": 0.0}
    
    def _update_workflow_metrics(self, successful_count: int, processing_time: float) -> None:
        """Update workflow performance metrics"""
        # Initialize metrics if not exists
        if "total_successful" not in self.workflow_metrics:
            self.workflow_metrics["total_successful"] = 0
        if "total_processing_time" not in self.workflow_metrics:
            self.workflow_metrics["total_processing_time"] = 0.0
        if "total_processed" not in self.workflow_metrics:
            self.workflow_metrics["total_processed"] = 0
        
        # Update counters - track actual attempts vs successes
        self.workflow_metrics["total_successful"] += successful_count
        # Increment total_processed by 1 for each workflow execution
        self.workflow_metrics["total_processed"] += 1
        self.workflow_metrics["total_processing_time"] += processing_time
        
        # Calculate correct success rate using total_processed as denominator
        total_processed = self.workflow_metrics["total_processed"]
        if total_processed > 0:
            self.workflow_metrics["success_rate"] = self.workflow_metrics["total_successful"] / total_processed
        
        # Calculate correct average processing time
        if total_processed > 0:
            self.workflow_metrics["avg_processing_time"] = self.workflow_metrics["total_processing_time"] / total_processed
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status and metrics with health checks"""
        agents_health = {}
        
        # Check each agent's health
        for agent_name, agent in [
            ("document_parser", self.document_parser),
            ("test_generator", self.test_generator),
            ("feedback_loop", self.feedback_loop),
            ("compliance_validator", self.compliance_validator),
            ("performance_monitor", self.performance_monitor),
            ("coordinator", self.coordinator)
        ]:
            try:
                # Simple health check - agent exists and has name
                if hasattr(agent, 'name') and agent.name:
                    agents_health[agent_name] = {"status": "healthy", "name": agent.name}
                else:
                    agents_health[agent_name] = {"status": "unhealthy", "name": "unknown"}
            except Exception as e:
                agents_health[agent_name] = {"status": "error", "error": str(e)}
        
        return {
            "agents_status": agents_health,
            "workflow_metrics": self.workflow_metrics,
            "overall_health": "healthy" if all(a.get("status") == "healthy" for a in agents_health.values()) else "degraded"
        }

