# =============================================================================
# CORRELATION SERVICES PACKAGE
# =============================================================================
# Provides cross-platform PII correlation and impersonation detection
# functionality for the Digital Footprint Analyzer.
# =============================================================================

"""
Correlation Services Package

This package provides:
- Correlator: Main correlation engine for comparing PII across platforms
- FuzzyMatcher: Fuzzy string matching utilities
- SimilarityScorer: Various similarity calculation methods

Example Usage:
    from app.services.correlation import Correlator, FuzzyMatcher
    
    correlator = Correlator()
    result = correlator.correlate_profiles(profiles)
    # Returns: {'overlaps': [...], 'contradictions': [...], 'impersonation_score': 45}
"""

from app.services.correlation.correlator import Correlator
from app.services.correlation.fuzzy_matcher import FuzzyMatcher
from app.services.correlation.similarity_scorer import SimilarityScorer

__all__ = [
    'Correlator',
    'FuzzyMatcher',
    'SimilarityScorer'
]
