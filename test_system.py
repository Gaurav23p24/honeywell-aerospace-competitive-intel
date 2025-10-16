#!/usr/bin/env python3
"""
Test script to verify individual components of the Honeywell Analysis System
"""

import sys
import os

def test_yfinance_tool():
    """Test the yfinance tool"""
    print("Testing yfinance tool...")
    try:
        from tools.yfinance_tool import YFinanceTool
        tool = YFinanceTool()
        
        # Test Honeywell data
        hon_data = tool.get_honeywell_data()
        print(f"+ Honeywell: {hon_data.get('company_name')} - ${hon_data.get('current_price', 0):.2f}")
        
        # Test competitor data
        ge_data = tool.get_competitor_data("GE")
        print(f"+ GE: {ge_data.get('company_name')} - ${ge_data.get('current_price', 0):.2f}")
        
        return True
    except Exception as e:
        print(f"- yfinance tool failed: {e}")
        return False

def test_scout_agent():
    """Test the scout agent"""
    print("\nTesting scout agent...")
    try:
        from agents.scout import ScoutAgent
        scout = ScoutAgent()
        
        result = scout.hunt("TFE731 Engine", "compare with Pratt & Whitney PW500")
        print(f"+ Scout gathered data from {len(result['sources'])} sources")
        print(f"+ Tools used: {result['metadata']['tools_used']}")
        
        return True
    except Exception as e:
        print(f"- Scout agent failed: {e}")
        return False

def test_validator_agent():
    """Test the validator agent"""
    print("\nTesting validator agent...")
    try:
        from agents.scout import ScoutAgent
        from agents.validator import ValidatorAgent
        
        scout = ScoutAgent()
        validator = ValidatorAgent()
        
        raw_data = scout.hunt("TFE731 Engine", "compare with Pratt & Whitney PW500")
        validated_data = validator.validate(raw_data)
        
        print(f"+ Validation complete: {validated_data['is_valid']}")
        print(f"+ Quality scores: {list(validated_data['quality_scores'].keys())}")
        
        return True
    except Exception as e:
        print(f"- Validator agent failed: {e}")
        return False

def test_analyst_agent():
    """Test the analyst agent"""
    print("\nTesting analyst agent...")
    try:
        from agents.scout import ScoutAgent
        from agents.validator import ValidatorAgent
        from agents.analyst import AnalystAgent
        
        scout = ScoutAgent()
        validator = ValidatorAgent()
        analyst = AnalystAgent()
        
        raw_data = scout.hunt("TFE731 Engine", "compare with Pratt & Whitney PW500")
        validated_data = validator.validate(raw_data)
        analysis = analyst.analyze(validated_data)
        
        print(f"+ Analysis complete: {len(analysis['competitive_gaps'])} gaps, {len(analysis['insights'])} insights")
        print(f"+ Confidence score: {analysis['confidence_score']:.2f}")
        
        return True
    except Exception as e:
        print(f"- Analyst agent failed: {e}")
        return False

def test_langgraph_workflow():
    """Test the LangGraph workflow"""
    print("\nTesting LangGraph workflow...")
    try:
        from workflow import run_analysis_workflow
        
        result = run_analysis_workflow("TFE731 Engine", "compare with Pratt & Whitney PW500")
        
        print(f"+ Workflow completed: {result['workflow_complete']}")
        print(f"+ Final step: {result['current_step']}")
        
        if result['pdf_path']:
            print(f"+ PDF generated: {result['pdf_path']}")
        else:
            print(f"- No PDF generated")
        
        return result['workflow_complete'] and result['current_step'] == 'complete'
    except Exception as e:
        print(f"- LangGraph workflow failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Honeywell Aerospace Analysis System - Component Tests")
    print("=" * 60)
    
    tests = [
        test_yfinance_tool,
        test_scout_agent,
        test_validator_agent,
        test_analyst_agent,
        test_langgraph_workflow
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All tests passed! System is ready for Phase 3.")
        return 0
    else:
        print("ERROR: Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
