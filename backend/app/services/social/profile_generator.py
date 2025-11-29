# =============================================================================
# PROFILE URL GENERATOR SERVICE
# =============================================================================
# Generates direct profile URLs for major social media platforms.
# Designed for Sri Lanka-focused OSINT digital footprint analysis.
# =============================================================================

"""
Profile URL Generator Service

This module generates direct profile URLs for social media platforms:
- Facebook
- Instagram
- LinkedIn
- X (Twitter)

Features:
- Generate direct profile URLs for a username across all platforms
- Generate username variations for impersonation detection
- Clean and normalize usernames

Example Usage:
    generator = ProfileURLGenerator()
    urls = generator.generate_urls("john_doe")
    # Returns URLs for all supported platforms
    
    variations = generator.generate_variations("john_doe")
    # Returns variations with URLs for each platform
"""

import re
from typing import Dict, List, Optional


class ProfileURLGenerator:
    """
    Generate social media profile URLs for usernames.
    
    This class provides methods to:
    1. Generate profile URLs for major social media platforms
    2. Create username variations for comprehensive searching
    3. Clean and normalize usernames for URL generation
    
    Attributes:
        PLATFORMS: Dictionary of supported platforms with URL templates
        VARIATION_SUFFIXES: List of common number suffixes for variations
    """
    
    # -------------------------------------------------------------------------
    # SUPPORTED PLATFORMS CONFIGURATION
    # -------------------------------------------------------------------------
    PLATFORMS = {
        "facebook": {
            "name": "Facebook",
            "url_template": "https://www.facebook.com/{username}"
        },
        "instagram": {
            "name": "Instagram",
            "url_template": "https://www.instagram.com/{username}/"
        },
        "linkedin": {
            "name": "LinkedIn",
            "url_template": "https://www.linkedin.com/in/{username}"
        },
        "x": {
            "name": "X (Twitter)",
            "url_template": "https://x.com/{username}"
        }
    }
    
    # -------------------------------------------------------------------------
    # VARIATION CONFIGURATION
    # -------------------------------------------------------------------------
    # Common number suffixes used for username variations
    VARIATION_SUFFIXES = ["1", "2", "123", "007"]
    
    def __init__(self):
        """Initialize the Profile URL Generator."""
        pass
    
    def _clean_username(self, username: str) -> str:
        """
        Clean and normalize a username for URL generation.
        
        Removes @ prefix, strips whitespace, and normalizes the username.
        
        Args:
            username: The raw username to clean
        
        Returns:
            str: Cleaned username suitable for URL generation
        
        Example:
            >>> generator._clean_username("@john_doe ")
            'john_doe'
        """
        if not username:
            return ""
        
        # Remove @ prefix if present
        cleaned = username.lstrip('@')
        
        # Strip whitespace
        cleaned = cleaned.strip()
        
        return cleaned
    
    def generate_urls(self, username: str) -> Dict[str, Dict[str, str]]:
        """
        Generate profile URLs for all supported platforms.
        
        Creates direct links to the user's potential profile on each
        major social media platform.
        
        Args:
            username: The username to generate URLs for
        
        Returns:
            Dict[str, Dict[str, str]]: Dictionary with platform IDs as keys,
                containing name and url for each platform
        
        Example:
            >>> generator.generate_urls("john_doe")
            {
                'facebook': {
                    'name': 'Facebook',
                    'url': 'https://www.facebook.com/john_doe'
                },
                'instagram': {
                    'name': 'Instagram',
                    'url': 'https://www.instagram.com/john_doe/'
                },
                ...
            }
        """
        clean_username = self._clean_username(username)
        
        if not clean_username:
            return {}
        
        urls = {}
        for platform_id, platform_info in self.PLATFORMS.items():
            urls[platform_id] = {
                "name": platform_info["name"],
                "url": platform_info["url_template"].format(username=clean_username)
            }
        
        return urls
    
    def generate_url(self, username: str, platform: str) -> Optional[str]:
        """
        Generate a profile URL for a specific platform.
        
        Args:
            username: The username to generate URL for
            platform: Platform ID (facebook, instagram, linkedin, x)
        
        Returns:
            str: Profile URL or None if platform not supported or username empty
        
        Example:
            >>> generator.generate_url("john_doe", "instagram")
            'https://www.instagram.com/john_doe/'
        """
        clean_username = self._clean_username(username)
        
        if not clean_username or platform not in self.PLATFORMS:
            return None
        
        return self.PLATFORMS[platform]["url_template"].format(username=clean_username)
    
    def generate_variations(self, username: str) -> List[Dict]:
        """
        Generate username variations with URLs for each platform.
        
        Creates common variations of the username that might be used
        by impersonators or that users might use across platforms.
        
        Variations include:
        - Original username
        - Without underscores/dots
        - With underscores replaced by dots and vice versa
        - Common number suffixes
        - Leading/trailing underscores
        
        Args:
            username: The original username
        
        Returns:
            List[Dict]: List of dictionaries containing username variations
                        and their URLs across platforms
        
        Example:
            >>> generator.generate_variations("john_doe")
            [
                {'username': 'john_doe', 'urls': {...}},
                {'username': 'johndoe', 'urls': {...}},
                {'username': 'john.doe', 'urls': {...}},
                ...
            ]
        """
        clean_username = self._clean_username(username)
        
        if not clean_username:
            return []
        
        # Generate variations
        variations = set()
        
        # Original
        variations.add(clean_username.lower())
        
        # Remove underscores
        variations.add(clean_username.replace('_', '').lower())
        
        # Remove dots
        variations.add(clean_username.replace('.', '').lower())
        
        # Replace underscores with dots
        variations.add(clean_username.replace('_', '.').lower())
        
        # Replace dots with underscores
        variations.add(clean_username.replace('.', '_').lower())
        
        # Leading underscore
        variations.add(f"_{clean_username.lower()}")
        
        # Trailing underscore
        variations.add(f"{clean_username.lower()}_")
        
        # Common number suffixes (using class constant)
        base = clean_username.replace('_', '').replace('.', '').lower()
        for suffix in self.VARIATION_SUFFIXES:
            variations.add(f"{base}{suffix}")
        
        # Remove empty strings
        variations.discard('')
        
        # Build result with URLs
        result = []
        for variation in sorted(variations):
            result.append({
                "username": variation,
                "urls": self.generate_urls(variation)
            })
        
        return result
    
    def get_supported_platforms(self) -> List[str]:
        """
        Get list of supported platform IDs.
        
        Returns:
            List[str]: List of platform IDs
        """
        return list(self.PLATFORMS.keys())


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

_default_generator = ProfileURLGenerator()


def generate_urls(username: str) -> Dict[str, Dict[str, str]]:
    """Module-level convenience function for URL generation."""
    return _default_generator.generate_urls(username)


def generate_variations(username: str) -> List[Dict]:
    """Module-level convenience function for variation generation."""
    return _default_generator.generate_variations(username)
