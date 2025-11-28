# =============================================================================
# PII EXTRACTOR SERVICE
# =============================================================================
# Extracts Personally Identifiable Information from text using regex patterns.
# Designed for Sri Lankan context with local phone number formats.
# =============================================================================

"""
PII Extractor Service

This module provides regex-based extraction of PII elements:
- Email addresses (RFC 5322 compliant pattern)
- Sri Lankan phone numbers (07X-XXXXXXX, +94 formats)
- URLs (general and social media platform specific)
- @mentions (social media handles)

All phone numbers are normalized to E.164 format for consistency.

Example Usage:
    extractor = PIIExtractor()
    results = extractor.extract_all("Contact me at john@example.com or 0771234567")
    # Returns: {"emails": ["john@example.com"], "phones": ["+94771234567"], ...}
"""

import re
from typing import List, Dict, Any


# =============================================================================
# PII EXTRACTOR CLASS
# =============================================================================

class PIIExtractor:
    """
    Extract Personally Identifiable Information from text.
    
    This class provides methods to identify and extract various types of PII
    from text input, with special consideration for Sri Lankan formats.
    
    Attributes:
        email_pattern: Compiled regex for email extraction
        phone_pattern: Compiled regex for Sri Lankan phone numbers
        url_pattern: Compiled regex for URL extraction
        mention_pattern: Compiled regex for @mention extraction
        social_url_patterns: Dict of platform-specific URL patterns
    """
    
    def __init__(self):
        """
        Initialize the PII Extractor with compiled regex patterns.
        
        Compiling patterns during initialization improves performance
        when processing multiple texts.
        """
        # ---------------------------------------------------------------------
        # EMAIL PATTERN (RFC 5322 Simplified)
        # ---------------------------------------------------------------------
        # Pattern explanation:
        # [a-zA-Z0-9._%+-]+  : Local part - letters, numbers, and special chars
        # @                   : Required @ symbol
        # [a-zA-Z0-9.-]+     : Domain name - letters, numbers, dots, hyphens
        # \.[a-zA-Z]{2,}     : TLD - dot followed by 2+ letters
        # ---------------------------------------------------------------------
        self.email_pattern = re.compile(
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            re.IGNORECASE
        )
        
        # ---------------------------------------------------------------------
        # SRI LANKAN PHONE NUMBER PATTERNS
        # ---------------------------------------------------------------------
        # Sri Lankan phone formats supported:
        # 1. Mobile: 07X XXXXXXX (local format)
        # 2. Mobile with country code: +94 7X XXXXXXX or 0094 7X XXXXXXX
        # 3. With various separators: spaces, hyphens, dots
        # 
        # Pattern breakdown:
        # (?:\+94|0094|0)  : Country code (+94 or 0094) or local prefix (0)
        # [\s.-]?          : Optional separator (space, dot, or hyphen)
        # 7[0-9]           : Sri Lankan mobile prefix (70-79)
        # [\s.-]?          : Optional separator
        # [0-9]{3}         : First group of 3 digits
        # [\s.-]?          : Optional separator
        # [0-9]{4}         : Last group of 4 digits
        # ---------------------------------------------------------------------
        self.phone_pattern = re.compile(
            r'(?:\+94|0094|0)[\s.-]?7[0-9][\s.-]?[0-9]{3}[\s.-]?[0-9]{4}',
            re.IGNORECASE
        )
        
        # ---------------------------------------------------------------------
        # URL PATTERN
        # ---------------------------------------------------------------------
        # Pattern explanation:
        # https?://         : http:// or https://
        # (?:www\.)?        : Optional www. prefix
        # [^\s<>"{}|\\^`\[\]]+ : URL characters (excluding invalid ones)
        # ---------------------------------------------------------------------
        self.url_pattern = re.compile(
            r'https?://(?:www\.)?[^\s<>"{}|\\^`\[\]]+',
            re.IGNORECASE
        )
        
        # ---------------------------------------------------------------------
        # @MENTION PATTERN
        # ---------------------------------------------------------------------
        # Pattern explanation:
        # @                 : Required @ prefix
        # [a-zA-Z0-9_]+     : Username characters (letters, numbers, underscore)
        # Minimum 1 character after @
        # ---------------------------------------------------------------------
        self.mention_pattern = re.compile(
            r'@[a-zA-Z0-9_]+',
            re.IGNORECASE
        )
        
        # ---------------------------------------------------------------------
        # SOCIAL MEDIA URL PATTERNS
        # ---------------------------------------------------------------------
        # Platform-specific patterns to identify social media profile URLs
        # ---------------------------------------------------------------------
        self.social_url_patterns = {
            "facebook": re.compile(
                r'(?:https?://)?(?:www\.)?facebook\.com/[a-zA-Z0-9._-]+',
                re.IGNORECASE
            ),
            "instagram": re.compile(
                r'(?:https?://)?(?:www\.)?instagram\.com/[a-zA-Z0-9._]+',
                re.IGNORECASE
            ),
            "twitter": re.compile(
                r'(?:https?://)?(?:www\.)?(?:twitter\.com|x\.com)/[a-zA-Z0-9_]+',
                re.IGNORECASE
            ),
            "linkedin": re.compile(
                r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+',
                re.IGNORECASE
            ),
            "tiktok": re.compile(
                r'(?:https?://)?(?:www\.)?tiktok\.com/@[a-zA-Z0-9._]+',
                re.IGNORECASE
            ),
            "youtube": re.compile(
                r'(?:https?://)?(?:www\.)?youtube\.com/(?:@|user/|channel/)[a-zA-Z0-9_-]+',
                re.IGNORECASE
            )
        }
    
    # =========================================================================
    # EXTRACTION METHODS
    # =========================================================================
    
    def extract_emails(self, text: str) -> List[str]:
        """
        Extract email addresses from text.
        
        Uses RFC 5322 simplified pattern to find email addresses.
        Duplicates are removed and results are lowercased.
        
        Args:
            text: Input text to search for emails
        
        Returns:
            List[str]: List of unique email addresses found
        
        Example:
            >>> extractor.extract_emails("Email: john@example.com")
            ['john@example.com']
        """
        if not text:
            return []
        
        matches = self.email_pattern.findall(text)
        # Remove duplicates and lowercase
        return list(set(email.lower() for email in matches))
    
    def extract_phones(self, text: str) -> List[str]:
        """
        Extract Sri Lankan phone numbers from text.
        
        Identifies phone numbers in various Sri Lankan formats and
        normalizes them to E.164 format (+94XXXXXXXXX).
        
        Args:
            text: Input text to search for phone numbers
        
        Returns:
            List[str]: List of unique phone numbers in E.164 format
        
        Example:
            >>> extractor.extract_phones("Call me at 0771234567")
            ['+94771234567']
        """
        if not text:
            return []
        
        matches = self.phone_pattern.findall(text)
        # Normalize all found numbers to E.164 format
        normalized = [self.normalize_phone(phone) for phone in matches]
        # Remove None values and duplicates
        return list(set(phone for phone in normalized if phone))
    
    def normalize_phone(self, phone: str) -> str:
        """
        Normalize a Sri Lankan phone number to E.164 format.
        
        E.164 format: +94XXXXXXXXX (country code + 9 digits)
        
        Conversion rules:
        - 07XXXXXXXX -> +947XXXXXXXX
        - +94 7X XXXX XXX -> +947XXXXXXXX
        - 0094 7X XXXX XXX -> +947XXXXXXXX
        
        Args:
            phone: Phone number in any Sri Lankan format
        
        Returns:
            str: Phone number in E.164 format, or empty string if invalid
        
        Example:
            >>> extractor.normalize_phone("077-123-4567")
            '+94771234567'
        """
        if not phone:
            return ""
        
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Handle different formats
        if cleaned.startswith('+94'):
            # Already has +94 country code
            number = cleaned[3:]
        elif cleaned.startswith('0094'):
            # Has 0094 country code
            number = cleaned[4:]
        elif cleaned.startswith('0'):
            # Local format starting with 0
            number = cleaned[1:]
        else:
            # Assume it's just the number without prefix
            number = cleaned
        
        # Validate: Sri Lankan mobile numbers should be 9 digits starting with 7
        if len(number) == 9 and number.startswith('7'):
            return f'+94{number}'
        
        return ""
    
    def extract_urls(self, text: str) -> List[str]:
        """
        Extract URLs from text.
        
        Finds general URLs in the text. Use extract_social_urls()
        for platform-specific extraction.
        
        Args:
            text: Input text to search for URLs
        
        Returns:
            List[str]: List of unique URLs found
        
        Example:
            >>> extractor.extract_urls("Visit https://example.com")
            ['https://example.com']
        """
        if not text:
            return []
        
        matches = self.url_pattern.findall(text)
        # Remove duplicates
        return list(set(matches))
    
    def extract_social_urls(self, text: str) -> Dict[str, List[str]]:
        """
        Extract social media platform URLs from text.
        
        Identifies URLs from specific social media platforms:
        - Facebook
        - Instagram
        - Twitter/X
        - LinkedIn
        - TikTok
        - YouTube
        
        Args:
            text: Input text to search for social URLs
        
        Returns:
            Dict[str, List[str]]: Dictionary with platform names as keys
                                  and lists of URLs as values
        
        Example:
            >>> extractor.extract_social_urls("fb.com/john instagram.com/john")
            {'facebook': ['facebook.com/john'], 'instagram': ['instagram.com/john']}
        """
        if not text:
            return {}
        
        results = {}
        for platform, pattern in self.social_url_patterns.items():
            matches = pattern.findall(text)
            if matches:
                results[platform] = list(set(matches))
        
        return results
    
    def extract_mentions(self, text: str) -> List[str]:
        """
        Extract @mentions from text.
        
        Finds social media style @mentions (e.g., @username).
        
        Args:
            text: Input text to search for mentions
        
        Returns:
            List[str]: List of unique mentions (including @ symbol)
        
        Example:
            >>> extractor.extract_mentions("Contact @john_doe")
            ['@john_doe']
        """
        if not text:
            return []
        
        matches = self.mention_pattern.findall(text)
        # Remove duplicates, preserve case
        return list(set(matches))
    
    def extract_all(self, text: str) -> Dict[str, Any]:
        """
        Extract all types of PII from text.
        
        Comprehensive extraction that runs all individual extractors
        and returns a combined result.
        
        Args:
            text: Input text to analyze
        
        Returns:
            Dict[str, Any]: Dictionary containing all extracted PII:
                - emails: List of email addresses
                - phones: List of phone numbers (E.164 format)
                - urls: List of general URLs
                - social_urls: Dict of platform-specific URLs
                - mentions: List of @mentions
        
        Example:
            >>> extractor.extract_all("Email john@test.com, call 0771234567")
            {
                'emails': ['john@test.com'],
                'phones': ['+94771234567'],
                'urls': [],
                'social_urls': {},
                'mentions': []
            }
        """
        return {
            "emails": self.extract_emails(text),
            "phones": self.extract_phones(text),
            "urls": self.extract_urls(text),
            "social_urls": self.extract_social_urls(text),
            "mentions": self.extract_mentions(text)
        }


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

# Create a default extractor instance for module-level usage
_default_extractor = PIIExtractor()


def extract_emails(text: str) -> List[str]:
    """Module-level convenience function for email extraction."""
    return _default_extractor.extract_emails(text)


def extract_phones(text: str) -> List[str]:
    """Module-level convenience function for phone extraction."""
    return _default_extractor.extract_phones(text)


def extract_all(text: str) -> Dict[str, Any]:
    """Module-level convenience function for all PII extraction."""
    return _default_extractor.extract_all(text)
