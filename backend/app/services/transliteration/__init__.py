# =============================================================================
# TRANSLITERATION SERVICES PACKAGE
# =============================================================================
# Provides Sinhala-to-English transliteration functionality for the
# Digital Footprint Analyzer. Supports Sri Lankan names and locations.
# =============================================================================

"""
Transliteration Services Package

This package provides:
- SinhalaTransliterator: Main transliteration engine for Sinhala text
- Grapheme mappings: Sinhala Unicode to Roman character mappings
- Name dictionary: Common Sri Lankan names with transliteration variants
- Location dictionary: Sri Lankan places with transliteration variants

Example Usage:
    from app.services.transliteration import SinhalaTransliterator
    
    transliterator = SinhalaTransliterator()
    result = transliterator.transliterate("දුෂාන්")
    # Returns: ['dushan', 'dushaan', 'dusan']
"""

from app.services.transliteration.sinhala_engine import SinhalaTransliterator
from app.services.transliteration.grapheme_map import (
    SINHALA_VOWELS,
    SINHALA_CONSONANTS,
    SINHALA_VOWEL_SIGNS,
    VARIANT_RULES
)
from app.services.transliteration.name_dictionary import (
    SINHALA_FIRST_NAMES,
    SINHALA_SURNAMES,
    get_name_variants
)
from app.services.transliteration.location_dictionary import (
    SINHALA_LOCATIONS,
    get_location_variants
)

__all__ = [
    'SinhalaTransliterator',
    'SINHALA_VOWELS',
    'SINHALA_CONSONANTS',
    'SINHALA_VOWEL_SIGNS',
    'VARIANT_RULES',
    'SINHALA_FIRST_NAMES',
    'SINHALA_SURNAMES',
    'get_name_variants',
    'SINHALA_LOCATIONS',
    'get_location_variants'
]
