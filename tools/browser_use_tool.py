"""
Browser-use tool for agentic browsing
Phase 3: Multi-source data gathering - REPLACEMENT FOR SKYVERN
"""

from typing import Dict, Any, List, Optional
import logging
import sys
import os
import asyncio
import signal
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_api_key

logger = logging.getLogger(__name__)

class BrowserUseTool:
    """Tool for agentic browsing using browser-use library with strict constraints"""
    
    def __init__(self):
        self.api_key = get_api_key('openai')
        if not self.api_key:
            logger.warning("OpenAI API key not found - browser-use tool will be disabled")
            self.enabled = False
        else:
            self.enabled = True
            try:
                # Import browser-use components
                from browser_use import Agent
                from browser_use.llm import ChatOpenAI
                self.Agent = Agent
                self.ChatOpenAI = ChatOpenAI
                
                # Set environment variable for browser-use
                os.environ['OPENAI_API_KEY'] = self.api_key
                
                # Configuration constants - OPTIMIZED FOR SPEED
                self.MAX_STEPS = 8  # Reduced from 15 - faster execution
                self.MAX_ACTIONS_PER_STEP = 3  # Allow more actions per step
                self.TIMEOUT_SECONDS = 60  # Reduced from 120 - faster timeout
                self.MAX_NAVIGATION_ATTEMPTS = 1  # Only 1 attempt per site
                self.MAX_SITES_TO_BROWSE = 1  # Only browse 1 site max
                self.KEEP_BROWSER_OPEN = True  # Keep browser session persistent
                
                logger.info("Browser-use tool initialized successfully with constraints")
            except Exception as e:
                logger.error(f"Failed to initialize browser-use tool: {e}")
                self.enabled = False
    
    def browse_website(self, url: str, prompt: str) -> Dict[str, Any]:
        """
        Browse a website and extract information using browser-use with strict constraints
        
        Args:
            url: The URL to browse
            prompt: What to look for on the website
        
        Returns:
            Dictionary containing browsing results
        """
        if not self.enabled:
            return self._create_error_response("Browser-use tool not enabled")
        
        try:
            logger.info(f"Browser-use: Browsing {url} for: {prompt}")
            print(f"Browser-use: Starting controlled browsing of {url}")
            print(f"Task: {prompt}")
            print(f"Timeout: {self.TIMEOUT_SECONDS}s, Max steps: {self.MAX_STEPS}")
            
            # Create structured task with DATA EXTRACTION FOCUS
            structured_task = f"""
            FAST DATA EXTRACTION - SPEED OPTIMIZED:
            
            1. Navigate to {url} - ONE TIME ONLY
            2. Find product specifications - MAX 8 steps
            3. EXTRACT and RETURN as JSON: {{'price': 'X', 'specs': ['spec1', 'spec2'], 'date': 'Y'}}
            4. Use SAME browser window throughout
            5. Return whatever data you find, even if incomplete
            6. STOP immediately after extracting data
            
            SPEED PRIORITY: Quick extraction over perfect data
            """
            
            # Suppress browser-use logging noise
            import logging
            browser_logger = logging.getLogger('browser_use')
            browser_logger.setLevel(logging.ERROR)  # Only show errors, hide info logs
            
            # Create agent with OpenAI - simplified configuration
            agent = self.Agent(
                task=structured_task,
                llm=self.ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
            )
            
            # Run with timeout and step limits - HARD ENFORCEMENT
            start_time = time.time()
            result = None
            step_count = 0
            
            try:
                # Set up timeout
                def timeout_handler(signum, frame):
                    raise TimeoutError("Browser-use operation timed out")
                
                # Use signal for timeout (Unix systems)
                if hasattr(signal, 'SIGALRM'):
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(self.TIMEOUT_SECONDS)
                
                # Run the agent with optimized settings for data extraction
                print(f"DATA EXTRACTION MODE: Maximum {self.MAX_STEPS} steps allowed")
                result = agent.run_sync(max_steps=self.MAX_STEPS)
                
                # Cancel timeout
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)
                
                elapsed_time = time.time() - start_time
                print(f"Browser-use completed in {elapsed_time:.1f}s (DATA EXTRACTION MODE)")
                
            except TimeoutError:
                logger.warning(f"Browser-use timed out after {self.TIMEOUT_SECONDS}s")
                print(f"Browser-use timed out after {self.TIMEOUT_SECONDS}s")
                return self._create_error_response(f"Operation timed out after {self.TIMEOUT_SECONDS}s")
            except Exception as e:
                logger.error(f"Browser-use execution failed: {e}")
                print(f"Browser-use execution failed: {e}")
                return self._create_error_response(f"Execution failed: {str(e)}")
            
            if result and hasattr(result, 'extracted_content'):
                logger.info("Browser-use: Task completed successfully")
                print(f"Browser-use: Task completed successfully")
                
                # Try to parse structured output
                extracted_data = self._parse_structured_output(result.extracted_content)
                
                return {
                    "url": url,
                    "prompt": prompt,
                    "status": "completed",
                    "data_source": "browser_use",
                    "extracted_content": result.extracted_content,
                    "structured_data": extracted_data,
                    "browsing_results": [{
                        "url": url,
                        "prompt": prompt,
                        "status": "completed",
                        "extracted_data": extracted_data
                    }]
                }
            else:
                error_msg = "Browser-use task failed to complete"
                logger.error(error_msg)
                print(f"Browser-use task failed to complete")
                return self._create_error_response(error_msg)
                
        except Exception as e:
            error_msg = f"Browser-use browsing failed: {str(e)}"
            logger.error(error_msg)
            print(f"Browser-use browsing failed: {str(e)}")
            return self._create_error_response(error_msg)
    
    def _parse_structured_output(self, content: str) -> Dict[str, Any]:
        """Parse structured output from browser-use agent"""
        try:
            import json
            import re
            
            # Try to find JSON in the content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                return parsed
            
            # If no JSON found, create structured data from content
            return {
                "price": "Not found",
                "specs": [content[:200] + "..." if len(content) > 200 else content],
                "date": "Not found",
                "raw_content": content
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse structured output: {e}")
            return {
                "price": "Parse error",
                "specs": ["Failed to parse structured data"],
                "date": "Parse error",
                "raw_content": content
            }
    
    def search_product_specs(self, honeywell_product: str, competitor_query: str) -> Dict[str, Any]:
        """Search for product specifications and technical data with controlled browsing"""
        if not self.enabled:
            return self._create_error_response("Browser-use tool not enabled")
        
        try:
            logger.info(f"Browser-use: Searching product specs for {honeywell_product} vs {competitor_query}")
            print(f"Browser-use: Starting product specs search")
            print(f"Honeywell Product: {honeywell_product}")
            print(f"Competitor Query: {competitor_query}")
            
            # Define target websites for aerospace products - HARD LIMIT: 2 sites max
            target_sites = [
                "https://aerospace.honeywell.com",
                "https://www.prattwhitney.com"
            ]
            
            # Enforce hard limit
            if len(target_sites) > self.MAX_SITES_TO_BROWSE:
                target_sites = target_sites[:self.MAX_SITES_TO_BROWSE]
                print(f"HARD GUARDRAIL: Limited to {self.MAX_SITES_TO_BROWSE} sites maximum")
            
            all_results = {
                "honeywell_product": honeywell_product,
                "competitor_query": competitor_query,
                "browsing_results": [],
                "data_source": "browser_use",
                "search_type": "product_specs"
            }
            
            # Browse each site for relevant information - HARD LIMITS ENFORCED
            successful_browses = 0
            max_attempts_per_site = 1  # Only 1 attempt per site
            
            for i, site in enumerate(target_sites):
                if successful_browses >= self.MAX_SITES_TO_BROWSE:
                    print(f"HARD GUARDRAIL: Reached maximum sites limit ({self.MAX_SITES_TO_BROWSE})")
                    break
                    
                try:
                    print(f"Browser-use: Browsing site {i+1}/{len(target_sites)}: {site}")
                    print(f"HARD GUARDRAIL: Maximum {max_attempts_per_site} attempt per site")
                    
                    if "honeywell" in site:
                        prompt = f"""DATA EXTRACTION TASK for {honeywell_product}:
                        1. Navigate to {site} - ONE TIME ONLY
                        2. Find {honeywell_product} specifications - take up to {self.MAX_STEPS} steps
                        3. EXTRACT and RETURN as JSON: {{'price': 'X', 'specs': ['spec1', 'spec2', 'spec3'], 'date': 'Y'}}
                        4. DO NOT close browser between steps - use SAME browser window
                        5. Return whatever data you find, even if incomplete
                        6. STOP immediately after extracting data"""
                    elif "prattwhitney" in site:
                        prompt = f"""DATA EXTRACTION TASK for Pratt & Whitney engines:
                        1. Navigate to {site} - ONE TIME ONLY  
                        2. Find engine specifications - take up to {self.MAX_STEPS} steps
                        3. EXTRACT and RETURN as JSON: {{'price': 'X', 'specs': ['spec1', 'spec2', 'spec3'], 'date': 'Y'}}
                        4. DO NOT close browser between steps - use SAME browser window
                        5. Return whatever data you find, even if incomplete
                        6. STOP immediately after extracting data"""
                    else:
                        prompt = f"""DATA EXTRACTION TASK for aerospace engines:
                        1. Navigate to {site} - ONE TIME ONLY
                        2. Find engine specifications - take up to {self.MAX_STEPS} steps  
                        3. EXTRACT and RETURN as JSON: {{'price': 'X', 'specs': ['spec1', 'spec2', 'spec3'], 'date': 'Y'}}
                        4. DO NOT close browser between steps - use SAME browser window
                        5. Return whatever data you find, even if incomplete
                        6. STOP immediately after extracting data"""
                    
                    result = self.browse_website(site, prompt)
                    all_results["browsing_results"].append(result)
                    successful_browses += 1
                    
                    # Add small delay between sites to avoid overwhelming
                    if i < len(target_sites) - 1:
                        time.sleep(2)  # Increased delay for stability
                    
                except Exception as e:
                    logger.warning(f"Browser-use browsing failed for {site}: {e}")
                    print(f"Browser-use failed for {site}: {e}")
                    all_results["browsing_results"].append(self._create_error_response(f"Failed to browse {site}: {e}"))
                    # Continue to next site even if this one failed
            
            print(f"Browser-use: Product specs search completed")
            return all_results
            
        except Exception as e:
            logger.error(f"Browser-use product specs search failed: {e}")
            print(f"Browser-use product specs search failed: {e}")
            return self._create_error_response(f"Product specs search failed: {e}")
    
    def get_market_data(self, query: str) -> Dict[str, Any]:
        """Get market data and industry insights with controlled browsing"""
        if not self.enabled:
            return self._create_error_response("Browser-use tool not enabled")
        
        try:
            logger.info(f"Browser-use: Getting market data for '{query}'")
            print(f"Browser-use: Starting market data search for '{query}'")
            
            # Target market research sites - HARD LIMIT: 1 site only
            market_sites = [
                "https://www.marketresearch.com"
            ]
            
            # Enforce hard limit
            if len(market_sites) > 1:
                market_sites = market_sites[:1]
                print(f"HARD GUARDRAIL: Limited to 1 market site maximum")
            
            all_results = {
                "query": query,
                "market_data": [],
                "data_source": "browser_use",
                "search_type": "market_data"
            }
            
            for i, site in enumerate(market_sites):
                try:
                    print(f"Browser-use: Browsing market site {i+1}/{len(market_sites)}: {site}")
                    
                    prompt = f"""DATA EXTRACTION TASK for market research:
                    1. Navigate to {site} - ONE TIME ONLY
                    2. Find market research for {query} - take up to {self.MAX_STEPS} steps
                    3. EXTRACT and RETURN as JSON: {{'market_size': 'X', 'growth_rate': 'Y', 'trends': ['trend1', 'trend2']}}
                    4. DO NOT close browser between steps - use SAME browser window
                    5. Return whatever data you find, even if incomplete
                    6. STOP immediately after extracting data"""
                    result = self.browse_website(site, prompt)
                    all_results["market_data"].append(result)
                    
                except Exception as e:
                    logger.warning(f"Browser-use market data search failed for {site}: {e}")
                    print(f"Browser-use failed for {site}: {e}")
                    all_results["market_data"].append(self._create_error_response(f"Failed to browse {site}: {e}"))
            
            print(f"Browser-use: Market data search completed")
            return all_results
            
        except Exception as e:
            logger.error(f"Browser-use market data search failed: {e}")
            print(f"Browser-use market data search failed: {e}")
            return self._create_error_response(f"Market data search failed: {e}")
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create a standardized error response"""
        return {
            "error": error_message,
            "status": "error",
            "data_source": "browser_use"
        }

# Example usage for testing
if __name__ == "__main__":
    tool = BrowserUseTool()
    
    if tool.enabled:
        print("Testing browser-use tool...")
        
        # Test simple browsing
        result = tool.browse_website("https://aerospace.honeywell.com", "Find TFE731 engine specifications")
        print(f"Browse result: {result.get('status', 'unknown')}")
        
        # Test product specs search
        specs_results = tool.search_product_specs("TFE731 Engine", "Pratt & Whitney PW500")
        print(f"Product specs search: {len(specs_results.get('browsing_results', []))} sites browsed")
        
    else:
        print("Browser-use tool not enabled - check OpenAI API key")
