"""
Writer Agent - Creates structured PDF reports
Phase 1: Basic PDF generation with ReportLab
"""

from typing import Dict, Any, List
import logging
from datetime import datetime
import os

# ReportLab imports
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

logger = logging.getLogger(__name__)

class WriterAgent:
    """Agent responsible for generating PDF reports"""
    
    def __init__(self):
        self.output_dir = "reports"
        self._ensure_output_dir()
        
    def _ensure_output_dir(self):
        """Ensure reports directory exists"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Writer: Created output directory: {self.output_dir}")
    
    def write_report(self, analysis: Dict[str, Any], honeywell_product: str, competitor_query: str) -> str:
        """
        Generate comprehensive PDF report from analysis data
        
        Args:
            analysis: Analysis results from Analyst agent
            honeywell_product: The Honeywell product being analyzed
            competitor_query: The competitor comparison query
            
        Returns:
            Path to the generated PDF file
        """
        logger.info("Writer: Starting comprehensive PDF report generation...")
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"honeywell_analysis_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        subheading_style = ParagraphStyle(
            'SubHeading',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            textColor=colors.darkblue
        )
        
        # Title page
        story.append(Paragraph("Honeywell Aerospace Competitive Analysis", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Report metadata with better formatting
        metadata_style = ParagraphStyle(
            'Metadata',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=20
        )
        
        story.append(Paragraph(f"<b>Product:</b> {honeywell_product}", metadata_style))
        story.append(Paragraph(f"<b>Analysis:</b> {competitor_query}", metadata_style))
        story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", metadata_style))
        
        # Confidence score with color coding
        confidence = analysis.get('confidence_score', 0)
        if confidence >= 0.8:
            conf_color = "green"
            conf_text = "High"
        elif confidence >= 0.6:
            conf_color = "orange"
            conf_text = "Medium"
        else:
            conf_color = "red"
            conf_text = "Low"
        
        story.append(Paragraph(f"<b>Confidence Score:</b> <font color='{conf_color}'>{confidence:.1%} ({conf_text})</font>", metadata_style))
        
        # Data sources summary
        sources = analysis.get('data_sources_used', [])
        if sources:
            story.append(Paragraph(f"<b>Data Sources:</b> {len(sources)} sources used", metadata_style))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        summary_text = self._generate_executive_summary(analysis)
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Competitive Gaps - ALL gaps, not just top 8
        gaps = analysis.get('competitive_gaps', [])
        if gaps:
            story.append(Paragraph("Competitive Gaps Identified", heading_style))
            story.append(self._create_gaps_table(gaps))
            story.append(Spacer(1, 0.2*inch))
        
        # Key Insights - ALL insights, not just top 10
        insights = analysis.get('insights', [])
        if insights:
            story.append(Paragraph("Key Insights", heading_style))
            for insight in insights:  # Show ALL insights
                story.append(Paragraph(f"• {insight}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Strategic Recommendations
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            story.append(Paragraph("Strategic Recommendations", heading_style))
            for i, rec in enumerate(recommendations, 1):
                story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # DETAILED DATA SECTIONS - NEW COMPREHENSIVE SECTIONS
        self._add_detailed_data_sections(story, analysis, heading_style, subheading_style, styles)
        
        # Analysis Details
        story.append(Paragraph("Analysis Details", heading_style))
        details_text = self._generate_analysis_details(analysis)
        story.append(Paragraph(details_text, styles['Normal']))
        
        # Build PDF
        try:
            doc.build(story)
            logger.info(f"Writer: Comprehensive PDF report generated successfully: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Writer: Error generating PDF: {e}")
            raise
    
    def _generate_executive_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate executive summary text"""
        gaps_count = len(analysis.get('competitive_gaps', []))
        insights_count = len(analysis.get('insights', []))
        confidence = analysis.get('confidence_score', 0)
        sources_count = len(analysis.get('data_sources_used', []))
        
        # Categorize gaps by impact
        gaps = analysis.get('competitive_gaps', [])
        high_impact_gaps = len([gap for gap in gaps if gap.get('impact') == 'High'])
        medium_impact_gaps = len([gap for gap in gaps if gap.get('impact') == 'Medium'])
        
        # Generate confidence assessment
        if confidence >= 0.8:
            conf_assessment = "highly reliable"
        elif confidence >= 0.6:
            conf_assessment = "moderately reliable"
        else:
            conf_assessment = "limited reliability due to data constraints"
        
        summary = f"""
        This competitive analysis examined {analysis.get('honeywell_product', 'the specified product')} 
        against competitors in the aerospace market. The analysis utilized {sources_count} data sources 
        and identified {gaps_count} competitive gaps ({high_impact_gaps} high-impact, {medium_impact_gaps} medium-impact) 
        along with {insights_count} key insights.
        
        The analysis has a confidence score of {confidence:.1%}, indicating {conf_assessment} findings 
        based on available data sources. Strategic recommendations are provided to address identified 
        competitive gaps and leverage market opportunities.
        
        Key findings include insights from financial analysis, market intelligence, and product 
        specifications research, providing a comprehensive view of the competitive landscape.
        """
        
        return summary.strip()
    
    def _create_gaps_table(self, gaps: List[Dict[str, Any]]) -> Table:
        """Create a table for competitive gaps"""
        if not gaps:
            return Spacer(1, 0.1*inch)
        
        # Table headers
        headers = ['Category', 'Gap Description', 'Impact', 'Opportunity']
        table_data = [headers]
        
        # Add gap data - ALL gaps, not just top 8
        for gap in gaps:  # Show ALL gaps
            row = [
                gap.get('category', 'N/A'),
                gap.get('gap', 'N/A')[:50] + '...' if len(gap.get('gap', '')) > 50 else gap.get('gap', 'N/A'),
                gap.get('impact', 'N/A'),
                gap.get('opportunity', 'N/A')[:40] + '...' if len(gap.get('opportunity', '')) > 40 else gap.get('opportunity', 'N/A')
            ]
            table_data.append(row)
        
        # Create table with adaptive column widths
        table = Table(table_data, colWidths=[1.2*inch, 2.8*inch, 0.8*inch, 1.8*inch])
        
        # Define impact colors
        impact_colors = {
            'High': colors.red,
            'Medium': colors.orange,
            'Low': colors.green
        }
        
        # Create table style
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]
        
        # Add impact-specific row coloring
        for i, gap in enumerate(gaps, 1):  # For ALL data rows
            impact = gap.get('impact', 'Low')
            if impact in impact_colors:
                table_style.append(('TEXTCOLOR', (2, i), (2, i), impact_colors[impact]))
        
        table.setStyle(TableStyle(table_style))
        
        return table
    
    def _add_detailed_data_sections(self, story, analysis: Dict[str, Any], heading_style, subheading_style, styles):
        """Add comprehensive data sections for each tool used"""
        
        # Get raw data from analysis
        raw_data = analysis.get('raw_data', {})
        sources = raw_data.get('sources', {})
        
        # Debug: Print what we have
        print(f"Writer: Raw data keys: {list(raw_data.keys())}")
        print(f"Writer: Sources keys: {list(sources.keys())}")
        for source_name, source_data in sources.items():
            print(f"Writer: {source_name} status: {source_data.get('status', 'unknown')}")
        
        # Debug: Show what data sources we have
        story.append(Paragraph("Data Sources Available", heading_style))
        if sources:
            for source_name, source_data in sources.items():
                # Check for success indicators
                if 'error' in source_data:
                    status = 'error'
                elif source_data.get('status') == 'success':
                    status = 'success'
                elif 'company_name' in source_data or 'news_items' in source_data or 'specifications' in source_data:
                    status = 'success'
                else:
                    status = 'unknown'
                story.append(Paragraph(f"• <b>{source_name}:</b> {status}", styles['Normal']))
        else:
            story.append(Paragraph("No data sources found", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # YFinance Data Section
        if any('yfinance' in source for source in sources.keys()):
            story.append(Paragraph("Financial Data Analysis (YFinance)", heading_style))
            
            # Honeywell Financial Data
            if 'yfinance_honeywell' in sources:
                story.append(Paragraph("Honeywell Financial Metrics", subheading_style))
                honeywell_data = sources['yfinance_honeywell']
                if 'error' not in honeywell_data:
                    # Data is directly in the response
                    market_cap = honeywell_data.get('market_cap', 'N/A')
                    if isinstance(market_cap, (int, float)):
                        story.append(Paragraph(f"<b>Market Cap:</b> ${market_cap:,}", styles['Normal']))
                    else:
                        story.append(Paragraph(f"<b>Market Cap:</b> {market_cap}", styles['Normal']))
                    story.append(Paragraph(f"<b>P/E Ratio:</b> {honeywell_data.get('pe_ratio', 'N/A')}", styles['Normal']))
                    story.append(Paragraph(f"<b>Profit Margin:</b> {honeywell_data.get('profit_margin', 'N/A')}%", styles['Normal']))
                    revenue = honeywell_data.get('revenue', 'N/A')
                    if isinstance(revenue, (int, float)):
                        story.append(Paragraph(f"<b>Revenue:</b> ${revenue:,}", styles['Normal']))
                    else:
                        story.append(Paragraph(f"<b>Revenue:</b> {revenue}", styles['Normal']))
                    story.append(Paragraph(f"<b>52-Week High:</b> ${honeywell_data.get('52_week_high', 'N/A')}", styles['Normal']))
                    story.append(Paragraph(f"<b>52-Week Low:</b> ${honeywell_data.get('52_week_low', 'N/A')}", styles['Normal']))
                    story.append(Paragraph(f"<b>Current Price:</b> ${honeywell_data.get('current_price', 'N/A')}", styles['Normal']))
                    story.append(Paragraph(f"<b>Company:</b> {honeywell_data.get('company_name', 'N/A')}", styles['Normal']))
                else:
                    story.append(Paragraph(f"Data collection failed: {honeywell_data.get('error', 'Unknown error')}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            
            # Competitor Financial Data
            if 'yfinance_competitor' in sources:
                story.append(Paragraph("Competitor Financial Metrics", subheading_style))
                competitor_data = sources['yfinance_competitor']
                if 'error' not in competitor_data:
                    # Data is directly in the response
                    market_cap = competitor_data.get('market_cap', 'N/A')
                    if isinstance(market_cap, (int, float)):
                        story.append(Paragraph(f"<b>Market Cap:</b> ${market_cap:,}", styles['Normal']))
                    else:
                        story.append(Paragraph(f"<b>Market Cap:</b> {market_cap}", styles['Normal']))
                    story.append(Paragraph(f"<b>P/E Ratio:</b> {competitor_data.get('pe_ratio', 'N/A')}", styles['Normal']))
                    story.append(Paragraph(f"<b>Profit Margin:</b> {competitor_data.get('profit_margin', 'N/A')}%", styles['Normal']))
                    revenue = competitor_data.get('revenue', 'N/A')
                    if isinstance(revenue, (int, float)):
                        story.append(Paragraph(f"<b>Revenue:</b> ${revenue:,}", styles['Normal']))
                    else:
                        story.append(Paragraph(f"<b>Revenue:</b> {revenue}", styles['Normal']))
                    story.append(Paragraph(f"<b>52-Week High:</b> ${competitor_data.get('52_week_high', 'N/A')}", styles['Normal']))
                    story.append(Paragraph(f"<b>52-Week Low:</b> ${competitor_data.get('52_week_low', 'N/A')}", styles['Normal']))
                    story.append(Paragraph(f"<b>Current Price:</b> ${competitor_data.get('current_price', 'N/A')}", styles['Normal']))
                    story.append(Paragraph(f"<b>Company:</b> {competitor_data.get('company_name', 'N/A')}", styles['Normal']))
                else:
                    story.append(Paragraph(f"Data collection failed: {competitor_data.get('error', 'Unknown error')}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            
            # Comparison Data
            if 'yfinance_comparison' in sources:
                story.append(Paragraph("Financial Comparison", subheading_style))
                comparison_data = sources['yfinance_comparison']
                if 'error' not in comparison_data:
                    comparison = comparison_data.get('comparison', {})
                    if comparison:
                        story.append(Paragraph(f"<b>Market Cap Ratio:</b> {comparison.get('market_cap_ratio', 'N/A')}", styles['Normal']))
                        story.append(Paragraph(f"<b>Price Ratio:</b> {comparison.get('price_ratio', 'N/A')}", styles['Normal']))
                        story.append(Paragraph(f"<b>P/E Ratio Difference:</b> {comparison.get('pe_ratio_difference', 'N/A')}", styles['Normal']))
                        story.append(Paragraph(f"<b>Profit Margin Difference:</b> {comparison.get('profit_margin_difference', 'N/A')}%", styles['Normal']))
                    else:
                        story.append(Paragraph("No comparison data available", styles['Normal']))
                else:
                    story.append(Paragraph(f"Comparison failed: {comparison_data.get('error', 'Unknown error')}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            
            story.append(Spacer(1, 0.2*inch))
        
        # Tavily News Data Section
        if any('tavily' in source for source in sources.keys()):
            story.append(Paragraph("Market Intelligence (Tavily Search)", heading_style))
            
            for source_name, source_data in sources.items():
                if 'tavily' in source_name:
                    story.append(Paragraph(f"{source_name.replace('_', ' ').title()} Results", subheading_style))
                    
                    if 'error' not in source_data:
                        news_items = source_data.get('news_items', [])
                        if news_items:
                            for i, item in enumerate(news_items[:5], 1):  # Show top 5 results
                                story.append(Paragraph(f"<b>{i}. {item.get('title', 'No Title')}</b>", styles['Normal']))
                                story.append(Paragraph(f"<i>Source: {item.get('url', 'No URL')}</i>", styles['Normal']))
                                content = item.get('content', 'No content available')
                                if len(content) > 200:
                                    content = content[:200] + "..."
                                story.append(Paragraph(f"{content}", styles['Normal']))
                                story.append(Spacer(1, 0.1*inch))
                        else:
                            story.append(Paragraph("No results found for this search.", styles['Normal']))
                    else:
                        story.append(Paragraph(f"Search failed: {source_data.get('error', 'Unknown error')}", styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
            
            story.append(Spacer(1, 0.2*inch))
        
        # Browser-Use Data Section
        if any('browser_use' in source for source in sources.keys()):
            story.append(Paragraph("Product Specifications (Browser-Use Tool)", heading_style))
            
            for source_name, source_data in sources.items():
                if 'browser_use' in source_name and 'error' not in source_data:
                    story.append(Paragraph(f"{source_name.replace('_', ' ').title()} Results", subheading_style))
                    
                    specifications = source_data.get('specifications', {})
                    if specifications:
                        story.append(Paragraph(f"<b>Product:</b> {source_data.get('competitor_product', 'Unknown Product')}", styles['Normal']))
                        story.append(Paragraph(f"<b>Search Query:</b> {source_data.get('search_query', 'N/A')}", styles['Normal']))
                        story.append(Paragraph(f"<b>Extraction Time:</b> {source_data.get('extraction_time', 'N/A')} seconds", styles['Normal']))
                        story.append(Paragraph(f"<b>Data Source:</b> {source_data.get('data_source', 'N/A')}", styles['Normal']))
                        story.append(Spacer(1, 0.1*inch))
                        
                        story.append(Paragraph("<b>Technical Specifications:</b>", styles['Normal']))
                        for spec_key, spec_value in specifications.items():
                            story.append(Paragraph(f"• <b>{spec_key}:</b> {spec_value}", styles['Normal']))
                    else:
                        story.append(Paragraph("No specifications extracted.", styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
            
            story.append(Spacer(1, 0.2*inch))
        
        # Data Quality Section
        story.append(Paragraph("Data Quality Assessment", heading_style))
        quality_scores = analysis.get('quality_scores', {})
        if quality_scores:
            story.append(Paragraph("Source Quality Scores:", subheading_style))
            for source_name, score in quality_scores.items():
                color = "green" if score >= 0.7 else "orange" if score >= 0.5 else "red"
                story.append(Paragraph(f"• <b>{source_name}:</b> <font color='{color}'>{score:.1%}</font>", styles['Normal']))
        else:
            story.append(Paragraph("No quality scores available.", styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
    
    def _generate_analysis_details(self, analysis: Dict[str, Any]) -> str:
        """Generate detailed analysis information"""
        details = f"""
        <b>Analysis Methodology:</b> This report was generated using automated competitive analysis 
        techniques, incorporating financial data, market positioning, and strategic assessment frameworks.
        
        <b>Data Quality:</b> The analysis utilized {len(analysis.get('data_sources_used', []))} validated 
        data sources with an overall confidence score of {analysis.get('confidence_score', 0):.1%}.
        
        <b>Scope:</b> The analysis focused on financial metrics, market positioning, and competitive 
        positioning between Honeywell Aerospace and identified competitors.
        
        <b>Limitations:</b> This analysis is based on publicly available financial data and may not 
        capture proprietary competitive intelligence or recent strategic developments.
        """
        
        return details.strip()

# Example usage for testing
if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from agents.scout import ScoutAgent
    from agents.validator import ValidatorAgent
    from agents.analyst import AnalystAgent
    
    # Test full pipeline
    scout = ScoutAgent()
    validator = ValidatorAgent()
    analyst = AnalystAgent()
    writer = WriterAgent()
    
    # Get data, validate, analyze
    raw_data = scout.hunt("TFE731 Engine", "compare with Pratt & Whitney PW500")
    validated_data = validator.validate(raw_data)
    analysis = analyst.analyze(validated_data)
    
    # Generate report
    pdf_path = writer.write_report(analysis, "TFE731 Engine", "compare with Pratt & Whitney PW500")
    
    print(f"Report generated: {pdf_path}")
    print(f"Report contains {len(analysis.get('competitive_gaps', []))} gaps and {len(analysis.get('insights', []))} insights")
