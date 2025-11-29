# =============================================================================
# TRANSLITERATION PACKAGE INITIALIZATION
# =============================================================================
# This package contains the Sinhala transliteration engine and supporting
# dictionaries for converting Sinhala text to romanized English.
# =============================================================================

"""
Transliteration Package

This package provides Sinhala to English transliteration capabilities:

Modules:
- sinhala_engine.py: Main SinhalaTransliterator class
- grapheme_map.py: Sinhala Unicode character mappings
- name_dictionary.py: Common Sri Lankan names with variants
- location_dictionary.py: Sri Lankan locations with variants

Usage:
    from app.services.transliteration import SinhalaTransliterator
    
    transliterator = SinhalaTransliterator()
    results = transliterator.transliterate("සුනිල් පෙරේරා")
    # Returns: ['sunil perera', 'suneel perera', ...]
    
Module-level convenience functions:
    from app.services.transliteration import is_sinhala, transliterate
    
    is_sinhala("ආයුබෝවන්")  # True
    transliterate("ගයාන්")   # ['gayan', 'gayaan', ...]
"""

from .sinhala_engine import (
    SinhalaTransliterator,
    is_sinhala,
    transliterate,
    generate_variants,
)

from .grapheme_map import (
    VOWELS,
    CONSONANTS,
    VOWEL_SIGNS,
    VARIANT_RULES,
    VARIANT_RULES_EXTENDED,
    SINHALA_UNICODE_START,
    SINHALA_UNICODE_END,
)

from .name_dictionary import (
    NAME_DICTIONARY,
    get_name_variants,
    search_by_romanized as search_name_by_romanized,
)

from .location_dictionary import (
    LOCATION_DICTIONARY,
    get_location_variants,
    search_by_romanized as search_location_by_romanized,
)


__all__ = [
    # Main class
    "SinhalaTransliterator",
    
    # Convenience functions
    "is_sinhala",
    "transliterate",
    "generate_variants",
    
    # Dictionaries
    "NAME_DICTIONARY",
    "LOCATION_DICTIONARY",
    
    # Dictionary helpers
    "get_name_variants",
    "get_location_variants",
    "search_name_by_romanized",
    "search_location_by_romanized",
    
    # Character mappings
    "VOWELS",
    "CONSONANTS",
    "VOWEL_SIGNS",
    "VARIANT_RULES",
    "VARIANT_RULES_EXTENDED",
    
    # Constants
    "SINHALA_UNICODE_START",
    "SINHALA_UNICODE_END",
]
