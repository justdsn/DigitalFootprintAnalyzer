# =============================================================================
# SIMILARITY SCORER
# =============================================================================
# Provides various string similarity calculation methods including
# Levenshtein ratio, Jaro-Winkler similarity, and token-based metrics.
# =============================================================================

"""
Similarity Scorer Module

This module provides various similarity scoring methods for comparing strings:
- Levenshtein ratio: Edit distance-based similarity
- Jaro-Winkler similarity: Designed for short strings like names
- Token sort ratio: Ignores word order in comparison
- Cosine similarity: For longer text comparison

These metrics are used by the correlation engine to compare PII fields
across different social media platforms.

Example Usage:
    scorer = SimilarityScorer()
    
    # Compare two strings using Levenshtein ratio
    score = scorer.levenshtein_ratio("john_doe", "johndoe")  # 0.875
    
    # Compare using Jaro-Winkler (better for names)
    score = scorer.jaro_winkler("John Doe", "John D")  # ~0.89
"""

from typing import List, Tuple, Optional, Dict, Any
import re
from collections import Counter
import math

# Try to import rapidfuzz for optimized string matching
# Falls back to basic implementations if not available
try:
    from rapidfuzz import fuzz
    from rapidfuzz.distance import Levenshtein, JaroWinkler
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False


# =============================================================================
# SIMILARITY SCORER CLASS
# =============================================================================

