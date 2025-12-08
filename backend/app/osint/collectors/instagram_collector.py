# =============================================================================
# INSTAGRAM COLLECTOR
# =============================================================================
# Playwright-based collector for Instagram profile data.
# =============================================================================

"""
Instagram Collector

Collects public data from Instagram profiles using Playwright headless browser.

Features:
- Profile HTML extraction
- Bio and metadata collection
- Login wall detection
- Rate limiting and error handling

Example Usage:
    collector = InstagramCollector()
    await collector.initialize_browser()
    result = await collector.collect("https://instagram.com/username")
    await collector.close_browser()
"""

import logging
from typing import Dict, Any

from .base_collector import BaseCollector

logger = logging.getLogger(__name__)


# =============================================================================
# INSTAGRAM COLLECTOR CLASS
# =============================================================================

class InstagramCollector(BaseCollector):
    """
    Instagram profile data collector using Playwright.
    """
    
    def get_platform_name(self) -> str:
        """Get platform name."""
        return "instagram"
    
    async def collect(self, url: str) -> Dict[str, Any]:
        """
        Collect data from an Instagram profile.
        
        Args:
            url: Instagram profile URL
        
        Returns:
            Collection results dict
        """
        result = {
            "success": False,
            "platform": "instagram",
            "url": url,
            "html": None,
            "text_blocks": {},
            "error": None
        }
        
        try:
            # Navigate to profile
            success = await self.navigate_to_url(url)
            if not success:
                result["error"] = "Navigation failed"
                return result
            
            # Check for login wall
            has_login_wall = await self.check_login_wall()
            if has_login_wall:
                logger.warning(f"Login wall detected for {url}")
                result["error"] = "Login wall detected - session may be expired"
                return result
            
            # Extract HTML
            html = await self.get_page_html()
            if not html:
                result["error"] = "Failed to extract HTML"
                return result
            
            result["html"] = html
            
            # Extract text blocks
            text_blocks = await self.extract_text_blocks()
            result["text_blocks"] = text_blocks
            
            result["success"] = True
            logger.info(f"Successfully collected data from {url}")
            
        except Exception as e:
            logger.error(f"Error collecting from Instagram {url}: {e}")
            result["error"] = str(e)
        
        return result
