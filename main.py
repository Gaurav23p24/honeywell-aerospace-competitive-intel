#!/usr/bin/env python3
"""
Honeywell Aerospace Competitive Analysis System
Phase 2: LangGraph orchestration with state management
"""

import os
from workflow import run_analysis_workflow

def main():
    """Main entry point - LangGraph workflow for Phase 2"""
    print("Honeywell Aerospace Competitive Analysis System")
    print("Phase 2: LangGraph Orchestration")
    print("=" * 50)
    
    # Hardcoded inputs for Phase 2
    honeywell_product = "TFE731 Engine"
    competitor_query = "compare with Pratt & Whitney PW500"
    
    print(f"Analyzing: {honeywell_product}")
    print(f"Query: {competitor_query}")
    print()
    
    try:
        # Run LangGraph workflow
        print("Starting LangGraph workflow...")
        result = run_analysis_workflow(honeywell_product, competitor_query)
        
        # Check results
        if result['workflow_complete'] and result['current_step'] == 'complete':
            print(f"SUCCESS: Report generated: {result['pdf_path']}")
            
            # Print summary
            if result.get('analysis_summary'):
                print(f"Analysis Summary: {result['analysis_summary']}")
            
            return 0
        else:
            print(f"ERROR: Workflow failed at step: {result['current_step']}")
            if result.get('error_message'):
                print(f"Error message: {result['error_message']}")
            return 1
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
