# =============================================================================
# USERNAME ANALYZER SERVICE TESTS
# =============================================================================
# Unit tests for the username analysis functionality.
# Tests URL generation, variations, and pattern analysis.
# =============================================================================

"""
Username Analyzer Tests

Comprehensive test suite for the UsernameAnalyzer service:
- Platform URL generation tests
- Username variation generation tests
- Pattern analysis tests
- Impersonation detection tests

Run with: pytest tests/test_username_analyzer.py -v
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.username_analyzer import UsernameAnalyzer


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def analyzer():
    """Create a UsernameAnalyzer instance for tests."""
    return UsernameAnalyzer()


# =============================================================================
# PLATFORM URL GENERATION TESTS
# =============================================================================

class TestPlatformURLGeneration:
    """Tests for platform URL generation."""
    
    def test_generate_all_platform_urls(self, analyzer):
        """Test that URLs are generated for all supported platforms."""
        result = analyzer.generate_platform_urls("johndoe")
        
        # Check all expected platforms are present
        expected_platforms = ["facebook", "instagram", "twitter", "linkedin"]
        for platform in expected_platforms:
            assert platform in result
    
    def test_facebook_url_format(self, analyzer):
        """Test Facebook URL format."""
        result = analyzer.generate_platform_urls("johndoe")
        assert result["facebook"]["url"] == "https://www.facebook.com/johndoe"
        assert result["facebook"]["name"] == "Facebook"
    
    def test_instagram_url_format(self, analyzer):
        """Test Instagram URL format."""
        result = analyzer.generate_platform_urls("johndoe")
        assert result["instagram"]["url"] == "https://www.instagram.com/johndoe"
    
    def test_twitter_url_format(self, analyzer):
        """Test Twitter/X URL format."""
        result = analyzer.generate_platform_urls("johndoe")
        assert result["twitter"]["url"] == "https://twitter.com/johndoe"
    
    def test_linkedin_url_format(self, analyzer):
        """Test LinkedIn URL format."""
        result = analyzer.generate_platform_urls("johndoe")
        assert result["linkedin"]["url"] == "https://www.linkedin.com/in/johndoe"

    def test_username_with_at_symbol_stripped(self, analyzer):
        """Test that @ symbol is stripped from username."""
        result = analyzer.generate_platform_urls("@johndoe")
        assert result["instagram"]["url"] == "https://www.instagram.com/johndoe"
    
    def test_empty_username_returns_empty_dict(self, analyzer):
        """Test that empty username returns empty dictionary."""
        result = analyzer.generate_platform_urls("")
        assert result == {}
    
    def test_single_platform_url(self, analyzer):
        """Test generating URL for a single platform."""
        result = analyzer.generate_platform_url("johndoe", "instagram")
        assert result == "https://www.instagram.com/johndoe"
    
    def test_invalid_platform_returns_empty(self, analyzer):
        """Test that invalid platform returns empty string."""
        result = analyzer.generate_platform_url("johndoe", "invalid_platform")
        assert result == ""


# =============================================================================
# USERNAME VARIATION TESTS
# =============================================================================

class TestUsernameVariations:
    """Tests for username variation generation."""
    
    def test_original_username_included(self, analyzer):
        """Test that original username is included in variations."""
        result = analyzer.generate_variations("john_doe")
        assert "john_doe" in result
    
    def test_no_underscore_variation(self, analyzer):
        """Test that underscore-removed variation is included."""
        result = analyzer.generate_variations("john_doe")
        assert "johndoe" in result
    
    def test_underscore_to_dot_variation(self, analyzer):
        """Test that underscore to dot variation is included."""
        result = analyzer.generate_variations("john_doe")
        assert "john.doe" in result
    
    def test_leading_underscore_variation(self, analyzer):
        """Test that leading underscore variation is included."""
        result = analyzer.generate_variations("johndoe")
        assert "_johndoe" in result
    
    def test_trailing_underscore_variation(self, analyzer):
        """Test that trailing underscore variation is included."""
        result = analyzer.generate_variations("johndoe")
        assert "johndoe_" in result
    
    def test_number_suffix_variations(self, analyzer):
        """Test that number suffix variations are included."""
        result = analyzer.generate_variations("johndoe")
        # Should include common number suffixes
        assert "johndoe123" in result or "johndoe1" in result
    
    def test_real_prefix_variation(self, analyzer):
        """Test that 'real_' prefix variation is included."""
        result = analyzer.generate_variations("johndoe")
        assert "real_johndoe" in result
    
    def test_official_suffix_variation(self, analyzer):
        """Test that '_official' suffix variation is included."""
        result = analyzer.generate_variations("johndoe")
        assert "johndoe_official" in result
    
    def test_empty_username_returns_empty_list(self, analyzer):
        """Test that empty username returns empty list."""
        result = analyzer.generate_variations("")
        assert result == []
    
    def test_variations_are_unique(self, analyzer):
        """Test that all variations are unique."""
        result = analyzer.generate_variations("john_doe")
        assert len(result) == len(set(result))
    
    def test_at_symbol_stripped(self, analyzer):
        """Test that @ symbol is stripped from username."""
        result = analyzer.generate_variations("@johndoe")
        assert "@johndoe" not in result
        assert "johndoe" in result


# =============================================================================
# PATTERN ANALYSIS TESTS
# =============================================================================

class TestPatternAnalysis:
    """Tests for username pattern analysis."""
    
    def test_basic_pattern_analysis(self, analyzer):
        """Test basic pattern analysis returns expected fields."""
        result = analyzer.analyze_patterns("johndoe")
        
        assert "length" in result
        assert "has_numbers" in result
        assert "has_underscores" in result
        assert "has_dots" in result
        assert "number_density" in result
        assert "detected_patterns" in result
        assert "has_suspicious_patterns" in result
    
    def test_username_length(self, analyzer):
        """Test that username length is calculated correctly."""
        result = analyzer.analyze_patterns("johndoe")
        assert result["length"] == 7
    
    def test_detects_numbers(self, analyzer):
        """Test that numbers are detected."""
        result = analyzer.analyze_patterns("johndoe123")
        assert result["has_numbers"] is True
        
        result = analyzer.analyze_patterns("johndoe")
        assert result["has_numbers"] is False
    
    def test_detects_underscores(self, analyzer):
        """Test that underscores are detected."""
        result = analyzer.analyze_patterns("john_doe")
        assert result["has_underscores"] is True
        
        result = analyzer.analyze_patterns("johndoe")
        assert result["has_underscores"] is False
    
    def test_detects_dots(self, analyzer):
        """Test that dots are detected."""
        result = analyzer.analyze_patterns("john.doe")
        assert result["has_dots"] is True
        
        result = analyzer.analyze_patterns("johndoe")
        assert result["has_dots"] is False
    
    def test_number_density_calculation(self, analyzer):
        """Test number density calculation."""
        # 50% numbers
        result = analyzer.analyze_patterns("abc123")
        assert result["number_density"] == 0.5
        
        # No numbers
        result = analyzer.analyze_patterns("johndoe")
        assert result["number_density"] == 0.0
    
    def test_detects_ends_with_numbers_pattern(self, analyzer):
        """Test detection of username ending with many numbers."""
        result = analyzer.analyze_patterns("johndoe123456")
        assert result["has_suspicious_patterns"] is True
        pattern_names = [p["name"] for p in result["detected_patterns"]]
        assert "ends_with_numbers" in pattern_names
    
    def test_detects_real_prefix_pattern(self, analyzer):
        """Test detection of 'real' prefix pattern."""
        result = analyzer.analyze_patterns("real_johndoe")
        assert result["has_suspicious_patterns"] is True
        pattern_names = [p["name"] for p in result["detected_patterns"]]
        assert "real_prefix" in pattern_names
    
    def test_detects_official_suffix_pattern(self, analyzer):
        """Test detection of 'official' suffix pattern."""
        result = analyzer.analyze_patterns("johndoe_official")
        assert result["has_suspicious_patterns"] is True
        pattern_names = [p["name"] for p in result["detected_patterns"]]
        assert "impersonation_suffix" in pattern_names
    
    def test_empty_username_analysis(self, analyzer):
        """Test analysis of empty username."""
        result = analyzer.analyze_patterns("")
        assert result["length"] == 0
        assert result["has_suspicious_patterns"] is False


# =============================================================================
# IMPERSONATION DETECTION TESTS
# =============================================================================

class TestImpersonationDetection:
    """Tests for impersonation detection."""
    
    def test_exact_match_not_impersonation(self, analyzer):
        """Test that exact match is not flagged as impersonation."""
        result = analyzer.is_likely_impersonation("johndoe", "johndoe")
        assert result is False
    
    def test_detects_prefix_impersonation(self, analyzer):
        """Test detection of prefix-based impersonation."""
        result = analyzer.is_likely_impersonation("johndoe", "real_johndoe")
        assert result is True
    
    def test_detects_suffix_impersonation(self, analyzer):
        """Test detection of suffix-based impersonation."""
        result = analyzer.is_likely_impersonation("johndoe", "johndoe_official")
        assert result is True
    
    def test_detects_underscore_variation_impersonation(self, analyzer):
        """Test detection of underscore variation impersonation."""
        result = analyzer.is_likely_impersonation("johndoe", "john_doe")
        assert result is True  # Stripped versions match
    
    def test_empty_username_not_impersonation(self, analyzer):
        """Test that empty usernames return False."""
        assert analyzer.is_likely_impersonation("", "johndoe") is False
        assert analyzer.is_likely_impersonation("johndoe", "") is False


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
