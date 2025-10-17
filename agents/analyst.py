"""
Analyst Agent - Finds competitive gaps and insights
Phase 1: Simple analysis with financial data
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class AnalystAgent:
    """Agent responsible for competitive analysis and insight generation"""
    
    def __init__(self):
        self.confidence_threshold = 0.7
        
    def analyze(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze validated data to find competitive gaps and insights
        
        Args:
            validated_data: Data validated by Validator agent
            
        Returns:
            Analysis results with competitive insights
        """
        logger.info("Analyst: Starting competitive analysis...")
        
        analysis = {
            "honeywell_product": validated_data["original_data"].get("honeywell_product"),
            "competitor_query": validated_data["original_data"].get("competitor_query"),
            "competitive_gaps": [],
            "insights": [],
            "recommendations": [],
            "confidence_score": 0.0,
            "data_sources_used": [],
            "analysis_timestamp": None,
            "raw_data": validated_data["original_data"],  # Include raw data for comprehensive PDF
            "quality_scores": validated_data.get("quality_scores", {})  # Include quality scores
        }
        
        # Get source data
        sources = validated_data["original_data"].get("sources", {})
        quality_scores = validated_data.get("quality_scores", {})
        
        # Track which sources we're using
        for source_name, score in quality_scores.items():
            if score >= 0.6:  # Use sources with 60%+ quality
                analysis["data_sources_used"].append(source_name)
        
        # Perform financial analysis
        if "yfinance_comparison" in sources:
            financial_analysis = self._analyze_financial_data(sources["yfinance_comparison"])
            analysis["competitive_gaps"].extend(financial_analysis["gaps"])
            analysis["insights"].extend(financial_analysis["insights"])
        
        # Perform individual company analysis
        if "yfinance_honeywell" in sources:
            honeywell_analysis = self._analyze_company_strengths(sources["yfinance_honeywell"], "Honeywell")
            analysis["insights"].extend(honeywell_analysis)
        
        if "yfinance_competitor" in sources:
            competitor_analysis = self._analyze_company_strengths(sources["yfinance_competitor"], "Competitor")
            analysis["insights"].extend(competitor_analysis)
        
        # Perform news/intelligence analysis
        for source_name in sources.keys():
            if "tavily" in source_name:
                news_analysis = self._analyze_news_data(sources[source_name])
                analysis["insights"].extend(news_analysis["insights"])
                analysis["competitive_gaps"].extend(news_analysis["gaps"])
                
                # Add Tavily data to data sources used
                if source_name not in analysis["data_sources_used"]:
                    analysis["data_sources_used"].append(source_name)
        
        # Perform product specifications analysis
        for source_name in sources.keys():
            if "browser_use" in source_name:
                specs_analysis = self._analyze_product_specifications(sources[source_name])
                analysis["insights"].extend(specs_analysis["insights"])
                analysis["competitive_gaps"].extend(specs_analysis["gaps"])
        
        # Generate strategic recommendations
        analysis["recommendations"] = self._generate_strategic_recommendations(analysis)
        
        # Calculate confidence score
        analysis["confidence_score"] = self._calculate_confidence_score(analysis, quality_scores)
        
        # Add timestamp
        from datetime import datetime
        analysis["analysis_timestamp"] = datetime.now().isoformat()
        
        logger.info(f"Analyst: Analysis complete. Found {len(analysis['competitive_gaps'])} gaps, {len(analysis['insights'])} insights")
        logger.info(f"Analyst: Confidence score: {analysis['confidence_score']:.2f}")
        
        return analysis
    
    def _analyze_financial_data(self, comparison_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial comparison data"""
        gaps = []
        insights = []
        
        try:
            comp = comparison_data.get("comparison", {})
            company1 = comparison_data.get("company1", {})
            company2 = comparison_data.get("company2", {})
            
            # Market cap analysis
            market_cap_ratio = comp.get("market_cap_ratio", 0)
            if market_cap_ratio > 1.5:
                gaps.append({
                    "category": "Market Position",
                    "gap": "Significant market cap advantage over competitor",
                    "metric": f"{market_cap_ratio:.1f}x larger market cap",
                    "impact": "High",
                    "opportunity": "Leverage financial strength for R&D investment"
                })
            elif market_cap_ratio < 0.7:
                gaps.append({
                    "category": "Market Position", 
                    "gap": "Smaller market cap than competitor",
                    "metric": f"{1/market_cap_ratio:.1f}x smaller market cap",
                    "impact": "Medium",
                    "opportunity": "Focus on niche markets or cost efficiency"
                })
            
            # P/E ratio analysis
            pe_diff = comp.get("pe_ratio_difference", 0)
            if abs(pe_diff) > 5:
                if pe_diff > 0:
                    gaps.append({
                        "category": "Valuation",
                        "gap": "Higher P/E ratio indicates growth expectations",
                        "metric": f"P/E ratio {pe_diff:.1f} points higher",
                        "impact": "Medium",
                        "opportunity": "Investor confidence in growth prospects"
                    })
                else:
                    gaps.append({
                        "category": "Valuation",
                        "gap": "Lower P/E ratio may indicate undervaluation",
                        "metric": f"P/E ratio {abs(pe_diff):.1f} points lower",
                        "impact": "Medium",
                        "opportunity": "Potential value investment opportunity"
                    })
            
            # Profit margin analysis
            margin_diff = comp.get("profit_margin_difference", 0)
            if margin_diff > 0.05:  # 5% difference
                gaps.append({
                    "category": "Profitability",
                    "gap": "Superior profit margins",
                    "metric": f"{margin_diff*100:.1f}% higher profit margin",
                    "impact": "High",
                    "opportunity": "Operational efficiency advantage"
                })
            elif margin_diff < -0.05:
                gaps.append({
                    "category": "Profitability",
                    "gap": "Lower profit margins than competitor",
                    "metric": f"{abs(margin_diff)*100:.1f}% lower profit margin",
                    "impact": "High",
                    "opportunity": "Focus on cost optimization and pricing"
                })
            
            # Generate insights
            if company1.get("revenue", 0) > 0 and company2.get("revenue", 0) > 0:
                revenue_ratio = company1.get("revenue", 0) / company2.get("revenue", 0)
                insights.append(f"Revenue comparison shows {'Honeywell' if revenue_ratio > 1 else 'Competitor'} has {revenue_ratio:.1f}x revenue scale")
            
            if company1.get("pe_ratio", 0) > 0 and company2.get("pe_ratio", 0) > 0:
                insights.append(f"Valuation comparison: Honeywell P/E {company1.get('pe_ratio', 0):.1f} vs Competitor P/E {company2.get('pe_ratio', 0):.1f}")
            
        except Exception as e:
            logger.error(f"Analyst: Error in financial analysis: {e}")
            gaps.append({
                "category": "Data Quality",
                "gap": "Financial analysis incomplete due to data issues",
                "metric": "N/A",
                "impact": "Medium",
                "opportunity": "Improve data collection for better analysis"
            })
        
        return {"gaps": gaps, "insights": insights}
    
    def _analyze_company_strengths(self, company_data: Dict[str, Any], company_name: str) -> List[str]:
        """Analyze individual company strengths and weaknesses"""
        insights = []
        
        try:
            # Market cap insights
            market_cap = company_data.get("market_cap", 0)
            if market_cap > 100_000_000_000:  # > $100B
                insights.append(f"{company_name} is a large-cap company with significant market presence (${market_cap/1e9:.1f}B market cap)")
            elif market_cap > 10_000_000_000:  # > $10B
                insights.append(f"{company_name} is a mid-to-large cap company (${market_cap/1e9:.1f}B market cap)")
            
            # Profitability insights
            profit_margin = company_data.get("profit_margin", 0)
            if profit_margin > 0.15:  # > 15%
                insights.append(f"{company_name} shows strong profitability with {profit_margin*100:.1f}% profit margins")
            elif profit_margin > 0.05:  # > 5%
                insights.append(f"{company_name} maintains reasonable profitability with {profit_margin*100:.1f}% profit margins")
            elif profit_margin > 0:
                insights.append(f"{company_name} has modest profitability with {profit_margin*100:.1f}% profit margins")
            
            # Valuation insights
            pe_ratio = company_data.get("pe_ratio", 0)
            if 15 <= pe_ratio <= 25:
                insights.append(f"{company_name} has reasonable valuation with P/E ratio of {pe_ratio:.1f}")
            elif pe_ratio > 25:
                insights.append(f"{company_name} has high growth expectations with P/E ratio of {pe_ratio:.1f}")
            elif 0 < pe_ratio < 15:
                insights.append(f"{company_name} appears undervalued with P/E ratio of {pe_ratio:.1f}")
            
            # Recent performance
            price_change = company_data.get("price_change_percent", 0)
            if abs(price_change) > 5:
                direction = "positive" if price_change > 0 else "negative"
                insights.append(f"{company_name} shows {direction} recent performance with {price_change:.1f}% price change")
            
        except Exception as e:
            logger.error(f"Analyst: Error analyzing {company_name}: {e}")
            insights.append(f"Limited analysis available for {company_name} due to data constraints")
        
        return insights
    
    def _analyze_news_data(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze news and intelligence data for competitor recent activity"""
        insights = []
        gaps = []
        
        try:
            news_items = news_data.get("news_items", [])
            if not news_items:
                return {"insights": insights, "gaps": gaps}
            
            # Analyze news content for competitive insights and recent activity
            competitor_activity = []
            technology_trends = []
            market_developments = []
            
            for item in news_items[:5]:  # Analyze top 5 results
                title = item.get("title", "").lower()
                content = item.get("content", "").lower()
                url = item.get("url", "")
                
                # Look for recent activity indicators
                recent_keywords = ["announced", "launched", "signed", "partnership", "contract", "deal", "investment", "expansion"]
                if any(keyword in title or keyword in content for keyword in recent_keywords):
                    competitor_activity.append(f"Recent activity: {item.get('title', 'Untitled')[:80]}...")
                
                # Look for technology trends
                tech_keywords = ["technology", "innovation", "development", "breakthrough", "new engine", "next generation"]
                if any(keyword in title or keyword in content for keyword in tech_keywords):
                    technology_trends.append(f"Technology trend: {item.get('title', 'Untitled')[:70]}...")
                
                # Look for market developments
                market_keywords = ["market share", "competition", "competitive", "advantage", "disadvantage", "pricing"]
                if any(keyword in title or keyword in content for keyword in market_keywords):
                    market_developments.append(f"Market development: {item.get('title', 'Untitled')[:70]}...")
            
            # Add insights based on findings
            insights.extend(competitor_activity[:3])  # Top 3 recent activities
            insights.extend(technology_trends[:2])   # Top 2 tech trends
            insights.extend(market_developments[:2])  # Top 2 market developments
            
            # Generate gaps based on news patterns
            if len(news_items) >= 3:
                insights.append(f"Strong industry coverage with {len(news_items)} relevant articles found")
            elif len(news_items) >= 1:
                gaps.append({
                    "category": "Market Intelligence",
                    "gap": "Limited recent news coverage",
                    "metric": f"Only {len(news_items)} relevant articles",
                    "impact": "Medium",
                    "opportunity": "Monitor industry news more closely for competitive intelligence"
                })
            
            # Add specific competitor activity insights
            if competitor_activity:
                insights.append(f"Competitor recent activity detected: {len(competitor_activity)} developments found")
            
        except Exception as e:
            logger.error(f"Analyst: Error in news analysis: {e}")
            insights.append("News analysis incomplete due to data processing issues")
        
        return {"insights": insights, "gaps": gaps}
    
    def _analyze_product_specifications(self, specs_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze product specifications data"""
        insights = []
        gaps = []
        
        try:
            browsing_results = specs_data.get("browsing_results", [])
            if not browsing_results:
                return {"insights": insights, "gaps": gaps}
            
            # Analyze each browsing result
            for result in browsing_results:
                structured_data = result.get("structured_data", {})
                if not structured_data:
                    continue
                
                # Analyze specifications
                specs = structured_data.get("specs", [])
                if specs:
                    insights.append(f"Product specifications found: {len(specs)} key features identified")
                    
                    # Look for specific technical advantages
                    for spec in specs:
                        spec_lower = spec.lower()
                        if any(keyword in spec_lower for keyword in ["thrust", "power", "efficiency"]):
                            insights.append(f"Technical specification: {spec[:60]}...")
                
                # Analyze pricing information
                price = structured_data.get("price", "")
                if price and price != "Not found" and price != "Not available":
                    insights.append(f"Pricing information available: {price}")
                else:
                    gaps.append({
                        "category": "Pricing Intelligence",
                        "gap": "Product pricing not publicly available",
                        "metric": "Price data missing",
                        "impact": "Medium",
                        "opportunity": "Consider alternative pricing research methods"
                    })
                
                # Analyze release date
                date = structured_data.get("date", "")
                if date and date != "Not found":
                    insights.append(f"Product timeline: First flight/launch in {date}")
            
            if not insights:
                gaps.append({
                    "category": "Product Intelligence",
                    "gap": "Limited product specification data",
                    "metric": "Specifications not found",
                    "impact": "High",
                    "opportunity": "Expand product research sources"
                })
            
        except Exception as e:
            logger.error(f"Analyst: Error in product specifications analysis: {e}")
            insights.append("Product specifications analysis incomplete due to data processing issues")
        
        return {"insights": insights, "gaps": gaps}
    
    def _generate_strategic_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations based on analysis"""
        recommendations = []
        
        gaps = analysis.get("competitive_gaps", [])
        insights = analysis.get("insights", [])
        
        # Categorize gaps by impact
        high_impact_gaps = [gap for gap in gaps if gap.get("impact") == "High"]
        medium_impact_gaps = [gap for gap in gaps if gap.get("impact") == "Medium"]
        
        if high_impact_gaps:
            recommendations.append("Focus on high-impact competitive gaps identified in financial analysis")
        
        if medium_impact_gaps:
            recommendations.append("Consider medium-impact opportunities for strategic advantage")
        
        # General recommendations based on insights
        if any("profitability" in insight.lower() for insight in insights):
            recommendations.append("Monitor and improve operational efficiency metrics")
        
        if any("market cap" in insight.lower() for insight in insights):
            recommendations.append("Leverage market position for strategic investments")
        
        if any("valuation" in insight.lower() for insight in insights):
            recommendations.append("Consider valuation metrics in strategic planning")
        
        if not recommendations:
            recommendations.append("Continue monitoring competitive landscape for emerging opportunities")
        
        return recommendations
    
    def _calculate_confidence_score(self, analysis: Dict[str, Any], quality_scores: Dict[str, float]) -> float:
        """Calculate confidence score for the analysis (0.0 to 1.0)"""
        if not quality_scores:
            return 0.0
        
        # Base confidence on data quality
        avg_quality = sum(quality_scores.values()) / len(quality_scores)
        
        # Adjust based on number of insights and gaps found
        insights_count = len(analysis.get("insights", []))
        gaps_count = len(analysis.get("competitive_gaps", []))
        
        # More insights and gaps generally indicate better analysis
        insight_bonus = min(0.2, (insights_count + gaps_count) * 0.02)
        
        # Bonus for data source diversity
        source_types = set()
        for source_name in analysis.get("data_sources_used", []):
            if "yfinance" in source_name:
                source_types.add("financial")
            elif "tavily" in source_name:
                source_types.add("news")
            elif "browser_use" in source_name:
                source_types.add("specifications")
        
        diversity_bonus = min(0.15, len(source_types) * 0.05)
        
        # Penalty for low-quality sources
        low_quality_penalty = 0.0
        for score in quality_scores.values():
            if score < 0.3:
                low_quality_penalty += 0.1
        
        # Calculate final confidence
        confidence = min(1.0, avg_quality + insight_bonus + diversity_bonus - low_quality_penalty)
        
        # Ensure minimum confidence if we have any data
        if insights_count > 0 or gaps_count > 0:
            confidence = max(0.3, confidence)
        
        return confidence

# Example usage for testing
if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from agents.scout import ScoutAgent
    from agents.validator import ValidatorAgent
    
    # Test analysis
    scout = ScoutAgent()
    validator = ValidatorAgent()
    analyst = AnalystAgent()
    
    # Get and validate data
    raw_data = scout.hunt("TFE731 Engine", "compare with Pratt & Whitney PW500")
    validated_data = validator.validate(raw_data)
    
    # Analyze it
    analysis = analyst.analyze(validated_data)
    
    print("Analysis Results:")
    print(f"Competitive gaps found: {len(analysis['competitive_gaps'])}")
    print(f"Insights generated: {len(analysis['insights'])}")
    print(f"Confidence score: {analysis['confidence_score']:.2f}")
    print(f"Recommendations: {len(analysis['recommendations'])}")
    
    if analysis['competitive_gaps']:
        print("\nTop competitive gaps:")
        for gap in analysis['competitive_gaps'][:2]:
            print(f"- {gap['gap']}: {gap['opportunity']}")
