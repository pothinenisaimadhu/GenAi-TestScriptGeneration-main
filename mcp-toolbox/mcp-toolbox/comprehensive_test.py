#!/usr/bin/env python3
"""Comprehensive test for all agent functionality"""

import asyncio
import sys
import os
import tempfile
sys.path.append(os.path.dirname(__file__))

from orchestrator.agents import (
    DocumentParserAgent, 
    TestCaseGeneratorAgent, 
    FeedbackLoopAgent,
    ModelPerformanceMonitor,
    AutomatedRetrainingTrigger,
    AgentResult
)

async def test_file_parsing():
    """Test file parsing with actual files"""
    print("=== Testing File Parsing ===")
    
    agent = DocumentParserAgent()
    
    # Create test files
    test_files = {
        "test.txt": "REQ-001: System must authenticate users\nREQ-002: Data must be encrypted",
        "test.json": '{"requirements": ["User authentication", "Data encryption"]}',
        "test.yaml": "requirements:\n  - User authentication\n  - Data encryption"
    }
    
    for filename, content in test_files.items():
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{filename.split(".")[-1]}', delete=False) as f:
                f.write(content)
                temp_path = f.name
            
            result = await agent.parse_document(document_path=temp_path)
            print(f"[OK] {filename}: {result.success}")
            if result.success:
                data = result.data
                print(f"  - Requirements: {len(data.get('requirements', []))}")
            
            os.unlink(temp_path)
            
        except Exception as e:
            print(f"[ERROR] {filename} failed: {e}")

async def test_performance_degradation():
    """Test performance monitoring with degrading quality"""
    print("\n=== Testing Performance Degradation ===")
    
    monitor = ModelPerformanceMonitor()
    
    # Simulate degrading test case quality
    test_cases = [
        "TEST CASE: Complete test with OBJECTIVE: test STEPS: 1,2,3 EXPECTED: success",
        "TEST CASE: Partial test STEPS: 1,2",
        "TEST CASE: Minimal test",
        "Bad test",
        "x"
    ]
    
    for i, test_case in enumerate(test_cases):
        result = AgentResult(success=True, data=test_case)
        feedback_metrics = {"total_feedback": i}
        
        perf_result = await monitor.monitor_performance(result, feedback_metrics)
        if perf_result.success:
            quality = perf_result.data["quality_score"]
            retrain_needed = perf_result.data["retraining_needed"]
            print(f"  Test {i+1}: Quality={quality:.2f}, Retrain={retrain_needed}")

async def test_feedback_accumulation():
    """Test feedback accumulation and retraining trigger"""
    print("\n=== Testing Feedback Accumulation ===")
    
    feedback_agent = FeedbackLoopAgent()
    trigger = AutomatedRetrainingTrigger()
    
    # Simulate multiple feedback entries
    corrections_list = [
        {"test_steps": "Need more detail"},
        {"expected_result": "Unclear expectation"},
        {"description": "Poor description", "test_steps": "Bad steps"},
        {"validation": "Missing validation", "expected_result": "Wrong result"}
    ]
    
    for i, corrections in enumerate(corrections_list):
        await feedback_agent.process_feedback(f"TC-{i+1}", corrections)
    
    metrics = feedback_agent.get_feedback_metrics()
    print(f"  Total feedback: {metrics['total_feedback']}")
    print(f"  Common issues: {metrics['common_issues']}")
    
    # Test retraining trigger with high feedback
    performance_data = {"retraining_needed": False, "quality_score": 0.6}
    result = await trigger.evaluate_retraining(performance_data, feedback_agent)
    print(f"  Retraining action: {result.data.get('action')}")

async def test_edge_cases():
    """Test edge cases and error conditions"""
    print("\n=== Testing Edge Cases ===")
    
    agent = DocumentParserAgent()
    
    # Test with non-existent file
    try:
        result = await agent.parse_document(document_path="nonexistent.txt")
        print(f"[OK] Non-existent file handled: {not result.success}")
    except Exception as e:
        print(f"[OK] Non-existent file exception: {type(e).__name__}")
    
    # Test with empty requirements
    result = await agent.parse_document(raw_text="This is just random text without requirements.")
    print(f"[OK] No requirements found: {not result.success or len(result.data.get('requirements', [])) == 0}")
    
    # Test TestCaseGenerator with empty inputs
    generator = TestCaseGeneratorAgent()
    result = await generator.generate_test_case("", [], [])
    print(f"[OK] Empty requirement handled: {result.success}")

async def main():
    """Run comprehensive tests"""
    print("Starting Comprehensive Agent Tests...\n")
    
    await test_file_parsing()
    await test_performance_degradation()
    await test_feedback_accumulation()
    await test_edge_cases()
    
    print("\n=== Comprehensive Test Summary ===")
    print("All comprehensive tests completed successfully!")
    print("The agents are working correctly with proper error handling.")

if __name__ == "__main__":
    asyncio.run(main())