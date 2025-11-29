# =============================================================================
# SOCIAL MEDIA DATA COLLECTOR SERVICE
# =============================================================================
# Extracts public data from social media profile pages.
# Uses Open Graph meta tags and HTML parsing.
# =============================================================================

"""
Social Media Data Collector Service

This module extracts public data from social media profile pages:
- Display name from og:title meta tag
- Bio/description from og:description meta tag
- Profile picture URL from og:image meta tag
- Location information when available

Features:
- Extract data using Open Graph meta tags
- Platform-specific parsing for better accuracy
- Handle missing or malformed data gracefully

Example Usage:
    collector = SocialMediaDataCollector()
    data = await collector.collect_profile_data(
        "https://www.instagram.com/john_doe/",
        "instagram"
    )
    # Returns: {"name": "John Doe", "bio": "...", ...}
"""

import re
from typing import Dict, Optional, Any
import logging

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# Set up logger
logger = logging.getLogger(__name__)


class SocialMediaDataCollector:
    """
    Collect public data from social media profiles.
    
    This class provides methods to:
    1. Fetch profile page content
    2. Extract data from Open Graph meta tags
    3. Parse platform-specific HTML elements
    
    Supported data extraction:
    - Display name
    - Bio/description
    - Profile picture URL
    - Location
    """
    
    # Default User-Agent
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    
    # Request timeout
    REQUEST_TIMEOUT = 15.0
    
    def __init__(self):
        """Initialize the Social Media Data Collector."""
        pass
    
    async def collect_profile_data(
        self,
        url: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Collect public data from a profile URL.
        
        Fetches the profile page and extracts available public information
        using Open Graph meta tags and platform-specific parsing.
        
        Args:
            url: The profile URL to collect data from
            platform: Platform ID (facebook, instagram, linkedin, x)
        
        Returns:
            Dict containing:
                - url: The profile URL
                - platform: Platform name
                - name: Display name (or None)
                - bio: Bio/description (or None)
                - profile_image: Profile picture URL (or None)
                - location: Location (or None)
                - raw_title: Raw og:title value
                - raw_description: Raw og:description value
                - success: Boolean indicating if data was collected
                - error: Error message if any
        
        Example:
            >>> await collector.collect_profile_data(
            ...     "https://www.instagram.com/john_doe/",
            ...     "instagram"
            ... )
            {
                'url': 'https://www.instagram.com/john_doe/',
                'platform': 'instagram',
                'name': 'John Doe',
                'bio': 'Software developer | Colombo',
                'profile_image': 'https://...',
                'location': None,
                'success': True,
                'error': None
            }
        """
        result = {
            "url": url,
            "platform": platform,
            "name": None,
            "bio": None,
            "profile_image": None,
            "location": None,
            "raw_title": None,
            "raw_description": None,
            "success": False,
            "error": None
        }
        
        if not HTTPX_AVAILABLE:
            result["error"] = "httpx library not available"
            return result
        
        if not BS4_AVAILABLE:
            result["error"] = "beautifulsoup4 library not available"
            return result
        
        if not url:
            result["error"] = "URL is required"
            return result
        
        try:
            async with httpx.AsyncClient(
                timeout=self.REQUEST_TIMEOUT,
                follow_redirects=True
            ) as client:
                headers = {
                    "User-Agent": self.DEFAULT_USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "en-US,en;q=0.9"
                }
                
                response = await client.get(url, headers=headers)
                
                if response.status_code != 200:
                    result["error"] = f"HTTP {response.status_code}"
                    return result
                
                # Parse HTML
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Extract data
                result["name"] = self._extract_name(soup, platform)
                result["bio"] = self._extract_bio(soup, platform)
                result["profile_image"] = self._extract_profile_image(soup, platform)
                result["location"] = self._extract_location(soup, platform)
                
                # Store raw values for debugging
                result["raw_title"] = self._get_og_content(soup, "og:title")
                result["raw_description"] = self._get_og_content(soup, "og:description")
                
                result["success"] = True
                
        except httpx.TimeoutException:
            result["error"] = "Request timed out"
        except httpx.RequestError as e:
            result["error"] = f"Request error: {str(e)}"
        except Exception as e:
            logger.error(f"Error collecting data from {url}: {e}")
            result["error"] = f"Unexpected error: {str(e)}"
        
        return result
    
    def _get_og_content(self, soup: Any, property_name: str) -> Optional[str]:
        """
        Get content from an Open Graph meta tag.
        
        Args:
            soup: BeautifulSoup object
            property_name: The og: property name (e.g., "og:title")
        
        Returns:
            str: Content value or None if not found
        """
        tag = soup.find("meta", property=property_name)
        if tag and tag.get("content"):
            return tag["content"].strip()
        return None
    
    def _get_meta_content(self, soup: Any, name: str) -> Optional[str]:
        """
        Get content from a meta tag by name.
        
        Args:
            soup: BeautifulSoup object
            name: The meta name attribute
        
        Returns:
            str: Content value or None if not found
        """
        tag = soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            return tag["content"].strip()
        return None
    
    def _extract_name(self, soup: Any, platform: str) -> Optional[str]:
        """
        Extract display name from profile page.
        
        Uses og:title meta tag with platform-specific cleaning.
        
        Args:
            soup: BeautifulSoup object
            platform: Platform ID
        
        Returns:
            str: Display name or None
        """
        og_title = self._get_og_content(soup, "og:title")
        
        if not og_title:
            return None
        
        # Platform-specific cleaning
        if platform == "instagram":
            # Instagram format: "Name (@username) • Instagram photos and videos"
            match = re.match(r"^([^@(]+)", og_title)
            if match:
                return match.group(1).strip()
        
        elif platform == "facebook":
            # Facebook format: "Name | Facebook"
            parts = og_title.split("|")
            if parts:
                return parts[0].strip()
        
        elif platform == "linkedin":
            # LinkedIn format: "Name - Title | LinkedIn"
            parts = og_title.split("-")
            if parts:
                return parts[0].strip()
        
        elif platform == "x":
            # X format: "Name (@username) / X"
            match = re.match(r"^([^@(]+)", og_title)
            if match:
                return match.group(1).strip()
        
        return og_title
    
    def _extract_bio(self, soup: Any, platform: str) -> Optional[str]:
        """
        Extract bio/description from profile page.
        
        Uses og:description meta tag with platform-specific cleaning.
        
        Args:
            soup: BeautifulSoup object
            platform: Platform ID
        
        Returns:
            str: Bio text or None
        """
        og_description = self._get_og_content(soup, "og:description")
        
        if not og_description:
            # Try regular description meta tag
            og_description = self._get_meta_content(soup, "description")
        
        if not og_description:
            return None
        
        # Platform-specific cleaning
        if platform == "instagram":
            # Instagram format: "X Followers, Y Following, Z Posts - See Instagram..."
            # Try to extract actual bio
            parts = og_description.split(" - ")
            if len(parts) > 1:
                # Skip the follower stats
                bio_part = " - ".join(parts[1:])
                if "See Instagram" not in bio_part:
                    return bio_part.strip()
        
        elif platform == "facebook":
            # Clean up common Facebook suffixes
            bio = og_description.replace("See photos, profile pictures and albums from", "").strip()
            if bio != og_description:
                return None  # This was just the default text
        
        elif platform == "x":
            # X descriptions are usually the actual bio
            pass
        
        return og_description
    
    def _extract_profile_image(self, soup: Any, platform: str) -> Optional[str]:
        """
        Extract profile image URL from profile page.
        
        Uses og:image meta tag.
        
        Args:
            soup: BeautifulSoup object
            platform: Platform ID
        
        Returns:
            str: Profile image URL or None
        """
        return self._get_og_content(soup, "og:image")
    
    def _extract_location(self, soup: Any, platform: str) -> Optional[str]:
        """
        Extract location from profile page.
        
        Tries various meta tags and HTML elements for location data.
        
        Args:
            soup: BeautifulSoup object
            platform: Platform ID
        
        Returns:
            str: Location or None
        """
        # Try og:locality
        location = self._get_og_content(soup, "og:locality")
        if location:
            return location
        
        # Try og:region
        region = self._get_og_content(soup, "og:region")
        if region:
            return region
        
        # Try profile:location
        profile_location = self._get_og_content(soup, "profile:location")
        if profile_location:
            return profile_location
        
        # Platform-specific location extraction could be added here
        # Most platforms don't expose location in meta tags
        
        return None


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

_default_collector = SocialMediaDataCollector()


async def collect_profile_data(url: str, platform: str) -> Dict[str, Any]:
    """Module-level convenience function for profile data collection."""
    return await _default_collector.collect_profile_data(url, platform)
