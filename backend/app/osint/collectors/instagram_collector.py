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

import asyncio
import logging
from typing import Dict, Any

from .base_collector import BaseCollector

logger = logging.getLogger(__name__)


# =============================================================================
# INSTAGRAM COLLECTOR CLASS
# =============================================================================

class InstagramCollector(BaseCollector):
    """
    Instagram profile data collector using Playwright with anti-bot/stealth features.
    """

    def __init__(self, session_manager=None, user_agent=None, proxy=None):
        super().__init__(session_manager=session_manager, user_agent=user_agent, proxy=proxy)

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
            "error": None,
            "requires_login": False
        }
        
        try:
            # Navigate to profile with random delay (anti-bot)
            success = await self.navigate_to_url(url, min_delay=2.0, max_delay=5.0)
            if not success:
                result["error"] = "Navigation failed"
                return result

            # Wait for page to fully load
            await asyncio.sleep(3)

            # Check for login wall (but don't fail immediately)
            has_login_wall = await self.check_login_wall()
            if has_login_wall:
                logger.warning(f"Login wall detected for {url} - attempting to extract anyway")
                result["requires_login"] = True
                # DON'T return here - try to extract what we can!

            # Extract HTML (even if login wall present)
            html = await self.get_page_html()
            if not html:
                result["error"] = "Failed to extract HTML"
                return result

            result["html"] = html

            # Extract text blocks
            text_blocks = await self.extract_text_blocks()
            result["text_blocks"] = text_blocks

            result["success"] = True
            logger.info(f"✅ Successfully collected data from {url}")

        except Exception as e:
            logger.error(f"❌ Error collecting from Instagram {url}: {e}")
            result["error"] = str(e)

        return result
