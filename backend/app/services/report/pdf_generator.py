# =============================================================================
# PDF REPORT GENERATOR SERVICE
# =============================================================================
# Generates downloadable PDF reports using ReportLab.
# Sri Lanka focused styling with comprehensive digital footprint analysis.
# =============================================================================

"""
PDF Report Generator Service

This module generates downloadable PDF reports including:
- Header with report title and date
- Risk score section with visual indicator
- Impersonation alerts
- Exposed PII table
- Platform breakdown table
- Recommendations list
- Complete findings with all URLs
- Sri Lanka focused styling

Example Usage:
    generator = PDFGenerator()
    pdf_bytes = generator.generate(report_data)
    # Returns PDF as bytes
"""

import io
from typing import Dict, Any, List, Optional
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT


class PDFGenerator:
    """
    Generate downloadable PDF reports from analysis data.
    Sri Lanka focused styling with Sinhala language support.
    """
    
    # -------------------------------------------------------------------------
    # STYLING CONFIGURATION
    # -------------------------------------------------------------------------
    
    # Brand colors
    PRIMARY_COLOR = colors.HexColor("#1877f2")  # Facebook blue
    SECONDARY_COLOR = colors.HexColor("#4a5568")  # Gray
    SUCCESS_COLOR = colors.HexColor("#28a745")
    WARNING_COLOR = colors.HexColor("#ffc107")
    DANGER_COLOR = colors.HexColor("#dc3545")
    
    # Risk level colors
    RISK_COLORS = {
        "critical": colors.HexColor("#dc3545"),
        "high": colors.HexColor("#fd7e14"),
        "medium": colors.HexColor("#ffc107"),
        "low": colors.HexColor("#28a745")
    }
    
    def __init__(self):
        """Initialize the PDF Generator."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=self.PRIMARY_COLOR,
            alignment=TA_CENTER
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
            textColor=self.SECONDARY_COLOR
        ))
        
        # Subsection style
        self.styles.add(ParagraphStyle(
            'SubSection',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceBefore=10,
            spaceAfter=5
        ))
        
        # Normal text with link support
        self.styles.add(ParagraphStyle(
            'NormalLink',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.PRIMARY_COLOR
        ))
        
        # Risk text styles
        for level, color in self.RISK_COLORS.items():
            self.styles.add(ParagraphStyle(
                f'Risk{level.capitalize()}',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=color,
                fontName='Helvetica-Bold'
            ))
    
    def generate(self, report_data: Dict[str, Any]) -> bytes:
        """
        Generate PDF report from analysis data.
        
        Args:
            report_data: Report data dictionary from ReportBuilder
            
        Returns:
            PDF content as bytes
        """
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Build document content
        story = []
        
        # Add header
        story.extend(self._build_header(report_data))
        
        # Add risk score section
        story.extend(self._build_risk_section(report_data))
        
        # Add impersonation alerts (if any)
        story.extend(self._build_impersonation_section(report_data))
        
        # Add exposed PII section
        story.extend(self._build_pii_section(report_data))
        
        # Add platform breakdown
        story.extend(self._build_platform_section(report_data))
        
        # Add recommendations
        story.extend(self._build_recommendations_section(report_data))
        
        # Add complete findings
        story.extend(self._build_findings_section(report_data))
        
        # Build PDF
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _build_header(self, report_data: Dict[str, Any]) -> List:
        """Build report header section."""
        elements = []
        
        # Title
        elements.append(Paragraph(
            "Digital Footprint Analysis Report",
            self.styles['CustomTitle']
        ))
        
        # Subtitle with identifier
        identifier = report_data.get("identifier", {})
        identifier_text = f"{identifier.get('type', 'Identifier').capitalize()}: {identifier.get('value', 'Unknown')}"
        elements.append(Paragraph(
            identifier_text,
            self.styles['Normal']
        ))
        
        # Report metadata
        generated_at = report_data.get("generated_at", datetime.now().isoformat())
        report_id = report_data.get("report_id", "N/A")
        
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            f"Report ID: {report_id}",
            self.styles['Normal']
        ))
        elements.append(Paragraph(
            f"Generated: {generated_at[:19].replace('T', ' ')} UTC",
            self.styles['Normal']
        ))
        
        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
        
        return elements
    
    def _build_risk_section(self, report_data: Dict[str, Any]) -> List:
        """Build risk score section with visual indicator."""
        elements = []
        
        risk_assessment = report_data.get("risk_assessment", {})
        score = risk_assessment.get("score", 0)
        level = risk_assessment.get("level", "low")
        summary = risk_assessment.get("summary", "No assessment available")
        
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Risk Assessment", self.styles['SectionHeader']))
        
        # Risk score indicator
        risk_color = self.RISK_COLORS.get(level, self.SUCCESS_COLOR)
        
        # Score and level display
        score_text = f"<font color='{risk_color.hexval()}'><b>Risk Score: {score}/100 ({level.upper()})</b></font>"
        elements.append(Paragraph(score_text, self.styles['Normal']))
        
        # Visual score bar
        bar_data = [["", ""]]
        bar_width = 4 * inch
        filled_width = (score / 100) * bar_width
        
        bar_style = TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), risk_color),
            ('BACKGROUND', (1, 0), (1, 0), colors.lightgrey),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.grey),
            ('LINEBEFORE', (0, 0), (0, 0), 1, colors.grey),
            ('LINEAFTER', (-1, 0), (-1, 0), 1, colors.grey),
        ])
        
        bar_table = Table(
            bar_data,
            colWidths=[filled_width, bar_width - filled_width],
            rowHeights=[20]
        )
        bar_table.setStyle(bar_style)
        elements.append(Spacer(1, 10))
        elements.append(bar_table)
        
        # Summary
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(summary, self.styles['Normal']))
        
        # Quick stats
        critical_high = risk_assessment.get("critical_items", 0) + risk_assessment.get("high_risk_items", 0)
        impersonation_count = risk_assessment.get("impersonation_count", 0)
        
        if critical_high > 0 or impersonation_count > 0:
            elements.append(Spacer(1, 10))
            stats_text = []
            if critical_high > 0:
                stats_text.append(f"<font color='#dc3545'>{critical_high} critical/high risk items</font>")
            if impersonation_count > 0:
                stats_text.append(f"<font color='#fd7e14'>{impersonation_count} potential impersonation risks</font>")
            elements.append(Paragraph(" | ".join(stats_text), self.styles['Normal']))
        
        return elements
    
    def _build_impersonation_section(self, report_data: Dict[str, Any]) -> List:
        """Build impersonation alerts section."""
        elements = []
        
        impersonation_risks = report_data.get("impersonation_risks", [])
        
        if not impersonation_risks:
            return elements
        
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Impersonation Alerts", self.styles['SectionHeader']))
        
        for risk in impersonation_risks:
            platform = risk.get("platform", "Unknown")
            profile_name = risk.get("profile_name", "Unknown")
            risk_level = risk.get("risk_level", "medium")
            recommendation = risk.get("recommendation", "")
            profile_url = risk.get("profile_url", "")
            report_url = risk.get("report_url", "")
            
            risk_color = self.RISK_COLORS.get(risk_level, self.WARNING_COLOR)
            
            # Alert box
            alert_text = f"""
            <font color='{risk_color.hexval()}'><b>{risk_level.upper()} RISK: {platform.capitalize()}</b></font><br/>
            Profile: {profile_name}<br/>
            {recommendation}<br/>
            """
            if profile_url:
                alert_text += f"<font color='#1877f2'>View: {profile_url}</font><br/>"
            if report_url:
                alert_text += f"<font color='#1877f2'>Report: {report_url}</font>"
            
            elements.append(Paragraph(alert_text, self.styles['Normal']))
            elements.append(Spacer(1, 10))
        
        return elements
    
    def _build_pii_section(self, report_data: Dict[str, Any]) -> List:
        """Build exposed PII table section."""
        elements = []
        
        exposed_pii = report_data.get("exposed_pii", {})
        
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Exposed Personal Information", self.styles['SectionHeader']))
        
        # Check if there's any exposed PII
        all_pii = []
        for severity in ["critical", "high", "medium", "low"]:
            all_pii.extend(exposed_pii.get(severity, []))
        
        if not all_pii:
            elements.append(Paragraph("No personally identifiable information found exposed.", self.styles['Normal']))
            return elements
        
        # Build table
        table_data = [["Type", "Value", "Risk", "Found On"]]
        
        for severity in ["critical", "high", "medium", "low"]:
            for item in exposed_pii.get(severity, []):
                pii_type = item.get("pii_label", item.get("type", "Unknown"))
                value = item.get("value", "")[:30] + "..." if len(item.get("value", "")) > 30 else item.get("value", "")
                risk_level = item.get("risk_level", severity)
                platforms = ", ".join(item.get("platforms", []))[:25]
                
                table_data.append([pii_type, value, risk_level.upper(), platforms])
        
        table = Table(table_data, colWidths=[1.2*inch, 2*inch, 0.8*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.PRIMARY_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.whitesmoke])
        ]))
        
        elements.append(table)
        
        return elements
    
    def _build_platform_section(self, report_data: Dict[str, Any]) -> List:
        """Build platform breakdown section."""
        elements = []
        
        platforms = report_data.get("platforms", [])
        
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Platform Breakdown", self.styles['SectionHeader']))
        
        if not platforms:
            elements.append(Paragraph("No platform data available.", self.styles['Normal']))
            return elements
        
        # Build table
        table_data = [["Platform", "Status", "Exposed Items", "Profile URL"]]
        
        for platform in platforms:
            name = platform.get("platform_name", "Unknown")
            status = platform.get("status", "unknown")
            exposed_count = platform.get("exposed_count", 0)
            url = platform.get("profile_url", "")
            
            # Truncate URL for display
            display_url = url[:35] + "..." if len(url) > 35 else url
            
            table_data.append([name, status.upper(), str(exposed_count), display_url])
        
        table = Table(table_data, colWidths=[1.2*inch, 1*inch, 1*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.PRIMARY_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.whitesmoke])
        ]))
        
        elements.append(table)
        
        return elements
    
    def _build_recommendations_section(self, report_data: Dict[str, Any]) -> List:
        """Build recommendations section."""
        elements = []
        
        recommendations = report_data.get("recommendations", [])
        
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Recommendations", self.styles['SectionHeader']))
        
        if not recommendations:
            elements.append(Paragraph("No specific recommendations at this time.", self.styles['Normal']))
            return elements
        
        for i, rec in enumerate(recommendations, 1):
            priority = rec.get("priority", i)
            severity = rec.get("severity", "low")
            title = rec.get("title", "Recommendation")
            description = rec.get("description", "")
            
            severity_color = self.RISK_COLORS.get(severity, self.SECONDARY_COLOR)
            
            rec_text = f"<b>{priority}. {title}</b><br/>{description}"
            elements.append(Paragraph(rec_text, self.styles['Normal']))
            elements.append(Spacer(1, 8))
        
        return elements
    
    def _build_findings_section(self, report_data: Dict[str, Any]) -> List:
        """Build complete findings section with all links."""
        elements = []
        
        complete_findings = report_data.get("complete_findings", {})
        
        elements.append(PageBreak())
        elements.append(Paragraph("Complete Findings", self.styles['SectionHeader']))
        
        # Discovered Profiles
        elements.append(Spacer(1, 15))
        elements.append(Paragraph("Discovered Profiles", self.styles['SubSection']))
        
        discovered_profiles = complete_findings.get("discovered_profiles", [])
        
        if discovered_profiles:
            for profile in discovered_profiles:
                found = profile.get("found", False)
                platform = profile.get("platform", "Unknown")
                status_text = "FOUND" if found else "NOT FOUND"
                status_color = self.SUCCESS_COLOR if found else colors.grey
                
                profile_text = f"<font color='{status_color.hexval()}'><b>{platform}: {status_text}</b></font><br/>"
                
                if found:
                    links = profile.get("links", {})
                    if links.get("view_profile"):
                        profile_text += f"View: <font color='#1877f2'>{links['view_profile']}</font><br/>"
                    if links.get("privacy_settings"):
                        profile_text += f"Privacy Settings: <font color='#1877f2'>{links['privacy_settings']}</font><br/>"
                    if links.get("report_profile"):
                        profile_text += f"Report: <font color='#1877f2'>{links['report_profile']}</font>"
                else:
                    checked_urls = profile.get("checked_urls", [])
                    if checked_urls:
                        profile_text += f"Checked: {checked_urls[0]}"
                
                elements.append(Paragraph(profile_text, self.styles['Normal']))
                elements.append(Spacer(1, 8))
        else:
            elements.append(Paragraph("No profile information available.", self.styles['Normal']))
        
        # Exposed PII Details
        elements.append(Spacer(1, 15))
        elements.append(Paragraph("Exposed PII Details", self.styles['SubSection']))
        
        exposed_pii_details = complete_findings.get("exposed_pii_details", [])
        
        if exposed_pii_details:
            for pii in exposed_pii_details:
                pii_type = pii.get("pii_label", pii.get("pii_type", "Unknown"))
                value = pii.get("exposed_value", "")
                risk_level = pii.get("risk_level", "low")
                risk_color = self.RISK_COLORS.get(risk_level, self.SECONDARY_COLOR)
                
                pii_text = f"<b>{pii_type}:</b> {value}<br/>"
                pii_text += f"<font color='{risk_color.hexval()}'>Risk: {risk_level.upper()}</font><br/>"
                
                found_on = pii.get("found_on", [])
                if found_on:
                    platforms = [f.get("platform", "") for f in found_on]
                    pii_text += f"Found on: {', '.join(platforms)}<br/>"
                    for source in found_on:
                        if source.get("direct_link"):
                            pii_text += f"<font color='#1877f2'>{source['direct_link']}</font><br/>"
                
                action = pii.get("recommended_action", "")
                if action:
                    pii_text += f"<i>Action: {action}</i>"
                
                elements.append(Paragraph(pii_text, self.styles['Normal']))
                elements.append(Spacer(1, 10))
        else:
            elements.append(Paragraph("No exposed PII details available.", self.styles['Normal']))
        
        # Summary statistics
        summary = report_data.get("summary", {})
        if summary:
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("Summary Statistics", self.styles['SubSection']))
            
            summary_text = f"""
            Platforms Checked: {summary.get('total_platforms_checked', 0)}<br/>
            Profiles Found: {summary.get('total_profiles_found', 0)}<br/>
            Total PII Exposed: {summary.get('total_pii_exposed', 0)}<br/>
            Critical/High Risk Items: {summary.get('critical_high_risk_items', 0)}<br/>
            Medium Risk Items: {summary.get('medium_risk_items', 0)}<br/>
            Low Risk Items: {summary.get('low_risk_items', 0)}<br/>
            Impersonation Risks: {summary.get('impersonation_risks_detected', 0)}
            """
            elements.append(Paragraph(summary_text, self.styles['Normal']))
        
        # Footer
        elements.append(Spacer(1, 30))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            "Generated by Digital Footprint Analyzer - Sri Lanka OSINT Tool",
            self.styles['Normal']
        ))
        
        return elements


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

_default_generator = PDFGenerator()


def generate_pdf(report_data: Dict[str, Any]) -> bytes:
    """Module-level convenience function for PDF generation."""
    return _default_generator.generate(report_data)
