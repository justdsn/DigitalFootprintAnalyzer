# =============================================================================
# FACEBOOK PARSER
# =============================================================================
# Parse Facebook profile HTML to extract structured data.
# =============================================================================

"""
Facebook Parser

Extracts profile data from Facebook HTML.
"""

import logging
from typing import Dict, Any

from .profile_parser import ProfileParser

logger = logging.getLogger(__name__)


class FacebookParser(ProfileParser):
    """Facebook profile HTML parser."""
    
    def get_platform_name(self) -> str:
        """Get platform name."""
        return "facebook"
    
    def parse(self, html: str) -> Dict[str, Any]:
        """
        Parse Facebook profile HTML.
        
        Args:
            html: HTML content
        
        Returns:
            Extracted profile data
        """
        soup = self.parse_html(html)
        
        profile = {
            "platform": "facebook",
            "name": None,
            "username": None,
            "bio": None,
            "followers": None,
            "following": None,
            "location": None,
            "urls": [],
            "job_title": None,
            "metadata": {}
        }
        
        try:
            # Extract from Open Graph meta tags
            profile["name"] = self.extract_meta_content(soup, "og:title")
            profile["bio"] = self.extract_meta_content(soup, "og:description")
            
            # Extract username from URL
            og_url = self.extract_meta_content(soup, "og:url")
            if og_url:
                parts = og_url.rstrip('/').split('/')
                if parts:
                    profile["username"] = parts[-1]
            
            # Extract URLs
            profile["urls"] = self.extract_urls(soup)
            
            logger.info(f"Parsed Facebook profile: {profile['username']}")
            
        except Exception as e:
            logger.error(f"Error parsing Facebook HTML: {e}")
        
        return profile
