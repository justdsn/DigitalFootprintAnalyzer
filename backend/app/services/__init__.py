# =============================================================================
# SERVICES PACKAGE INITIALIZATION
# =============================================================================
# This package contains all business logic services for the application.
# =============================================================================

"""
Services Package

Contains the core services for digital footprint analysis:
- pii_extractor.py: Extract PII using regex patterns
- ner_engine.py: Named Entity Recognition with Sri Lankan context
- username_analyzer.py: Username analysis and platform URL generation

Each service is designed to be stateless and can be instantiated as a singleton.
"""

from app.services.pii_extractor import PIIExtractor
from app.services.ner_engine import NEREngine
from app.services.username_analyzer import UsernameAnalyzer

__all__ = ["PIIExtractor", "NEREngine", "UsernameAnalyzer"]
