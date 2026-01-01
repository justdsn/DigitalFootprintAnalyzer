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

import json
import logging
from typing import Dict, Any

from .profile_parser import ProfileParser

logger = logging.getLogger(__name__)


class InstagramParser(ProfileParser):
    """Instagram profile HTML parser."""
    
    def get_platform_name(self) -> str:
        """Get platform name."""
        return "instagram"
    
    def _extract_json_ld(self, soup) -> Dict[str, Any]:
        """
        Extract Instagram's JSON-LD structured data.
        
        Instagram embeds comprehensive profile data in JSON-LD format.
        This is MORE reliable than Open Graph meta tags.
        
        Args:
            soup: BeautifulSoup object
        
        Returns:
            Dict with extracted JSON-LD data
        """
        json_ld_data = {}
        
        try:
            # Find JSON-LD script tags
            scripts = soup.find_all('script', type='application/ld+json')
            
            for script in scripts:
                if script.string:
                    try:
                        data = json.loads(script.string)
                        
                        # Check if it's a ProfilePage
                        if isinstance(data, dict) and data.get('@type') == 'ProfilePage':
                            json_ld_data['name'] = data.get('name')
                            json_ld_data['identifier'] = data.get('identifier')  # username
                            json_ld_data['description'] = data.get('description')  # bio
                            
                            # Extract follower count
                            interaction = data.get('interactionStatistic', {})
                            if isinstance(interaction, dict):
                                json_ld_data['followers'] = interaction.get('userInteractionCount')
                            
                            logger.info(f"Extracted JSON-LD data: {json_ld_data}")
                            break
                            
                    except json.JSONDecodeError as e:
                        logger.debug(f"Failed to parse JSON-LD: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Error extracting JSON-LD: {e}")
        
        return json_ld_data
    
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
            # PRIORITY 1: Extract from JSON-LD (most reliable)
            json_ld_data = self._extract_json_ld(soup)
            if json_ld_data:
                profile["name"] = json_ld_data.get("name") or profile["name"]
                profile["username"] = json_ld_data.get("identifier") or profile["username"]
                profile["bio"] = json_ld_data.get("description") or profile["bio"]
                profile["followers"] = json_ld_data.get("followers") or profile["followers"]
                logger.info(f"✅ Extracted from JSON-LD: {profile['username']}")
            
            # PRIORITY 2: Extract from Open Graph (fallback)
            if not profile["name"]:
                profile["name"] = self.extract_meta_content(soup, "og:title")
            
            if not profile["bio"]:
                profile["bio"] = self.extract_meta_content(soup, "og:description")
            
            # PRIORITY 3: Extract from page content (last resort)
            if not profile["username"]:
                og_url = self.extract_meta_content(soup, "og:url")
                if og_url:
                    parts = og_url.rstrip('/').split('/')
                    if parts:
                        profile["username"] = parts[-1]
            
            # Extract URLs from bio text
            if profile["bio"]:
                bio_urls = self.extract_urls_from_text(profile["bio"])
                profile["urls"].extend(bio_urls)
            
            # Extract URLs from HTML links
            html_urls = self.extract_urls(soup)
            profile["urls"].extend(html_urls)
            
            # Deduplicate URLs
            profile["urls"] = list(set(profile["urls"]))
            
            logger.info(f"✅ Parsed Instagram profile: @{profile['username']} - {profile['name']}")
            
        except Exception as e:
            logger.error(f"Error parsing Instagram HTML: {e}")
        
        return profile
