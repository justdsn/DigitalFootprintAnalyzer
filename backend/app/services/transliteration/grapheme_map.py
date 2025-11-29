# =============================================================================
# SINHALA VARIANT RULES
# =============================================================================
# Rules for generating spelling variants from romanized Sinhala text.
# Used by the SinhalaTransliterator for variant generation only.
# Grapheme mapping (character-by-character transliteration) has been removed
# for simplicity - the system now uses Dictionary + Indic NLP Library.
# =============================================================================

"""
Sinhala Variant Rules

This module contains rules for generating spelling variants from romanized
Sinhala text. These rules are used for fuzzy matching support.

NOTE: Grapheme mapping (VOWELS, CONSONANTS, VOWEL_SIGNS) has been removed.
The transliteration engine now uses only:
  - Tier 1: Dictionary lookup for known names/locations
  - Tier 2: Indic NLP Library for unknown Sinhala words

This module provides:
- VARIANT_RULES: Simple pattern → replacement mappings
- VARIANT_RULES_EXTENDED: Comprehensive pattern → alternatives mappings
- SINHALA_UNICODE_START/END: Constants for Sinhala detection
- is_sinhala_char(): Helper function for character detection

Example:
    >>> from grapheme_map import VARIANT_RULES, is_sinhala_char
    >>> VARIANT_RULES.get('aa')
    'a'
    >>> is_sinhala_char('ක')
    True
"""


# =============================================================================
# VARIANT RULES (Dictionary Format)
# =============================================================================
# Rules for generating common spelling alternatives.
# These account for different romanization conventions and common variations
# in Sri Lankan English spellings.
#
# Format: source pattern -> primary simplified variant
# This dictionary format enables efficient lookup for common romanization
# patterns used in Sri Lankan names and locations.
# =============================================================================

VARIANT_RULES = {
    # Vowel length variations (long vowels → short vowels)
    # These simplifications handle common spelling variations in Sri Lankan names
    'aa': 'a',      # e.g., 'kamaal' → 'kamal'
    'ee': 'i',      # e.g., 'suneel' → 'sunil'
    'oo': 'u',      # e.g., 'roohaan' → 'ruhan'
    
    # Aspirated consonant simplifications
    # Common in Sri Lankan romanization where aspiration is often dropped
    'th': 't',      # e.g., 'thilak' → 'tilak'
    'dh': 'd',      # e.g., 'dharma' → 'darma'
    'sh': 's',      # e.g., 'shantha' → 'santa'
    'ch': 'c',      # e.g., 'chandra' → 'candra'
}

# Extended variant rules for comprehensive variant generation
# Maps source patterns to all possible alternatives
VARIANT_RULES_EXTENDED = {
    # Vowel length variations (aa ↔ a)
    'aa': ['a', 'ah'],
    'ee': ['e', 'i', 'ey'],
    'ii': ['i', 'ee', 'y'],
    'oo': ['o', 'u'],
    'uu': ['u', 'oo'],
    
    # Consonant variations
    'th': ['t', 'd'],
    'dh': ['d', 'th'],
    'sh': ['s', 'ch'],
    'ch': ['c', 'tch'],
    'ph': ['p', 'f'],
    'bh': ['b'],
    'kh': ['k', 'c'],
    'gh': ['g'],
    
    # Name-specific variations
    'v': ['w'],
    'w': ['v'],
    'j': ['g', 'dj'],
    'y': ['i', 'ie'],
    
    # Common suffix variations
    'ka': ['ke', 'ga'],
    'na': ['ne'],
    'ra': ['re'],
    'la': ['le'],
    'ya': ['ia', 'iya'],
    
    # Common endings
    'an': ['en', 'on'],
    'am': ['em', 'um'],
    'ar': ['er', 'or'],
    'al': ['el', 'ol'],
}


# =============================================================================
# SINHALA UNICODE RANGE
# =============================================================================
# Constants for detecting Sinhala text
# =============================================================================

SINHALA_UNICODE_START = 0x0D80  # Start of Sinhala Unicode block
SINHALA_UNICODE_END = 0x0DFF    # End of Sinhala Unicode block


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def is_sinhala_char(char: str) -> bool:
    """
    Check if a single character is in the Sinhala Unicode range.
    
    Args:
        char: A single character to check
        
    Returns:
        bool: True if character is Sinhala, False otherwise
        
    Example:
        >>> is_sinhala_char('ක')
        True
        >>> is_sinhala_char('a')
        False
    """
    if not char:
        return False
    code_point = ord(char[0])
    return SINHALA_UNICODE_START <= code_point <= SINHALA_UNICODE_END
