# =============================================================================
# LINKEDIN PARSER
# =============================================================================
# Parse LinkedIn profile HTML to extract structured data.
# =============================================================================

"""
LinkedIn Parser

Extracts profile data from LinkedIn HTML.
"""

import logging
from typing import Dict, Any

from .profile_parser import ProfileParser

logger = logging.getLogger(__name__)


class LinkedInParser(ProfileParser):
    """LinkedIn profile HTML parser."""
    
    def get_platform_name(self) -> str:
        """Get platform name."""
        return "linkedin"
    
    def parse(self, html: str) -> Dict[str, Any]:
        """
        Parse LinkedIn profile HTML.
        
        Args:
            html: HTML content
        
        Returns:
            Extracted profile data
        """
        soup = self.parse_html(html)
        
        profile = {
            "platform": "linkedin",
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
            
            # Try to extract job title from title
            title = profile["name"]
            if title and " - " in title:
                parts = title.split(" - ")
                profile["name"] = parts[0].strip()
                profile["job_title"] = parts[1].strip() if len(parts) > 1 else None
            
            # Extract username from URL
            og_url = self.extract_meta_content(soup, "og:url")
            if og_url:
                parts = og_url.rstrip('/').split('/')
                if 'in' in parts:
                    idx = parts.index('in')
                    if idx + 1 < len(parts):
                        profile["username"] = parts[idx + 1]
            
            # Extract URLs
            profile["urls"] = self.extract_urls(soup)
            
            logger.info(f"Parsed LinkedIn profile: {profile['username']}")
            
        except Exception as e:
            logger.error(f"Error parsing LinkedIn HTML: {e}")
        
        return profile
