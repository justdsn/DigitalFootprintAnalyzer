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

    async def search_profile(self, identifier: str) -> str:
        """
        Search for a profile using Instagram's search UI.
        
        Args:
            identifier: Search term (name or username)
            
        Returns:
            URL of the best matching profile, or None if not found
        """
        if not self.page:
            logger.error("Page not initialized")
            return None
            
        try:
            logger.info(f"🔎 Converting identifier '{identifier}' to profile URL via Search...")
            
            # Go to home page first
            await self.navigate_to_url("https://www.instagram.com/", min_delay=2.0)
            await asyncio.sleep(3)  # Wait for page to fully load
            
            # Take screenshot for debugging
            try:
                await self.page.screenshot(path="debug_instagram_home.png")
                logger.info("📸 Saved debug screenshot of Instagram home")
            except:
                pass
            
            # Updated search selectors for Instagram's current UI (2025-2026)
            # Instagram uses various selectors depending on viewport and version
            search_selectors = [
                # Primary: SVG with Search aria-label
                'svg[aria-label="Search"]',
                # Parent link containing Search SVG
                'a:has(svg[aria-label="Search"])',
                # Span containing "Search" text in sidebar
                'span:text("Search")',
                # Navigation link with Search
                'a[href="#"]:has-text("Search")',
                # Div role="button" approach
                'div[role="button"]:has-text("Search")',
                # Generic clickable search area
                '[data-testid="search"]',
                # Mobile/responsive search icon
                'a[aria-label="Search"]',
                # Newer Instagram UI patterns
                'div[class*="search"] svg',
                'nav svg[aria-label="Search"]',
                # Fallback: any element with Search text
                ':text("Search"):visible'
            ]
            
            search_clicked = False
            for selector in search_selectors:
                try:
                    logger.debug(f"Trying search selector: {selector}")
                    element = await self.page.wait_for_selector(selector, timeout=2000, state="visible")
                    if element:
                        await element.click()
                        search_clicked = True
                        logger.info(f"✅ Clicked search using selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not search_clicked:
                # Fallback: Try keyboard shortcut
                logger.warning("Could not click search icon, trying keyboard shortcut...")
                try:
                    await self.page.keyboard.press("Control+k")
                    await asyncio.sleep(1)
                    # Check if search opened
                    search_input = await self.page.query_selector('input[placeholder*="Search"], input[aria-label*="Search"]')
                    if search_input:
                        search_clicked = True
                        logger.info("✅ Opened search via keyboard shortcut")
                except:
                    pass
            
            if not search_clicked:
                # Last resort: Navigate directly to search URL pattern
                logger.warning("All search methods failed. Taking debug screenshot...")
                try:
                    await self.page.screenshot(path="debug_search_failed.png")
                except:
                    pass
                raise RuntimeError("Could not find/click Search icon - Instagram UI may have changed")
            
            # Wait for search drawer/modal animation
            await asyncio.sleep(2)
            
            # Updated input selectors for current Instagram
            input_selectors = [
                'input[aria-label="Search input"]',
                'input[placeholder="Search"]',
                'input[type="text"][placeholder*="Search"]',
                'input[autocomplete="off"]',
                'input[class*="search"]',
                'input[name="search"]',
                # Generic visible text input after search opens
                'input[type="text"]:visible'
            ]
            
            search_input = None
            for selector in input_selectors:
                try:
                    search_input = await self.page.wait_for_selector(selector, timeout=3000, state="visible")
                    if search_input:
                        logger.info(f"✅ Found search input: {selector}")
                        break
                except:
                    continue
            
            if not search_input:
                logger.error("Search input not found after clicking search icon")
                try:
                    await self.page.screenshot(path="debug_no_input.png")
                except:
                    pass
                raise RuntimeError("Search input not visible")
            
            # Clear any existing text and type the identifier
            await search_input.fill("")
            await asyncio.sleep(0.5)
            
            # Type slowly to trigger autocomplete
            await search_input.type(identifier, delay=100)
            logger.info(f"Typed '{identifier}' into search")
            
            # Wait for search results to load
            await asyncio.sleep(4)
            
            # Take screenshot of search results
            try:
                await self.page.screenshot(path="debug_search_results.png")
                logger.info("📸 Saved debug screenshot of search results")
            except:
                pass
            
            # Updated result extraction for current Instagram UI
            profile_url = await self.page.evaluate("""
                () => {
                    // Method 1: Look for search result links in the search panel
                    // Instagram search results typically appear in a specific container
                    const searchResults = document.querySelectorAll('a[href^="/"]');
                    
                    // Reserved paths to exclude
                    const reserved = [
                        'explore', 'direct', 'reels', 'stories', 'p', 'tv', 'reel', 
                        'tags', 'locations', 'api', 'static', 'legal', 'about', 
                        'instagram', 'accounts', 'emails', 'privacy', 'help', 
                        'session', 'settings', 'nametag', 'web', 'developer'
                    ];
                    
                    for (const link of searchResults) {
                        const href = link.getAttribute('href');
                        if (!href || href === '/') continue;
                        
                        // Clean the href
                        const cleanHref = href.replace(/\\/$/, '');
                        const parts = cleanHref.split('/').filter(p => p);
                        
                        // We want single-segment paths like /username
                        if (parts.length === 1) {
                            const username = parts[0].toLowerCase();
                            
                            // Check if it's a reserved word
                            if (reserved.includes(username)) continue;
                            
                            // Check if it looks like a username (alphanumeric, underscores, dots)
                            if (/^[a-z0-9._]+$/.test(username) && username.length > 1 && username.length < 31) {
                                // Additional check: the link should be visible and in search results area
                                const rect = link.getBoundingClientRect();
                                if (rect.top > 0 && rect.top < window.innerHeight) {
                                    return href;
                                }
                            }
                        }
                    }
                    
                    // Method 2: Look for user profile cards with avatar images
                    const userCards = document.querySelectorAll('[role="link"], [role="button"]');
                    for (const card of userCards) {
                        const anchor = card.closest('a') || card.querySelector('a');
                        if (anchor) {
                            const href = anchor.getAttribute('href');
                            if (href && href.match(/^\\/[a-z0-9._]+\\/?$/i)) {
                                const username = href.replace(/\\//g, '');
                                if (!reserved.includes(username.toLowerCase())) {
                                    return href;
                                }
                            }
                        }
                    }
                    
                    return null;
                }
            """)
            
            if profile_url:
                # Ensure full URL
                if profile_url.startswith('/'):
                    full_url = f"https://www.instagram.com{profile_url}"
                else:
                    full_url = profile_url
                logger.info(f"📍 Search found profile: {full_url}")
                return full_url
            
            # Fallback: Try clicking the first search result directly
            logger.warning("No profile URL found via evaluation, trying direct click...")
            try:
                # Look for clickable search result items
                result_selectors = [
                    'div[role="none"] a[href^="/"]',
                    '[data-testid="user-result"] a',
                    'a[href^="/"]:has(img[alt])',
                    'div[class*="result"] a[href^="/"]'
                ]
                
                for selector in result_selectors:
                    try:
                        result_link = await self.page.wait_for_selector(selector, timeout=2000)
                        if result_link:
                            href = await result_link.get_attribute('href')
                            if href and href.match(r'^/[a-z0-9._]+/?$'):
                                await result_link.click()
                                await asyncio.sleep(2)
                                # Get current URL
                                current_url = self.page.url
                                if '/p/' not in current_url and '/explore/' not in current_url:
                                    logger.info(f"📍 Navigated to profile: {current_url}")
                                    return current_url
                    except:
                        continue
            except Exception as e:
                logger.debug(f"Fallback click failed: {e}")
            
            logger.warning("No valid profile URL found in search results")
            return None

        except Exception as e:
            logger.error(f"Error during search: {e}")
            try:
                await self.page.screenshot(path="debug_search_error.png")
            except:
                pass
            return None

    async def search_and_collect(self, identifier: str) -> Dict[str, Any]:
        """
        Search for a profile then collect its data.
        """
        profile_url = await self.search_profile(identifier)
        if profile_url:
            return await self.collect(profile_url)
        else:
            return {
                "success": False,
                "platform": "instagram",
                "error": "Profile not found via search",
                "input_identifier": identifier
            }

