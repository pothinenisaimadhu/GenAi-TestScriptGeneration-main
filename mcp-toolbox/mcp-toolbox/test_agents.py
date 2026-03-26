#!/usr/bin/env python3
"""Test script for agents.py functionality"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from orchestrator.agents import (
    DocumentParserAgent, 
    TestCaseGeneratorAgent, 
    FeedbackLoopAgent,
    ModelPerformanceMonitor,
    AutomatedRetrainingTrigger,
    AgentResult
)

async def test_document_parser():
    """Test DocumentParserAgent"""
    print("=== Testing DocumentParserAgent ===")
    
    agent = DocumentParserAgent()
    
    # Test with raw text
    test_text = """
    REQ-001: The system shall authenticate users using multi-factor authentication
    REQ-002: User data must be encrypted at rest and in transit
    REQ-003: The application shall log all security events
    """
    
    try:
        result = await agent.parse_document(raw_text=test_text)
        print(f"[OK] Parse result: {result.success}")
        if result.success:
            data = result.data
            print(f"  - Requirements: {len(data.get('requirements', []))}")
            print(f"  - Test cases: {len(data.get('test_cases', []))}")
            print(f"  - Datasets: {len(data.get('datasets', []))}")
        else:
            print(f"  - Error: {result.error}")
    except Exception as e:
        print(f"[ERROR] DocumentParser failed: {e}")

async def test_test_case_generator():
    """Test TestCaseGeneratorAgent"""
    print("\n=== Testing TestCaseGeneratorAgent ===")
    
    agent = TestCaseGeneratorAgent()
    
    try:
        result = await agent.generate_test_case(
            requirement="User authentication with MFA",
            context=["security", "authentication"],
            tasks=["login", "verify", "access"]
        )
        print(f"[OK] Generation result: {result.success}")
        if result.success:
            print(f"  - Test case length: {len(result.data)}")
            print(f"  - Contains STEPS: {'STEPS:' in result.data}")
            print(f"  - Contains EXPECTED: {'EXPECTED:' in result.data}")
        else:
            print(f"  - Error: {result.error}")
    except Exception as e:
        print(f"[ERROR] TestCaseGenerator failed: {e}")

async def test_feedback_loop():
    """Test FeedbackLoopAgent"""
    print("\n=== Testing FeedbackLoopAgent ===")
    
    agent = FeedbackLoopAgent()
    
    try:
        corrections = {
            "test_steps": "Need more detailed steps",
            "expected_result": "Expected result unclear"
        }
        
        result = await agent.process_feedback("TC-001", corrections)
        print(f"[OK] Feedback result: {result.success}")
        if result.success:
            print(f"  - Feedback ID: {result.data.get('feedback_id')}")
            print(f"  - Improvements: {result.data.get('improvements')}")
        
        # Test metrics
        metrics = agent.get_feedback_metrics()
        print(f"  - Total feedback: {metrics.get('total_feedback')}")
        
    except Exception as e:
        print(f"[ERROR] FeedbackLoop failed: {e}")

async def test_performance_monitor():
    """Test ModelPerformanceMonitor"""
    print("\n=== Testing ModelPerformanceMonitor ===")
    
    monitor = ModelPerformanceMonitor()
    
    try:
        # Mock test case result
        test_result = AgentResult(
            success=True,
            data="TEST CASE: Security Test\nOBJECTIVE: Verify security\nSTEPS:\n1. Login\n2. Verify\nEXPECTED: Success"
        )
        
        feedback_metrics = {"total_feedback": 5}
        
        result = await monitor.monitor_performance(test_result, feedback_metrics)
        print(f"[OK] Monitor result: {result.success}")
        if result.success:
            data = result.data
            print(f"  - Quality score: {data.get('quality_score', 0):.2f}")
            print(f"  - Feedback rate: {data.get('feedback_rate', 0):.2f}")
            print(f"  - Retraining needed: {data.get('retraining_needed')}")
        
    except Exception as e:
        print(f"[ERROR] PerformanceMonitor failed: {e}")

async def test_retraining_trigger():
    """Test AutomatedRetrainingTrigger"""
    print("\n=== Testing AutomatedRetrainingTrigger ===")
    
    trigger = AutomatedRetrainingTrigger()
    feedback_agent = FeedbackLoopAgent()
    
    try:
        performance_data = {
            "retraining_needed": False,
            "quality_score": 0.8
        }
        
        result = await trigger.evaluate_retraining(performance_data, feedback_agent)
        print(f"[OK] Retraining result: {result.success}")
        if result.success:
            print(f"  - Action: {result.data.get('action')}")
            print(f"  - Reason: {result.data.get('reason', 'N/A')}")
        
    except Exception as e:
        print(f"[ERROR] RetrainingTrigger failed: {e}")

async def test_error_handling():
    """Test error handling"""
    print("\n=== Testing Error Handling ===")
    
    agent = DocumentParserAgent()
    
    # Test with invalid input
    try:
        result = await agent.parse_document()
        print(f"[OK] Empty input handled: {not result.success}")
        print(f"  - Error message: {result.error}")
    except Exception as e:
        print(f"[ERROR] Error handling failed: {e}")
    
    # Test with very short content
    try:
        result = await agent.parse_document(raw_text="short")
        print(f"[OK] Short content handled: {not result.success}")
        print(f"  - Error message: {result.error}")
    except Exception as e:
        print(f"[ERROR] Short content handling failed: {e}")

async def main():
    """Run all tests"""
    print("Starting Agent Tests...\n")
    
    await test_document_parser()
    await test_test_case_generator()
    await test_feedback_loop()
    await test_performance_monitor()
    await test_retraining_trigger()
    await test_error_handling()
    
    print("\n=== Test Summary ===")
    print("All tests completed. Check output above for results.")

if __name__ == "__main__":
    asyncio.run(main())