#!/usr/bin/env python3
"""
Test browser-use functionality
"""

from browser_use import Agent
from browser_use.llm import ChatOpenAI
import os
from config import get_api_key

def test_browser_use():
    """Test basic browser-use functionality"""
    try:
        # Get OpenAI API key
        api_key = get_api_key('openai')
        if not api_key:
            print("OpenAI API key not found")
            return False
        
        # Set environment variable
        os.environ['OPENAI_API_KEY'] = api_key
        
        # Create agent with OpenAI
        agent = Agent(
            task="Go to https://aerospace.honeywell.com and find information about TFE731 engine",
            llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.1),
        )
        
        print("Running browser-use agent...")
        result = agent.run_sync()
        
        print(f"Task completed: {result}")
        return True
        
    except Exception as e:
        print(f"Browser-use test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_browser_use()
    print(f"Test {'PASSED' if success else 'FAILED'}")
