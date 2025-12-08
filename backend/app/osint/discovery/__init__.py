# =============================================================================
# DISCOVERY MODULE
# =============================================================================
# Profile discovery and URL generation utilities.
# =============================================================================

"""
Discovery Module

Utilities for profile discovery:
- Identifier detection (email, username, name, phone)
- URL generation for platform profiles
- Search engine integration for profile discovery
"""

from .identifier_detector import IdentifierDetector
from .url_generator import URLGenerator
from .search_engine import SearchEngine

__all__ = [
    "IdentifierDetector",
    "URLGenerator",
    "SearchEngine",
]
