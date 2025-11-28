# =============================================================================
# SINHALA TRANSLITERATION ENGINE
# =============================================================================
# Main transliteration engine for converting Sinhala Unicode text to
# romanized English. Supports multiple spelling variants for names.
# =============================================================================

"""
Sinhala Transliteration Engine

This module provides the SinhalaTransliterator class which handles:
- Detection of Sinhala text (Unicode range 0D80-0DFF)
- Conversion of Sinhala text to romanized English
- Generation of multiple spelling variants
- Dictionary-based lookups for known names and places

The transliteration follows standard Sri Lankan conventions while
generating multiple variants that cover common English spelling patterns.

Example Usage:
    transliterator = SinhalaTransliterator()
    
    # Check if text contains Sinhala
    is_sinhala = transliterator.is_sinhala("දුෂාන්")  # True
    
    # Transliterate Sinhala text
    result = transliterator.transliterate("දුෂාන්")  # ['dushan', ...]
    
    # Generate variants for a base romanization
    variants = transliterator.generate_variants("dushan")  # ['dushan', 'dushaan', ...]
"""

from typing import List, Set, Optional, Tuple
import re

# Import grapheme mappings and dictionaries
from app.services.transliteration.grapheme_map import (
    SINHALA_VOWELS,
    SINHALA_CONSONANTS,
    SINHALA_VOWEL_SIGNS,
    SPECIAL_COMBINATIONS,
    ANUSVARA_VISARGA,
    VARIANT_RULES,
    get_all_mappings,
    is_sinhala_char
)
from app.services.transliteration.name_dictionary import (
    get_name_variants,
    get_all_name_variants
)
from app.services.transliteration.location_dictionary import (
    get_location_variants,
    get_all_location_variants
)


# =============================================================================
# SINHALA TRANSLITERATOR CLASS
# =============================================================================

