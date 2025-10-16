"""
Skyvern tool for agentic browsing
Phase 3: Multi-source data gathering - FIXED VERSION
"""

from typing import Dict, Any, List, Optional
import logging
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_api_key

logger = logging.getLogger(__name__)

class SkyvernTool:
    """Tool for agentic browsing using Skyvern Python client"""
    
    def __init__(self):
        self.api_key = get_api_key('skyvern')
        if not self.api_key:
            logger.warning("Skyvern API key not found - tool will be disabled")
            self.enabled = False
        else:
            self.enabled = True
            try:
                # Import Skyvern client
                from skyvern import Skyvern
                self.client = Skyvern(api_key=self.api_key)
                logger.info("Skyvern tool initialized successfully with Python client")
            except Exception as e:
                logger.error(f"Failed to initialize Skyvern tool: {e}")
                self.enabled = False
    
    def browse_website(self, url: str, prompt: str) -> Dict[str, Any]:
        """
        Browse a website and extract information using Skyvern
        
        Args:
            url: The URL to browse
            prompt: What to look for on the website
        
        Returns:
            Dictionary containing browsing results
        """
        if not self.enabled:
            return self._create_error_response("Skyvern tool not enabled")
        
        try:
            logger.info(f"Skyvern: Browsing {url} for: {prompt}")
            
            # Run task asynchronously
            async def run_skyvern_task():
                try:
                    result = await self.client.run_task(
                        prompt=prompt,
                        url=url,
                        max_steps=3,  # Limit steps for cost control
                        engine="skyvern-2.0",
                        wait_for_completion=True,
                        timeout=60  # 1 minute timeout
                    )
                    return result
                except Exception as e:
                    logger.error(f"Skyvern async task failed: {e}")
                    return None
            
            # Run the async task
            result = asyncio.run(run_skyvern_task())
            
            if result and hasattr(result, 'run_id'):
                logger.info(f"Skyvern: Task completed successfully: {result.run_id}")
                
                return {
                    "url": url,
                    "prompt": prompt,
                    "run_id": result.run_id,
                    "status": "completed",
                    "data_source": "skyvern",
                    "browsing_results": [{
                        "url": url,
                        "prompt": prompt,
                        "run_id": result.run_id,
                        "status": "completed",
                        "extracted_data": getattr(result, 'extracted_data', None)
                    }]
                }
            else:
                error_msg = "Skyvern task failed to complete"
                logger.error(error_msg)
                return self._create_error_response(error_msg)
                
        except Exception as e:
            error_msg = f"Skyvern browsing failed: {str(e)}"
            logger.error(error_msg)
            return self._create_error_response(error_msg)
    
    def search_product_specs(self, honeywell_product: str, competitor_query: str) -> Dict[str, Any]:
        """Search for product specifications and technical data"""
        if not self.enabled:
            return self._create_error_response("Skyvern tool not enabled")
        
        try:
            logger.info(f"Skyvern: Searching product specs for {honeywell_product} vs {competitor_query}")
            
            # Define target websites for aerospace products
            target_sites = [
                "https://aerospace.honeywell.com",
                "https://www.prattwhitney.com",
                "https://www.ge.com/aerospace"
            ]
            
            all_results = {
                "honeywell_product": honeywell_product,
                "competitor_query": competitor_query,
                "browsing_results": [],
                "data_source": "skyvern",
                "search_type": "product_specs"
            }
            
            # Browse each site for relevant information
            for site in target_sites:
                try:
                    if "honeywell" in site:
                        prompt = f"Find detailed specifications and features for {honeywell_product} engine"
                    elif "prattwhitney" in site:
                        prompt = f"Find information about Pratt & Whitney engines and specifications"
                    elif "ge" in site:
                        prompt = f"Find information about GE Aerospace engines and specifications"
                    else:
                        prompt = f"Find aerospace engine specifications and technical data"
                    
                    result = self.browse_website(site, prompt)
                    all_results["browsing_results"].append(result)
                    
                except Exception as e:
                    logger.warning(f"Skyvern browsing failed for {site}: {e}")
                    all_results["browsing_results"].append(self._create_error_response(f"Failed to browse {site}: {e}"))
            
            return all_results
            
        except Exception as e:
            logger.error(f"Skyvern product specs search failed: {e}")
            return self._create_error_response(f"Product specs search failed: {e}")
    
    def get_market_data(self, query: str) -> Dict[str, Any]:
        """Get market data and industry insights"""
        if not self.enabled:
            return self._create_error_response("Skyvern tool not enabled")
        
        try:
            logger.info(f"Skyvern: Getting market data for '{query}'")
            
            # Target market research sites
            market_sites = [
                "https://www.marketresearch.com",
                "https://www.grandviewresearch.com"
            ]
            
            all_results = {
                "query": query,
                "market_data": [],
                "data_source": "skyvern",
                "search_type": "market_data"
            }
            
            for site in market_sites:
                try:
                    prompt = f"Find market research and industry analysis for {query}"
                    result = self.browse_website(site, prompt)
                    all_results["market_data"].append(result)
                    
                except Exception as e:
                    logger.warning(f"Skyvern market data search failed for {site}: {e}")
                    all_results["market_data"].append(self._create_error_response(f"Failed to browse {site}: {e}"))
            
            return all_results
            
        except Exception as e:
            logger.error(f"Skyvern market data search failed: {e}")
            return self._create_error_response(f"Market data search failed: {e}")
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create a standardized error response"""
        return {
            "error": error_message,
            "status": "error",
            "data_source": "skyvern"
        }

# Example usage for testing
if __name__ == "__main__":
    tool = SkyvernTool()
    
    if tool.enabled:
        print("Testing Skyvern tool...")
        
        # Test simple browsing
        result = tool.browse_website("https://aerospace.honeywell.com", "Find TFE731 engine specifications")
        print(f"Browse result: {result.get('status', 'unknown')}")
        
        # Test product specs search
        specs_results = tool.search_product_specs("TFE731 Engine", "Pratt & Whitney PW500")
        print(f"Product specs search: {len(specs_results.get('browsing_results', []))} sites browsed")
        
    else:
        print("Skyvern tool not enabled - check API key")