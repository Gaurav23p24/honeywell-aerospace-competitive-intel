#!/usr/bin/env python3
"""
Test script for browser-use tool with hard guardrails
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.browser_use_tool import BrowserUseTool

def test_browser_guardrails():
    """Test browser-use tool with hard guardrails"""
    print("Testing Browser-use Tool with Hard Guardrails")
    print("=" * 50)
    
    tool = BrowserUseTool()
    
    if not tool.enabled:
        print("Browser-use tool not enabled - check OpenAI API key")
        return
    
    print(f"Tool initialized with constraints:")
    print(f"- Max steps: {tool.MAX_STEPS}")
    print(f"- Max actions per step: {tool.MAX_ACTIONS_PER_STEP}")
    print(f"- Timeout: {tool.TIMEOUT_SECONDS}s")
    print(f"- Max navigation attempts: {tool.MAX_NAVIGATION_ATTEMPTS}")
    print(f"- Max sites to browse: {tool.MAX_SITES_TO_BROWSE}")
    print()
    
    # Test 1: Simple browsing with hard limits
    print("Test 1: Simple browsing with hard limits")
    print("-" * 40)
    
    try:
        result = tool.browse_website(
            "https://aerospace.honeywell.com", 
            "Find TFE731 engine specifications"
        )
        
        print(f"Result status: {result.get('status', 'unknown')}")
        print(f"Data source: {result.get('data_source', 'unknown')}")
        
        if 'structured_data' in result:
            print(f"Structured data: {result['structured_data']}")
        
        if 'error' in result:
            print(f"Error: {result['error']}")
            
    except Exception as e:
        print(f"Test 1 failed: {e}")
    
    print()
    
    # Test 2: Product specs search with limits
    print("Test 2: Product specs search with limits")
    print("-" * 40)
    
    try:
        result = tool.search_product_specs("TFE731 Engine", "Pratt & Whitney PW500")
        
        print(f"Search type: {result.get('search_type', 'unknown')}")
        print(f"Browsing results: {len(result.get('browsing_results', []))}")
        
        for i, browse_result in enumerate(result.get('browsing_results', [])):
            print(f"  Site {i+1}: {browse_result.get('status', 'unknown')}")
            if 'error' in browse_result:
                print(f"    Error: {browse_result['error']}")
                
    except Exception as e:
        print(f"Test 2 failed: {e}")
    
    print()
    print("Hard guardrails test completed!")

if __name__ == "__main__":
    test_browser_guardrails()
