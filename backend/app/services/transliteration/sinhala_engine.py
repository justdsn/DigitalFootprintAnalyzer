# =============================================================================
# SINHALA TRANSLITERATION ENGINE (TWO-TIER APPROACH)
# =============================================================================
# Main transliteration service for converting Sinhala text to romanized English.
# Implements a simple two-tier approach:
#   1. Dictionary Lookup - Names and locations
#   2. Indic NLP Library - For all other Sinhala text
# Supports names, locations, and general text with spelling variant generation.
# =============================================================================

"""
Sinhala Transliteration Engine (Two-Tier Approach)

This module provides comprehensive Sinhala to English transliteration
capabilities using a simple two-tier approach:

Tier 1 - Dictionary Lookup:
    - Checks custom dictionaries for known Sri Lankan names and locations
    - Returns pre-defined transliteration variants for accurate results
    - Covers 50+ common first names, surnames, and locations

Tier 2 - Indic NLP Library:
    - Uses UnicodeIndicTransliterator for unknown Sinhala words
    - Provides linguistically-informed transliteration using established
      Indic NLP algorithms
    - If unavailable and word not in dictionary, returns word as-is

Benefits:
    - High accuracy for common names (dictionary lookup)
    - Linguistic correctness for unknown words (Indic NLP)
    - Simple and maintainable codebase

Example Usage:
    transliterator = SinhalaTransliterator()
    
    # Check if text is Sinhala
    is_sinhala = transliterator.is_sinhala("සුනිල්")  # True
    
    # Transliterate text (uses two-tier approach automatically)
    results = transliterator.transliterate("සුනිල් පෙරේරා")
    # Returns: ['sunil perera', 'suneel perera', ...]
"""

import re
from typing import List, Optional, Set, Tuple

# Import variant rules only (grapheme mapping removed)
from .grapheme_map import (
    VARIANT_RULES,
    VARIANT_RULES_EXTENDED,
    SINHALA_UNICODE_START,
    SINHALA_UNICODE_END,
    is_sinhala_char,
)

# Import dictionaries
from .name_dictionary import NAME_DICTIONARY, get_name_variants
from .location_dictionary import LOCATION_DICTIONARY, get_location_variants

# =============================================================================
# INDIC NLP LIBRARY INTEGRATION
# =============================================================================
# Attempt to import Indic NLP Library for transliteration of unknown words.
# The library provides UnicodeIndicTransliterator for Sinhala→Latin conversion.
# If unavailable, unknown words (not in dictionary) are returned as-is.
# =============================================================================

# Flag to track Indic NLP Library availability
INDIC_NLP_AVAILABLE = False

try:
    # Import UnicodeIndicTransliterator from Indic NLP Library
    # This provides linguistically-informed transliteration for Indic scripts
    from indicnlp.transliterate.unicode_transliterate import UnicodeIndicTransliterator
    INDIC_NLP_AVAILABLE = True
except ImportError:
    # Indic NLP Library not installed - unknown words will be returned as-is
    UnicodeIndicTransliterator = None


# =============================================================================
# CONSTANTS
# =============================================================================

# Maximum number of spelling variants to generate
MAX_VARIANTS = 10

# Maximum variants per word when combining multi-word phrases
MAX_VARIANTS_PER_WORD = 3


# =============================================================================
# SINHALA TRANSLITERATOR CLASS
# =============================================================================

