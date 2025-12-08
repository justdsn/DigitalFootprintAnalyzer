# =============================================================================
# OSINT PARSERS TESTS
# =============================================================================
# Unit tests for HTML parsers.
# =============================================================================

"""
OSINT Parsers Tests

Test suite for profile HTML parsers:
- Profile parser base utilities
- Platform-specific parsing
- Meta tag extraction
- Text extraction

Run with: pytest tests/test_osint_parsers.py -v
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.osint.parsers import (
    ProfileParser,
    InstagramParser,
    FacebookParser,
    LinkedInParser,
    TwitterParser
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def mock_instagram_html():
    """Mock Instagram profile HTML."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta property="og:title" content="John Doe">
        <meta property="og:description" content="Software Developer | Travel Enthusiast">
        <meta property="og:url" content="https://www.instagram.com/johndoe/">
    </head>
    <body>
        <h1>John Doe</h1>
        <span>Software Developer | Travel Enthusiast</span>
    </body>
    </html>
    """


@pytest.fixture
def mock_facebook_html():
    """Mock Facebook profile HTML."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta property="og:title" content="Jane Smith">
        <meta property="og:description" content="Marketing Manager at Tech Corp">
        <meta property="og:url" content="https://www.facebook.com/janesmith">
    </head>
    <body>
        <h1>Jane Smith</h1>
    </body>
    </html>
    """


@pytest.fixture
def mock_linkedin_html():
    """Mock LinkedIn profile HTML."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta property="og:title" content="Bob Johnson - CEO at StartupCo">
        <meta property="og:description" content="Experienced entrepreneur and tech leader">
        <meta property="og:url" content="https://www.linkedin.com/in/bobjohnson/">
    </head>
    <body>
        <h1>Bob Johnson - CEO at StartupCo</h1>
    </body>
    </html>
    """


@pytest.fixture
def mock_twitter_html():
    """Mock Twitter profile HTML."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta property="og:title" content="Alice Brown (@alicebrown)">
        <meta property="og:description" content="Designer & Artist | Creating beautiful things">
        <meta name="twitter:creator" content="@alicebrown">
    </head>
    <body>
        <h1>Alice Brown</h1>
    </body>
    </html>
    """


# =============================================================================
# PROFILE PARSER BASE TESTS
# =============================================================================

class TestProfileParserUtilities:
    """Tests for ProfileParser base utilities."""
    
    def test_extract_number_from_text(self):
        """Test number extraction from text."""
        parser = InstagramParser()  # Use concrete implementation
        
        assert parser.extract_number_from_text("1,234") == 1234
        assert parser.extract_number_from_text("1.5K") == 1500
        assert parser.extract_number_from_text("2M") == 2000000
        assert parser.extract_number_from_text("3.5B") == 3500000000
        assert parser.extract_number_from_text("no number") is None
    
    def test_parse_html(self):
        """Test HTML parsing."""
        parser = InstagramParser()
        html = "<html><body><p>Test</p></body></html>"
        soup = parser.parse_html(html)
        
        assert soup is not None
        assert soup.find('p').get_text() == "Test"


# =============================================================================
# INSTAGRAM PARSER TESTS
# =============================================================================

class TestInstagramParser:
    """Tests for Instagram profile parser."""
    
    def test_parse_instagram_profile(self, mock_instagram_html):
        """Test parsing Instagram profile."""
        parser = InstagramParser()
        result = parser.parse(mock_instagram_html)
        
        assert result["platform"] == "instagram"
        assert result["name"] == "John Doe"
        assert "Software Developer" in result["bio"]
        assert result["username"] == "johndoe"
    
    def test_platform_name(self):
        """Test platform name."""
        parser = InstagramParser()
        assert parser.get_platform_name() == "instagram"


# =============================================================================
# FACEBOOK PARSER TESTS
# =============================================================================

class TestFacebookParser:
    """Tests for Facebook profile parser."""
    
    def test_parse_facebook_profile(self, mock_facebook_html):
        """Test parsing Facebook profile."""
        parser = FacebookParser()
        result = parser.parse(mock_facebook_html)
        
        assert result["platform"] == "facebook"
        assert result["name"] == "Jane Smith"
        assert "Marketing Manager" in result["bio"]
    
    def test_platform_name(self):
        """Test platform name."""
        parser = FacebookParser()
        assert parser.get_platform_name() == "facebook"


# =============================================================================
# LINKEDIN PARSER TESTS
# =============================================================================

class TestLinkedInParser:
    """Tests for LinkedIn profile parser."""
    
    def test_parse_linkedin_profile(self, mock_linkedin_html):
        """Test parsing LinkedIn profile."""
        parser = LinkedInParser()
        result = parser.parse(mock_linkedin_html)
        
        assert result["platform"] == "linkedin"
        assert "Bob Johnson" in result["name"]
        assert result["job_title"] == "CEO at StartupCo"
    
    def test_platform_name(self):
        """Test platform name."""
        parser = LinkedInParser()
        assert parser.get_platform_name() == "linkedin"


# =============================================================================
# TWITTER PARSER TESTS
# =============================================================================

class TestTwitterParser:
    """Tests for Twitter profile parser."""
    
    def test_parse_twitter_profile(self, mock_twitter_html):
        """Test parsing Twitter profile."""
        parser = TwitterParser()
        result = parser.parse(mock_twitter_html)
        
        assert result["platform"] == "twitter"
        assert "Alice Brown" in result["name"]
        assert result["username"] == "alicebrown"
        assert "Designer" in result["bio"]
    
    def test_platform_name(self):
        """Test platform name."""
        parser = TwitterParser()
        assert parser.get_platform_name() == "twitter"


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class TestParserErrorHandling:
    """Tests for parser error handling."""
    
    def test_parse_empty_html(self):
        """Test parsing empty HTML."""
        parser = InstagramParser()
        result = parser.parse("")
        
        assert result["platform"] == "instagram"
        assert result["name"] is None
    
    def test_parse_malformed_html(self):
        """Test parsing malformed HTML."""
        parser = FacebookParser()
        html = "<html><body><div>Unclosed tag"
        result = parser.parse(html)
        
        assert result["platform"] == "facebook"
        # Should not crash, but may have None values
