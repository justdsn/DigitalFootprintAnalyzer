# =============================================================================
# TWITTER/X PARSER
# =============================================================================
# Parse Twitter/X profile HTML to extract structured data.
# =============================================================================

"""
Twitter/X Parser

Extracts profile data from X (Twitter) HTML.
"""

import logging
from typing import Dict, Any

from .profile_parser import ProfileParser

logger = logging.getLogger(__name__)


class TwitterParser(ProfileParser):
    """Twitter/X profile HTML parser."""
    
    def get_platform_name(self) -> str:
        """Get platform name."""
        return "twitter"
    
    def parse(self, html: str) -> Dict[str, Any]:
        """
        Parse Twitter/X profile HTML.
        
        Args:
            html: HTML content
        
        Returns:
            Extracted profile data
        """
        soup = self.parse_html(html)
        
        profile = {
            "platform": "twitter",
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
            
            # Extract username
            twitter_creator = self.extract_meta_content(soup, "twitter:creator")
            if twitter_creator:
                profile["username"] = twitter_creator.lstrip('@')
            
            # Alternative: from URL
            if not profile["username"]:
                og_url = self.extract_meta_content(soup, "og:url")
                if og_url:
                    parts = og_url.rstrip('/').split('/')
                    if parts:
                        profile["username"] = parts[-1]
            
            # Extract URLs
            profile["urls"] = self.extract_urls(soup)
            
            logger.info(f"Parsed Twitter profile: {profile['username']}")
            
        except Exception as e:
            logger.error(f"Error parsing Twitter HTML: {e}")
        
        return profile
