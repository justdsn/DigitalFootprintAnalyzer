# =============================================================================
# SINHALA TRANSLITERATION ENGINE
# =============================================================================
# Main transliteration service for converting Sinhala text to romanized English.
# Supports names, locations, and general text with spelling variant generation.
# =============================================================================

"""
Sinhala Transliteration Engine

This module provides comprehensive Sinhala to English transliteration
capabilities with support for:

- Automatic Sinhala script detection
- Character-by-character transliteration
- Dictionary-based name and location lookup
- Spelling variant generation for fuzzy matching

The transliteration follows common Sri Lankan romanization conventions
and generates multiple variants to account for different spelling practices.

Example Usage:
    transliterator = SinhalaTransliterator()
    
    # Check if text is Sinhala
    is_sinhala = transliterator.is_sinhala("සුනිල්")  # True
    
    # Transliterate text
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
    SINHALA_UNICODE_START,
    SINHALA_UNICODE_END,
    is_sinhala_char,
)

# Import dictionaries
from .name_dictionary import NAME_DICTIONARY, get_name_variants
from .location_dictionary import LOCATION_DICTIONARY, get_location_variants


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
        
        Loads the name and location dictionaries for lookup-based
        transliteration of common Sri Lankan names and places.
        """
        # Load dictionaries
        self.name_dict = NAME_DICTIONARY
        self.location_dict = LOCATION_DICTIONARY
        self.variant_rules = VARIANT_RULES
        
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
        Transliterate a single Sinhala word.
        
        First checks the dictionary for known names/locations,
        then falls back to character-by-character transliteration.
        
        Args:
            word: Single Sinhala word
            
        Returns:
            List[str]: List of transliteration variants for this word
        """
        # First, try dictionary lookup
        dict_variants = self._dictionary_lookup(word)
        if dict_variants:
            return dict_variants
        
        # Fall back to character-based transliteration
        base_transliteration = self.transliterate_word(word)
        
        # Generate variants from base transliteration
        variants = self.generate_variants(base_transliteration)
        
        # Always include the base transliteration
        if base_transliteration not in variants:
            variants.insert(0, base_transliteration)
        
        return variants
    
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
        
        Applies variant rules to generate alternative spellings
        that account for different romanization conventions.
        
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
        
        # Apply each variant rule
        for pattern, replacements in self.variant_rules.items():
            new_variants = set()
            for variant in variants:
                if pattern in variant:
                    for replacement in replacements:
                        new_variant = variant.replace(pattern, replacement, 1)
                        new_variants.add(new_variant)
            variants.update(new_variants)
        
        # Limit number of variants
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
