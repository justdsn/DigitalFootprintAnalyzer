# =============================================================================
# OSINT MODULE
# =============================================================================
# Playwright-based OSINT data collection system for social media platforms.
# =============================================================================

"""
OSINT Module

This module provides headless browser automation for OSINT data collection
from Instagram, Facebook, LinkedIn, and X (Twitter) using Playwright.

Components:
- session_manager: Persistent login session management
- collectors: Platform-specific data collectors
- parsers: HTML parsing for profile data extraction
- discovery: Profile discovery and URL generation
- orchestrator: Main OSINT workflow controller
"""

from .session_manager import SessionManager
from .orchestrator import OSINTOrchestrator

__all__ = [
    "SessionManager",
    "OSINTOrchestrator",
]