class SinhalaTransliterator:
    """
    Transliterates Sinhala Unicode text to romanized English.
    
    This class provides methods for:
    - Detecting Sinhala text in strings
    - Converting Sinhala text to Roman characters
    - Generating multiple spelling variants for transliterated text
    
    The transliteration uses character mappings for vowels, consonants,
    and diacritics, while also consulting dictionaries for known names
    and places to provide accurate variants.
    
    Attributes:
        mappings: Combined dictionary of all Sinhala to Roman mappings
        virama: The Sinhala virama character (removes inherent vowel)
    
    Example:
        >>> t = SinhalaTransliterator()
        >>> t.is_sinhala("හෙලෝ")
        True
        >>> t.transliterate("දුෂාන්")
        ['dushan', 'dushaan', 'dusan', 'dusaan', 'dhushan']
    """
    
    # Sinhala Unicode range constants
    SINHALA_UNICODE_START = 0x0D80
    SINHALA_UNICODE_END = 0x0DFF
    
    # Virama (hal kirima) - removes inherent vowel
    VIRAMA = '්'  # U+0DCA
    
    def __init__(self):
        """
        Initialize the SinhalaTransliterator.
        
        Loads all character mappings and prepares the transliteration engine.
        """
        # Get combined mappings for all character types
        self.mappings = get_all_mappings()
        
        # Pre-compute sorted special combinations for matching
        # Sort by length (longest first) to ensure proper matching
        self.special_combinations = sorted(
            SPECIAL_COMBINATIONS.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )
    
    # =========================================================================
    # SINHALA DETECTION METHODS
    # =========================================================================
    
    def is_sinhala(self, text: str) -> bool:
        """
        Check if a text contains Sinhala characters.
        
        Examines each character in the text to determine if any fall
        within the Sinhala Unicode range (U+0D80 - U+0DFF).
        
        Args:
            text: The text to check for Sinhala characters
        
        Returns:
            bool: True if any Sinhala characters are found, False otherwise
        
        Example:
            >>> t = SinhalaTransliterator()
            >>> t.is_sinhala("හෙලෝ World")
            True
            >>> t.is_sinhala("Hello World")
            False
        """
        if not text:
            return False
        
        for char in text:
            code_point = ord(char)
            # Check if character is in Sinhala Unicode range
            if self.SINHALA_UNICODE_START <= code_point <= self.SINHALA_UNICODE_END:
                return True
        
        return False
    
    def get_sinhala_ratio(self, text: str) -> float:
        """
        Calculate the ratio of Sinhala characters in the text.
        
        Args:
            text: The text to analyze
        
        Returns:
            float: Ratio of Sinhala characters (0.0 to 1.0)
        
        Example:
            >>> t = SinhalaTransliterator()
            >>> t.get_sinhala_ratio("හෙලෝ")
            1.0
            >>> t.get_sinhala_ratio("50% සිංහල")
            0.5
        """
        if not text:
            return 0.0
        
        # Filter out whitespace for ratio calculation
        non_space_chars = [c for c in text if not c.isspace()]
        if not non_space_chars:
            return 0.0
        
        sinhala_count = sum(1 for c in non_space_chars if is_sinhala_char(c))
        return sinhala_count / len(non_space_chars)
    
    def extract_sinhala_words(self, text: str) -> List[str]:
        """
        Extract words that contain Sinhala characters from text.
        
        Args:
            text: The text to extract Sinhala words from
        
        Returns:
            List[str]: List of words containing Sinhala characters
        
        Example:
            >>> t = SinhalaTransliterator()
            >>> t.extract_sinhala_words("Hello දුෂාන් World")
            ['දුෂාන්']
        """
        if not text:
            return []
        
        # Split by whitespace and filter words containing Sinhala
        words = text.split()
        sinhala_words = [word for word in words if self.is_sinhala(word)]
        
        return sinhala_words
    
    # =========================================================================
    # TRANSLITERATION METHODS
    # =========================================================================
    
    def transliterate(self, text: str) -> List[str]:
        """
        Convert Sinhala text to romanized English with multiple variants.
        
        This is the main transliteration method. It handles:
        1. Dictionary lookup for known names and places
        2. Character-by-character transliteration for unknown text
        3. Generation of spelling variants
        
        Args:
            text: The Sinhala text to transliterate
        
        Returns:
            List[str]: List of possible romanized spellings
        
        Example:
            >>> t = SinhalaTransliterator()
            >>> t.transliterate("දුෂාන්")
            ['dushan', 'dushaan', 'dusan', 'dusaan', 'dhushan']
            
            >>> t.transliterate("කොළඹ")
            ['colombo', 'kolamba', 'kolomba', 'columbo']
        """
        if not text:
            return []
        
        # Clean the input text
        text = text.strip()
        
        # First, check if this is a known name or place in the dictionary
        name_result = get_name_variants(text)
        if name_result:
            return name_result['transliterations']
        
        location_result = get_location_variants(text)
        if location_result:
            return location_result['transliterations']
        
        # If not a known name/place, perform character-by-character transliteration
        base_transliteration = self._transliterate_chars(text)
        
        if not base_transliteration:
            return []
        
        # Generate variants from the base transliteration
        variants = self.generate_variants(base_transliteration)
        
        return variants
    
    def _transliterate_chars(self, text: str) -> str:
        """
        Perform character-by-character transliteration.
        
        Handles consonant-vowel sign combinations and special sequences.
        
        Args:
            text: The Sinhala text to transliterate
        
        Returns:
            str: The base romanized form
        """
        result = []
        i = 0
        
        while i < len(text):
            # Check for special multi-character combinations first
            matched = False
            for combo, roman in self.special_combinations:
                if text[i:].startswith(combo):
                    result.append(roman)
                    i += len(combo)
                    matched = True
                    break
            
            if matched:
                continue
            
            char = text[i]
            
            # Handle vowel signs (diacritics)
            if char in SINHALA_VOWEL_SIGNS:
                result.append(SINHALA_VOWEL_SIGNS[char])
                i += 1
                continue
            
            # Handle virama (hal kirima) - removes inherent vowel
            if char == self.VIRAMA:
                # Virama removes the inherent 'a' from the previous consonant
                i += 1
                continue
            
            # Handle consonants
            if char in SINHALA_CONSONANTS:
                result.append(SINHALA_CONSONANTS[char])
                
                # Check if followed by virama or vowel sign
                if i + 1 < len(text):
                    next_char = text[i + 1]
                    if next_char == self.VIRAMA:
                        # No inherent vowel
                        i += 2
                        continue
                    elif next_char in SINHALA_VOWEL_SIGNS:
                        # Vowel sign replaces inherent 'a'
                        i += 1
                        continue
                
                # No virama or vowel sign, add inherent 'a'
                result.append('a')
                i += 1
                continue
            
            # Handle independent vowels
            if char in SINHALA_VOWELS:
                result.append(SINHALA_VOWELS[char])
                i += 1
                continue
            
            # Handle anusvara and visarga
            if char in ANUSVARA_VISARGA:
                result.append(ANUSVARA_VISARGA[char])
                i += 1
                continue
            
            # For any other character (spaces, punctuation, etc.)
            if not is_sinhala_char(char):
                result.append(char)
            
            i += 1
        
        return ''.join(result)
    
    # =========================================================================
    # VARIANT GENERATION METHODS
    # =========================================================================
    
    def generate_variants(self, base: str) -> List[str]:
        """
        Generate spelling variations for a romanized base form.
        
        Applies common spelling variation rules to create multiple
        possible English spellings. For example:
        - 'aa' -> 'a', 'ah'
        - 'th' -> 't', 'dh'
        - 'sh' -> 's', 'sch'
        
        Args:
            base: The base romanized form to generate variants from
        
        Returns:
            List[str]: List of spelling variants (including the base form)
        
        Example:
            >>> t = SinhalaTransliterator()
            >>> t.generate_variants("dushan")
            ['dushan', 'dushaan', 'dusan', 'dusaan', 'dhushan']
        """
        if not base:
            return []
        
        # Start with the base form
        variants: Set[str] = {base.lower()}
        
        # First, check if base matches a known name/place and get dictionary variants
        name_variants = get_all_name_variants(base)
        if name_variants:
            variants.update([v.lower() for v in name_variants])
        
        location_variants = get_all_location_variants(base)
        if location_variants:
            variants.update([v.lower() for v in location_variants])
        
        # Apply variant rules to generate more variants
        base_lower = base.lower()
        
        # Apply each variant rule
        for pattern, replacements in VARIANT_RULES.items():
            # Handle end-of-string patterns
            if pattern.endswith('$'):
                actual_pattern = pattern[:-1]
                if base_lower.endswith(actual_pattern):
                    prefix = base_lower[:-len(actual_pattern)]
                    for replacement in replacements:
                        variants.add(prefix + replacement)
            else:
                # Regular pattern matching
                if pattern in base_lower:
                    for replacement in replacements:
                        variant = base_lower.replace(pattern, replacement, 1)
                        variants.add(variant)
        
        # Generate additional common variants
        additional = self._generate_common_variants(base_lower)
        variants.update(additional)
        
        # Sort variants with the base form first
        sorted_variants = sorted(list(variants), key=lambda x: (x != base_lower, x))
        
        return sorted_variants
    
    def _generate_common_variants(self, base: str) -> Set[str]:
        """
        Generate additional common spelling variants.
        
        Applies heuristics for common Sri Lankan name spelling patterns.
        
        Args:
            base: The base romanized form
        
        Returns:
            Set[str]: Set of additional variants
        """
        variants: Set[str] = set()
        
        # Common ending variations
        if base.endswith('an'):
            variants.add(base + 'e')  # dushan -> dushane
            variants.add(base[:-2] + 'en')  # dushan -> dushen
        
        if base.endswith('a'):
            variants.add(base + 'h')  # prasada -> prasadah
        
        if base.endswith('e'):
            variants.add(base[:-1] + 'a')  # perera -> perera (but also perere -> perera)
        
        # W/V interchange (common in Sri Lankan names)
        if 'w' in base:
            variants.add(base.replace('w', 'v'))
        if 'v' in base:
            variants.add(base.replace('v', 'w'))
        
        # C/K interchange
        if 'c' in base and 'ch' not in base:
            variants.add(base.replace('c', 'k'))
        
        return variants
    
    # =========================================================================
    # BATCH PROCESSING METHODS
    # =========================================================================
    
    def transliterate_names(self, names: List[str]) -> List[Tuple[str, List[str]]]:
        """
        Transliterate a list of names.
        
        Args:
            names: List of names (in Sinhala or romanized form)
        
        Returns:
            List of tuples containing (original_name, [variants])
        
        Example:
            >>> t = SinhalaTransliterator()
            >>> t.transliterate_names(["දුෂාන්", "perera"])
            [("දුෂාන්", ["dushan", ...]), ("perera", ["perera", "pererah", ...])]
        """
        results = []
        for name in names:
            if self.is_sinhala(name):
                variants = self.transliterate(name)
            else:
                variants = self.generate_variants(name)
            results.append((name, variants))
        return results
    
    def find_matches(self, sinhala_text: str, romanized_list: List[str]) -> List[str]:
        """
        Find romanized strings that match a Sinhala name.
        
        Useful for finding potential matches across different spellings.
        
        Args:
            sinhala_text: The Sinhala text to match
            romanized_list: List of romanized strings to search
        
        Returns:
            List[str]: Romanized strings that match the Sinhala text
        
        Example:
            >>> t = SinhalaTransliterator()
            >>> t.find_matches("දුෂාන්", ["dushan", "john", "dushaan"])
            ["dushan", "dushaan"]
        """
        if not self.is_sinhala(sinhala_text):
            return []
        
        variants = set(self.transliterate(sinhala_text))
        matches = [r for r in romanized_list if r.lower() in variants]
        
        return matches


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
