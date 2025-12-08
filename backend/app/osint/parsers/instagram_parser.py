# =============================================================================
# INSTAGRAM PARSER
# =============================================================================
# Parse Instagram profile HTML to extract structured data.
# =============================================================================

"""
Instagram Parser

Extracts profile data from Instagram HTML using BeautifulSoup and
Open Graph meta tags.
"""

import logging
from typing import Dict, Any

from .profile_parser import ProfileParser

logger = logging.getLogger(__name__)


class InstagramParser(ProfileParser):
    """Instagram profile HTML parser."""
    
    def get_platform_name(self) -> str:
        """Get platform name."""
        return "instagram"
    
    def parse(self, html: str) -> Dict[str, Any]:
        """
        Parse Instagram profile HTML.
        
        Args:
            html: HTML content
        
        Returns:
            Extracted profile data
        """
        soup = self.parse_html(html)
        
        profile = {
            "platform": "instagram",
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
            profile["username"] = self.extract_meta_content(soup, "instapp:owner_user_id")
            
            # Try alternative username extraction
            if not profile["username"]:
                og_url = self.extract_meta_content(soup, "og:url")
                if og_url:
                    parts = og_url.rstrip('/').split('/')
                    if parts:
                        profile["username"] = parts[-1]
            
            # Extract follower/following counts from bio or structured data
            bio_text = profile["bio"] or ""
            if "follower" in bio_text.lower():
                profile["followers"] = self.extract_number_from_text(bio_text)
            
            # Extract URLs
            profile["urls"] = self.extract_urls(soup)
            
            logger.info(f"Parsed Instagram profile: {profile['username']}")
            
        except Exception as e:
            logger.error(f"Error parsing Instagram HTML: {e}")
        
        return profile
