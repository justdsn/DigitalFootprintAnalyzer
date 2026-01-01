# =============================================================================
# OSINT DISCOVERY TESTS
# =============================================================================
# Unit tests for OSINT discovery utilities.
# =============================================================================

"""
OSINT Discovery Tests

Test suite for discovery utilities:
- Identifier detection
- URL generation
- Username variations

Run with: pytest tests/test_osint_discovery.py -v
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.osint.discovery import IdentifierDetector, URLGenerator


# =============================================================================
# IDENTIFIER DETECTION TESTS
# =============================================================================

class TestIdentifierDetector:
    """Tests for identifier type detection."""
    
    def test_detect_email(self):
        """Test email detection."""
        detector = IdentifierDetector()
        
        assert detector.detect("john@example.com") == "email"
        assert detector.detect("user.name@domain.co.uk") == "email"
        assert detector.detect("test+tag@gmail.com") == "email"
    
    def test_detect_phone_sri_lankan(self):
        """Test Sri Lankan phone number detection."""
        detector = IdentifierDetector()
        
        assert detector.detect("0771234567") == "phone"
        assert detector.detect("+94771234567") == "phone"
        assert detector.detect("94771234567") == "phone"
        assert detector.detect("077 123 4567") == "phone"
        assert detector.detect("077-123-4567") == "phone"
    
    def test_detect_phone_international(self):
        """Test international phone number detection."""
        detector = IdentifierDetector()
        
        assert detector.detect("+1234567890") == "phone"
        assert detector.detect("001234567890") == "phone"
    
    def test_detect_name(self):
        """Test full name detection."""
        detector = IdentifierDetector()
        
        assert detector.detect("John Perera") == "name"
        assert detector.detect("Sunil Silva") == "name"
        assert detector.detect("Jane Mary Doe") == "name"
    
    def test_detect_username(self):
        """Test username detection (default)."""
        detector = IdentifierDetector()
        
        assert detector.detect("johndoe") == "username"
        assert detector.detect("john_doe") == "username"
        assert detector.detect("john.doe") == "username"
        assert detector.detect("@johndoe") == "username"
        assert detector.detect("johndoe123") == "username"


# =============================================================================
# URL GENERATOR TESTS
# =============================================================================

class TestURLGenerator:
    """Tests for profile URL generation."""
    
    def test_generate_instagram_url(self):
        """Test Instagram URL generation."""
        url = URLGenerator.generate_url("instagram", "johndoe")
        assert url == "https://www.instagram.com/johndoe/"
    
    def test_generate_facebook_url(self):
        """Test Facebook URL generation."""
        url = URLGenerator.generate_url("facebook", "johndoe")
        assert url == "https://www.facebook.com/johndoe"
    
    def test_generate_linkedin_url(self):
        """Test LinkedIn URL generation."""
        url = URLGenerator.generate_url("linkedin", "johndoe")
        assert url == "https://www.linkedin.com/in/johndoe/"
    
    def test_generate_twitter_url(self):
        """Test Twitter URL generation."""
        url = URLGenerator.generate_url("twitter", "johndoe")
        assert url == "https://twitter.com/johndoe"
    
    def test_generate_x_url(self):
        """Test X (Twitter) URL generation."""
        url = URLGenerator.generate_url("x", "johndoe")
        assert url == "https://x.com/johndoe"
    
    def test_clean_username_with_at_symbol(self):
        """Test username cleaning (@ symbol removal)."""
        url = URLGenerator.generate_url("instagram", "@johndoe")
        assert "@" not in url
        assert url == "https://www.instagram.com/johndoe/"
    
    def test_generate_all_urls(self):
        """Test generating URLs for all platforms."""
        urls = URLGenerator.generate_all_urls("johndoe")
        
        assert isinstance(urls, dict)
        assert len(urls) >= 4  # At least 4 platforms
        assert "instagram" in urls
        assert "facebook" in urls
        assert "linkedin" in urls
        assert "twitter" in urls
    
    def test_unsupported_platform_raises_error(self):
        """Test that unsupported platform raises error."""
        with pytest.raises(ValueError, match="Unsupported platform"):
            URLGenerator.generate_url("unsupported", "johndoe")


# =============================================================================
# USERNAME VARIATION TESTS
# =============================================================================

class TestUsernameVariations:
    """Tests for username variation generation."""
    
    def test_basic_variations(self):
        """Test basic username variations."""
        variations = URLGenerator.generate_username_variations("johndoe")
        
        assert "johndoe" in variations
        assert "johndoe_" in variations
        assert "_johndoe" in variations
        assert "johndoe1" in variations
        assert "johndoe123" in variations
    
    def test_underscore_variations(self):
        """Test variations for usernames with underscores."""
        variations = URLGenerator.generate_username_variations("john_doe")
        
        assert "john_doe" in variations
        assert "johndoe" in variations  # Underscore removed
        assert "john.doe" in variations  # Underscore to dot
    
    def test_dot_variations(self):
        """Test variations for usernames with dots."""
        variations = URLGenerator.generate_username_variations("john.doe")
        
        assert "john.doe" in variations
        assert "johndoe" in variations  # Dot removed
        assert "john_doe" in variations  # Dot to underscore
    
    def test_no_duplicate_variations(self):
        """Test that variations are deduplicated."""
        variations = URLGenerator.generate_username_variations("test")
        
        # Should have no duplicates
        assert len(variations) == len(set(variations))


# =============================================================================
# SEARCH URL GENERATION TESTS
# =============================================================================

class TestSearchURLGenerator:
    """Tests for search URL generation."""
    
    def test_generate_instagram_search_url(self):
        """Test Instagram search URL generation."""
        url = URLGenerator.generate_search_url("instagram", "cristiano")
        assert "google.com/search" in url
        assert "site:instagram.com" in url
        assert "cristiano" in url
    
    def test_generate_facebook_search_url(self):
        """Test Facebook search URL generation."""
        url = URLGenerator.generate_search_url("facebook", "John Doe")
        assert "facebook.com/search/people" in url
        assert "John+Doe" in url or "John%20Doe" in url
    
    def test_generate_linkedin_search_url(self):
        """Test LinkedIn search URL generation."""
        url = URLGenerator.generate_search_url("linkedin", "Software Engineer")
        assert "linkedin.com/search/results/people" in url
        assert "Software" in url
    
    def test_generate_twitter_search_url(self):
        """Test Twitter/X search URL generation."""
        url = URLGenerator.generate_search_url("twitter", "johndoe")
        assert "x.com/search" in url
        assert "johndoe" in url
    
    def test_generate_x_search_url(self):
        """Test X search URL generation."""
        url = URLGenerator.generate_search_url("x", "username")
        assert "x.com/search" in url
        assert "username" in url
    
    def test_unsupported_platform_search_raises_error(self):
        """Test that unsupported platform search raises error."""
        with pytest.raises(ValueError, match="Search not supported"):
            URLGenerator.generate_search_url("unsupported_platform", "query")
