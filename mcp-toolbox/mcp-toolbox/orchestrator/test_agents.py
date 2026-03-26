import pytest
import asyncio
from agents import (DocumentParserAgent, TestCaseGeneratorAgent, FeedbackLoopAgent, 
                   ComplianceValidationAgent, PerformanceMonitorAgent, CoordinatorAgent)

class TestAgents:
    """Basic unit tests for all agents"""
    
    @pytest.mark.asyncio
    async def test_document_parser_agent(self):
        agent = DocumentParserAgent()
        result = await agent.parse_document(raw_text="REQ-001: System must authenticate users")
        assert result.success
        assert result.data is not None
    
    @pytest.mark.asyncio
    async def test_test_generator_agent(self):
        agent = TestCaseGeneratorAgent()
        result = await agent.generate_test_case("Test requirement", ["context"], ["task1"])
        assert result.success
        assert result.data is not None
    
    @pytest.mark.asyncio
    async def test_feedback_loop_agent(self):
        agent = FeedbackLoopAgent()
        feedback_data = {"rating": 4, "improvement": "Add more details"}
        result = await agent.process_feedback("TC-001", feedback_data)
        assert result.success
        assert result.data is not None
    
    @pytest.mark.asyncio
    async def test_compliance_validation_agent(self):
        agent = ComplianceValidationAgent()
        result = await agent.validate_compliance("GDPR compliance required", ["regulatory context"])
        assert result.success
        assert result.data is not None
    
    @pytest.mark.asyncio
    async def test_performance_monitor_agent(self):
        agent = PerformanceMonitorAgent()
        operation_result = {"success": True, "quality_score": 0.8}
        result = await agent.track_performance(operation_result)
        assert result.success
        assert result.data is not None
    
    @pytest.mark.asyncio
    async def test_coordinator_agent(self):
        agent = CoordinatorAgent()
        result = await agent.coordinate_workflow("Security requirement for authentication")
        assert result.success
        assert result.data is not None
        assert "tasks" in result.data

if __name__ == "__main__":
    pytest.main([__file__])