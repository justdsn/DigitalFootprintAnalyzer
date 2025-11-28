# =============================================================================
# CROSS-PLATFORM CORRELATION SERVICE TESTS
# =============================================================================
# Unit tests for the cross-platform correlation functionality.
# Tests overlap detection, contradiction finding, and impersonation scoring.
# =============================================================================

"""
Cross-Platform Correlation Tests

Comprehensive test suite for the correlation service:
- Fuzzy matching tests
- Similarity scoring tests
- Overlap detection tests
- Contradiction detection tests
- Impersonation scoring tests

Run with: pytest tests/test_correlation.py -v
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.correlation import (
    CrossPlatformCorrelator,
    PlatformProfile,
    CorrelationResult,
    FuzzyMatcher,
    SimilarityScorer,
    correlate,
    match_names,
    match_usernames,
    match_bios,
    levenshtein_ratio,
    jaro_winkler,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def correlator():
    """Create a CrossPlatformCorrelator instance for tests."""
    return CrossPlatformCorrelator()


@pytest.fixture
def matcher():
    """Create a FuzzyMatcher instance for tests."""
    return FuzzyMatcher()


@pytest.fixture
def scorer():
    """Create a SimilarityScorer instance for tests."""
    return SimilarityScorer()


@pytest.fixture
def sample_profiles():
    """Create sample profiles for testing."""
    return [
        {
            "platform": "facebook",
            "username": "john_doe",
            "name": "John Doe",
            "bio": "Software developer from Colombo",
            "location": "Colombo"
        },
        {
            "platform": "twitter",
            "username": "johndoe",
            "name": "John Doe",
            "bio": "Developer | Tech enthusiast",
            "location": "Colombo"
        }
    ]


# =============================================================================
# SIMILARITY SCORER TESTS
# =============================================================================

class TestSimilarityScorer:
    """Tests for the SimilarityScorer class."""
    
    def test_levenshtein_distance_identical(self, scorer):
        """Test Levenshtein distance for identical strings."""
        assert scorer.levenshtein_distance("hello", "hello") == 0
    
    def test_levenshtein_distance_one_edit(self, scorer):
        """Test Levenshtein distance for one edit."""
        assert scorer.levenshtein_distance("hello", "hallo") == 1
        assert scorer.levenshtein_distance("hello", "helloo") == 1
        assert scorer.levenshtein_distance("hello", "ello") == 1
    
    def test_levenshtein_ratio(self, scorer):
        """Test Levenshtein ratio calculation."""
        assert scorer.levenshtein_ratio("hello", "hello") == 1.0
        assert scorer.levenshtein_ratio("hello", "hallo") == 0.8
        assert scorer.levenshtein_ratio("hello", "world") < 0.5
    
    def test_levenshtein_ratio_empty(self, scorer):
        """Test Levenshtein ratio with empty strings."""
        assert scorer.levenshtein_ratio("", "") == 1.0
        assert scorer.levenshtein_ratio("hello", "") == 0.0
        assert scorer.levenshtein_ratio("", "hello") == 0.0
    
    def test_jaro_winkler_identical(self, scorer):
        """Test Jaro-Winkler for identical strings."""
        assert scorer.jaro_winkler("hello", "hello") == 1.0
    
    def test_jaro_winkler_similar(self, scorer):
        """Test Jaro-Winkler for similar strings."""
        score = scorer.jaro_winkler("johnson", "jonson")
        assert score > 0.85
    
    def test_jaro_winkler_prefix_boost(self, scorer):
        """Test that Jaro-Winkler gives prefix boost."""
        # Same prefix should score higher
        score_same_prefix = scorer.jaro_winkler("johnson", "johnsen")
        score_diff_prefix = scorer.jaro_winkler("johnson", "xohnson")
        assert score_same_prefix > score_diff_prefix
    
    def test_token_sort_ratio(self, scorer):
        """Test token sort ratio for word reordering."""
        # Order-independent matching
        score = scorer.token_sort_ratio("John Smith", "Smith John")
        assert score > 0.95
    
    def test_cosine_similarity(self, scorer):
        """Test cosine similarity."""
        score = scorer.cosine_similarity("hello world", "hello there world")
        assert score > 0.7
    
    def test_module_level_levenshtein(self):
        """Test module-level levenshtein_ratio function."""
        assert levenshtein_ratio("hello", "hello") == 1.0
    
    def test_module_level_jaro_winkler(self):
        """Test module-level jaro_winkler function."""
        assert jaro_winkler("hello", "hello") == 1.0


# =============================================================================
# FUZZY MATCHER TESTS
# =============================================================================

class TestFuzzyMatcher:
    """Tests for the FuzzyMatcher class."""
    
    def test_match_names_identical(self, matcher):
        """Test matching identical names."""
        score = matcher.match_names("John Doe", "John Doe")
        assert score == 100.0
    
    def test_match_names_similar(self, matcher):
        """Test matching similar names."""
        score = matcher.match_names("John Doe", "Jon Doe")
        assert score > 85
    
    def test_match_names_different(self, matcher):
        """Test matching different names."""
        score = matcher.match_names("John Doe", "Jane Smith")
        assert score < 50
    
    def test_match_names_empty(self, matcher):
        """Test matching with empty names."""
        assert matcher.match_names("", "John") == 0.0
        assert matcher.match_names("John", "") == 0.0
    
    def test_match_names_case_insensitive(self, matcher):
        """Test that name matching is case-insensitive."""
        score1 = matcher.match_names("John Doe", "JOHN DOE")
        score2 = matcher.match_names("John Doe", "john doe")
        assert score1 == 100.0
        assert score2 == 100.0
    
    def test_match_usernames_identical(self, matcher):
        """Test matching identical usernames."""
        score = matcher.match_usernames("john_doe", "john_doe")
        assert score == 100.0
    
    def test_match_usernames_similar(self, matcher):
        """Test matching similar usernames."""
        score = matcher.match_usernames("john_doe", "johndoe")
        assert score > 80
    
    def test_match_usernames_different(self, matcher):
        """Test matching different usernames."""
        score = matcher.match_usernames("john_doe", "jane_smith")
        assert score < 50
    
    def test_match_bios_similar(self, matcher):
        """Test matching similar bios."""
        bio1 = "Software developer from Colombo"
        bio2 = "Developer based in Colombo"
        score = matcher.match_bios(bio1, bio2)
        assert score > 50
    
    def test_detect_typosquatting_character_substitution(self, matcher):
        """Test typosquatting detection with character substitution."""
        is_typo, score, techniques = matcher.detect_typosquatting(
            "official_bank", "0fficial_bank"
        )
        assert is_typo is True
        assert "character_substitution" in techniques
    
    def test_detect_typosquatting_character_omission(self, matcher):
        """Test typosquatting detection with character omission."""
        is_typo, score, techniques = matcher.detect_typosquatting(
            "official", "offical"
        )
        assert is_typo is True
        assert "character_omission" in techniques
    
    def test_detect_typosquatting_different(self, matcher):
        """Test that different usernames are not typosquatting."""
        is_typo, score, techniques = matcher.detect_typosquatting(
            "john_doe", "jane_smith"
        )
        assert is_typo is False
    
    def test_find_similar(self, matcher):
        """Test finding similar strings."""
        candidates = ["jon", "jane", "jack", "josh"]  # Removed "john" to test similarity
        results = matcher.find_similar("john", candidates, threshold=60)
        assert len(results) > 0
        # "jon" should be most similar to "john"
        assert results[0][0] == "jon"
    
    def test_module_level_match_names(self):
        """Test module-level match_names function."""
        assert match_names("John", "John") == 100.0
    
    def test_module_level_match_usernames(self):
        """Test module-level match_usernames function."""
        assert match_usernames("john", "john") == 100.0


# =============================================================================
# CORRELATOR TESTS
# =============================================================================

class TestCorrelator:
    """Tests for the CrossPlatformCorrelator class."""
    
    def test_correlate_returns_result(self, correlator, sample_profiles):
        """Test that correlate returns a CorrelationResult."""
        result = correlator.correlate(sample_profiles)
        assert isinstance(result, CorrelationResult)
    
    def test_correlate_finds_overlaps(self, correlator, sample_profiles):
        """Test that correlate finds overlapping information."""
        result = correlator.correlate(sample_profiles)
        # Should find overlaps in name and location
        assert len(result.overlaps) > 0
    
    def test_correlate_with_contradictions(self, correlator):
        """Test that correlate finds contradictions."""
        profiles = [
            {
                "platform": "facebook",
                "username": "john_doe",
                "name": "John Doe",
                "location": "Colombo"
            },
            {
                "platform": "twitter",
                "username": "john_doe",  # Same username
                "name": "Jane Smith",     # Different name - contradiction
                "location": "Kandy"       # Different location
            }
        ]
        result = correlator.correlate(profiles)
        # Should find contradictions
        assert len(result.contradictions) > 0
    
    def test_correlate_insufficient_profiles(self, correlator):
        """Test correlate with insufficient profiles."""
        result = correlator.correlate([{"platform": "facebook", "username": "john"}])
        assert len(result.recommendations) > 0
        assert "more profiles" in result.recommendations[0].lower()
    
    def test_correlate_empty_profiles(self, correlator):
        """Test correlate with empty profiles list."""
        result = correlator.correlate([])
        assert isinstance(result, CorrelationResult)
    
    def test_impersonation_score_low(self, correlator, sample_profiles):
        """Test that consistent profiles get low impersonation score."""
        result = correlator.correlate(sample_profiles)
        # Consistent profiles should have low score
        assert result.impersonation_score < 50
        assert result.impersonation_level in ["low", "medium"]
    
    def test_impersonation_score_high(self, correlator):
        """Test that suspicious profiles get high impersonation score."""
        profiles = [
            {
                "platform": "facebook",
                "username": "real_bank",
                "name": "Real Bank Official"
            },
            {
                "platform": "twitter",
                "username": "rea1_bank",  # Typosquatting
                "name": "Different Name"   # Different name
            }
        ]
        result = correlator.correlate(profiles)
        # Suspicious profiles should have higher score
        assert result.impersonation_score > 30
    
    def test_find_overlaps(self, correlator):
        """Test the find_overlaps method."""
        profiles = [
            PlatformProfile("facebook", "john", name="John Doe"),
            PlatformProfile("twitter", "john", name="John Doe"),
        ]
        overlaps = correlator.find_overlaps(profiles)
        assert len(overlaps) > 0
        # Should find username and name overlaps
        fields = [o["field"] for o in overlaps]
        assert "username" in fields or "name" in fields
    
    def test_find_contradictions(self, correlator):
        """Test the find_contradictions method."""
        profiles = [
            PlatformProfile("facebook", "john_doe", name="John Doe"),
            PlatformProfile("twitter", "john_doe", name="Jane Smith"),
        ]
        contradictions = correlator.find_contradictions(profiles)
        assert len(contradictions) > 0
        # Should find name mismatch
        assert any(c["type"] == "name_mismatch" for c in contradictions)
    
    def test_generate_flags(self, correlator):
        """Test that flags are generated for issues."""
        profiles = [
            {
                "platform": "facebook",
                "username": "official_account",
                "name": "Official"
            },
            {
                "platform": "twitter",
                "username": "0fficial_account",  # Typosquatting
                "name": "Different Name"
            }
        ]
        result = correlator.correlate(profiles)
        # Should generate warning flags
        assert len(result.flags) > 0
    
    def test_generate_recommendations(self, correlator, sample_profiles):
        """Test that recommendations are generated."""
        result = correlator.correlate(sample_profiles)
        assert len(result.recommendations) > 0
    
    def test_module_level_correlate(self, sample_profiles):
        """Test module-level correlate function."""
        result = correlate(sample_profiles)
        assert isinstance(result, dict)
        assert "overlaps" in result
        assert "contradictions" in result
        assert "impersonation_score" in result


# =============================================================================
# PLATFORM PROFILE TESTS
# =============================================================================

class TestPlatformProfile:
    """Tests for the PlatformProfile dataclass."""
    
    def test_create_profile(self):
        """Test creating a PlatformProfile."""
        profile = PlatformProfile(
            platform="facebook",
            username="john_doe",
            name="John Doe"
        )
        assert profile.platform == "facebook"
        assert profile.username == "john_doe"
        assert profile.name == "John Doe"
        assert profile.bio is None
    
    def test_profile_to_dict(self):
        """Test converting profile to dictionary."""
        profile = PlatformProfile(
            platform="facebook",
            username="john_doe",
            name="John Doe",
            location="Colombo"
        )
        d = profile.to_dict()
        assert d["platform"] == "facebook"
        assert d["username"] == "john_doe"
        assert d["name"] == "John Doe"
        assert d["location"] == "Colombo"


# =============================================================================
# CORRELATION RESULT TESTS
# =============================================================================

class TestCorrelationResult:
    """Tests for the CorrelationResult dataclass."""
    
    def test_create_result(self):
        """Test creating a CorrelationResult."""
        result = CorrelationResult(
            impersonation_score=50,
            impersonation_level="medium"
        )
        assert result.impersonation_score == 50
        assert result.impersonation_level == "medium"
        assert result.overlaps == []
        assert result.contradictions == []
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = CorrelationResult(
            overlaps=[{"field": "name"}],
            impersonation_score=25,
            impersonation_level="low"
        )
        d = result.to_dict()
        assert d["impersonation_score"] == 25
        assert d["impersonation_level"] == "low"
        assert len(d["overlaps"]) == 1


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and special scenarios."""
    
    def test_unicode_names(self, matcher):
        """Test matching names with unicode characters."""
        score = matcher.match_names("Kärl Müller", "Karl Muller")
        assert score > 50  # Should still find similarity
    
    def test_very_long_bio(self, matcher):
        """Test matching very long bios."""
        bio1 = "word " * 100
        bio2 = "word " * 100 + "extra"
        score = matcher.match_bios(bio1, bio2)
        assert score > 90  # Should be very similar
    
    def test_many_profiles(self, correlator):
        """Test correlation with many profiles."""
        profiles = [
            {"platform": f"platform{i}", "username": "john", "name": "John"}
            for i in range(5)
        ]
        result = correlator.correlate(profiles)
        assert isinstance(result, CorrelationResult)
    
    def test_profiles_with_missing_fields(self, correlator):
        """Test correlation with profiles missing optional fields."""
        profiles = [
            {"platform": "facebook", "username": "john"},  # Minimal
            {"platform": "twitter", "username": "john", "name": "John", "bio": "Test"}
        ]
        result = correlator.correlate(profiles)
        assert isinstance(result, CorrelationResult)
    
    def test_special_characters_in_username(self, matcher):
        """Test usernames with special characters."""
        score = matcher.match_usernames("john.doe", "john_doe")
        assert score > 70  # Should recognize similarity


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
