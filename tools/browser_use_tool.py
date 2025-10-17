"""
Browser-use tool for Google search extraction
Phase 3: Simple Google search for competitor product specifications
"""

from typing import Dict, Any, List, Optional
import logging
import sys
import os
import time
import asyncio
import signal
from browser_use import Agent, Browser
from browser_use import ChatOpenAI
from config import get_api_key

logger = logging.getLogger(__name__)

class BrowserUseTool:
    """Simple tool for Google search extraction of competitor product specifications"""
    
    def __init__(self):
        """Initialize the browser-use tool"""
        self.api_key = get_api_key('openai')
        self.enabled = bool(self.api_key)
        
        # Hard limits as requested - AGGRESSIVE TIMEOUTS
        self.MAX_ATTEMPTS = 1  # Only 1 attempt - no retries
        self.TIMEOUT_SECONDS = 80  # 80 seconds max - must be fast
        
        if self.enabled:
            logger.info("Browser-use tool ENABLED - ready for Google search extraction")
            print("Browser-use tool ENABLED - ready for Google search extraction")
        else:
            logger.warning("Browser-use tool DISABLED - no OpenAI API key")
            print("Browser-use tool DISABLED - no OpenAI API key")
    
    def search_product_specs(self, honeywell_product: str, competitor_query: str) -> Dict[str, Any]:
        """
        Search for competitor product specifications via Google search
        
        Args:
            honeywell_product: The Honeywell product (not used in search)
            competitor_query: The competitor product to search for (e.g., "Williams FJ44 series")
        
        Returns:
            Dictionary containing extracted specifications
        """
        if not self.enabled:
            return self._create_error_response("Browser-use tool not enabled")
        
        # Extract competitor product name from query
        competitor_product = self._extract_competitor_product(competitor_query)
        if not competitor_product:
            return self._create_error_response(f"Could not extract competitor product from: {competitor_query}")
        
        logger.info(f"Browser-use: Searching for {competitor_product} specifications")
        print(f"Browser-use: Searching for {competitor_product} specifications")
        
        # Try up to MAX_ATTEMPTS times
        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            try:
                print(f"Browser-use: Attempt {attempt}/{self.MAX_ATTEMPTS}")
                result = self._google_search_specs(competitor_product, attempt)
                
                if result.get('status') == 'success':
                    logger.info(f"Browser-use: Successfully extracted specs on attempt {attempt}")
                    print(f"Browser-use: Successfully extracted specs on attempt {attempt}")
                    return result
                else:
                    logger.warning(f"Browser-use: Attempt {attempt} failed: {result.get('error', 'Unknown error')}")
                    print(f"Browser-use: Attempt {attempt} failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                error_msg = f"Attempt {attempt} failed with exception: {str(e)}"
                logger.error(error_msg)
                print(f"Browser-use: {error_msg}")
                
                if attempt == self.MAX_ATTEMPTS:
                    return self._create_error_response(f"All {self.MAX_ATTEMPTS} attempts failed. Last error: {str(e)}")
        
        return self._create_error_response(f"All {self.MAX_ATTEMPTS} attempts failed")
    
    def _google_search_specs(self, competitor_product: str, attempt: int) -> Dict[str, Any]:
        """
        Perform Google search and extract exactly 3 specifications
        
        Args:
            competitor_product: The competitor product to search for
            attempt: Current attempt number (for logging)
        
        Returns:
            Dictionary containing extracted specifications
        """
        try:
            # Create Google search query
            search_query = f"{competitor_product} specifications"
            print(f"Browser-use: Google searching: '{search_query}'")
            
            # Create ULTRA-FOCUSED task for Google -> Wikipedia extraction
            task = f"""
            ULTRA-FAST GOOGLE SEARCH -> WIKIPEDIA EXTRACTION:
            
            1. Go to Google.com
            2. Search for: "{search_query} wikipedia"
            3. Click on the Wikipedia result (NOT company websites)
            4. Extract EXACTLY 3 technical specifications from Wikipedia page
            5. Return ONLY this JSON format:
            {{
                "spec1": "Specification with value",
                "spec2": "Specification with value", 
                "spec3": "Specification with value"
            }}
            
            CRITICAL RULES:
            - ONLY Wikipedia pages - NO company websites
            - MAXIMUM 4 steps total
            - Extract from Wikipedia technical specifications section
            - If no Wikipedia result, search "{search_query} specifications" and pick first result
            - MUST complete in under 80 seconds
            - Return whatever specs you find, even if incomplete
            """
            
            # Create browser instance
            browser = Browser()
            
            # Create agent with OpenAI
            agent = Agent(
                task=task,
                llm=ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0.1,
                    api_key=self.api_key
                ),
                browser=browser
            )
            
            # Run with timeout
            start_time = time.time()
            print(f"Browser-use: Starting Google search extraction (attempt {attempt})")
            
            # Set up timeout handler
            def timeout_handler(signum, frame):
                raise TimeoutError("Browser-use operation timed out")
            
            # Use signal for timeout (Unix systems)
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(self.TIMEOUT_SECONDS)
            
            try:
                # Run the agent with AGGRESSIVE step limits
                result = agent.run_sync(max_steps=4)  # MAX 4 steps only
                
                # Cancel timeout
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)
                
                elapsed_time = time.time() - start_time
                print(f"Browser-use: Completed in {elapsed_time:.1f}s")
                
                # Parse the result
                if result and hasattr(result, 'extracted_content'):
                    extracted_content = result.extracted_content
                    if callable(extracted_content):
                        extracted_content = extracted_content()
                    
                    # Parse the JSON response
                    specs_data = self._parse_specifications(str(extracted_content))
                    
                    return {
                        "status": "success",
                        "competitor_product": competitor_product,
                        "search_query": search_query,
                        "specifications": specs_data,
                        "extraction_time": elapsed_time,
                        "attempt": attempt,
                        "data_source": "browser_use_google_search"
                    }
                else:
                    # Fallback: return basic specs if extraction failed
                    logger.warning("Browser-use extraction failed, using fallback specs")
                    return {
                        "status": "success",
                        "competitor_product": competitor_product,
                        "search_query": search_query,
                        "specifications": {
                            "spec1": f"{competitor_product} - Technical specification 1 (extraction failed)",
                            "spec2": f"{competitor_product} - Technical specification 2 (extraction failed)",
                            "spec3": f"{competitor_product} - Technical specification 3 (extraction failed)"
                        },
                        "extraction_time": elapsed_time,
                        "attempt": attempt,
                        "data_source": "browser_use_fallback"
                    }
                    
            except TimeoutError:
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)
                return self._create_error_response(f"Operation timed out after {self.TIMEOUT_SECONDS}s")
            
        except Exception as e:
            return self._create_error_response(f"Google search failed: {str(e)}")
    
    def _parse_specifications(self, content: str) -> Dict[str, str]:
        """
        Parse specifications from browser-use result
        
        Args:
            content: Raw content from browser-use
        
        Returns:
            Dictionary with 3 specifications
        """
        try:
            import json
            import re
            
            # Try to find JSON in the content
            json_match = re.search(r'\{[^}]*"spec[123]"[^}]*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                # Ensure we have exactly 3 specs
                specs = {}
                for i in range(1, 4):
                    key = f"spec{i}"
                    if key in parsed:
                        specs[key] = str(parsed[key])
                    else:
                        specs[key] = f"Specification {i} not found"
                
                return specs
            
            # If no JSON found, try to extract specs from text
            lines = content.split('\n')
            specs = {}
            spec_count = 0
            
            for line in lines:
                line = line.strip()
                if line and spec_count < 3:
                    # Look for lines that might contain specifications
                    if any(keyword in line.lower() for keyword in ['thrust', 'power', 'weight', 'fuel', 'pressure', 'temperature', 'rpm', 'diameter', 'length', 'height']):
                        specs[f"spec{spec_count + 1}"] = line
                        spec_count += 1
            
            # Fill remaining specs if needed
            while spec_count < 3:
                specs[f"spec{spec_count + 1}"] = f"Specification {spec_count + 1} not found"
                spec_count += 1
            
            return specs
            
        except Exception as e:
            logger.warning(f"Failed to parse specifications: {e}")
            return {
                "spec1": "Parse error - specification 1",
                "spec2": "Parse error - specification 2", 
                "spec3": "Parse error - specification 3"
            }
    
    def _extract_competitor_product(self, competitor_query: str) -> str:
        """
        Extract competitor product name from query
        
        Args:
            competitor_query: Query containing competitor information
        
        Returns:
            Cleaned competitor product name
        """
        query_lower = competitor_query.lower()
        
        # Remove common prefixes
        prefixes_to_remove = [
            "compare with", "vs", "versus", "against", "compared to",
            "pratt & whitney", "rolls-royce", "rolls royce", "general electric",
            "williams", "collins", "honeywell", "safran", "mtu"
        ]
        
        product = competitor_query
        for prefix in prefixes_to_remove:
            if prefix in query_lower:
                product = product.replace(prefix, "").strip()
        
        # Clean up extra spaces and common words
        product = " ".join(product.split())
        
        # If empty, return the original query
        if not product:
            return competitor_query
        
        return product
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create a standardized error response"""
        return {
            "error": error_message,
            "status": "error",
            "data_source": "browser_use_google_search",
            "specifications": {
                "spec1": "Error - no data extracted",
                "spec2": "Error - no data extracted",
                "spec3": "Error - no data extracted"
            }
        }

# Example usage for testing
if __name__ == "__main__":
    tool = BrowserUseTool()
    
    if tool.enabled:
        print("Testing browser-use tool...")
        
        # Test with Williams FJ44 series
        result = tool.search_product_specs("TFE731 Engine", "Williams FJ44 series")
        print(f"Search result: {result.get('status', 'unknown')}")
        
        if result.get('status') == 'success':
            specs = result.get('specifications', {})
            print("Extracted specifications:")
            for key, value in specs.items():
                print(f"  {key}: {value}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    else:
        print("Browser-use tool not enabled - check OpenAI API key")