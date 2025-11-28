# =============================================================================
# FUZZY MATCHER
# =============================================================================
# Provides fuzzy string matching capabilities for profile comparison.
# Uses rapidfuzz library for efficient string matching operations.
# =============================================================================

"""
Fuzzy Matcher

This module provides fuzzy string matching capabilities for:
- Name comparison across profiles
- Bio/description similarity
- Username typosquatting detection
- Finding similar strings from candidates

Uses the rapidfuzz library for high-performance fuzzy matching,
with fallback to custom implementations if not available.

Example:
    matcher = FuzzyMatcher()
    score = matcher.match_names("John Smith", "Jon Smith")  # ~90
"""

from typing import List, Optional, Tuple
from .similarity_scorer import SimilarityScorer

# Try to import rapidfuzz, fall back to custom implementation
try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False


# =============================================================================
# FUZZY MATCHER CLASS
# =============================================================================

class FuzzyMatcher:
    """
    Fuzzy string matching for profile comparison.
    
    Provides methods optimized for different types of profile data:
    - Names: Uses Jaro-Winkler for good prefix matching
    - Bios: Uses token-based matching for longer text
    - Usernames: Uses strict matching with typosquatting detection
    
    Attributes:
        scorer: SimilarityScorer instance for calculations
        use_rapidfuzz: Whether rapidfuzz is available
        
    Example:
        >>> matcher = FuzzyMatcher()
        >>> matcher.match_names("Kamal Perera", "Kamaal Pereera")
        92.5
    """
    
    def __init__(self):
        """Initialize the FuzzyMatcher."""
        self.scorer = SimilarityScorer()
        self.use_rapidfuzz = RAPIDFUZZ_AVAILABLE
    
    # =========================================================================
    # NAME MATCHING
    # =========================================================================
    
    def match_names(self, name1: str, name2: str) -> float:
        """
        Compare two names with fuzzy matching.
        
        Uses a combination of:
        - Jaro-Winkler (good for name prefixes)
        - Token sort ratio (handles name order differences)
        
        Args:
            name1: First name
            name2: Second name
            
        Returns:
            float: Similarity score (0-100)
            
        Example:
            >>> matcher.match_names("John Smith", "Smith, John")
            95.0
        """
        if not name1 or not name2:
            return 0.0
        
        # Normalize names
        name1 = self._normalize_name(name1)
        name2 = self._normalize_name(name2)
        
        if name1 == name2:
            return 100.0
        
        if self.use_rapidfuzz:
            # Use rapidfuzz for high-performance matching
            jw_score = fuzz.WRatio(name1, name2)
            token_score = fuzz.token_sort_ratio(name1, name2)
            # Weight Jaro-Winkler higher for names
            return (jw_score * 0.6 + token_score * 0.4)
        else:
            # Fallback to custom implementation
            jw_score = self.scorer.jaro_winkler(name1, name2) * 100
            token_score = self.scorer.token_sort_ratio(name1, name2) * 100
            return (jw_score * 0.6 + token_score * 0.4)
    
    def _normalize_name(self, name: str) -> str:
        """
        Normalize a name for comparison.
        
        - Converts to lowercase
        - Removes extra whitespace
        - Removes common titles and suffixes
        
        Args:
            name: Name to normalize
            
        Returns:
            str: Normalized name
        """
        if not name:
            return ""
        
        # Convert to lowercase and strip
        name = name.lower().strip()
        
        # Remove common titles
        titles = ['mr', 'mrs', 'ms', 'dr', 'prof', 'sir', 'madam']
        words = name.split()
        words = [w for w in words if w.rstrip('.') not in titles]
        
        # Remove extra whitespace
        return ' '.join(words)
    
    # =========================================================================
    # BIO/DESCRIPTION MATCHING
    # =========================================================================
    
    def match_bios(self, bio1: str, bio2: str) -> float:
        """
        Compare two bio/description texts with fuzzy matching.
        
        Uses token-based comparison which works well for longer texts
        where word order may differ.
        
        Args:
            bio1: First bio text
            bio2: Second bio text
            
        Returns:
            float: Similarity score (0-100)
            
        Example:
            >>> matcher.match_bios("Software developer from Colombo", "Developer based in Colombo")
            75.0
        """
        if not bio1 or not bio2:
            return 0.0
        
        # Normalize bios
        bio1 = bio1.lower().strip()
        bio2 = bio2.lower().strip()
        
        if bio1 == bio2:
            return 100.0
        
        if self.use_rapidfuzz:
            # Token set ratio works well for longer texts
            return fuzz.token_set_ratio(bio1, bio2)
        else:
            # Fallback: use token set and cosine similarity
            token_score = self.scorer.token_set_ratio(bio1, bio2) * 100
            cosine_score = self.scorer.cosine_similarity(bio1, bio2) * 100
            return (token_score * 0.5 + cosine_score * 0.5)
    
    # =========================================================================
    # USERNAME MATCHING
    # =========================================================================
    
    def match_usernames(self, user1: str, user2: str) -> float:
        """
        Compare two usernames for similarity (typosquatting detection).
        
        Uses strict character-level comparison since usernames
        are typically short and character substitutions matter.
        
        Args:
            user1: First username
            user2: Second username
            
        Returns:
            float: Similarity score (0-100)
            
        Example:
            >>> matcher.match_usernames("john_doe", "john.doe")
            90.0
            >>> matcher.match_usernames("john_doe", "j0hn_doe")
            85.0
        """
        if not user1 or not user2:
            return 0.0
        
        # Normalize usernames
        user1 = self._normalize_username(user1)
        user2 = self._normalize_username(user2)
        
        if user1 == user2:
            return 100.0
        
        if self.use_rapidfuzz:
            # Use ratio for character-level comparison
            return fuzz.ratio(user1, user2)
        else:
            return self.scorer.levenshtein_ratio(user1, user2) * 100
    
    def _normalize_username(self, username: str) -> str:
        """
        Normalize a username for comparison.
        
        - Converts to lowercase
        - Removes @ prefix
        - Strips whitespace
        
        Args:
            username: Username to normalize
            
        Returns:
            str: Normalized username
        """
        if not username:
            return ""
        
        username = username.lower().strip()
        
        # Remove @ prefix
        if username.startswith('@'):
            username = username[1:]
        
        return username
    
    def detect_typosquatting(self, original: str, suspect: str) -> Tuple[bool, float, List[str]]:
        """
        Detect if a username might be typosquatting another.
        
        Checks for common typosquatting techniques:
        - Character substitution (l→1, o→0, etc.)
        - Character omission
        - Character addition
        - Character transposition
        
        Args:
            original: Original username
            suspect: Potentially typosquatting username
            
        Returns:
            Tuple of (is_typosquat: bool, confidence: float, techniques: List[str])
            
        Example:
            >>> matcher.detect_typosquatting("official_bank", "0fficial_bank")
            (True, 85.0, ['character_substitution'])
        """
        if not original or not suspect:
            return (False, 0.0, [])
        
        original = self._normalize_username(original)
        suspect = self._normalize_username(suspect)
        
        if original == suspect:
            return (False, 100.0, [])
        
        techniques = []
        
        # Check for character substitution
        substitution_pairs = {
            'l': '1', '1': 'l',
            'o': '0', '0': 'o',
            'i': '1', '1': 'i',
            's': '5', '5': 's',
            'e': '3', '3': 'e',
            'a': '4', '4': 'a',
            'b': '8', '8': 'b',
            'g': '9', '9': 'g',
            't': '7', '7': 't',
            'i': 'l', 'l': 'i',
            'rn': 'm', 'm': 'rn',
            'vv': 'w', 'w': 'vv',
        }
        
        for orig_char, sub_char in substitution_pairs.items():
            if orig_char in original:
                test_version = original.replace(orig_char, sub_char)
                if test_version == suspect:
                    techniques.append('character_substitution')
                    break
        
        # Check for character omission
        for i in range(len(original)):
            omitted = original[:i] + original[i+1:]
            if omitted == suspect:
                techniques.append('character_omission')
                break
        
        # Check for character addition
        for i in range(len(suspect)):
            removed = suspect[:i] + suspect[i+1:]
            if removed == original:
                techniques.append('character_addition')
                break
        
        # Check for transposition
        for i in range(len(original) - 1):
            transposed = (
                original[:i] +
                original[i+1] +
                original[i] +
                original[i+2:]
            )
            if transposed == suspect:
                techniques.append('character_transposition')
                break
        
        # Calculate similarity score
        score = self.match_usernames(original, suspect)
        
        # Determine if likely typosquatting
        # High similarity + known techniques = likely typosquat
        is_typosquat = bool(
            (score >= 70 and len(techniques) > 0) or
            (score >= 85)  # Very similar even without known technique
        )
        
        return (is_typosquat, score, techniques)
    
    # =========================================================================
    # FIND SIMILAR
    # =========================================================================
    
    def find_similar(
        self,
        target: str,
        candidates: List[str],
        threshold: float = 70.0,
        limit: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Find strings similar to target from a list of candidates.
        
        Args:
            target: Target string to match
            candidates: List of candidate strings
            threshold: Minimum similarity score (0-100)
            limit: Maximum number of results
            
        Returns:
            List of (candidate, score) tuples, sorted by score descending
            
        Example:
            >>> matcher.find_similar("john", ["jon", "jane", "jack"], threshold=60)
            [("jon", 85.7), ("jane", 62.5)]
        """
        if not target or not candidates:
            return []
        
        target = target.lower().strip()
        
        if self.use_rapidfuzz:
            # Use rapidfuzz's extract function for efficiency
            results = process.extract(
                target,
                candidates,
                scorer=fuzz.WRatio,
                limit=limit
            )
            # Filter by threshold and format
            return [
                (match, score)
                for match, score, _ in results
                if score >= threshold
            ]
        else:
            # Fallback to manual comparison
            scored = []
            for candidate in candidates:
                score = self.scorer.jaro_winkler(target, candidate.lower()) * 100
                if score >= threshold:
                    scored.append((candidate, score))
            
            # Sort by score descending
            scored.sort(key=lambda x: x[1], reverse=True)
            return scored[:limit]
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def get_best_match(
        self,
        target: str,
        candidates: List[str]
    ) -> Optional[Tuple[str, float]]:
        """
        Get the best matching candidate for a target string.
        
        Args:
            target: Target string to match
            candidates: List of candidate strings
            
        Returns:
            Tuple of (best_match, score) or None if no candidates
        """
        results = self.find_similar(target, candidates, threshold=0.0, limit=1)
        return results[0] if results else None


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

_default_matcher = FuzzyMatcher()


def match_names(name1: str, name2: str) -> float:
    """Module-level convenience function for name matching."""
    return _default_matcher.match_names(name1, name2)


def match_bios(bio1: str, bio2: str) -> float:
    """Module-level convenience function for bio matching."""
    return _default_matcher.match_bios(bio1, bio2)


def match_usernames(user1: str, user2: str) -> float:
    """Module-level convenience function for username matching."""
    return _default_matcher.match_usernames(user1, user2)


def find_similar(target: str, candidates: List[str], threshold: float = 70.0) -> List[Tuple[str, float]]:
    """Module-level convenience function for finding similar strings."""
    return _default_matcher.find_similar(target, candidates, threshold)
