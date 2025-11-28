# =============================================================================
# PII EXTRACTOR SERVICE TESTS
# =============================================================================
# Unit tests for the PII extraction functionality.
# Tests email, phone, URL, and mention extraction with Sri Lankan context.
# =============================================================================

"""
PII Extractor Tests

Comprehensive test suite for the PIIExtractor service:
- Email extraction tests
- Sri Lankan phone number extraction and normalization
- URL and social media URL extraction
- @mention extraction
- Combined extraction tests

Run with: pytest tests/test_pii_extractor.py -v
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.pii_extractor import PIIExtractor


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def extractor():
    """Create a PIIExtractor instance for tests."""
    return PIIExtractor()


# =============================================================================
# EMAIL EXTRACTION TESTS
# =============================================================================

class TestEmailExtraction:
    """Tests for email address extraction."""
    
    def test_extract_simple_email(self, extractor):
        """Test extraction of a simple email address."""
        text = "Contact me at john@example.com"
        result = extractor.extract_emails(text)
        assert "john@example.com" in result
    
    def test_extract_multiple_emails(self, extractor):
        """Test extraction of multiple email addresses."""
        text = "Email john@example.com or jane@test.org for info"
        result = extractor.extract_emails(text)
        assert len(result) == 2
        assert "john@example.com" in result
        assert "jane@test.org" in result
    
    def test_extract_email_with_subdomain(self, extractor):
        """Test extraction of email with subdomain."""
        text = "Contact admin@mail.company.com"
        result = extractor.extract_emails(text)
        assert "admin@mail.company.com" in result
    
    def test_extract_email_with_special_chars(self, extractor):
        """Test extraction of email with special characters."""
        text = "Email john.doe+newsletter@example.com"
        result = extractor.extract_emails(text)
        assert "john.doe+newsletter@example.com" in result
    
    def test_no_email_returns_empty_list(self, extractor):
        """Test that text without email returns empty list."""
        text = "No email here, just regular text"
        result = extractor.extract_emails(text)
        assert result == []
    
    def test_empty_text_returns_empty_list(self, extractor):
        """Test that empty text returns empty list."""
        result = extractor.extract_emails("")
        assert result == []
    
    def test_none_text_returns_empty_list(self, extractor):
        """Test that None text returns empty list."""
        result = extractor.extract_emails(None)
        assert result == []


# =============================================================================
# PHONE NUMBER EXTRACTION TESTS
# =============================================================================

class TestPhoneExtraction:
    """Tests for Sri Lankan phone number extraction."""
    
    def test_extract_local_format_no_separator(self, extractor):
        """Test extraction of local format without separators (07XXXXXXXX)."""
        text = "Call me at 0771234567"
        result = extractor.extract_phones(text)
        assert "+94771234567" in result
    
    def test_extract_local_format_with_hyphen(self, extractor):
        """Test extraction of local format with hyphens (077-123-4567)."""
        text = "Phone: 077-123-4567"
        result = extractor.extract_phones(text)
        assert "+94771234567" in result
    
    def test_extract_local_format_with_spaces(self, extractor):
        """Test extraction of local format with spaces (077 123 4567)."""
        text = "Contact: 077 123 4567"
        result = extractor.extract_phones(text)
        assert "+94771234567" in result
    
    def test_extract_international_format_plus94(self, extractor):
        """Test extraction of +94 international format."""
        text = "International: +94771234567"
        result = extractor.extract_phones(text)
        assert "+94771234567" in result
    
    def test_extract_international_format_0094(self, extractor):
        """Test extraction of 0094 international format."""
        text = "Call: 0094771234567"
        result = extractor.extract_phones(text)
        assert "+94771234567" in result
    
    def test_extract_multiple_phones(self, extractor):
        """Test extraction of multiple phone numbers."""
        text = "Call 0771234567 or 0779876543"
        result = extractor.extract_phones(text)
        assert len(result) == 2
        assert "+94771234567" in result
        assert "+94779876543" in result
    
    def test_extract_mixed_formats(self, extractor):
        """Test extraction with mixed formats."""
        text = "Local: 0771234567, International: +94779876543"
        result = extractor.extract_phones(text)
        assert len(result) == 2
    
    def test_no_phone_returns_empty_list(self, extractor):
        """Test that text without phone returns empty list."""
        text = "No phone here"
        result = extractor.extract_phones(text)
        assert result == []


# =============================================================================
# PHONE NORMALIZATION TESTS
# =============================================================================

class TestPhoneNormalization:
    """Tests for phone number normalization to E.164 format."""
    
    def test_normalize_local_format(self, extractor):
        """Test normalization of local format."""
        assert extractor.normalize_phone("0771234567") == "+94771234567"
    
    def test_normalize_with_hyphens(self, extractor):
        """Test normalization with hyphens."""
        assert extractor.normalize_phone("077-123-4567") == "+94771234567"
    
    def test_normalize_with_spaces(self, extractor):
        """Test normalization with spaces."""
        assert extractor.normalize_phone("077 123 4567") == "+94771234567"
    
    def test_normalize_international_plus94(self, extractor):
        """Test normalization of +94 format."""
        assert extractor.normalize_phone("+94771234567") == "+94771234567"
    
    def test_normalize_international_0094(self, extractor):
        """Test normalization of 0094 format."""
        assert extractor.normalize_phone("0094771234567") == "+94771234567"
    
    def test_normalize_empty_returns_empty(self, extractor):
        """Test that empty string returns empty."""
        assert extractor.normalize_phone("") == ""
    
    def test_normalize_none_returns_empty(self, extractor):
        """Test that None returns empty."""
        assert extractor.normalize_phone(None) == ""


# =============================================================================
# URL EXTRACTION TESTS
# =============================================================================

class TestURLExtraction:
    """Tests for URL extraction."""
    
    def test_extract_http_url(self, extractor):
        """Test extraction of HTTP URL."""
        text = "Visit http://example.com"
        result = extractor.extract_urls(text)
        assert "http://example.com" in result
    
    def test_extract_https_url(self, extractor):
        """Test extraction of HTTPS URL."""
        text = "Visit https://example.com"
        result = extractor.extract_urls(text)
        assert "https://example.com" in result
    
    def test_extract_url_with_path(self, extractor):
        """Test extraction of URL with path."""
        text = "Check https://example.com/path/to/page"
        result = extractor.extract_urls(text)
        assert len(result) == 1
        assert "example.com/path/to/page" in result[0]
    
    def test_extract_multiple_urls(self, extractor):
        """Test extraction of multiple URLs."""
        text = "Visit https://example.com and http://test.org"
        result = extractor.extract_urls(text)
        assert len(result) == 2


# =============================================================================
# SOCIAL URL EXTRACTION TESTS
# =============================================================================

class TestSocialURLExtraction:
    """Tests for social media URL extraction."""
    
    def test_extract_facebook_url(self, extractor):
        """Test extraction of Facebook URL."""
        text = "Follow me at https://www.facebook.com/johndoe"
        result = extractor.extract_social_urls(text)
        assert "facebook" in result
        assert len(result["facebook"]) == 1
    
    def test_extract_instagram_url(self, extractor):
        """Test extraction of Instagram URL."""
        text = "Instagram: https://www.instagram.com/johndoe"
        result = extractor.extract_social_urls(text)
        assert "instagram" in result
    
    def test_extract_twitter_url(self, extractor):
        """Test extraction of Twitter/X URL."""
        text = "Twitter: https://twitter.com/johndoe"
        result = extractor.extract_social_urls(text)
        assert "twitter" in result
    
    def test_extract_linkedin_url(self, extractor):
        """Test extraction of LinkedIn URL."""
        text = "LinkedIn: https://www.linkedin.com/in/johndoe"
        result = extractor.extract_social_urls(text)
        assert "linkedin" in result


# =============================================================================
# MENTION EXTRACTION TESTS
# =============================================================================

class TestMentionExtraction:
    """Tests for @mention extraction."""
    
    def test_extract_single_mention(self, extractor):
        """Test extraction of single @mention."""
        text = "Follow @johndoe"
        result = extractor.extract_mentions(text)
        assert "@johndoe" in result
    
    def test_extract_multiple_mentions(self, extractor):
        """Test extraction of multiple @mentions."""
        text = "Thanks @john and @jane!"
        result = extractor.extract_mentions(text)
        assert "@john" in result
        assert "@jane" in result
    
    def test_mention_with_underscore(self, extractor):
        """Test extraction of @mention with underscore."""
        text = "Follow @john_doe_123"
        result = extractor.extract_mentions(text)
        assert "@john_doe_123" in result


# =============================================================================
# COMBINED EXTRACTION TESTS
# =============================================================================

class TestCombinedExtraction:
    """Tests for the extract_all method."""
    
    def test_extract_all_types(self, extractor):
        """Test extraction of all PII types."""
        text = """
        Contact John at john@example.com or call 0771234567.
        Follow @johndoe on Twitter: https://twitter.com/johndoe
        """
        result = extractor.extract_all(text)
        
        assert "emails" in result
        assert "john@example.com" in result["emails"]
        
        assert "phones" in result
        assert "+94771234567" in result["phones"]
        
        assert "mentions" in result
        assert "@johndoe" in result["mentions"]
        
        assert "urls" in result
        assert "social_urls" in result
    
    def test_extract_all_empty_text(self, extractor):
        """Test extract_all with empty text."""
        result = extractor.extract_all("")
        
        assert result["emails"] == []
        assert result["phones"] == []
        assert result["urls"] == []
        assert result["mentions"] == []


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
