def generate_llm_questions(req_text):
    """Generate LLM-based questions for the requirement"""
    import os
    
    try:
        orchestrator_path = os.path.join(os.path.dirname(__file__), '..', 'orchestrator')
        original_cwd = os.getcwd()
        os.chdir(orchestrator_path)
        
        try:
            import tools
            
            prompt = f"""Analyze this requirement and generate 4 specific questions that would help create accurate test cases:

Requirement: {req_text}

Generate questions about:
1. Specific technical details needed for testing
2. Edge cases and error conditions
3. Performance or security requirements
4. Integration points or dependencies

Return only the questions, one per line:"""
            
            llm_response = tools.call_ai_generator(prompt, max_tokens=400)
            
            if llm_response and len(llm_response.strip()) > 20:
                questions = [q.strip() for q in llm_response.strip().split('\n') if q.strip() and len(q.strip()) > 10]
                return questions[:4]
        
        finally:
            os.chdir(original_cwd)
            
    except Exception as e:
        print(f"LLM question generation failed: {e}")
    
    # Fallback to requirement-specific questions
    return [
        f"What specific validation is needed for: '{req_text[:60]}...'?",
        f"What error conditions should be tested?",
        f"What are the acceptance criteria?",
        f"What edge cases apply to this requirement?"
    ]