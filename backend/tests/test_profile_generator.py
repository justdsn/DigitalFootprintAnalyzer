# =============================================================================
# PROFILE URL GENERATOR SERVICE TESTS
# =============================================================================
# Unit tests for the Profile URL Generator functionality.
# Tests URL generation for all platforms and username variations.
# =============================================================================

"""
Profile URL Generator Tests

Comprehensive test suite for the ProfileURLGenerator service:
- URL generation for all platforms
- Username cleaning and normalization
- Variation generation
- Module-level convenience functions

Run with: pytest tests/test_profile_generator.py -v
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.social.profile_generator import ProfileURLGenerator


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def generator():
    """Create a ProfileURLGenerator instance for tests."""
    return ProfileURLGenerator()


# =============================================================================
# URL GENERATION TESTS
# =============================================================================

class TestURLGeneration:
    """Tests for profile URL generation."""
    
    def test_generate_urls_all_platforms(self, generator):
        """Test URL generation for all platforms."""
        urls = generator.generate_urls("john_doe")
        
        assert "facebook" in urls
        assert "instagram" in urls
        assert "linkedin" in urls
        assert "x" in urls
    
    def test_facebook_url_format(self, generator):
        """Test Facebook URL format."""
        urls = generator.generate_urls("john_doe")
        
        assert urls["facebook"]["name"] == "Facebook"
        assert urls["facebook"]["url"] == "https://www.facebook.com/john_doe"
    
    def test_instagram_url_format(self, generator):
        """Test Instagram URL format (with trailing slash)."""
        urls = generator.generate_urls("john_doe")
        
        assert urls["instagram"]["name"] == "Instagram"
        assert urls["instagram"]["url"] == "https://www.instagram.com/john_doe/"
    
    def test_linkedin_url_format(self, generator):
        """Test LinkedIn URL format."""
        urls = generator.generate_urls("john_doe")
        
        assert urls["linkedin"]["name"] == "LinkedIn"
        assert urls["linkedin"]["url"] == "https://www.linkedin.com/in/john_doe"
    
    def test_x_url_format(self, generator):
        """Test X (Twitter) URL format."""
        urls = generator.generate_urls("john_doe")
        
        assert urls["x"]["name"] == "X (Twitter)"
        assert urls["x"]["url"] == "https://x.com/john_doe"
    
    def test_single_platform_url(self, generator):
        """Test single platform URL generation."""
        url = generator.generate_url("john_doe", "instagram")
        
        assert url == "https://www.instagram.com/john_doe/"
    
    def test_invalid_platform_returns_none(self, generator):
        """Test that invalid platform returns None."""
        url = generator.generate_url("john_doe", "invalid_platform")
        
        assert url is None
    
    def test_empty_username_returns_empty_dict(self, generator):
        """Test that empty username returns empty dict."""
        urls = generator.generate_urls("")
        
        assert urls == {}
    
    def test_empty_username_single_returns_none(self, generator):
        """Test that empty username for single platform returns None."""
        url = generator.generate_url("", "facebook")
        
        assert url is None


# =============================================================================
# USERNAME CLEANING TESTS
# =============================================================================

class TestUsernameCleaning:
    """Tests for username cleaning functionality."""
    
    def test_at_symbol_stripped(self, generator):
        """Test that @ symbol is removed from username."""
        urls = generator.generate_urls("@john_doe")
        
        assert "john_doe" in urls["facebook"]["url"]
        assert "@john_doe" not in urls["facebook"]["url"]
    
    def test_whitespace_stripped(self, generator):
        """Test that whitespace is stripped from username."""
        urls = generator.generate_urls("  john_doe  ")
        
        assert "john_doe" in urls["facebook"]["url"]
        assert " john_doe" not in urls["facebook"]["url"]
    
    def test_clean_username_method(self, generator):
        """Test the _clean_username method directly."""
        assert generator._clean_username("@john_doe ") == "john_doe"
        assert generator._clean_username("  username  ") == "username"
        assert generator._clean_username("") == ""
        assert generator._clean_username(None) == ""


# =============================================================================
# VARIATION GENERATION TESTS
# =============================================================================

class TestVariationGeneration:
    """Tests for username variation generation."""
    
    def test_variations_include_original(self, generator):
        """Test that variations include the original username."""
        variations = generator.generate_variations("john_doe")
        usernames = [v["username"] for v in variations]
        
        assert "john_doe" in usernames
    
    def test_variations_include_no_underscore(self, generator):
        """Test that variations include version without underscore."""
        variations = generator.generate_variations("john_doe")
        usernames = [v["username"] for v in variations]
        
        assert "johndoe" in usernames
    
    def test_variations_include_dot_version(self, generator):
        """Test that variations include dot version."""
        variations = generator.generate_variations("john_doe")
        usernames = [v["username"] for v in variations]
        
        assert "john.doe" in usernames
    
    def test_variations_include_leading_underscore(self, generator):
        """Test that variations include leading underscore version."""
        variations = generator.generate_variations("john_doe")
        usernames = [v["username"] for v in variations]
        
        assert "_john_doe" in usernames
    
    def test_variations_include_trailing_underscore(self, generator):
        """Test that variations include trailing underscore version."""
        variations = generator.generate_variations("john_doe")
        usernames = [v["username"] for v in variations]
        
        assert "john_doe_" in usernames
    
    def test_variations_include_number_suffixes(self, generator):
        """Test that variations include number suffix versions."""
        variations = generator.generate_variations("john_doe")
        usernames = [v["username"] for v in variations]
        
        # Should have number suffix on the cleaned version (no underscore)
        assert "johndoe1" in usernames or "johndoe123" in usernames
    
    def test_variations_have_urls(self, generator):
        """Test that each variation has associated URLs."""
        variations = generator.generate_variations("john_doe")
        
        for variation in variations:
            assert "username" in variation
            assert "urls" in variation
            assert len(variation["urls"]) > 0
    
    def test_variations_empty_username(self, generator):
        """Test that empty username returns empty list."""
        variations = generator.generate_variations("")
        
        assert variations == []
    
    def test_variations_are_unique(self, generator):
        """Test that variations are unique."""
        variations = generator.generate_variations("john_doe")
        usernames = [v["username"] for v in variations]
        
        assert len(usernames) == len(set(usernames))


# =============================================================================
# PLATFORM LIST TESTS
# =============================================================================

class TestPlatformList:
    """Tests for platform listing functionality."""
    
    def test_get_supported_platforms(self, generator):
        """Test getting list of supported platforms."""
        platforms = generator.get_supported_platforms()
        
        assert "facebook" in platforms
        assert "instagram" in platforms
        assert "linkedin" in platforms
        assert "x" in platforms
    
    def test_platforms_count(self, generator):
        """Test that we have the expected number of platforms."""
        platforms = generator.get_supported_platforms()
        
        assert len(platforms) == 4


# =============================================================================
# MODULE-LEVEL FUNCTION TESTS
# =============================================================================

class TestModuleFunctions:
    """Tests for module-level convenience functions."""
    
    def test_module_generate_urls(self):
        """Test module-level generate_urls function."""
        from app.services.social.profile_generator import generate_urls
        
        urls = generate_urls("test_user")
        
        assert "facebook" in urls
        assert "instagram" in urls
    
    def test_module_generate_variations(self):
        """Test module-level generate_variations function."""
        from app.services.social.profile_generator import generate_variations
        
        variations = generate_variations("test_user")
        
        assert len(variations) > 0


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and special scenarios."""
    
    def test_special_characters_in_username(self, generator):
        """Test username with special characters."""
        urls = generator.generate_urls("john.doe_123")
        
        assert "john.doe_123" in urls["facebook"]["url"]
    
    def test_very_long_username(self, generator):
        """Test very long username."""
        long_username = "a" * 100
        urls = generator.generate_urls(long_username)
        
        assert len(urls) == 4
        assert long_username in urls["facebook"]["url"]
    
    def test_unicode_username(self, generator):
        """Test username with unicode characters."""
        urls = generator.generate_urls("user_鳩")
        
        assert "user_鳩" in urls["facebook"]["url"]
    
    def test_numeric_username(self, generator):
        """Test purely numeric username."""
        urls = generator.generate_urls("123456")
        
        assert "123456" in urls["facebook"]["url"]
