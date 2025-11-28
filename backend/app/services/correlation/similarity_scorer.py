# =============================================================================
# SIMILARITY SCORER
# =============================================================================
# Provides various similarity calculation methods for text comparison.
# Used by the FuzzyMatcher and CrossPlatformCorrelator for string matching.
# =============================================================================

"""
Similarity Scorer

This module provides various algorithms for calculating text similarity:

- Levenshtein ratio: Edit distance-based similarity
- Jaro-Winkler: Weighted for prefix matches (good for names)
- Token sort ratio: Order-independent word matching
- Cosine similarity: Vector-based text comparison

All methods return a similarity score between 0.0 and 1.0 (or 0-100).

Example:
    scorer = SimilarityScorer()
    score = scorer.levenshtein_ratio("john", "jon")  # ~0.86
"""

from typing import List, Set
import math


# =============================================================================
# SIMILARITY SCORER CLASS
# =============================================================================

class SimilarityScorer:
    """
    Calculate text similarity using various algorithms.
    
    Provides multiple similarity metrics optimized for different use cases:
    - Levenshtein: General-purpose edit distance
    - Jaro-Winkler: Names and short strings
    - Token sort: Multi-word strings
    - Cosine: Document-level comparison
    
    Example:
        >>> scorer = SimilarityScorer()
        >>> scorer.levenshtein_ratio("hello", "hallo")
        0.8
    """
    
    def __init__(self):
        """Initialize the SimilarityScorer."""
        pass
    
    # =========================================================================
    # LEVENSHTEIN DISTANCE
    # =========================================================================
    
    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate the Levenshtein (edit) distance between two strings.
        
        The edit distance is the minimum number of single-character edits
        (insertions, deletions, substitutions) required to change one
        string into the other.
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            int: Edit distance (0 = identical)
            
        Example:
            >>> scorer.levenshtein_distance("kitten", "sitting")
            3
        """
        if not s1:
            return len(s2) if s2 else 0
        if not s2:
            return len(s1)
        
        # Create distance matrix
        rows = len(s1) + 1
        cols = len(s2) + 1
        
        # Initialize first row and column
        dist = [[0 for _ in range(cols)] for _ in range(rows)]
        for i in range(rows):
            dist[i][0] = i
        for j in range(cols):
            dist[0][j] = j
        
        # Fill in the rest of the matrix
        for i in range(1, rows):
            for j in range(1, cols):
                cost = 0 if s1[i-1] == s2[j-1] else 1
                dist[i][j] = min(
                    dist[i-1][j] + 1,      # deletion
                    dist[i][j-1] + 1,      # insertion
                    dist[i-1][j-1] + cost  # substitution
                )
        
        return dist[rows-1][cols-1]
    
    def levenshtein_ratio(self, s1: str, s2: str) -> float:
        """
        Calculate similarity ratio based on Levenshtein distance.
        
        Returns a value between 0.0 (completely different) and 1.0 (identical).
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            float: Similarity ratio (0.0 to 1.0)
            
        Example:
            >>> scorer.levenshtein_ratio("hello", "hallo")
            0.8
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        
        distance = self.levenshtein_distance(s1.lower(), s2.lower())
        max_len = max(len(s1), len(s2))
        
        return 1.0 - (distance / max_len)
    
    # =========================================================================
    # JARO-WINKLER SIMILARITY
    # =========================================================================
    
    def jaro_similarity(self, s1: str, s2: str) -> float:
        """
        Calculate Jaro similarity between two strings.
        
        Jaro similarity accounts for:
        - Number of matching characters
        - Number of transpositions
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            float: Jaro similarity (0.0 to 1.0)
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        
        s1 = s1.lower()
        s2 = s2.lower()
        
        if s1 == s2:
            return 1.0
        
        len1, len2 = len(s1), len(s2)
        
        # Match window
        match_distance = max(len1, len2) // 2 - 1
        if match_distance < 0:
            match_distance = 0
        
        s1_matches = [False] * len1
        s2_matches = [False] * len2
        
        matches = 0
        transpositions = 0
        
        # Find matches
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
        
        jaro = (
            (matches / len1) +
            (matches / len2) +
            ((matches - transpositions / 2) / matches)
        ) / 3
        
        return jaro
    
    def jaro_winkler(self, s1: str, s2: str, p: float = 0.1) -> float:
        """
        Calculate Jaro-Winkler similarity between two strings.
        
        Jaro-Winkler gives higher scores to strings that match from
        the beginning (prefix matching). This makes it particularly
        good for name matching.
        
        Args:
            s1: First string
            s2: Second string
            p: Prefix scaling factor (default 0.1)
            
        Returns:
            float: Jaro-Winkler similarity (0.0 to 1.0)
            
        Example:
            >>> scorer.jaro_winkler("johnson", "jonson")
            0.89
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        
        jaro = self.jaro_similarity(s1, s2)
        
        s1 = s1.lower()
        s2 = s2.lower()
        
        # Find common prefix (up to 4 characters)
        prefix_len = 0
        for i in range(min(len(s1), len(s2), 4)):
            if s1[i] == s2[i]:
                prefix_len += 1
            else:
                break
        
        return jaro + prefix_len * p * (1 - jaro)
    
    # =========================================================================
    # TOKEN-BASED SIMILARITY
    # =========================================================================
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into lowercase words.
        
        Args:
            text: Input text
            
        Returns:
            List[str]: List of lowercase tokens
        """
        if not text:
            return []
        
        # Simple tokenization - split on whitespace and punctuation
        import re
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
    
    def token_sort_ratio(self, s1: str, s2: str) -> float:
        """
        Calculate similarity after sorting tokens alphabetically.
        
        This method is order-independent, so "John Smith" matches
        "Smith John" perfectly.
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            float: Token sort similarity (0.0 to 1.0)
            
        Example:
            >>> scorer.token_sort_ratio("john smith", "smith john")
            1.0
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        
        # Tokenize and sort
        tokens1 = sorted(self.tokenize(s1))
        tokens2 = sorted(self.tokenize(s2))
        
        # Join back to strings
        sorted1 = ' '.join(tokens1)
        sorted2 = ' '.join(tokens2)
        
        return self.levenshtein_ratio(sorted1, sorted2)
    
    def token_set_ratio(self, s1: str, s2: str) -> float:
        """
        Calculate similarity using set intersection of tokens.
        
        Computes the ratio of common tokens to total unique tokens.
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            float: Token set similarity (0.0 to 1.0)
            
        Example:
            >>> scorer.token_set_ratio("hello world", "world hello there")
            0.67  # 2 common tokens / 3 unique tokens
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        
        set1 = set(self.tokenize(s1))
        set2 = set(self.tokenize(s2))
        
        if not set1 and not set2:
            return 1.0
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return len(intersection) / len(union) if union else 0.0
    
    # =========================================================================
    # COSINE SIMILARITY
    # =========================================================================
    
    def cosine_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts.
        
        Uses term frequency vectors to compute the cosine of the
        angle between the two text representations.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            float: Cosine similarity (0.0 to 1.0)
            
        Example:
            >>> scorer.cosine_similarity("hello world", "hello there world")
            0.82
        """
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
        
        # Get term frequency vectors
        tokens1 = self.tokenize(text1)
        tokens2 = self.tokenize(text2)
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Build vocabulary
        vocab = set(tokens1) | set(tokens2)
        
        # Create frequency vectors
        vec1 = {word: 0 for word in vocab}
        vec2 = {word: 0 for word in vocab}
        
        for token in tokens1:
            vec1[token] += 1
        for token in tokens2:
            vec2[token] += 1
        
        # Calculate cosine similarity
        dot_product = sum(vec1[w] * vec2[w] for w in vocab)
        magnitude1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        magnitude2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    # =========================================================================
    # COMBINED SIMILARITY
    # =========================================================================
    
    def combined_similarity(
        self,
        s1: str,
        s2: str,
        weights: dict = None
    ) -> float:
        """
        Calculate weighted combination of multiple similarity metrics.
        
        Args:
            s1: First string
            s2: Second string
            weights: Dict of metric weights (default: equal weights)
            
        Returns:
            float: Combined similarity score (0.0 to 1.0)
        """
        if weights is None:
            weights = {
                'levenshtein': 0.3,
                'jaro_winkler': 0.3,
                'token_sort': 0.2,
                'cosine': 0.2
            }
        
        scores = {
            'levenshtein': self.levenshtein_ratio(s1, s2),
            'jaro_winkler': self.jaro_winkler(s1, s2),
            'token_sort': self.token_sort_ratio(s1, s2),
            'cosine': self.cosine_similarity(s1, s2)
        }
        
        weighted_sum = sum(
            scores[metric] * weight
            for metric, weight in weights.items()
            if metric in scores
        )
        
        total_weight = sum(
            weight for metric, weight in weights.items()
            if metric in scores
        )
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

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


def cosine_similarity(text1: str, text2: str) -> float:
    """Module-level convenience function for cosine similarity."""
    return _default_scorer.cosine_similarity(text1, text2)
