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
            username: Username or identifier (can be full name with spaces)
        
        Returns:
            Profile URL
        """
        platform = platform.lower()
        
        # Clean username
        username = username.lstrip('@').strip()
        
        if platform not in URLGenerator.PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # Special handling when username contains spaces (full name)
        if ' ' in username:
            if platform == "facebook":
                # For Facebook, use search URL with full name
                encoded_name = username.replace(' ', '+')
                return f"https://www.facebook.com/search/people/?q={encoded_name}"
            elif platform == "linkedin":
                # For LinkedIn, use search URL with full name
                encoded_name = username.replace(' ', '+')
                return f"https://www.linkedin.com/search/results/people/?keywords={encoded_name}"
            elif platform in ["twitter", "x"]:
                # For X/Twitter, use search URL with full name
                encoded_name = username.replace(' ', '+')
                return f"https://x.com/search?q={encoded_name}&f=user"
            # For Instagram, the orchestrator will use search_and_collect instead
            # For other platforms with spaces, convert to possible username format
            else:
                # Try converting "first last" to "firstlast" or "first.last"
                username = username.replace(' ', '')
        
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
    
    @staticmethod
    def generate_search_url(platform: str, query: str) -> str:
        """
        Generate a search URL to find multiple profiles.
        
        Use this to find impersonation accounts and similar profiles.
        
        Args:
            platform: Platform name (lowercase)
            query: Search query
        
        Returns:
            Search URL for the platform
        
        Raises:
            ValueError: If platform doesn't support search
        """
        platform = platform.lower()
        query = query.strip()
        
        SEARCH_URLS = {
            "instagram": f'https://www.google.com/search?q=site:instagram.com+"{query}"',
            "facebook": f'https://www.facebook.com/search/people/?q={query.replace(" ", "+")}',
            "linkedin": f'https://www.linkedin.com/search/results/people/?keywords={query.replace(" ", "+")}',
            "twitter": f'https://x.com/search?q={query.replace(" ", "+")}&f=user',
            "x": f'https://x.com/search?q={query.replace(" ", "+")}&f=user'
        }
        
        if platform not in SEARCH_URLS:
            raise ValueError(f"Search not supported for platform: {platform}")
        
        return SEARCH_URLS[platform]
