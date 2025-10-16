"""
yfinance tool for gathering financial data
Phase 1: Simple implementation for Honeywell and competitor data
"""

import yfinance as yf
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class YFinanceTool:
    """Tool for gathering financial data using yfinance"""
    
    def __init__(self):
        self.honeywell_ticker = "HON"  # Honeywell International Inc.
    
    def get_company_data(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive company data from yfinance"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get basic info
            info = stock.info
            hist = stock.history(period="1y")  # 1 year of data
            
            # Get recent news (if available)
            news = []
            try:
                news = stock.news[:5]  # Last 5 news items
            except:
                logger.warning(f"No news available for {ticker}")
            
            return {
                "ticker": ticker,
                "company_name": info.get("longName", ticker),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "market_cap": info.get("marketCap", 0),
                "current_price": info.get("currentPrice", 0),
                "price_change": info.get("regularMarketChange", 0),
                "price_change_percent": info.get("regularMarketChangePercent", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "revenue": info.get("totalRevenue", 0),
                "profit_margin": info.get("profitMargins", 0),
                "52_week_high": info.get("fiftyTwoWeekHigh", 0),
                "52_week_low": info.get("fiftyTwoWeekLow", 0),
                "volume": info.get("volume", 0),
                "avg_volume": info.get("averageVolume", 0),
                "historical_data": hist.to_dict() if not hist.empty else {},
                "news": news,
                "data_source": "yfinance",
                "timestamp": stock.history(period="1d").index[-1].isoformat() if not hist.empty else None
            }
            
        except Exception as e:
            logger.error(f"Error getting data for {ticker}: {e}")
            return {
                "ticker": ticker,
                "error": str(e),
                "data_source": "yfinance"
            }
    
    def get_honeywell_data(self) -> Dict[str, Any]:
        """Get Honeywell specific data"""
        return self.get_company_data(self.honeywell_ticker)
    
    def get_competitor_data(self, competitor_ticker: str) -> Dict[str, Any]:
        """Get competitor data"""
        return self.get_company_data(competitor_ticker)
    
    def compare_companies(self, ticker1: str, ticker2: str) -> Dict[str, Any]:
        """Compare two companies side by side"""
        data1 = self.get_company_data(ticker1)
        data2 = self.get_company_data(ticker2)
        
        return {
            "company1": data1,
            "company2": data2,
            "comparison": {
                "market_cap_ratio": data1.get("market_cap", 0) / data2.get("market_cap", 1) if data2.get("market_cap", 0) > 0 else 0,
                "price_ratio": data1.get("current_price", 0) / data2.get("current_price", 1) if data2.get("current_price", 0) > 0 else 0,
                "pe_ratio_difference": data1.get("pe_ratio", 0) - data2.get("pe_ratio", 0),
                "profit_margin_difference": data1.get("profit_margin", 0) - data2.get("profit_margin", 0)
            }
        }

# Example usage for testing
if __name__ == "__main__":
    tool = YFinanceTool()
    
    # Test Honeywell data
    print("Honeywell Data:")
    hon_data = tool.get_honeywell_data()
    print(f"Company: {hon_data.get('company_name')}")
    print(f"Price: ${hon_data.get('current_price', 0):.2f}")
    print(f"Market Cap: ${hon_data.get('market_cap', 0):,}")
    
    # Test competitor (using GE as example)
    print("\nCompetitor Data (GE):")
    ge_data = tool.get_competitor_data("GE")
    print(f"Company: {ge_data.get('company_name')}")
    print(f"Price: ${ge_data.get('current_price', 0):.2f}")
    print(f"Market Cap: ${ge_data.get('market_cap', 0):,}")
