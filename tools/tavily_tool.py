"""
Tavily tool for news and web search
Phase 3: Multi-source data gathering
"""

from typing import Dict, Any, List, Optional
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_api_key

logger = logging.getLogger(__name__)

class TavilyTool:
    """Tool for gathering news and web search data using Tavily API"""
    
    def __init__(self):
        self.api_key = get_api_key('tavily')
        if not self.api_key:
            logger.warning("Tavily API key not found - tool will be disabled")
            self.enabled = False
        else:
            self.enabled = True
            try:
                from tavily import TavilyClient
                self.client = TavilyClient(api_key=self.api_key)
                logger.info("Tavily tool initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Tavily client: {e}")
                self.enabled = False
    
    def search_news(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search for recent news related to the query"""
        if not self.enabled:
            return {"error": "Tavily tool not enabled", "data_source": "tavily"}
        
        try:
            logger.info(f"Tavily: Searching news for '{query}'")
            
            # Search for news with better parameters
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=["reuters.com", "bloomberg.com", "wsj.com", "ft.com", "aviationweek.com", "flightglobal.com", "ainonline.com"],
                exclude_domains=["wikipedia.org", "reddit.com"]
            )
            
            # Process results
            news_items = []
            for result in response.get('results', []):
                news_items.append({
                    "title": result.get('title', ''),
                    "url": result.get('url', ''),
                    "content": result.get('content', ''),
                    "published_date": result.get('published_date', ''),
                    "score": result.get('score', 0)
                })
            
            return {
                "query": query,
                "news_items": news_items,
                "total_results": len(news_items),
                "data_source": "tavily",
                "search_type": "news"
            }
            
        except Exception as e:
            logger.error(f"Tavily news search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "data_source": "tavily",
                "search_type": "news"
            }
    
    def search_web(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search the web for general information"""
        if not self.enabled:
            return {"error": "Tavily tool not enabled", "data_source": "tavily"}
        
        try:
            logger.info(f"Tavily: Searching web for '{query}'")
            
            # Search the web
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=["honeywell.com", "prattwhitney.com", "ge.com", "rolls-royce.com"],
                exclude_domains=["wikipedia.org", "reddit.com"]
            )
            
            # Process results
            web_results = []
            for result in response.get('results', []):
                web_results.append({
                    "title": result.get('title', ''),
                    "url": result.get('url', ''),
                    "content": result.get('content', ''),
                    "score": result.get('score', 0)
                })
            
            return {
                "query": query,
                "web_results": web_results,
                "total_results": len(web_results),
                "data_source": "tavily",
                "search_type": "web"
            }
            
        except Exception as e:
            logger.error(f"Tavily web search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "data_source": "tavily",
                "search_type": "web"
            }
    
    def search_competitive_intelligence(self, honeywell_product: str, competitor_query: str) -> Dict[str, Any]:
        """Search for competitive intelligence data"""
        if not self.enabled:
            return {"error": "Tavily tool not enabled", "data_source": "tavily"}
        
        try:
            logger.info(f"Tavily: Searching competitive intelligence for {honeywell_product} vs {competitor_query}")
            
            # Create search queries
            queries = [
                f"{honeywell_product} competitive analysis",
                f"{competitor_query} market position",
                f"{honeywell_product} vs {competitor_query} comparison",
                f"aerospace industry {honeywell_product} news",
                f"{competitor_query} aerospace products"
            ]
            
            all_results = {
                "honeywell_product": honeywell_product,
                "competitor_query": competitor_query,
                "searches": [],
                "data_source": "tavily",
                "search_type": "competitive_intelligence"
            }
            
            # Perform multiple searches
            for query in queries:
                try:
                    response = self.client.search(
                        query=query,
                        search_depth="basic",
                        max_results=3,
                        include_domains=["aviationweek.com", "flightglobal.com", "ainonline.com", "honeywell.com"],
                        exclude_domains=["wikipedia.org", "reddit.com"]
                    )
                    
                    search_results = []
                    for result in response.get('results', []):
                        search_results.append({
                            "title": result.get('title', ''),
                            "url": result.get('url', ''),
                            "content": result.get('content', ''),
                            "score": result.get('score', 0)
                        })
                    
                    all_results["searches"].append({
                        "query": query,
                        "results": search_results,
                        "total_results": len(search_results)
                    })
                    
                except Exception as e:
                    logger.warning(f"Tavily search failed for query '{query}': {e}")
                    all_results["searches"].append({
                        "query": query,
                        "error": str(e),
                        "results": [],
                        "total_results": 0
                    })
            
            return all_results
            
        except Exception as e:
            logger.error(f"Tavily competitive intelligence search failed: {e}")
            return {
                "honeywell_product": honeywell_product,
                "competitor_query": competitor_query,
                "error": str(e),
                "data_source": "tavily",
                "search_type": "competitive_intelligence"
            }

# Example usage for testing
if __name__ == "__main__":
    tool = TavilyTool()
    
    if tool.enabled:
        print("Testing Tavily tool...")
        
        # Test news search
        news_results = tool.search_news("Honeywell aerospace TFE731 engine")
        print(f"News search results: {news_results.get('total_results', 0)} items")
        
        # Test competitive intelligence
        comp_results = tool.search_competitive_intelligence("TFE731 Engine", "Pratt & Whitney PW500")
        print(f"Competitive intelligence: {len(comp_results.get('searches', []))} searches")
        
    else:
        print("Tavily tool not enabled - check API key")
