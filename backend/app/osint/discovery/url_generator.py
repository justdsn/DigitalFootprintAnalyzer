# =============================================================================
# URL GENERATOR
# =============================================================================
# Generates profile URLs for supported platforms.
# =============================================================================

"""
URL Generator

Generates profile URLs for Instagram, Facebook, LinkedIn, and X (Twitter)
based on username or identifier.
"""

from typing import Dict, List


class URLGenerator:
    """
    Generate profile URLs for supported platforms.
    """
    
    PLATFORMS = {
        "instagram": "https://www.instagram.com/{username}/",
        "facebook": "https://www.facebook.com/{username}",
        "linkedin": "https://www.linkedin.com/in/{username}/",
        "twitter": "https://twitter.com/{username}",
        "x": "https://x.com/{username}",
    }
    
    @staticmethod
    def generate_url(platform: str, username: str) -> str:
        """
        Generate a profile URL for a specific platform.
        
        Args:
            platform: Platform name (lowercase)
            username: Username or identifier
        
        Returns:
            Profile URL
        """
        platform = platform.lower()
        
        # Clean username
        username = username.lstrip('@').strip()
        
        if platform not in URLGenerator.PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return URLGenerator.PLATFORMS[platform].format(username=username)
    
    @staticmethod
    def generate_all_urls(username: str) -> Dict[str, str]:
        """
        Generate profile URLs for all supported platforms.
        
        Args:
            username: Username or identifier
        
        Returns:
            Dict mapping platform name to URL
        """
        urls = {}
        for platform in URLGenerator.PLATFORMS:
            try:
                urls[platform] = URLGenerator.generate_url(platform, username)
            except ValueError:
                pass
        
        return urls
    
    @staticmethod
    def generate_username_variations(username: str) -> List[str]:
        """
        Generate common username variations.
        
        Args:
            username: Base username
        
        Returns:
            List of username variations
        """
        username = username.strip().lower()
        
        variations = [username]
        
        # Underscore variations
        if '_' in username:
            variations.append(username.replace('_', ''))
            variations.append(username.replace('_', '.'))
        else:
            variations.append(f"{username}_")
            variations.append(f"_{username}")
        
        # Dot variations
        if '.' in username:
            variations.append(username.replace('.', ''))
            variations.append(username.replace('.', '_'))
        
        # Common numeric suffixes
        for num in ['1', '123', '007', '21']:
            variations.append(f"{username}{num}")
        
        # Deduplicate and return
        return list(set(variations))
