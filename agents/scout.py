"""
Scout Agent - Gathers data from multiple sources in parallel
Phase 3: Multi-source data gathering with Tavily and Skyvern
"""

from typing import Dict, Any, List
import logging
import concurrent.futures
from tools.yfinance_tool import YFinanceTool
from tools.tavily_tool import TavilyTool
from tools.browser_use_tool import BrowserUseTool

logger = logging.getLogger(__name__)

class ScoutAgent:
    """Agent responsible for gathering data from multiple sources in parallel"""
    
    def __init__(self):
        self.yfinance_tool = YFinanceTool()
        self.tavily_tool = TavilyTool()
        self.browser_use_tool = BrowserUseTool()
        
        # Available tools based on API key availability
        self.available_tools = ["yfinance"]  # Always available
        
        if self.tavily_tool.enabled:
            self.available_tools.append("tavily")
        
        if self.browser_use_tool.enabled:
            self.available_tools.append("browser_use")
        
        logger.info(f"Scout: Initialized with tools: {self.available_tools}")
        
    def hunt(self, honeywell_product: str, competitor_query: str) -> Dict[str, Any]:
        """
        Main hunting method - gathers data from all available tools in parallel
        
        Args:
            honeywell_product: The Honeywell product to analyze
            competitor_query: Query about competitor (e.g., "compare with Pratt & Whitney PW500")
        
        Returns:
            Dictionary containing all gathered data
        """
        logger.info(f"Scout: Starting hunt for {honeywell_product} vs {competitor_query}")
        
        gathered_data = {
            "honeywell_product": honeywell_product,
            "competitor_query": competitor_query,
            "sources": {},
            "errors": [],
            "metadata": {
                "tools_used": [],
                "total_sources": 0,
                "successful_sources": 0
            }
        }
        
        # Define tasks for parallel execution - OPTIMIZED FOR SPEED
        tasks = []
        
        # yfinance tasks (always run) - keep these as they're fast
        tasks.append(("yfinance_honeywell", self._get_honeywell_financial_data))
        tasks.append(("yfinance_competitor", self._get_competitor_financial_data, competitor_query))
        tasks.append(("yfinance_comparison", self._get_financial_comparison, competitor_query))
        
        # Tavily tasks (if enabled) - reduce to 1 task only
        if self.tavily_tool.enabled:
            tasks.append(("tavily_news", self._get_tavily_news, honeywell_product, competitor_query))
        
        # Browser-use tasks (if enabled) - limit to 1 task for efficiency
        if self.browser_use_tool.enabled:
            tasks.append(("browser_use_specs", self._get_browser_use_product_specs, honeywell_product, competitor_query))
        
        # Execute tasks in parallel
        print(f"Scout: Starting parallel data gathering with {len(tasks)} tasks")
        print(f"Available tools: {self.available_tools}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            # Submit all tasks
            future_to_task = {}
            for task in tasks:
                if len(task) == 2:
                    source_name, func = task
                    future = executor.submit(func)
                elif len(task) == 3:
                    source_name, func, arg1 = task
                    future = executor.submit(func, arg1)
                elif len(task) == 4:
                    source_name, func, arg1, arg2 = task
                    future = executor.submit(func, arg1, arg2)
                
                future_to_task[future] = source_name
                print(f"Scout: Submitted task: {source_name}")
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_task):
                source_name = future_to_task[future]
                try:
                    result = future.result()
                    gathered_data["sources"][source_name] = result
                    gathered_data["metadata"]["successful_sources"] += 1
                    
                    # Track which tools were used
                    tool_name = source_name.split('_')[0]
                    if tool_name not in gathered_data["metadata"]["tools_used"]:
                        gathered_data["metadata"]["tools_used"].append(tool_name)
                    
                    logger.info(f"Scout: {source_name} completed successfully")
                    print(f"Scout: {source_name} completed successfully")
                    
                except Exception as e:
                    error_msg = f"{source_name} failed: {str(e)}"
                    logger.error(error_msg)
                    gathered_data["errors"].append(error_msg)
                    print(f"Scout: {source_name} failed: {str(e)}")
        
        gathered_data["metadata"]["total_sources"] = len(tasks)
        
        logger.info(f"Scout: Hunt complete. {gathered_data['metadata']['successful_sources']}/{gathered_data['metadata']['total_sources']} sources successful")
        logger.info(f"Scout: Tools used: {gathered_data['metadata']['tools_used']}")
        
        print(f"Scout: Hunt complete!")
        print(f"Results: {gathered_data['metadata']['successful_sources']}/{gathered_data['metadata']['total_sources']} sources successful")
        print(f"Tools used: {', '.join(gathered_data['metadata']['tools_used'])}")
        if gathered_data["errors"]:
            print(f"Errors: {len(gathered_data['errors'])} failures")
        
        return gathered_data
    
    def _get_honeywell_financial_data(self) -> Dict[str, Any]:
        """Get Honeywell financial data"""
        return self.yfinance_tool.get_honeywell_data()
    
    def _get_competitor_financial_data(self, competitor_query: str) -> Dict[str, Any]:
        """Get competitor financial data"""
        competitor_ticker = self._extract_competitor_ticker(competitor_query)
        return self.yfinance_tool.get_competitor_data(competitor_ticker)
    
    def _get_financial_comparison(self, competitor_query: str) -> Dict[str, Any]:
        """Get financial comparison data"""
        competitor_ticker = self._extract_competitor_ticker(competitor_query)
        return self.yfinance_tool.compare_companies(
            self.yfinance_tool.honeywell_ticker, 
            competitor_ticker
        )
    
    def _get_tavily_news(self, honeywell_product: str, competitor_query: str) -> Dict[str, Any]:
        """Get Tavily news data - OPTIMIZED FOR SPEED"""
        # Use simpler, more effective search queries
        queries = [
            f"{honeywell_product} aerospace news",
            f"Honeywell aerospace {honeywell_product}",
            f"aerospace engine news {honeywell_product}"
        ]
        
        all_results = []
        for query in queries:
            try:
                result = self.tavily_tool.search_news(query, max_results=2)
                if result.get('news_items'):
                    all_results.extend(result['news_items'])
            except Exception as e:
                logger.warning(f"Tavily search failed for '{query}': {e}")
        
        # Return combined results
        return {
            "query": f"{honeywell_product} aerospace news",
            "news_items": all_results[:5],  # Limit to 5 total results
            "total_results": len(all_results),
            "data_source": "tavily",
            "search_type": "news"
        }
    
    def _get_tavily_competitive_intelligence(self, honeywell_product: str, competitor_query: str) -> Dict[str, Any]:
        """Get Tavily competitive intelligence"""
        return self.tavily_tool.search_competitive_intelligence(honeywell_product, competitor_query)
    
    def _get_browser_use_product_specs(self, honeywell_product: str, competitor_query: str) -> Dict[str, Any]:
        """Get browser-use product specifications"""
        return self.browser_use_tool.search_product_specs(honeywell_product, competitor_query)
    
    def _get_browser_use_market_data(self, honeywell_product: str, competitor_query: str) -> Dict[str, Any]:
        """Get browser-use market data"""
        query = f"{honeywell_product} {competitor_query} aerospace market analysis"
        return self.browser_use_tool.get_market_data(query)
    
    def _extract_competitor_ticker(self, competitor_query: str) -> str:
        """
        Extract competitor ticker from query
        Phase 1: Simple mapping, Phase 2+: Use LLM parsing
        """
        query_lower = competitor_query.lower()
        
        # Simple mapping for Phase 1
        if "pratt" in query_lower or "whitney" in query_lower:
            return "RTX"  # Raytheon Technologies (owns Pratt & Whitney)
        elif "general electric" in query_lower or "ge" in query_lower:
            return "GE"
        elif "boeing" in query_lower:
            return "BA"
        elif "airbus" in query_lower:
            return "EADSY"  # Airbus SE ADR
        elif "rolls royce" in query_lower:
            return "RYCEY"  # Rolls-Royce Holdings ADR
        else:
            # Default to GE for Phase 1
            logger.warning(f"Unknown competitor in query '{competitor_query}', defaulting to GE")
            return "GE"
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return self.available_tools.copy()
    
    def add_tool(self, tool_name: str):
        """Add a new tool (for Phase 2+)"""
        if tool_name not in self.available_tools:
            self.available_tools.append(tool_name)
            logger.info(f"Scout: Added tool {tool_name}")

# Example usage for testing
if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    scout = ScoutAgent()
    
    # Test hunt with all tools
    result = scout.hunt("TFE731 Engine", "compare with Pratt & Whitney PW500")
    
    print("Scout Hunt Results:")
    print(f"Sources: {list(result['sources'].keys())}")
    print(f"Tools used: {result['metadata']['tools_used']}")
    print(f"Errors: {result['errors']}")
    
    # Print some sample data
    if "yfinance_honeywell" in result["sources"]:
        hon_data = result["sources"]["yfinance_honeywell"]
        print(f"\nHoneywell: {hon_data.get('company_name')} - ${hon_data.get('current_price', 0):.2f}")
    
    if "tavily_news" in result["sources"]:
        news_data = result["sources"]["tavily_news"]
        print(f"Tavily News: {news_data.get('total_results', 0)} articles found")
    
    if "browser_use_specs" in result["sources"]:
        specs_data = result["sources"]["browser_use_specs"]
        print(f"Browser-use Specs: {len(specs_data.get('browsing_results', []))} sites browsed")
