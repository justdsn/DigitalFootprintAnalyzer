# =============================================================================
# REPORT SERVICES MODULE
# =============================================================================
# Phase 4: Enhanced Results Presentation with PDF Export
# =============================================================================

"""
Report Services Module

This module provides services for report generation and presentation:
- ReportBuilder: Build comprehensive analysis reports
- PDFGenerator: Generate downloadable PDF reports
- Platform configuration for supported social media platforms

Example Usage:
    from app.services.report import (
        ReportBuilder,
        PDFGenerator,
        SUPPORTED_PLATFORMS,
    )
    
    # Build a report
    builder = ReportBuilder()
    report = builder.build_report(scan_results, user_identifiers)
    
    # Generate PDF
    generator = PDFGenerator()
    pdf_bytes = generator.generate(report)
"""

from .report_builder import ReportBuilder
from .pdf_generator import PDFGenerator
from .platform_config import SUPPORTED_PLATFORMS, get_platform_config

__all__ = [
    "ReportBuilder",
    "PDFGenerator",
    "SUPPORTED_PLATFORMS",
    "get_platform_config",
]