class SimilarityScorer:
    """
    Provides various string similarity scoring methods.
    
    This class implements multiple similarity metrics commonly used for
    comparing names, usernames, and text across social media profiles.
    
    If rapidfuzz is available, optimized implementations are used.
    Otherwise, falls back to pure Python implementations.
    
    Attributes:
        use_rapidfuzz: Whether rapidfuzz library is being used
    
    Example:
        >>> scorer = SimilarityScorer()
        >>> scorer.levenshtein_ratio("hello", "hallo")
        0.8
        >>> scorer.jaro_winkler("John", "Jon")
        0.9333...
    """
    
    def __init__(self):
        """
        Initialize the SimilarityScorer.
        
        Checks for rapidfuzz availability and sets up the scorer.
        """
        self.use_rapidfuzz = RAPIDFUZZ_AVAILABLE
    
    # =========================================================================
    # LEVENSHTEIN DISTANCE METHODS
    # =========================================================================
    
    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate the Levenshtein (edit) distance between two strings.
        
        The Levenshtein distance is the minimum number of single-character
        edits (insertions, deletions, substitutions) required to change
        one string into the other.
        
        Args:
            s1: First string
            s2: Second string
        
        Returns:
            int: The Levenshtein distance
        
        Example:
            >>> scorer = SimilarityScorer()
            >>> scorer.levenshtein_distance("hello", "hallo")
            1
            >>> scorer.levenshtein_distance("abc", "xyz")
            3
        """
        if not s1:
            return len(s2) if s2 else 0
        if not s2:
            return len(s1)
        
        if self.use_rapidfuzz:
            return Levenshtein.distance(s1, s2)
        
        # Pure Python implementation using dynamic programming
        m, n = len(s1), len(s2)
        
        # Create distance matrix
        # Use only two rows to save memory
        prev_row = list(range(n + 1))
        curr_row = [0] * (n + 1)
        
        for i in range(1, m + 1):
            curr_row[0] = i
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    curr_row[j] = prev_row[j - 1]
                else:
                    curr_row[j] = 1 + min(
                        prev_row[j],      # deletion
                        curr_row[j - 1],  # insertion
                        prev_row[j - 1]   # substitution
                    )
            prev_row, curr_row = curr_row, prev_row
        
        return prev_row[n]
    
    def levenshtein_ratio(self, s1: str, s2: str) -> float:
        """
        Calculate the Levenshtein similarity ratio between two strings.
        
        The ratio is calculated as:
        1 - (levenshtein_distance / max_length)
        
        This gives a value between 0.0 (completely different) and 
        1.0 (identical).
        
        Args:
            s1: First string
            s2: Second string
        
        Returns:
            float: Similarity ratio between 0.0 and 1.0
        
        Example:
            >>> scorer = SimilarityScorer()
            >>> scorer.levenshtein_ratio("hello", "hello")
            1.0
            >>> scorer.levenshtein_ratio("hello", "hallo")
            0.8
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        
        if self.use_rapidfuzz:
            return fuzz.ratio(s1, s2) / 100.0
        
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 1.0
        
        distance = self.levenshtein_distance(s1, s2)
        return 1.0 - (distance / max_len)
    
    # =========================================================================
    # JARO-WINKLER SIMILARITY
    # =========================================================================
    
    def jaro_similarity(self, s1: str, s2: str) -> float:
        """
        Calculate the Jaro similarity between two strings.
        
        Jaro similarity is designed for short strings like names.
        It considers the number of matching characters and transpositions.
        
        Args:
            s1: First string
            s2: Second string
        
        Returns:
            float: Jaro similarity between 0.0 and 1.0
        
        Example:
            >>> scorer = SimilarityScorer()
            >>> scorer.jaro_similarity("MARTHA", "MARHTA")
            0.944...
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        if s1 == s2:
            return 1.0
        
        if self.use_rapidfuzz:
            return JaroWinkler.similarity(s1, s2, prefix_weight=0.0)
        
        # Pure Python implementation
        len1, len2 = len(s1), len(s2)
        
        # Calculate match window
        match_distance = max(len1, len2) // 2 - 1
        if match_distance < 0:
            match_distance = 0
        
        s1_matches = [False] * len1
        s2_matches = [False] * len2
        
        matches = 0
        transpositions = 0
        
        # Find matching characters
        for i in range(len1):
            start = max(0, i - match_distance)
            end = min(i + match_distance + 1, len2)
            
            for j in range(start, end):
                if s2_matches[j] or s1[i] != s2[j]:
                    continue
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break
        
        if matches == 0:
            return 0.0
        
        # Count transpositions
        k = 0
        for i in range(len1):
            if not s1_matches[i]:
                continue
            while not s2_matches[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1
        
        # Calculate Jaro similarity
        jaro = (
            matches / len1 +
            matches / len2 +
            (matches - transpositions / 2) / matches
        ) / 3
        
        return jaro
    
    def jaro_winkler(self, s1: str, s2: str, prefix_weight: float = 0.1) -> float:
        """
        Calculate the Jaro-Winkler similarity between two strings.
        
        Jaro-Winkler gives more weight to strings that match from the
        beginning (common prefix). This is particularly useful for names
        where the first few characters are most important.
        
        Args:
            s1: First string
            s2: Second string
            prefix_weight: Weight for common prefix (default 0.1)
        
        Returns:
            float: Jaro-Winkler similarity between 0.0 and 1.0
        
        Example:
            >>> scorer = SimilarityScorer()
            >>> scorer.jaro_winkler("MARTHA", "MARHTA")
            0.961...
            >>> scorer.jaro_winkler("John", "Jon")
            0.933...
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        if s1 == s2:
            return 1.0
        
        if self.use_rapidfuzz:
            return JaroWinkler.similarity(s1, s2, prefix_weight=prefix_weight)
        
        # Get Jaro similarity
        jaro = self.jaro_similarity(s1, s2)
        
        # Calculate common prefix length (up to 4 characters)
        prefix_len = 0
        for i in range(min(len(s1), len(s2), 4)):
            if s1[i] == s2[i]:
                prefix_len += 1
            else:
                break
        
        # Apply Winkler modification
        return jaro + prefix_len * prefix_weight * (1 - jaro)
    
    # =========================================================================
    # TOKEN-BASED SIMILARITY
    # =========================================================================
    
    def token_sort_ratio(self, s1: str, s2: str) -> float:
        """
        Calculate similarity after sorting tokens alphabetically.
        
        This is useful when word order doesn't matter, for example:
        "John Smith" vs "Smith, John" should have high similarity.
        
        Args:
            s1: First string
            s2: Second string
        
        Returns:
            float: Similarity ratio between 0.0 and 1.0
        
        Example:
            >>> scorer = SimilarityScorer()
            >>> scorer.token_sort_ratio("John Smith", "Smith John")
            1.0
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        
        if self.use_rapidfuzz:
            return fuzz.token_sort_ratio(s1, s2) / 100.0
        
        # Tokenize, sort, and compare
        tokens1 = sorted(self._tokenize(s1.lower()))
        tokens2 = sorted(self._tokenize(s2.lower()))
        
        sorted1 = ' '.join(tokens1)
        sorted2 = ' '.join(tokens2)
        
        return self.levenshtein_ratio(sorted1, sorted2)
    
    def token_set_ratio(self, s1: str, s2: str) -> float:
        """
        Calculate similarity using set operations on tokens.
        
        Compares the intersection and differences of token sets.
        Useful for comparing texts where extra words should be ignored.
        
        Args:
            s1: First string
            s2: Second string
        
        Returns:
            float: Similarity ratio between 0.0 and 1.0
        
        Example:
            >>> scorer = SimilarityScorer()
            >>> scorer.token_set_ratio("John Smith Jr", "John Smith")
            # High score since "John Smith" is contained in both
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        
        if self.use_rapidfuzz:
            return fuzz.token_set_ratio(s1, s2) / 100.0
        
        # Tokenize
        tokens1 = set(self._tokenize(s1.lower()))
        tokens2 = set(self._tokenize(s2.lower()))
        
        # Calculate intersection and differences
        intersection = tokens1 & tokens2
        diff1 = tokens1 - tokens2
        diff2 = tokens2 - tokens1
        
        if not intersection:
            # No common tokens, compare the full strings
            return self.token_sort_ratio(s1, s2)
        
        # Build comparison strings
        sorted_intersection = ' '.join(sorted(intersection))
        sorted_diff1 = ' '.join(sorted(diff1))
        sorted_diff2 = ' '.join(sorted(diff2))
        
        combined1 = f"{sorted_intersection} {sorted_diff1}".strip()
        combined2 = f"{sorted_intersection} {sorted_diff2}".strip()
        
        # Compare in multiple ways and take the best score
        scores = [
            self.levenshtein_ratio(sorted_intersection, sorted_intersection),  # 1.0
            self.levenshtein_ratio(sorted_intersection, combined1),
            self.levenshtein_ratio(sorted_intersection, combined2),
            self.levenshtein_ratio(combined1, combined2)
        ]
        
        return max(scores)
    
    def partial_ratio(self, s1: str, s2: str) -> float:
        """
        Calculate partial string matching ratio.
        
        Compares the shorter string against substrings of the longer string
        to find the best match. Useful when one string is contained in another.
        
        Args:
            s1: First string
            s2: Second string
        
        Returns:
            float: Similarity ratio between 0.0 and 1.0
        
        Example:
            >>> scorer = SimilarityScorer()
            >>> scorer.partial_ratio("john_doe", "john_doe_official")
            1.0  # "john_doe" perfectly matches a substring
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        
        if self.use_rapidfuzz:
            return fuzz.partial_ratio(s1, s2) / 100.0
        
        # Make s1 the shorter string
        if len(s1) > len(s2):
            s1, s2 = s2, s1
        
        # Slide the shorter string over the longer one
        best_score = 0.0
        for i in range(len(s2) - len(s1) + 1):
            substring = s2[i:i + len(s1)]
            score = self.levenshtein_ratio(s1, substring)
            if score > best_score:
                best_score = score
                if best_score == 1.0:
                    break
        
        return best_score
    
    # =========================================================================
    # COSINE SIMILARITY
    # =========================================================================
    
    def cosine_similarity(self, s1: str, s2: str) -> float:
        """
        Calculate cosine similarity between two strings using word vectors.
        
        Treats each string as a bag of words and calculates the cosine
        of the angle between the word frequency vectors.
        
        Args:
            s1: First string
            s2: Second string
        
        Returns:
            float: Cosine similarity between 0.0 and 1.0
        
        Example:
            >>> scorer = SimilarityScorer()
            >>> scorer.cosine_similarity("I love coding", "I love programming")
            0.666...  # 2 common words out of 3+3-2=4 unique
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        
        # Tokenize and count word frequencies
        words1 = Counter(self._tokenize(s1.lower()))
        words2 = Counter(self._tokenize(s2.lower()))
        
        # Get all unique words
        all_words = set(words1.keys()) | set(words2.keys())
        
        if not all_words:
            return 0.0
        
        # Calculate dot product and magnitudes
        dot_product = sum(words1.get(w, 0) * words2.get(w, 0) for w in all_words)
        magnitude1 = math.sqrt(sum(count ** 2 for count in words1.values()))
        magnitude2 = math.sqrt(sum(count ** 2 for count in words2.values()))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Removes punctuation and splits on whitespace.
        
        Args:
            text: Text to tokenize
        
        Returns:
            List[str]: List of tokens
        """
        # Remove punctuation and split
        cleaned = re.sub(r'[^\w\s]', ' ', text)
        return [token for token in cleaned.split() if token]
    
    # =========================================================================
    # COMBINED SCORING
    # =========================================================================
    
    def combined_score(
        self,
        s1: str,
        s2: str,
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate a weighted combination of multiple similarity metrics.
        
        Args:
            s1: First string
            s2: Second string
            weights: Dictionary of metric names to weights. 
                     If None, uses default weights.
        
        Returns:
            float: Combined similarity score between 0.0 and 1.0
        
        Example:
            >>> scorer = SimilarityScorer()
            >>> scorer.combined_score("John Doe", "Jon Doe")
            # Returns weighted average of multiple metrics
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        
        # Default weights optimized for name comparison
        default_weights = {
            'levenshtein': 0.3,
            'jaro_winkler': 0.3,
            'token_sort': 0.2,
            'partial': 0.2
        }
        
        weights = weights or default_weights
        
        # Calculate individual scores
        scores = {
            'levenshtein': self.levenshtein_ratio(s1, s2),
            'jaro_winkler': self.jaro_winkler(s1, s2),
            'token_sort': self.token_sort_ratio(s1, s2),
            'partial': self.partial_ratio(s1, s2)
        }
        
        # Calculate weighted sum
        total_weight = sum(weights.get(metric, 0) for metric in scores.keys())
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(
            scores[metric] * weights.get(metric, 0)
            for metric in scores.keys()
        )
        
        return weighted_sum / total_weight


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

# Create a default scorer instance for module-level usage
_default_scorer = SimilarityScorer()


def levenshtein_ratio(s1: str, s2: str) -> float:
    """Module-level convenience function for Levenshtein ratio."""
    return _default_scorer.levenshtein_ratio(s1, s2)


def jaro_winkler(s1: str, s2: str) -> float:
    """Module-level convenience function for Jaro-Winkler similarity."""
    return _default_scorer.jaro_winkler(s1, s2)


def token_sort_ratio(s1: str, s2: str) -> float:
    """Module-level convenience function for token sort ratio."""
    return _default_scorer.token_sort_ratio(s1, s2)


def cosine_similarity(s1: str, s2: str) -> float:
    """Module-level convenience function for cosine similarity."""
    return _default_scorer.cosine_similarity(s1, s2)
