# =============================================================================
# FUZZY MATCHER
# =============================================================================
# Provides fuzzy string matching utilities for comparing names, bios,
# and detecting username typosquatting across platforms.
# =============================================================================

"""
Fuzzy Matcher Module

This module provides fuzzy matching utilities for:
- Name matching with support for multiple name formats
- Bio text similarity comparison
- Username typosquatting detection

These utilities are used by the correlation engine to find matches
and detect potential impersonation across social media platforms.

Example Usage:
    matcher = FuzzyMatcher()
    
    # Compare names with fuzzy logic
    match = matcher.match_names("John Doe", "Jon D.")  # True, score ~0.8
    
    # Check if a username is typosquatting another
    is_squat = matcher.is_typosquatting("john_doe", "j0hn_d0e")  # True
"""

from typing import List, Tuple, Optional, Dict, Set
import re
from app.services.correlation.similarity_scorer import SimilarityScorer


# =============================================================================
# FUZZY MATCHER CLASS
# =============================================================================

class FuzzyMatcher:
    """
    Provides fuzzy matching utilities for name and text comparison.
    
    This class handles the nuances of comparing PII fields across
    social media platforms, including:
    - Name format variations (First Last vs Last, First)
    - Abbreviations and nicknames
    - Username typosquatting patterns
    
    Attributes:
        scorer: SimilarityScorer instance for calculating similarity metrics
        name_threshold: Minimum score to consider names as matching
        typosquat_threshold: Maximum score difference to flag as typosquatting
    
    Example:
        >>> matcher = FuzzyMatcher()
        >>> matcher.match_names("John Smith", "J. Smith")
        (True, 0.75)
    """
    
    # Common typosquatting character substitutions
    TYPOSQUAT_SUBSTITUTIONS = {
        'a': ['4', '@'],
        'e': ['3'],
        'i': ['1', '!', 'l'],
        'l': ['1', 'i', '|'],
        'o': ['0'],
        's': ['5', '$'],
        't': ['7', '+'],
        'b': ['8'],
        'g': ['9', '6'],
        '_': ['.', '-', ''],
        '.': ['_', '-', ''],
    }
    
    # Common name abbreviations
    NAME_ABBREVIATIONS = {
        'william': ['will', 'bill', 'billy', 'willy'],
        'robert': ['rob', 'bob', 'bobby', 'robbie'],
        'richard': ['rick', 'dick', 'rich', 'ricky'],
        'michael': ['mike', 'mikey', 'mick'],
        'james': ['jim', 'jimmy', 'jamie'],
        'john': ['jon', 'johnny', 'jack'],
        'joseph': ['joe', 'joey'],
        'thomas': ['tom', 'tommy'],
        'david': ['dave', 'davey'],
        'matthew': ['matt', 'matty'],
        'christopher': ['chris', 'kit'],
        'daniel': ['dan', 'danny'],
        'anthony': ['tony', 'ant'],
        'elizabeth': ['liz', 'beth', 'betty', 'lizzy'],
        'jennifer': ['jen', 'jenny'],
        'katherine': ['kate', 'kathy', 'katie', 'kat'],
        'margaret': ['meg', 'maggie', 'peggy', 'marge'],
        'patricia': ['pat', 'patty', 'trish'],
        'susanna': ['sue', 'susie', 'suzy'],
        'samantha': ['sam', 'sammy'],
    }
    
    def __init__(
        self,
        name_threshold: float = 0.7,
        typosquat_threshold: float = 0.85
    ):
        """
        Initialize the FuzzyMatcher.
        
        Args:
            name_threshold: Minimum similarity score to consider names as matching
            typosquat_threshold: Similarity threshold for typosquatting detection
        """
        self.scorer = SimilarityScorer()
        self.name_threshold = name_threshold
        self.typosquat_threshold = typosquat_threshold
        
        # Build reverse abbreviation lookup
        self._abbreviation_map = {}
        for full_name, abbrevs in self.NAME_ABBREVIATIONS.items():
            for abbrev in abbrevs:
                self._abbreviation_map[abbrev] = full_name
            self._abbreviation_map[full_name] = full_name
    
    # =========================================================================
    # NAME MATCHING METHODS
    # =========================================================================
    
    def match_names(
        self,
        name1: str,
        name2: str,
        threshold: Optional[float] = None
    ) -> Tuple[bool, float]:
        """
        Compare two names using fuzzy matching.
        
        Handles various name formats:
        - Full names: "John Smith" vs "John Smith"
        - Reordered: "John Smith" vs "Smith, John"
        - Abbreviated: "John Smith" vs "J. Smith"
        - Nicknames: "William Smith" vs "Bill Smith"
        
        Args:
            name1: First name to compare
            name2: Second name to compare
            threshold: Custom threshold (uses default if None)
        
        Returns:
            Tuple[bool, float]: (is_match, similarity_score)
        
        Example:
            >>> matcher = FuzzyMatcher()
            >>> matcher.match_names("John Smith", "J. Smith")
            (True, 0.75)
            >>> matcher.match_names("John Doe", "Jane Smith")
            (False, 0.3)
        """
        if not name1 or not name2:
            return (False, 0.0)
        
        threshold = threshold or self.name_threshold
        
        # Normalize names
        norm1 = self._normalize_name(name1)
        norm2 = self._normalize_name(name2)
        
        # Direct comparison
        direct_score = self.scorer.token_sort_ratio(norm1, norm2)
        
        # Try expanded names (handle nicknames/abbreviations)
        expanded1 = self._expand_name(norm1)
        expanded2 = self._expand_name(norm2)
        expanded_score = self.scorer.token_sort_ratio(expanded1, expanded2)
        
        # Try partial name matching (first name or last name)
        partial_score = self._partial_name_match(norm1, norm2)
        
        # Use the best score
        best_score = max(direct_score, expanded_score, partial_score)
        
        return (best_score >= threshold, best_score)
    
    def _normalize_name(self, name: str) -> str:
        """
        Normalize a name for comparison.
        
        - Removes punctuation
        - Converts to lowercase
        - Normalizes whitespace
        - Handles "Last, First" format
        
        Args:
            name: Name to normalize
        
        Returns:
            str: Normalized name
        """
        if not name:
            return ""
        
        # Convert to lowercase
        name = name.lower().strip()
        
        # Handle "Last, First" format
        if ',' in name:
            parts = [p.strip() for p in name.split(',', 1)]
            if len(parts) == 2:
                name = f"{parts[1]} {parts[0]}"
        
        # Remove titles and suffixes
        titles = ['mr', 'mrs', 'ms', 'dr', 'prof', 'jr', 'sr', 'ii', 'iii', 'iv']
        words = name.split()
        words = [w for w in words if w.rstrip('.') not in titles]
        
        # Remove punctuation (keep spaces)
        name = ' '.join(words)
        name = re.sub(r'[^\w\s]', '', name)
        
        # Normalize whitespace
        name = ' '.join(name.split())
        
        return name
    
    def _expand_name(self, name: str) -> str:
        """
        Expand abbreviated/nickname names to full forms.
        
        Args:
            name: Name to expand
        
        Returns:
            str: Name with expanded first name if it's a known nickname
        """
        if not name:
            return ""
        
        words = name.split()
        if not words:
            return name
        
        # Try to expand the first word (first name)
        first_name = words[0]
        if first_name in self._abbreviation_map:
            words[0] = self._abbreviation_map[first_name]
        
        return ' '.join(words)
    
    def _partial_name_match(self, name1: str, name2: str) -> float:
        """
        Match names partially (first name or last name match).
        
        Args:
            name1: First name
            name2: Second name
        
        Returns:
            float: Partial match score
        """
        words1 = name1.split()
        words2 = name2.split()
        
        if not words1 or not words2:
            return 0.0
        
        # Check if any word from name1 closely matches any word from name2
        best_match = 0.0
        for w1 in words1:
            for w2 in words2:
                if len(w1) > 1 and len(w2) > 1:  # Skip single-letter initials
                    score = self.scorer.jaro_winkler(w1, w2)
                    best_match = max(best_match, score)
        
        return best_match * 0.9  # Slight penalty for partial match
    
    # =========================================================================
    # BIO SIMILARITY METHODS
    # =========================================================================
    
    def compare_bios(self, bio1: str, bio2: str) -> Tuple[float, Dict[str, any]]:
        """
        Compare two bio texts for similarity.
        
        Uses cosine similarity for overall text comparison and
        also identifies common keywords and phrases.
        
        Args:
            bio1: First bio text
            bio2: Second bio text
        
        Returns:
            Tuple[float, Dict]: (similarity_score, analysis_details)
        
        Example:
            >>> matcher = FuzzyMatcher()
            >>> score, details = matcher.compare_bios(
            ...     "Software developer from Colombo",
            ...     "Developer based in Colombo, Sri Lanka"
            ... )
            >>> print(f"Score: {score:.2f}")
            Score: 0.65
        """
        if not bio1 and not bio2:
            return (1.0, {'common_words': [], 'unique_words_1': [], 'unique_words_2': []})
        if not bio1 or not bio2:
            return (0.0, {'common_words': [], 'unique_words_1': [], 'unique_words_2': []})
        
        # Calculate cosine similarity
        cosine_score = self.scorer.cosine_similarity(bio1, bio2)
        
        # Extract meaningful words (longer than 3 chars)
        words1 = set(w.lower() for w in re.findall(r'\b\w+\b', bio1) if len(w) > 3)
        words2 = set(w.lower() for w in re.findall(r'\b\w+\b', bio2) if len(w) > 3)
        
        common_words = words1 & words2
        unique_words_1 = words1 - words2
        unique_words_2 = words2 - words1
        
        # Jaccard similarity of word sets
        if words1 | words2:
            jaccard_score = len(common_words) / len(words1 | words2)
        else:
            jaccard_score = 0.0
        
        # Combined score (weighted average)
        combined_score = 0.6 * cosine_score + 0.4 * jaccard_score
        
        analysis = {
            'common_words': list(common_words),
            'unique_words_1': list(unique_words_1),
            'unique_words_2': list(unique_words_2),
            'cosine_score': cosine_score,
            'jaccard_score': jaccard_score
        }
        
        return (combined_score, analysis)
    
    # =========================================================================
    # TYPOSQUATTING DETECTION METHODS
    # =========================================================================
    
    def is_typosquatting(
        self,
        original_username: str,
        suspicious_username: str,
        threshold: Optional[float] = None
    ) -> Tuple[bool, float, List[str]]:
        """
        Detect if a username is typosquatting another.
        
        Typosquatting involves creating usernames that look similar
        to legitimate ones, often using character substitutions like:
        - john_doe -> j0hn_d0e (letter to number)
        - john_doe -> john__doe (added characters)
        - john_doe -> johndoe (removed separator)
        
        Args:
            original_username: The legitimate username
            suspicious_username: The potentially typosquatting username
        
        Returns:
            Tuple[bool, float, List[str]]: 
                (is_typosquatting, similarity_score, detected_techniques)
        
        Example:
            >>> matcher = FuzzyMatcher()
            >>> is_squat, score, techniques = matcher.is_typosquatting(
            ...     "john_doe", "j0hn_d0e"
            ... )
            >>> print(f"Typosquatting: {is_squat}, Techniques: {techniques}")
            Typosquatting: True, Techniques: ['letter_to_number']
        """
        if not original_username or not suspicious_username:
            return (False, 0.0, [])
        
        threshold = threshold or self.typosquat_threshold
        
        # Normalize usernames (lowercase, no extra spaces)
        orig = original_username.lower().strip()
        susp = suspicious_username.lower().strip()
        
        # Exact match is not typosquatting
        if orig == susp:
            return (False, 1.0, [])
        
        detected_techniques = []
        
        # Check for character substitutions
        if self._has_character_substitutions(orig, susp):
            detected_techniques.append('character_substitution')
        
        # Check for added/removed characters
        if self._has_added_characters(orig, susp):
            detected_techniques.append('added_characters')
        
        if self._has_removed_characters(orig, susp):
            detected_techniques.append('removed_characters')
        
        # Check for homoglyphs (visually similar characters)
        if self._has_homoglyphs(orig, susp):
            detected_techniques.append('homoglyph_substitution')
        
        # Check for repeated characters
        if self._has_repeated_characters(orig, susp):
            detected_techniques.append('repeated_characters')
        
        # Calculate similarity score
        similarity = self.scorer.levenshtein_ratio(orig, susp)
        
        # Also check "normalized" versions (remove all special chars)
        norm_orig = re.sub(r'[^a-z0-9]', '', orig)
        norm_susp = re.sub(r'[^a-z0-9]', '', susp)
        norm_similarity = self.scorer.levenshtein_ratio(norm_orig, norm_susp)
        
        # If normalized versions are very similar but original aren't,
        # that's suspicious
        if norm_similarity > similarity + 0.1:
            detected_techniques.append('separator_manipulation')
        
        # High similarity + detected techniques = typosquatting
        is_typosquat = (
            similarity >= threshold and
            len(detected_techniques) > 0 and
            similarity < 1.0  # Not exact match
        )
        
        # Also flag if very high similarity even without detected techniques
        if not is_typosquat and similarity >= 0.9 and similarity < 1.0:
            is_typosquat = True
            detected_techniques.append('high_similarity')
        
        return (is_typosquat, similarity, detected_techniques)
    
    def _has_character_substitutions(self, orig: str, susp: str) -> bool:
        """Check if suspicious username has typosquat character substitutions."""
        if len(orig) != len(susp):
            return False
        
        for i, (c1, c2) in enumerate(zip(orig, susp)):
            if c1 != c2:
                # Check if c2 is a known substitution for c1
                if c1 in self.TYPOSQUAT_SUBSTITUTIONS:
                    if c2 in self.TYPOSQUAT_SUBSTITUTIONS[c1]:
                        return True
        
        return False
    
    def _has_added_characters(self, orig: str, susp: str) -> bool:
        """Check if suspicious username has added characters."""
        # Check for doubled characters
        if len(susp) > len(orig):
            # Remove one occurrence of each char and see if it matches
            for i in range(len(susp)):
                shortened = susp[:i] + susp[i+1:]
                if self.scorer.levenshtein_ratio(orig, shortened) > 0.95:
                    return True
        return False
    
    def _has_removed_characters(self, orig: str, susp: str) -> bool:
        """Check if suspicious username has removed characters."""
        if len(susp) < len(orig):
            # Check if adding any char to susp makes it match orig
            ratio = self.scorer.levenshtein_ratio(orig, susp)
            if ratio > 0.85:
                return True
        return False
    
    def _has_homoglyphs(self, orig: str, susp: str) -> bool:
        """Check for homoglyph (visually similar character) substitutions."""
        # Common homoglyph pairs
        homoglyphs = {
            'l': ['1', 'i', '|'],
            'i': ['1', 'l', '!'],
            'o': ['0'],
            '0': ['o'],
            '1': ['l', 'i'],
            'rn': ['m'],  # Two-char homoglyph
            'vv': ['w'],
            'cl': ['d'],
        }
        
        for char, similars in homoglyphs.items():
            if char in orig:
                for similar in similars:
                    if orig.replace(char, similar) == susp:
                        return True
        
        return False
    
    def _has_repeated_characters(self, orig: str, susp: str) -> bool:
        """Check for repeated character manipulation."""
        # Check if collapsing repeated chars makes them equal
        def collapse_repeats(s):
            return re.sub(r'(.)\1+', r'\1', s)
        
        collapsed_orig = collapse_repeats(orig)
        collapsed_susp = collapse_repeats(susp)
        
        if collapsed_orig == collapsed_susp and orig != susp:
            return True
        
        return False
    
    # =========================================================================
    # BATCH MATCHING METHODS
    # =========================================================================
    
    def find_best_match(
        self,
        query: str,
        candidates: List[str],
        threshold: float = 0.6
    ) -> Optional[Tuple[str, float]]:
        """
        Find the best matching string from a list of candidates.
        
        Args:
            query: The string to match
            candidates: List of candidate strings
            threshold: Minimum score to be considered a match
        
        Returns:
            Tuple[str, float] or None: Best match and score, or None if no match
        
        Example:
            >>> matcher = FuzzyMatcher()
            >>> result = matcher.find_best_match("John", ["Jon", "Jane", "Jack"])
            >>> print(result)
            ('Jon', 0.89)
        """
        if not query or not candidates:
            return None
        
        best_match = None
        best_score = 0.0
        
        for candidate in candidates:
            score = self.scorer.combined_score(query, candidate)
            if score > best_score and score >= threshold:
                best_score = score
                best_match = candidate
        
        if best_match:
            return (best_match, best_score)
        
        return None
    
    def find_all_matches(
        self,
        query: str,
        candidates: List[str],
        threshold: float = 0.6
    ) -> List[Tuple[str, float]]:
        """
        Find all matching strings from a list of candidates.
        
        Args:
            query: The string to match
            candidates: List of candidate strings
            threshold: Minimum score to be considered a match
        
        Returns:
            List[Tuple[str, float]]: List of (candidate, score) tuples,
                                     sorted by score descending
        
        Example:
            >>> matcher = FuzzyMatcher()
            >>> results = matcher.find_all_matches("John", ["Jon", "Johnny", "Jack"])
            >>> print(results)
            [('Jon', 0.89), ('Johnny', 0.75)]
        """
        if not query or not candidates:
            return []
        
        matches = []
        
        for candidate in candidates:
            score = self.scorer.combined_score(query, candidate)
            if score >= threshold:
                matches.append((candidate, score))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

# Create a default matcher instance for module-level usage
_default_matcher = FuzzyMatcher()


def match_names(name1: str, name2: str) -> Tuple[bool, float]:
    """Module-level convenience function for name matching."""
    return _default_matcher.match_names(name1, name2)


def is_typosquatting(original: str, suspicious: str) -> Tuple[bool, float, List[str]]:
    """Module-level convenience function for typosquatting detection."""
    return _default_matcher.is_typosquatting(original, suspicious)


def compare_bios(bio1: str, bio2: str) -> Tuple[float, Dict[str, any]]:
    """Module-level convenience function for bio comparison."""
    return _default_matcher.compare_bios(bio1, bio2)
