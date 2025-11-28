# =============================================================================
# CORRELATION PACKAGE INITIALIZATION
# =============================================================================
# This package contains the cross-platform correlation engine for analyzing
# profiles across social media platforms and detecting impersonation.
# =============================================================================

"""
Correlation Package

This package provides cross-platform profile correlation capabilities:

Modules:
- correlator.py: Main CrossPlatformCorrelator class
- fuzzy_matcher.py: Fuzzy string matching for profile comparison
- similarity_scorer.py: Various similarity calculation algorithms

Usage:
    from app.services.correlation import CrossPlatformCorrelator
    
    correlator = CrossPlatformCorrelator()
    result = correlator.correlate([
        {"platform": "facebook", "username": "john_doe", "name": "John Doe"},
        {"platform": "twitter", "username": "johndoe", "name": "John D"},
    ])
    print(result.impersonation_score)  # 0-100
    
Module-level convenience functions:
    from app.services.correlation import correlate, match_names
    
    correlate(profiles)  # Returns correlation results
    match_names("John", "Jon")  # Returns similarity score
"""

from .correlator import (
    CrossPlatformCorrelator,
    PlatformProfile,
    CorrelationResult,
    correlate,
    find_overlaps,
    find_contradictions,
)

from .fuzzy_matcher import (
    FuzzyMatcher,
    match_names,
    match_bios,
    match_usernames,
    find_similar,
)

from .similarity_scorer import (
    SimilarityScorer,
    levenshtein_ratio,
    jaro_winkler,
    token_sort_ratio,
    cosine_similarity,
)


__all__ = [
    # Main classes
    "CrossPlatformCorrelator",
    "PlatformProfile",
    "CorrelationResult",
    "FuzzyMatcher",
    "SimilarityScorer",
    
    # Correlator functions
    "correlate",
    "find_overlaps",
    "find_contradictions",
    
    # Matching functions
    "match_names",
    "match_bios",
    "match_usernames",
    "find_similar",
    
    # Similarity functions
    "levenshtein_ratio",
    "jaro_winkler",
    "token_sort_ratio",
    "cosine_similarity",
]
