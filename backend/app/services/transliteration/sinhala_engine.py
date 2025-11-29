# =============================================================================
# SINHALA TRANSLITERATION ENGINE (HYBRID APPROACH)
# =============================================================================
# Main transliteration service for converting Sinhala text to romanized English.
# Implements a three-tier hybrid approach combining:
#   1. Custom dictionaries for known names/locations
#   2. Indic NLP Library for unknown Sinhala words
#   3. Grapheme mapping as fallback
# Supports names, locations, and general text with spelling variant generation.
# =============================================================================

"""
Sinhala Transliteration Engine (Hybrid Approach)

This module provides comprehensive Sinhala to English transliteration
capabilities using a three-tier hybrid approach:

Tier 1 - Dictionary Lookup:
    - Checks custom dictionaries for known Sri Lankan names and locations
    - Returns pre-defined transliteration variants for accurate results
    - Covers 50+ common first names, surnames, and locations

Tier 2 - Indic NLP Library:
    - Uses UnicodeIndicTransliterator for unknown Sinhala words
    - Provides linguistically-informed transliteration using established
      Indic NLP algorithms
    - Falls back gracefully if library is unavailable

Tier 3 - Grapheme Mapping:
    - Character-by-character transliteration as final fallback
    - Uses comprehensive Sinhala Unicode to English mappings
    - Handles edge cases and mixed-script text

Benefits of Hybrid Approach:
    - High accuracy for common names (dictionary lookup)
    - Linguistic correctness for unknown words (Indic NLP)
    - Robust fallback for edge cases (grapheme mapping)
    - Graceful degradation when dependencies unavailable

Example Usage:
    transliterator = SinhalaTransliterator()
    
    # Check if text is Sinhala
    is_sinhala = transliterator.is_sinhala("සුනිල්")  # True
    
    # Transliterate text (uses hybrid approach automatically)
    results = transliterator.transliterate("සුනිල් පෙරේරා")
    # Returns: ['sunil perera', 'suneel perera', ...]
"""

import re
from typing import List, Optional, Set, Tuple

