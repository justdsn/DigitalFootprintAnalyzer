# =============================================================================
# BASE COLLECTOR
# =============================================================================
# Abstract base class for all platform-specific collectors.
# =============================================================================

"""
Base Collector

Abstract base class that defines the interface for all platform collectors.
Handles common Playwright operations like browser initialization, navigation,
and error handling.

Features:
- Playwright browser management
- Persistent session loading
- Rate limiting and retry logic
- Error handling and logging
- HTML extraction

Example Usage:
    class MyCollector(BaseCollector):
        def get_platform_name(self) -> str:
            return "myplatform"
        
        async def collect(self, url: str) -> Dict[str, Any]:
            # Implementation
            pass
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
import logging
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError

from app.core.config import settings
from app.osint.session_manager import SessionManager

logger = logging.getLogger(__name__)


# =============================================================================
# BASE COLLECTOR CLASS
# =============================================================================

class BaseCollector(ABC):
    """
    Abstract base class for platform-specific collectors.
    
    All platform collectors must inherit from this class and implement
    the abstract methods.
    
    Attributes:
        session_manager: Session manager instance
        browser: Playwright browser instance
        context: Browser context with session
        page: Current page
    """
    
    def __init__(self, session_manager: Optional[SessionManager] = None):
        """
        Initialize the base collector.
        
        Args:
            session_manager: Optional SessionManager instance
        """
        self.session_manager = session_manager or SessionManager()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """
        Get the platform name for this collector.
        
        Returns:
            Platform name (lowercase)
        """
        pass
    
    async def initialize_browser(self) -> None:
        """
        Initialize Playwright browser with session if available.
        """
        platform = self.get_platform_name()
        
        try:
            # Load session if exists
            storage_state = self.session_manager.load_session(platform)
            
            playwright = await async_playwright().start()
            
            # Launch browser
            self.browser = await playwright.chromium.launch(
                headless=settings.OSINT_BROWSER_HEADLESS
            )
            
            # Create context with or without session
            if storage_state:
                logger.info(f"Loading session for {platform}")
                self.context = await self.browser.new_context(
                    storage_state=storage_state
                )
            else:
                logger.warning(f"No session available for {platform}, using anonymous mode")
                self.context = await self.browser.new_context()
            
            # Set timeout
            self.context.set_default_timeout(settings.OSINT_BROWSER_TIMEOUT)
            
            # Create page
            self.page = await self.context.new_page()
            
            logger.info(f"Browser initialized for {platform}")
            
        except Exception as e:
            logger.error(f"Error initializing browser for {platform}: {e}")
            raise
    
    async def close_browser(self) -> None:
        """
        Close browser and cleanup resources.
        """
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            
            logger.info(f"Browser closed for {self.get_platform_name()}")
            
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    async def navigate_to_url(self, url: str, wait_for_selector: Optional[str] = None) -> bool:
        """
        Navigate to a URL and optionally wait for a selector.
        
        Args:
            url: URL to navigate to
            wait_for_selector: CSS selector to wait for (optional)
        
        Returns:
            True if navigation successful, False otherwise
        """
        if not self.page:
            logger.error("Page not initialized")
            return False
        
        try:
            # Navigate to URL
            await self.page.goto(url, wait_until="domcontentloaded")
            logger.info(f"Navigated to {url}")
            
            # Wait for specific selector if provided
            if wait_for_selector:
                await self.page.wait_for_selector(wait_for_selector, timeout=10000)
                logger.info(f"Selector found: {wait_for_selector}")
            
            # Add small delay to ensure content is loaded
            await asyncio.sleep(settings.OSINT_RATE_LIMIT_DELAY)
            
            return True
            
        except PlaywrightTimeoutError:
            logger.warning(f"Timeout navigating to {url}")
            return False
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            return False
    
    async def get_page_html(self) -> Optional[str]:
        """
        Get the complete HTML content of the current page.
        
        Returns:
            HTML content as string, or None if error
        """
        if not self.page:
            logger.error("Page not initialized")
            return None
        
        try:
            html = await self.page.content()
            return html
        except Exception as e:
            logger.error(f"Error getting page HTML: {e}")
            return None
    
    async def extract_text_blocks(self) -> Dict[str, Any]:
        """
        Extract visible text blocks from the page.
        
        Returns:
            Dict with extracted text elements
        """
        if not self.page:
            logger.error("Page not initialized")
            return {}
        
        try:
            # Extract visible text from common elements
            text_data = await self.page.evaluate("""
                () => {
                    const getText = (selector) => {
                        const elements = document.querySelectorAll(selector);
                        return Array.from(elements).map(el => el.textContent.trim()).filter(t => t.length > 0);
                    };
                    
                    return {
                        headings: getText('h1, h2, h3'),
                        paragraphs: getText('p'),
                        spans: getText('span'),
                        divs: getText('div[class*="bio"], div[class*="description"], div[class*="about"]')
                    };
                }
            """)
            
            return text_data
            
        except Exception as e:
            logger.error(f"Error extracting text blocks: {e}")
            return {}
    
    async def check_login_wall(self) -> bool:
        """
        Check if the page shows a login wall.
        
        Returns:
            True if login wall detected, False otherwise
        """
        if not self.page:
            return False
        
        try:
            # Common login wall indicators
            login_indicators = [
                'text="Log In"',
                'text="Sign In"',
                'text="Login"',
                'text="Sign Up"',
                '[data-testid="loginButton"]',
                '[name="login"]',
                'form[action*="login"]'
            ]
            
            for indicator in login_indicators:
                try:
                    element = await self.page.query_selector(indicator)
                    if element:
                        logger.warning(f"Login wall detected: {indicator}")
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking login wall: {e}")
            return False
    
    async def collect_with_retry(self, url: str, max_retries: Optional[int] = None) -> Dict[str, Any]:
        """
        Collect data with retry logic.
        
        Args:
            url: URL to collect from
            max_retries: Max retry attempts (uses config default if None)
        
        Returns:
            Collection results
        """
        max_retries = max_retries or settings.OSINT_MAX_RETRIES
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = await self.collect(url)
                if result.get("success"):
                    return result
                
                logger.warning(f"Collection attempt {attempt + 1} failed for {url}")
                last_error = result.get("error", "Unknown error")
                
                # Wait before retry
                if attempt < max_retries - 1:
                    await asyncio.sleep(settings.OSINT_RETRY_DELAY * (attempt + 1))
                    
            except Exception as e:
                logger.error(f"Collection attempt {attempt + 1} error for {url}: {e}")
                last_error = str(e)
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(settings.OSINT_RETRY_DELAY * (attempt + 1))
        
        return {
            "success": False,
            "error": f"Max retries exceeded: {last_error}",
            "platform": self.get_platform_name(),
            "url": url
        }
    
    @abstractmethod
    async def collect(self, url: str) -> Dict[str, Any]:
        """
        Collect data from a profile URL.
        
        Must be implemented by each platform collector.
        
        Args:
            url: Profile URL to collect from
        
        Returns:
            Dict with collection results:
            {
                "success": bool,
                "platform": str,
                "url": str,
                "html": str (if successful),
                "text_blocks": dict (if successful),
                "error": str (if failed)
            }
        """
        pass
