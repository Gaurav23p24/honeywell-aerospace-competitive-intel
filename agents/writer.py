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
        Generate PDF report from analysis data
        
        Args:
            analysis: Analysis results from Analyst agent
            honeywell_product: The Honeywell product being analyzed
            competitor_query: The competitor comparison query
            
        Returns:
            Path to the generated PDF file
        """
        logger.info("Writer: Starting PDF report generation...")
        
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
        
        # Competitive Gaps
        gaps = analysis.get('competitive_gaps', [])
        if gaps:
            story.append(Paragraph("Competitive Gaps Identified", heading_style))
            story.append(self._create_gaps_table(gaps))
            story.append(Spacer(1, 0.2*inch))
        
        # Key Insights
        insights = analysis.get('insights', [])
        if insights:
            story.append(Paragraph("Key Insights", heading_style))
            for insight in insights[:10]:  # Limit to top 10 insights
                story.append(Paragraph(f"• {insight}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Strategic Recommendations
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            story.append(Paragraph("Strategic Recommendations", heading_style))
            for i, rec in enumerate(recommendations, 1):
                story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Data Sources
        sources = analysis.get('data_sources_used', [])
        if sources:
            story.append(Paragraph("Data Sources", heading_style))
            sources_text = ", ".join(sources)
            story.append(Paragraph(f"<b>Sources used:</b> {sources_text}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Analysis Details
        story.append(Paragraph("Analysis Details", heading_style))
        details_text = self._generate_analysis_details(analysis)
        story.append(Paragraph(details_text, styles['Normal']))
        
        # Build PDF
        try:
            doc.build(story)
            logger.info(f"Writer: PDF report generated successfully: {filepath}")
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
        
        # Add gap data
        for gap in gaps[:8]:  # Limit to top 8 gaps
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
        for i, gap in enumerate(gaps[:8], 1):  # Only for data rows
            impact = gap.get('impact', 'Low')
            if impact in impact_colors:
                table_style.append(('TEXTCOLOR', (2, i), (2, i), impact_colors[impact]))
        
        table.setStyle(TableStyle(table_style))
        
        return table
    
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