# Import grapheme mappings
from .grapheme_map import (
    VOWELS,
    CONSONANTS,
    CONSONANT_ROOTS,
    VOWEL_SIGNS,
    SPECIAL_CHARS,
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
# Attempt to import Indic NLP Library for enhanced transliteration.
# The library provides UnicodeIndicTransliterator for Sinhala→Latin conversion.
# If unavailable, the engine falls back to grapheme-based transliteration.
# =============================================================================

# Flag to track Indic NLP Library availability for graceful degradation
INDIC_NLP_AVAILABLE = False

try:
    # Import UnicodeIndicTransliterator from Indic NLP Library
    # This provides linguistically-informed transliteration for Indic scripts
    from indicnlp.transliterate.unicode_transliterate import UnicodeIndicTransliterator
    INDIC_NLP_AVAILABLE = True
except ImportError:
    # Indic NLP Library not installed - will use grapheme fallback
    # This ensures the engine works even without the optional dependency
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
        
        Sets up the hybrid transliteration engine with:
        - Name and location dictionaries for Tier 1 lookup
        - Indic NLP Library integration for Tier 2 (if available)
        - Extended variant rules for comprehensive spelling variant generation
        
        The engine automatically detects Indic NLP Library availability
        and falls back to grapheme mapping when necessary.
        """
        # Load dictionaries for Tier 1 - Dictionary lookup
        self.name_dict = NAME_DICTIONARY
        self.location_dict = LOCATION_DICTIONARY
        
        # Use extended variant rules for comprehensive variant generation
        # Supports both dictionary format (single value) and list format
        self.variant_rules = VARIANT_RULES_EXTENDED
        
        # Store availability flag for Tier 2 - Indic NLP
        self.indic_nlp_available = INDIC_NLP_AVAILABLE
        
        # Build combined lookup for fast dictionary matching
        self._build_lookup_cache()
    
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
        Transliterate a single Sinhala word using three-tier hybrid approach.
        
        This method implements the hybrid transliteration strategy:
        
        Tier 1 - Dictionary Lookup:
            First checks custom dictionaries for known Sri Lankan names
            and locations. Returns pre-defined variants if found.
        
        Tier 2 - Indic NLP Library:
            If dictionary lookup fails and Indic NLP Library is available,
            uses UnicodeIndicTransliterator for linguistically-informed
            transliteration of unknown Sinhala words.
        
        Tier 3 - Grapheme Mapping:
            Falls back to character-by-character transliteration using
            the comprehensive Sinhala grapheme mappings.
        
        All approaches generate spelling variants for fuzzy matching support.
        
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
        dict_variants = self._dictionary_lookup(word)
        if dict_variants:
            return dict_variants
        
        # ---------------------------------------------------------------------
        # TIER 2: Indic NLP Library for unknown Sinhala words
        # Uses linguistically-informed transliteration algorithms when
        # the library is available, providing better results than
        # simple character mapping for complex Sinhala phonemes
        # ---------------------------------------------------------------------
        indic_transliteration = self._indic_nlp_transliterate(word)
        if indic_transliteration:
            # Generate variants from Indic NLP result for fuzzy matching
            variants = self.generate_variants(indic_transliteration)
            if indic_transliteration not in variants:
                variants.insert(0, indic_transliteration)
            return variants
        
        # ---------------------------------------------------------------------
        # TIER 3: Grapheme mapping as fallback
        # Character-by-character transliteration using comprehensive
        # Sinhala Unicode mappings - ensures robustness when other
        # methods are unavailable or fail
        # ---------------------------------------------------------------------
        base_transliteration = self.transliterate_word(word)
        
        # Generate variants from base transliteration for fuzzy matching
        variants = self.generate_variants(base_transliteration)
        
        # Always include the base transliteration
        if base_transliteration not in variants:
            variants.insert(0, base_transliteration)
        
        return variants
    
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
            # Use Indic NLP transliterator: Sinhala (si) to Latin (la)
            # The library handles complex phoneme mappings and conjuncts
            result = UnicodeIndicTransliterator.transliterate(word, 'si', 'la')
            
            # Return lowercase for consistent matching
            return result.lower() if result else None
        except Exception:
            # Graceful degradation if transliteration fails
            # Fall through to grapheme mapping in calling method
            return None
    
    def _dictionary_lookup(self, word: str) -> Optional[List[str]]:
        """
        Look up a word in the name/location dictionaries.
        
        Args:
            word: Sinhala word to look up
            
        Returns:
            List[str] or None: Dictionary variants if found, None otherwise
        """
        # Strip any punctuation
        clean_word = word.strip()
        
        # Check combined lookup cache
        if clean_word in self.lookup_cache:
            return self.lookup_cache[clean_word].copy()
        
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
    # CHARACTER-LEVEL TRANSLITERATION
    # =========================================================================
    
    def transliterate_word(self, word: str) -> str:
        """
        Transliterate a single Sinhala word character by character.
        
        Handles:
        - Independent vowels
        - Consonants with inherent vowels
        - Consonant + vowel sign combinations
        - Special characters (anusvara, visarga)
        - Virama (hal kirīma) for consonant-only sounds
        
        Args:
            word: Single Sinhala word to transliterate
            
        Returns:
            str: Romanized transliteration of the word
            
        Example:
            >>> transliterator.transliterate_word("සිංහල")
            'sinhala'
        """
        if not word:
            return ''
        
        result = []
        i = 0
        
        while i < len(word):
            char = word[i]
            
            # Skip non-Sinhala characters
            if not is_sinhala_char(char):
                if char not in ['\u200d', '\u200c']:  # Skip ZWJ/ZWNJ
                    result.append(char)
                i += 1
                continue
            
            # Handle independent vowels
            if char in VOWELS:
                result.append(VOWELS[char])
                i += 1
                continue
            
            # Handle special characters (anusvara, visarga)
            if char in SPECIAL_CHARS:
                result.append(SPECIAL_CHARS[char])
                i += 1
                continue
            
            # Handle consonants
            if char in CONSONANTS:
                # Get consonant root
                consonant_root = CONSONANT_ROOTS.get(char, CONSONANTS[char][:-1])
                
                # Check what follows
                if i + 1 < len(word):
                    next_char = word[i + 1]
                    
                    # Check for virama (hal kirīma)
                    if next_char == '්':
                        result.append(consonant_root)
                        i += 2
                        continue
                    
                    # Check for vowel sign
                    if next_char in VOWEL_SIGNS:
                        vowel_sound = VOWEL_SIGNS[next_char]
                        if vowel_sound:  # Not virama
                            result.append(consonant_root + vowel_sound)
                        else:
                            result.append(consonant_root)
                        i += 2
                        continue
                
                # Consonant with inherent 'a' vowel
                result.append(CONSONANTS[char])
                i += 1
                continue
            
            # Handle standalone vowel signs (shouldn't occur normally)
            if char in VOWEL_SIGNS:
                result.append(VOWEL_SIGNS[char])
                i += 1
                continue
            
            # Unknown character - skip
            i += 1
        
        return ''.join(result)
    
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
                    # Handle both dict format (single value) and list format
                    if isinstance(replacements, list):
                        for replacement in replacements:
                            new_variant = variant.replace(pattern, replacement, 1)
                            new_variants.add(new_variant)
                    else:
                        # Dictionary format: single replacement value
                        new_variant = variant.replace(pattern, replacements, 1)
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
