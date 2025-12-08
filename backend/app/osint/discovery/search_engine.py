# =============================================================================
# SEARCH ENGINE
# =============================================================================
# Google Custom Search API integration for profile discovery.
# =============================================================================

"""
Search Engine

Google Custom Search API integration for discovering social media profiles.
Optional component - requires API key configuration.
"""

import logging
from typing import List, Dict, Any, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class SearchEngine:
    """
    Google Custom Search integration for profile discovery.
    """
    
    def __init__(self, api_key: Optional[str] = None, cse_id: Optional[str] = None):
        """
        Initialize search engine.
        
        Args:
            api_key: Google API key (uses config if not provided)
            cse_id: Custom Search Engine ID (uses config if not provided)
        """
        self.api_key = api_key or settings.GOOGLE_API_KEY
        self.cse_id = cse_id or settings.GOOGLE_CSE_ID
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def is_configured(self) -> bool:
        """
        Check if API is configured.
        
        Returns:
            True if API key and CSE ID are available
        """
        return bool(self.api_key and self.cse_id)
    
    async def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Perform a Google Custom Search.
        
        Args:
            query: Search query
            num_results: Number of results to return (max 10)
        
        Returns:
            List of search results
        """
        if not self.is_configured():
            logger.warning("Google Custom Search API not configured")
            return []
        
        try:
            params = {
                "key": self.api_key,
                "cx": self.cse_id,
                "q": query,
                "num": min(num_results, 10)
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                items = data.get("items", [])
                
                results = []
                for item in items:
                    results.append({
                        "title": item.get("title"),
                        "link": item.get("link"),
                        "snippet": item.get("snippet"),
                        "displayLink": item.get("displayLink")
                    })
                
                return results
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during search: {e}")
            return []
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []
    
    async def search_profiles(self, identifier: str, platforms: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for profiles across specific platforms.
        
        Args:
            identifier: Username, name, or email
            platforms: List of platform names
        
        Returns:
            Dict mapping platform to search results
        """
        results = {}
        
        for platform in platforms:
            query = f'site:{self._get_platform_domain(platform)} "{identifier}"'
            search_results = await self.search(query, num_results=5)
            results[platform] = search_results
        
        return results
    
    @staticmethod
    def _get_platform_domain(platform: str) -> str:
        """
        Get the domain for a platform.
        
        Args:
            platform: Platform name
        
        Returns:
            Domain string
        """
        domains = {
            "instagram": "instagram.com",
            "facebook": "facebook.com",
            "linkedin": "linkedin.com",
            "twitter": "twitter.com",
            "x": "x.com"
        }
        
        return domains.get(platform.lower(), "")