class SinhalaTransliterator:
    """
    Sinhala to English transliteration service.
    
    This class provides methods for detecting Sinhala text and converting
    it to romanized English with support for multiple spelling variants.
    Uses a simple two-tier approach: dictionary lookup + Indic NLP Library.
    
    Attributes:
        name_dict: Dictionary of Sri Lankan names with variants
        location_dict: Dictionary of Sri Lankan locations with variants
        variant_rules: Rules for generating spelling alternatives
        
    Example:
        >>> transliterator = SinhalaTransliterator()
        >>> transliterator.is_sinhala("ගයාන්")
        True
        >>> transliterator.transliterate("ගයාන්")
        ['gayan', 'gayaan']
    """
    
    def __init__(self):
        """
        Initialize the Sinhala Transliterator with dictionaries and rules.
        
        Sets up the two-tier transliteration engine with:
        - Name and location dictionaries for Tier 1 lookup
        - Indic NLP Library integration for Tier 2 (if available)
        - Extended variant rules for comprehensive spelling variant generation
        
        The engine automatically detects Indic NLP Library availability.
        If Indic NLP is unavailable and word is not in dictionary, 
        the word is returned as-is.
        """
        # Load dictionaries for Tier 1 - Dictionary lookup
        self.name_dict = NAME_DICTIONARY
        self.location_dict = LOCATION_DICTIONARY
        
        # Use extended variant rules for comprehensive variant generation
        # Each pattern maps to a list of possible replacements
        self.variant_rules = VARIANT_RULES_EXTENDED
        
        # Store availability flag for Tier 2 - Indic NLP
        self.indic_nlp_available = INDIC_NLP_AVAILABLE
        
        # Build combined lookup for fast dictionary matching
        self._build_lookup_cache()
        
        # Build combined dictionary for _transliterate_word
        self.all_dictionaries = {}
        self.all_dictionaries.update(self.name_dict)
        self.all_dictionaries.update(self.location_dict)
    
    def _build_lookup_cache(self) -> None:
        """
        Build a cache for fast dictionary lookups.
        
        Combines name and location dictionaries into a single lookup
        structure for efficient transliteration.
        """
        self.lookup_cache = {}
        self.lookup_cache.update(self.name_dict)
        self.lookup_cache.update(self.location_dict)
    
    # =========================================================================
    # SINHALA DETECTION
    # =========================================================================
    
    def is_sinhala(self, text: str) -> bool:
        """
        Detect if text contains Sinhala Unicode characters.
        
        Checks if any character in the text falls within the Sinhala
        Unicode range (U+0D80-U+0DFF).
        
        Args:
            text: Input text to check
            
        Returns:
            bool: True if text contains Sinhala characters, False otherwise
            
        Example:
            >>> transliterator.is_sinhala("Hello")
            False
            >>> transliterator.is_sinhala("ආයුබෝවන්")
            True
            >>> transliterator.is_sinhala("Hello ආයුබෝවන්")
            True
        """
        if not text:
            return False
        
        # Use any() for early return on first Sinhala character found
        return any(
            SINHALA_UNICODE_START <= ord(char) <= SINHALA_UNICODE_END
            for char in text
        )
    
    def get_sinhala_ratio(self, text: str) -> float:
        """
        Calculate the ratio of Sinhala characters in the text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            float: Ratio of Sinhala characters (0.0 to 1.0)
            
        Example:
            >>> transliterator.get_sinhala_ratio("Hello ආයුබෝවන්")
            0.5  # approximately
        """
        if not text:
            return 0.0
        
        # Count non-whitespace characters
        non_space_chars = [c for c in text if not c.isspace()]
        if not non_space_chars:
            return 0.0
        
        sinhala_count = sum(1 for c in non_space_chars if is_sinhala_char(c))
        return sinhala_count / len(non_space_chars)
    
    # =========================================================================
    # MAIN TRANSLITERATION
    # =========================================================================
    
    def transliterate(self, text: str) -> List[str]:
        """
        Transliterate Sinhala text to romanized English variants.
        
        This method:
        1. Checks for dictionary matches (names/locations)
        2. Falls back to character-by-character transliteration
        3. Generates spelling variants for each result
        
        Args:
            text: Sinhala text to transliterate
            
        Returns:
            List[str]: List of romanized variants (unique, sorted)
            
        Example:
            >>> transliterator.transliterate("දුෂාන් පෙරේරා")
            ['dushan perera', 'dushaan perera', 'dushan pereera', ...]
        """
        if not text:
            return []
        
        # Check if text is Sinhala
        if not self.is_sinhala(text):
            return [text.lower()]
        
        # Split into words and transliterate each
        words = text.strip().split()
        if not words:
            return []
        
        # Transliterate each word
        word_variants = []
        for word in words:
            variants = self._transliterate_word(word)
            word_variants.append(variants)
        
        # Combine word variants
        results = self._combine_word_variants(word_variants)
        
        # Remove duplicates and sort
        unique_results = list(set(results))
        unique_results.sort(key=len)
        
        return unique_results
    
    def _transliterate_word(self, word: str) -> List[str]:
        """
        Transliterate a single Sinhala word using two-tier approach.
        
        This method implements the simple two-tier transliteration strategy:
        
        Tier 1 - Dictionary Lookup:
            First checks custom dictionaries for known Sri Lankan names
            and locations. Returns pre-defined variants if found.
        
        Tier 2 - Indic NLP Library:
            If dictionary lookup fails and Indic NLP Library is available,
            uses UnicodeIndicTransliterator for linguistically-informed
            transliteration of unknown Sinhala words.
        
        If neither works, the word is returned as-is.
        
        Args:
            word: Single Sinhala word to transliterate
            
        Returns:
            List[str]: List of transliteration variants for this word
        """
        # ---------------------------------------------------------------------
        # TIER 1: Dictionary lookup for known names/locations
        # Priority given to custom dictionaries for accurate Sri Lankan
        # name/location transliteration with pre-defined variants
        # ---------------------------------------------------------------------
        if word in self.all_dictionaries:
            return self.all_dictionaries[word].copy()
        
        # ---------------------------------------------------------------------
        # TIER 2: Indic NLP Library for unknown Sinhala words
        # Uses linguistically-informed transliteration algorithms when
        # the library is available
        # ---------------------------------------------------------------------
        if INDIC_NLP_AVAILABLE and self.is_sinhala(word):
            result = self._indic_nlp_transliterate(word)
            if result:
                return self.generate_variants(result)
        
        # ---------------------------------------------------------------------
        # If neither works, return word as-is
        # ---------------------------------------------------------------------
        return [word]
    
    def _indic_nlp_transliterate(self, word: str) -> Optional[str]:
        """
        Transliterate a word using Indic NLP Library.
        
        Uses UnicodeIndicTransliterator to convert Sinhala text to Latin
        script using linguistically-informed algorithms.
        
        Args:
            word: Sinhala word to transliterate
            
        Returns:
            str or None: Transliterated text, or None if unavailable/failed
        """
        # Check if Indic NLP Library is available
        if not INDIC_NLP_AVAILABLE or UnicodeIndicTransliterator is None:
            return None
        
        try:
            # Use Indic NLP transliterator: Sinhala (si) to English (en)
            # The library handles complex phoneme mappings and conjuncts
            result = UnicodeIndicTransliterator.transliterate(word, 'si', 'en')
            
            # Check if transliteration produced a different result (not just original text)
            if result and result != word:
                return result.lower()
            return None
        except Exception:
            # Graceful degradation if transliteration fails
            return None
    
    def _combine_word_variants(self, word_variants: List[List[str]]) -> List[str]:
        """
        Combine variants from multiple words into complete phrases.
        
        For efficiency, limits combinations when there are many variants.
        
        Args:
            word_variants: List of variant lists, one per word
            
        Returns:
            List[str]: Combined phrase variants
        """
        if not word_variants:
            return []
        
        if len(word_variants) == 1:
            return word_variants[0]
        
        # Limit variants per word to avoid combinatorial explosion
        limited_variants = [
            variants[:MAX_VARIANTS_PER_WORD] for variants in word_variants
        ]
        
        # Build combinations
        results = ['']
        for word_list in limited_variants:
            new_results = []
            for prefix in results:
                for word in word_list:
                    if prefix:
                        new_results.append(f"{prefix} {word}")
                    else:
                        new_results.append(word)
            results = new_results
        
        return results
    
    # =========================================================================
    # VARIANT GENERATION
    # =========================================================================
    
    def generate_variants(self, base: str) -> List[str]:
        """
        Generate spelling variants from a base romanization.
        
        Uses the extended variant rules (VARIANT_RULES_EXTENDED) to generate
        alternative spellings that account for different romanization
        conventions common in Sri Lankan names and places.
        
        The method applies pattern replacements iteratively to generate
        comprehensive spelling variants for fuzzy matching support.
        
        Args:
            base: Base romanized text
            
        Returns:
            List[str]: List of spelling variants (including original)
            
        Example:
            >>> transliterator.generate_variants("dushan")
            ['dushan', 'dushaan', 'dusan']
        """
        if not base:
            return []
        
        variants = {base}
        
        # Apply each variant rule from extended rules
        # Extended rules map patterns to lists of possible replacements
        for pattern, replacements in self.variant_rules.items():
            new_variants = set()
            for variant in variants:
                if pattern in variant:
                    # Iterate through all replacement options for comprehensive variants
                    for replacement in replacements:
                        new_variant = variant.replace(pattern, replacement, 1)
                        new_variants.add(new_variant)
            variants.update(new_variants)
        
        # Limit number of variants to prevent explosion
        result = list(variants)
        result.sort(key=len)
        return result[:MAX_VARIANTS]
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def get_name_variants(self, sinhala_name: str) -> List[str]:
        """
        Get transliteration variants for a known name.
        
        Args:
            sinhala_name: Name in Sinhala script
            
        Returns:
            List[str]: List of romanized name variants
            
        Example:
            >>> transliterator.get_name_variants("කමල්")
            ['kamal', 'kamaal']
        """
        return get_name_variants(sinhala_name)
    
    def get_location_variants(self, sinhala_location: str) -> List[str]:
        """
        Get transliteration variants for a known location.
        
        Args:
            sinhala_location: Location name in Sinhala script
            
        Returns:
            List[str]: List of romanized location variants
            
        Example:
            >>> transliterator.get_location_variants("කොළඹ")
            ['colombo', 'kolamba', 'kolomba']
        """
        return get_location_variants(sinhala_location)
    
    def contains_name(self, text: str) -> Tuple[bool, Optional[str], List[str]]:
        """
        Check if text contains a known Sri Lankan name.
        
        Args:
            text: Text to check (can be Sinhala or English)
            
        Returns:
            Tuple of (found: bool, sinhala_name: str or None, variants: List[str])
        """
        if not text:
            return (False, None, [])
        
        # Check if text is a known Sinhala name
        if text in self.name_dict:
            return (True, text, self.name_dict[text])
        
        # Check if text matches a romanized variant
        text_lower = text.lower()
        for sinhala, variants in self.name_dict.items():
            if text_lower in [v.lower() for v in variants]:
                return (True, sinhala, variants)
        
        return (False, None, [])
    
    def contains_location(self, text: str) -> Tuple[bool, Optional[str], List[str]]:
        """
        Check if text contains a known Sri Lankan location.
        
        Args:
            text: Text to check (can be Sinhala or English)
            
        Returns:
            Tuple of (found: bool, sinhala_location: str or None, variants: List[str])
        """
        if not text:
            return (False, None, [])
        
        # Check if text is a known Sinhala location
        if text in self.location_dict:
            return (True, text, self.location_dict[text])
        
        # Check if text matches a romanized variant
        text_lower = text.lower()
        for sinhala, variants in self.location_dict.items():
            if text_lower in [v.lower() for v in variants]:
                return (True, sinhala, variants)
        
        return (False, None, [])


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

# Create a default transliterator instance for module-level usage
_default_transliterator = SinhalaTransliterator()


def is_sinhala(text: str) -> bool:
    """Module-level convenience function for Sinhala detection."""
    return _default_transliterator.is_sinhala(text)


def transliterate(text: str) -> List[str]:
    """Module-level convenience function for transliteration."""
    return _default_transliterator.transliterate(text)


def generate_variants(base: str) -> List[str]:
    """Module-level convenience function for variant generation."""
    return _default_transliterator.generate_variants(base)
