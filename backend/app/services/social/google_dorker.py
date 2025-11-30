# =============================================================================
# GOOGLE DORK SEARCHER SERVICE
# =============================================================================
# Searches for social media profiles using Google Dorking techniques.
# No authentication required - uses public Google search.
# =============================================================================

"""
Google Dork Searcher Service

This module provides Google Dork-based profile discovery:
- Search by name with optional location filtering
- Search by email (extracts username)
- Search by username variations
- Search by phone number (Sri Lankan formats)

Features:
- Platform-specific dork queries
- Sri Lanka focused location filtering
- Filters out non-profile URLs (search pages, help pages, etc.)
- No authentication required

Example Usage:
    searcher = GoogleDorkSearcher()
    results = searcher.search_by_username("john_doe")
    # Returns list of potential profile URLs
    
    results = searcher.search_by_phone("0771234567")
    # Returns results with Sri Lankan phone format variations
"""

import re
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus
import logging

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

# Set up logger
logger = logging.getLogger(__name__)


class GoogleDorkSearcher:
    """
    Search for social media profiles using Google Dorking techniques.
    
    This class provides methods to:
    1. Generate Google Dork queries for social media platforms
    2. Search by various identifier types (name, email, username, phone)
    3. Filter and parse search results for profile URLs
    
    Attributes:
        PLATFORM_DORKS: Platform-specific Google Dork templates
        NON_PROFILE_PATTERNS: Patterns to filter out non-profile URLs
        SRI_LANKAN_PHONE_FORMATS: Phone number format patterns for Sri Lanka
    """
    
    # -------------------------------------------------------------------------
    # PLATFORM-SPECIFIC DORK TEMPLATES
    # -------------------------------------------------------------------------
    PLATFORM_DORKS = {
        "facebook": {
            "name": "Facebook",
            "site": "facebook.com",
            "profile_pattern": r"facebook\.com/([a-zA-Z0-9._]+)/?$",
            "dork_template": 'site:facebook.com "{query}"',
            "dork_username": 'site:facebook.com/"{username}"',
        },
        "instagram": {
            "name": "Instagram",
            "site": "instagram.com",
            "profile_pattern": r"instagram\.com/([a-zA-Z0-9._]+)/?$",
            "dork_template": 'site:instagram.com "{query}"',
            "dork_username": 'site:instagram.com/"{username}"',
        },
        "linkedin": {
            "name": "LinkedIn",
            "site": "linkedin.com/in",
            "profile_pattern": r"linkedin\.com/in/([a-zA-Z0-9-]+)/?$",
            "dork_template": 'site:linkedin.com/in "{query}"',
            "dork_username": 'site:linkedin.com/in/"{username}"',
        },
        "x": {
            "name": "X (Twitter)",
            "site": "x.com",
            "profile_pattern": r"(?:x\.com|twitter\.com)/([a-zA-Z0-9_]+)/?$",
            "dork_template": 'site:x.com OR site:twitter.com "{query}"',
            "dork_username": 'site:x.com/"{username}" OR site:twitter.com/"{username}"',
        }
    }
    
    # -------------------------------------------------------------------------
    # NON-PROFILE URL PATTERNS (to filter out)
    # -------------------------------------------------------------------------
    NON_PROFILE_PATTERNS = [
        r"/search\??",           # Search pages
        r"/help",                # Help pages  
        r"/about",               # About pages
        r"/login",               # Login pages
        r"/signup",              # Signup pages
        r"/register",            # Register pages
        r"/settings",            # Settings pages
        r"/privacy",             # Privacy pages
        r"/terms",               # Terms pages
        r"/policy",              # Policy pages
        r"/support",             # Support pages
        r"/explore",             # Explore/discover pages
        r"/hashtag",             # Hashtag pages
        r"/directory",           # Directory pages
        r"/pages/",              # Facebook pages category
        r"/groups/",             # Facebook groups
        r"/events/",             # Events pages
        r"/jobs/",               # Jobs pages
        r"/feed/",               # Feed pages
        r"/stories/",            # Stories pages
        r"/reels/",              # Reels pages
    ]
    
    # -------------------------------------------------------------------------
    # SRI LANKAN PHONE NUMBER FORMATS
    # -------------------------------------------------------------------------
    SRI_LANKAN_PHONE_FORMATS = {
        "mobile_local": r"^07\d{8}$",        # 07XXXXXXXX
        "mobile_intl": r"^\+947\d{8}$",       # +947XXXXXXXX
        "mobile_intl_no_plus": r"^947\d{8}$", # 947XXXXXXXX
        "mobile_00": r"^00947\d{8}$",         # 00947XXXXXXXX
    }
    
    # -------------------------------------------------------------------------
    # GOOGLE SEARCH URL TEMPLATE
    # -------------------------------------------------------------------------
    GOOGLE_SEARCH_URL = "https://www.google.com/search?q={query}"
    
    # Request settings
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
    REQUEST_TIMEOUT = 15.0
    
    def __init__(self):
        """Initialize the Google Dork Searcher."""
        self._compiled_non_profile_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.NON_PROFILE_PATTERNS
        ]
    
    # -------------------------------------------------------------------------
    # PUBLIC SEARCH METHODS
    # -------------------------------------------------------------------------
    
    def search_by_name(
        self, 
        name: str, 
        location: Optional[str] = "Sri Lanka"
    ) -> List[Dict[str, Any]]:
        """
        Search for social media profiles by name.
        
        Generates Google Dork queries to search for profiles
        matching the given name, optionally filtered by location.
        
        Args:
            name: Full name to search for
            location: Optional location filter (default: "Sri Lanka")
        
        Returns:
            List of search result dictionaries containing:
                - platform: Platform name
                - query: Google Dork query used
                - search_url: Google search URL
                - potential_profiles: List of potential profile URLs found
        
        Example:
            >>> searcher.search_by_name("John Perera", "Colombo")
            [
                {
                    'platform': 'Facebook',
                    'query': 'site:facebook.com "John Perera" "Colombo"',
                    'search_url': 'https://...',
                    'potential_profiles': []
                },
                ...
            ]
        """
        if not name or not name.strip():
            return []
        
        name = name.strip()
        results = []
        
        for platform_id, config in self.PLATFORM_DORKS.items():
            # Build query with location if provided
            if location:
                query = f'{config["dork_template"].format(query=name)} "{location}"'
            else:
                query = config["dork_template"].format(query=name)
            
            search_url = self.GOOGLE_SEARCH_URL.format(query=quote_plus(query))
            
            results.append({
                "platform": config["name"],
                "platform_id": platform_id,
                "query": query,
                "search_url": search_url,
                "search_type": "name",
                "identifier": name,
                "potential_profiles": []  # To be populated by actual search
            })
        
        return results
    
    def search_by_email(self, email: str) -> List[Dict[str, Any]]:
        """
        Search for social media profiles by email address.
        
        Extracts the username portion of the email and searches
        for profiles using both the full email and username.
        
        Args:
            email: Email address to search
        
        Returns:
            List of search result dictionaries
        
        Example:
            >>> searcher.search_by_email("john.perera@gmail.com")
            # Searches for "john.perera@gmail.com" and "john.perera"
        """
        if not email or not email.strip():
            return []
        
        email = email.strip().lower()
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return []
        
        # Extract username from email
        username = email.split('@')[0]
        
        results = []
        
        for platform_id, config in self.PLATFORM_DORKS.items():
            # Search with full email
            email_query = config["dork_template"].format(query=email)
            email_search_url = self.GOOGLE_SEARCH_URL.format(
                query=quote_plus(email_query)
            )
            
            results.append({
                "platform": config["name"],
                "platform_id": platform_id,
                "query": email_query,
                "search_url": email_search_url,
                "search_type": "email",
                "identifier": email,
                "potential_profiles": []
            })
            
            # Search with extracted username
            username_query = config["dork_username"].format(username=username)
            username_search_url = self.GOOGLE_SEARCH_URL.format(
                query=quote_plus(username_query)
            )
            
            results.append({
                "platform": config["name"],
                "platform_id": platform_id,
                "query": username_query,
                "search_url": username_search_url,
                "search_type": "email_username",
                "identifier": username,
                "potential_profiles": []
            })
        
        return results
    
    def search_by_username(self, username: str) -> List[Dict[str, Any]]:
        """
        Search for social media profiles by username.
        
        Generates platform-specific dork queries for the username
        and common variations.
        
        Args:
            username: Username to search for
        
        Returns:
            List of search result dictionaries
        
        Example:
            >>> searcher.search_by_username("john_doe")
            # Searches for "john_doe", "johndoe", "john.doe" variations
        """
        if not username or not username.strip():
            return []
        
        username = username.strip().lstrip('@')
        
        # Generate username variations
        variations = self._generate_username_variations(username)
        
        results = []
        
        for variation in variations:
            for platform_id, config in self.PLATFORM_DORKS.items():
                query = config["dork_username"].format(username=variation)
                search_url = self.GOOGLE_SEARCH_URL.format(
                    query=quote_plus(query)
                )
                
                results.append({
                    "platform": config["name"],
                    "platform_id": platform_id,
                    "query": query,
                    "search_url": search_url,
                    "search_type": "username",
                    "identifier": variation,
                    "is_variation": variation != username.lower(),
                    "original_username": username,
                    "potential_profiles": []
                })
        
        return results
    
    def search_by_phone(self, phone: str) -> List[Dict[str, Any]]:
        """
        Search for social media profiles by phone number.
        
        Generates searches for multiple Sri Lankan phone number formats:
        - Local format: 07XXXXXXXX
        - International with +: +947XXXXXXXX
        - International without +: 947XXXXXXXX
        - Formatted: 077-XXX-XXXX, 077 XXX XXXX
        
        Args:
            phone: Sri Lankan phone number in any format
        
        Returns:
            List of search result dictionaries with various formats
        
        Example:
            >>> searcher.search_by_phone("0771234567")
            # Searches for "0771234567", "+94771234567", "077-123-4567", etc.
        """
        if not phone or not phone.strip():
            return []
        
        # Clean phone number
        phone = phone.strip()
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Generate phone format variations
        phone_variations = self._generate_phone_variations(cleaned)
        
        if not phone_variations:
            return []
        
        results = []
        
        for phone_format in phone_variations:
            for platform_id, config in self.PLATFORM_DORKS.items():
                query = config["dork_template"].format(query=phone_format)
                search_url = self.GOOGLE_SEARCH_URL.format(
                    query=quote_plus(query)
                )
                
                results.append({
                    "platform": config["name"],
                    "platform_id": platform_id,
                    "query": query,
                    "search_url": search_url,
                    "search_type": "phone",
                    "identifier": phone_format,
                    "original_phone": phone,
                    "potential_profiles": []
                })
        
        return results
    
    # -------------------------------------------------------------------------
    # URL FILTERING AND VALIDATION
    # -------------------------------------------------------------------------
    
    def is_profile_url(self, url: str) -> bool:
        """
        Check if a URL is likely a profile URL (not a search/help page).
        
        Filters out URLs that match non-profile patterns like search pages,
        help pages, login pages, etc.
        
        Args:
            url: URL to check
        
        Returns:
            bool: True if URL appears to be a profile URL
        """
        if not url:
            return False
        
        url_lower = url.lower()
        
        # Check against non-profile patterns
        for pattern in self._compiled_non_profile_patterns:
            if pattern.search(url_lower):
                return False
        
        return True
    
    def extract_username_from_url(self, url: str, platform_id: str) -> Optional[str]:
        """
        Extract username from a profile URL.
        
        Args:
            url: Profile URL
            platform_id: Platform identifier
        
        Returns:
            Extracted username or None if not found
        """
        if not url or platform_id not in self.PLATFORM_DORKS:
            return None
        
        config = self.PLATFORM_DORKS[platform_id]
        pattern = config.get("profile_pattern")
        
        if not pattern:
            return None
        
        match = re.search(pattern, url)
        return match.group(1) if match else None
    
    def filter_profile_urls(
        self, 
        urls: List[str], 
        platform_id: str
    ) -> List[Dict[str, Any]]:
        """
        Filter a list of URLs to only include valid profile URLs.
        
        Args:
            urls: List of URLs to filter
            platform_id: Platform identifier
        
        Returns:
            List of filtered profile URL dictionaries
        """
        filtered = []
        
        for url in urls:
            if self.is_profile_url(url):
                username = self.extract_username_from_url(url, platform_id)
                filtered.append({
                    "url": url,
                    "platform_id": platform_id,
                    "platform": self.PLATFORM_DORKS[platform_id]["name"],
                    "username": username
                })
        
        return filtered
    
    # -------------------------------------------------------------------------
    # HELPER METHODS
    # -------------------------------------------------------------------------
    
    def _generate_username_variations(self, username: str) -> List[str]:
        """
        Generate common username variations.
        
        Args:
            username: Base username
        
        Returns:
            List of username variations
        """
        username = username.lower()
        variations = set()
        
        # Original
        variations.add(username)
        
        # Remove underscores
        variations.add(username.replace('_', ''))
        
        # Remove dots
        variations.add(username.replace('.', ''))
        
        # Replace underscores with dots
        variations.add(username.replace('_', '.'))
        
        # Replace dots with underscores
        variations.add(username.replace('.', '_'))
        
        # Remove all special characters
        clean = re.sub(r'[^a-z0-9]', '', username)
        variations.add(clean)
        
        # Filter out empty strings
        variations.discard('')
        
        return list(variations)
    
    def _generate_phone_variations(self, cleaned_phone: str) -> List[str]:
        """
        Generate Sri Lankan phone number format variations.
        
        Args:
            cleaned_phone: Phone number with only digits and +
        
        Returns:
            List of phone format variations
        """
        variations = []
        
        # Remove leading + for processing
        digits_only = cleaned_phone.lstrip('+')
        
        # Determine base number (last 9 digits for mobile)
        base_number = None
        
        # Check if starts with 07 (local mobile)
        if digits_only.startswith('07') and len(digits_only) == 10:
            base_number = digits_only
            
        # Check if starts with 947 (international)
        elif digits_only.startswith('947') and len(digits_only) == 11:
            base_number = '0' + digits_only[2:]
            
        # Check if starts with 0094 (international with 00)
        elif digits_only.startswith('00947') and len(digits_only) == 13:
            base_number = '0' + digits_only[4:]
        
        if not base_number:
            # Not a valid Sri Lankan mobile format
            # Return original if it looks like a phone number
            if len(digits_only) >= 7:
                return [cleaned_phone]
            return []
        
        # Generate variations from base_number (e.g., "0771234567")
        # Local format: 0771234567
        variations.append(base_number)
        
        # International with +: +94771234567
        intl = "+94" + base_number[1:]
        variations.append(intl)
        
        # International without +: 94771234567
        variations.append("94" + base_number[1:])
        
        # Formatted local: 077-123-4567
        formatted = f"{base_number[:3]}-{base_number[3:6]}-{base_number[6:]}"
        variations.append(formatted)
        
        # Formatted with spaces: 077 123 4567
        spaced = f"{base_number[:3]} {base_number[3:6]} {base_number[6:]}"
        variations.append(spaced)
        
        # International formatted: +94 77 123 4567
        intl_formatted = f"+94 {base_number[1:3]} {base_number[3:6]} {base_number[6:]}"
        variations.append(intl_formatted)
        
        return list(set(variations))
    
    def get_supported_platforms(self) -> List[str]:
        """
        Get list of supported platform IDs.
        
        Returns:
            List of platform IDs
        """
        return list(self.PLATFORM_DORKS.keys())
    
    def build_combined_dork_query(
        self,
        identifier: str,
        identifier_type: str,
        platforms: Optional[List[str]] = None
    ) -> str:
        """
        Build a combined Google Dork query for multiple platforms.
        
        Args:
            identifier: The identifier to search for
            identifier_type: Type of identifier (name, email, username, phone)
            platforms: Optional list of platforms (default: all)
        
        Returns:
            Combined dork query string
        """
        if platforms is None:
            platforms = self.get_supported_platforms()
        
        site_parts = []
        for platform_id in platforms:
            if platform_id in self.PLATFORM_DORKS:
                site = self.PLATFORM_DORKS[platform_id]["site"]
                site_parts.append(f"site:{site}")
        
        sites_query = " OR ".join(site_parts)
        return f'({sites_query}) "{identifier}"'


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

_default_searcher = GoogleDorkSearcher()


def search_by_name(
    name: str, 
    location: Optional[str] = "Sri Lanka"
) -> List[Dict[str, Any]]:
    """Module-level convenience function for name search."""
    return _default_searcher.search_by_name(name, location)


def search_by_email(email: str) -> List[Dict[str, Any]]:
    """Module-level convenience function for email search."""
    return _default_searcher.search_by_email(email)


def search_by_username(username: str) -> List[Dict[str, Any]]:
    """Module-level convenience function for username search."""
    return _default_searcher.search_by_username(username)


def search_by_phone(phone: str) -> List[Dict[str, Any]]:
    """Module-level convenience function for phone search."""
    return _default_searcher.search_by_phone(phone)
