"""
Validator Agent - Checks data quality and requests more if needed
Phase 1: Simple validation, max tries 2
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class ValidatorAgent:
    """Agent responsible for validating data quality"""
    
    def __init__(self):
        self.max_retries = 2
        self.retry_count = 0
        
    def validate(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the gathered data and determine if more data is needed
        
        Args:
            raw_data: Data gathered by Scout agent
            
        Returns:
            Validated data with quality scores and recommendations
        """
        logger.info("Validator: Starting data validation...")
        
        validated_data = {
            "original_data": raw_data,
            "quality_scores": {},
            "validation_results": {},
            "recommendations": [],
            "is_valid": False,
            "retry_needed": False,
            "retry_count": self.retry_count
        }
        
        # Check each data source
        sources = raw_data.get("sources", {})
        
        for source_name, source_data in sources.items():
            quality_score = self._assess_data_quality(source_name, source_data)
            validated_data["quality_scores"][source_name] = quality_score
            
            # Determine if this source is valid
            is_source_valid = quality_score >= 0.6  # 60% quality threshold
            validated_data["validation_results"][source_name] = is_source_valid
            
            if not is_source_valid:
                logger.warning(f"Validator: {source_name} failed quality check (score: {quality_score:.2f})")
        
        # Overall validation
        valid_sources = sum(1 for is_valid in validated_data["validation_results"].values() if is_valid)
        total_sources = len(validated_data["validation_results"])
        
        if total_sources > 0:
            validation_ratio = valid_sources / total_sources
            validated_data["is_valid"] = validation_ratio >= 0.5  # At least 50% of sources valid
            
            # Determine if retry is needed
            if not validated_data["is_valid"] and self.retry_count < self.max_retries:
                validated_data["retry_needed"] = True
                self.retry_count += 1
                logger.info(f"Validator: Retry needed (attempt {self.retry_count}/{self.max_retries})")
            elif not validated_data["is_valid"]:
                logger.error("Validator: Max retries reached, proceeding with available data")
        
        # Generate recommendations
        validated_data["recommendations"] = self._generate_recommendations(validated_data)
        
        logger.info(f"Validator: Validation complete. Valid: {validated_data['is_valid']}, Retry needed: {validated_data['retry_needed']}")
        
        return validated_data
    
    def _assess_data_quality(self, source_name: str, source_data: Dict[str, Any]) -> float:
        """
        Assess quality of a data source (0.0 to 1.0)
        
        Args:
            source_name: Name of the data source
            source_data: The actual data
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        score = 0.0
        max_score = 0.0
        
        # Check for errors
        if "error" in source_data:
            logger.warning(f"Validator: {source_name} has error: {source_data['error']}")
            return 0.0
        
        # yfinance specific checks
        if "yfinance" in source_name:
            max_score = 10.0
            
            # Different validation for comparison data vs individual company data
            if "comparison" in source_name:
                # For comparison data, check for company1 and company2
                if "company1" in source_data and "company2" in source_data:
                    score += 6.0  # 3 points per company
                    
                    # Check if companies have essential data
                    for company in ["company1", "company2"]:
                        comp_data = source_data.get(company, {})
                        if comp_data.get("company_name") and comp_data.get("current_price"):
                            score += 1.0
                
                # Check comparison metrics
                comparison = source_data.get("comparison", {})
                if comparison.get("market_cap_ratio"):
                    score += 1.0
                if comparison.get("pe_ratio_difference"):
                    score += 1.0
                if comparison.get("profit_margin_difference"):
                    score += 1.0
                    
            else:
                # For individual company data
                essential_fields = ["company_name", "current_price", "market_cap"]
                for field in essential_fields:
                    if field in source_data and source_data[field] is not None:
                        score += 2.0
                    else:
                        logger.warning(f"Validator: {source_name} missing essential field: {field}")
                
                # Important fields (1 point each)
                important_fields = ["sector", "industry", "pe_ratio", "revenue"]
                for field in important_fields:
                    if field in source_data and source_data[field] is not None:
                        score += 1.0
                
                # Bonus for additional data
                if source_data.get("news"):
                    score += 1.0
                
                if source_data.get("historical_data"):
                    score += 1.0
        
        # Tavily specific checks
        elif "tavily" in source_name:
            max_score = 6.0  # Reduced max score
            
            # Check for results
            if "results" in source_data and source_data["results"]:
                score += 3.0  # Base score for having results
                
                # Check result quality
                results = source_data["results"]
                if len(results) >= 1:  # Lowered threshold
                    score += 2.0  # Good number of results
                
                # Check if results have content
                for result in results[:2]:  # Check first 2 results
                    if result.get("content") and len(result.get("content", "")) > 20:  # Lowered threshold
                        score += 0.5
                    if result.get("title") and len(result.get("title", "")) > 5:  # Lowered threshold
                        score += 0.5
            else:
                logger.warning(f"Validator: {source_name} has no results")
                # Give partial credit if there's any data structure
                if source_data:
                    score += 1.0  # Partial credit for having some data
        
        # Browser-use specific checks
        elif "browser_use" in source_name:
            max_score = 6.0
            
            # Check for browsing results
            if "browsing_results" in source_data:
                browsing_results = source_data["browsing_results"]
                if browsing_results:
                    score += 2.0  # Base score for having results
                    
                    # Check each browsing result
                    for result in browsing_results:
                        if result.get("status") == "completed":
                            score += 1.0
                        
                        # Check for extracted data
                        if result.get("structured_data"):
                            structured_data = result["structured_data"]
                            if structured_data.get("specs") and len(structured_data["specs"]) > 0:
                                score += 1.0
                            if structured_data.get("price") and structured_data["price"] != "Not found":
                                score += 1.0
                            if structured_data.get("date") and structured_data["date"] != "Not found":
                                score += 1.0
            else:
                logger.warning(f"Validator: {source_name} has no browsing results")
        
        final_score = score / max_score if max_score > 0 else 0.0
        logger.debug(f"Validator: {source_name} quality score: {final_score:.2f}")
        
        return min(1.0, max(0.0, final_score))
    
    def _generate_recommendations(self, validated_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        quality_scores = validated_data.get("quality_scores", {})
        validation_results = validated_data.get("validation_results", {})
        
        # Check for low-quality sources
        for source_name, score in quality_scores.items():
            if score < 0.6:
                recommendations.append(f"Consider retrying {source_name} (quality score: {score:.2f})")
        
        # Check for missing critical data
        original_data = validated_data.get("original_data", {})
        sources = original_data.get("sources", {})
        
        if not sources:
            recommendations.append("No data sources available - scout may need to retry all tools")
        
        # Check for competitor data specifically
        if "yfinance_competitor" not in sources:
            recommendations.append("Missing competitor financial data - may affect analysis quality")
        
        # Check for news/intelligence data
        if not any("tavily" in source for source in sources.keys()):
            recommendations.append("Missing news/intelligence data - consider adding Tavily search")
        
        # Check for product specifications
        if not any("browser_use" in source for source in sources.keys()):
            recommendations.append("Missing product specifications - consider adding browser-use search")
        
        # Check data diversity
        source_types = set()
        for source_name in sources.keys():
            if "yfinance" in source_name:
                source_types.add("financial")
            elif "tavily" in source_name:
                source_types.add("news")
            elif "browser_use" in source_name:
                source_types.add("specifications")
        
        if len(source_types) < 2:
            recommendations.append("Limited data diversity - consider adding more data sources")
        
        if not recommendations:
            recommendations.append("Data quality is acceptable for analysis")
        
        return recommendations
    
    def reset_retry_count(self):
        """Reset retry count for new validation cycle"""
        self.retry_count = 0
        logger.info("Validator: Retry count reset")

# Example usage for testing
if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from agents.scout import ScoutAgent
    
    # Test validation
    scout = ScoutAgent()
    validator = ValidatorAgent()
    
    # Get some data to validate
    raw_data = scout.hunt("TFE731 Engine", "compare with Pratt & Whitney PW500")
    
    # Validate it
    validated_data = validator.validate(raw_data)
    
    print("Validation Results:")
    print(f"Is valid: {validated_data['is_valid']}")
    print(f"Retry needed: {validated_data['retry_needed']}")
    print(f"Quality scores: {validated_data['quality_scores']}")
    print(f"Recommendations: {validated_data['recommendations']}")
