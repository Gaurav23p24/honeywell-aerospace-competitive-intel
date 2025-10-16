#!/usr/bin/env python3
"""
Test script to show individual tool outputs
"""

def test_tavily():
    print("=== TESTING TAVILY TOOL ===")
    try:
        from tools.tavily_tool import TavilyTool
        tool = TavilyTool()
        print(f"Tavily enabled: {tool.enabled}")
        
        if tool.enabled:
            result = tool.search_news("Honeywell aerospace TFE731 engine", 3)
            print(f"Query: {result.get('query', 'N/A')}")
            print(f"Total articles: {result.get('total_results', 0)}")
            print(f"Data source: {result.get('data_source', 'N/A')}")
            
            print("\nArticles found:")
            for i, item in enumerate(result.get('news_items', []), 1):
                print(f"{i}. {item.get('title', 'No title')}")
                print(f"   URL: {item.get('url', 'No URL')}")
                print(f"   Score: {item.get('score', 0)}")
                print()
        else:
            print("Tavily tool not enabled")
            
    except Exception as e:
        print(f"Tavily test failed: {e}")

def test_skyvern():
    print("=== TESTING SKYVERN TOOL ===")
    try:
        from tools.skyvern_tool import SkyvernTool
        tool = SkyvernTool()
        print(f"Skyvern enabled: {tool.enabled}")
        
        if tool.enabled:
            result = tool.browse_website("https://aerospace.honeywell.com", "Find TFE731 engine specifications")
            print(f"URL: {result.get('url', 'N/A')}")
            print(f"Status: {result.get('status', 'unknown')}")
            print(f"Task ID: {result.get('task_id', 'N/A')}")
            print(f"Error: {result.get('error', 'No error')}")
            print(f"Data source: {result.get('data_source', 'N/A')}")
        else:
            print("Skyvern tool not enabled")
            
    except Exception as e:
        print(f"Skyvern test failed: {e}")

def test_yfinance():
    print("=== TESTING YFINANCE TOOL ===")
    try:
        from tools.yfinance_tool import YFinanceTool
        tool = YFinanceTool()
        
        hon_data = tool.get_honeywell_data()
        print(f"Honeywell: {hon_data.get('company_name')} - ${hon_data.get('current_price', 0):.2f}")
        print(f"Market Cap: ${hon_data.get('market_cap', 0):,}")
        print(f"Sector: {hon_data.get('sector', 'N/A')}")
        
        ge_data = tool.get_competitor_data("GE")
        print(f"GE: {ge_data.get('company_name')} - ${ge_data.get('current_price', 0):.2f}")
        print(f"Market Cap: ${ge_data.get('market_cap', 0):,}")
        print(f"Sector: {ge_data.get('sector', 'N/A')}")
        
    except Exception as e:
        print(f"YFinance test failed: {e}")

if __name__ == "__main__":
    test_tavily()
    print("\n" + "="*50 + "\n")
    test_skyvern()
    print("\n" + "="*50 + "\n")
    test_yfinance()
