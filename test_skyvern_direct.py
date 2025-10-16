#!/usr/bin/env python3
"""
Test Skyvern API directly
"""

import asyncio
from skyvern import Skyvern
from config import get_api_key

async def test_skyvern():
    api_key = get_api_key('skyvern')
    print(f"API key length: {len(api_key) if api_key else 0}")
    print(f"API key starts with: {api_key[:10] if api_key else 'None'}")
    
    if not api_key:
        print("No API key found")
        return
    
    try:
        client = Skyvern(api_key=api_key)
        print("Skyvern client created successfully")
        
        # Test with a simple task
        result = await client.run_task(
            prompt="Find information about aerospace engines",
            url="https://aerospace.honeywell.com",
            max_steps=1,
            wait_for_completion=True,
            timeout=30
        )
        print(f"Task result: {result}")
        
    except Exception as e:
        print(f"Skyvern test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_skyvern())
