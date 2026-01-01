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
from typing import Dict, Any, Optional, List
import asyncio
import logging
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError

from app.core.config import settings
import random
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
        user_agent: User-Agent string for this session
        proxy: Proxy server (if any)
    """
    # List of common user agents (can be expanded)
    USER_AGENTS: List[str] = [
        # Chrome Win10
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Firefox Win10
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        # Edge Win10
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        # Mac Safari
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        # Linux Chrome
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def __init__(self, session_manager: Optional[SessionManager] = None, user_agent: Optional[str] = None, proxy: Optional[str] = None):
        """
        Initialize the base collector with anti-bot/stealth options.
        Args:
            session_manager: Optional SessionManager instance
            user_agent: Optional user-agent string (random if None)
            proxy: Optional proxy server (e.g., 'http://user:pass@host:port')
        """
        self.session_manager = session_manager or SessionManager()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.user_agent = user_agent or random.choice(self.USER_AGENTS)
        self.proxy = proxy
    
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
        
        Raises:
            RuntimeError: If browser fails to initialize
        """
        platform = self.get_platform_name()
        
        try:
            logger.info(f"[{platform}] Initializing Playwright browser...")
            
            # Load session if exists
            storage_state = self.session_manager.load_session(platform)
            
            playwright = await async_playwright().start()
            
            # Launch browser with stealthy args
            launch_args = {
                "headless": settings.OSINT_BROWSER_HEADLESS,
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                ]
            }
            if self.proxy:
                launch_args["proxy"] = {"server": self.proxy}

            logger.info(f"[{platform}] Launching Chromium browser...")
            self.browser = await playwright.chromium.launch(**launch_args)

            # Context options for stealth
            context_args = {
                "user_agent": self.user_agent,
                "viewport": {"width": 1280, "height": 800},
                "java_script_enabled": True,
            }
            if storage_state:
                logger.info(f"[{platform}] Loading session for authenticated access")
                context_args["storage_state"] = storage_state
            else:
                logger.warning(f"[{platform}] No session available, using anonymous mode")

            self.context = await self.browser.new_context(**context_args)
            self.context.set_default_timeout(settings.OSINT_BROWSER_TIMEOUT)
            self.page = await self.context.new_page()

            # Apply stealth patches
            await self._apply_stealth(self.page)

            logger.info(f"✅ [{platform}] Browser initialized successfully")

        except Exception as e:
            logger.error(f"❌ [{platform}] Browser initialization failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {str(e)}")
            
            # Clean up partial initialization
            try:
                if self.page:
                    await self.page.close()
                if self.context:
                    await self.context.close()
                if self.browser:
                    await self.browser.close()
            except Exception:
                pass
            
            # Re-raise with more context
            raise RuntimeError(
                f"Failed to initialize Playwright browser for {platform}. "
                f"Error: {type(e).__name__}: {str(e)}. "
                "This may be due to Python 3.13 compatibility issues or missing browser installation. "
                "Try: playwright install chromium"
            ) from e

    async def _apply_stealth(self, page: Page):
        """
        Apply manual stealth patches to evade bot detection.
        """
        try:
            # Remove webdriver property
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            # Fake plugins and languages
            await page.add_init_script("Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]})")
            await page.add_init_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            # Fake chrome object
            await page.add_init_script("window.chrome = { runtime: {} }")
            # WebGL vendor spoof
            await page.add_init_script("const getParameter = WebGLRenderingContext.prototype.getParameter; WebGLRenderingContext.prototype.getParameter = function(parameter) { if (parameter === 37445) { return 'Intel Inc.'; } if (parameter === 37446) { return 'Intel Iris OpenGL Engine'; } return getParameter(parameter); }")
            # Audio spoof
            await page.add_init_script("const getChannelData = AudioBuffer.prototype.getChannelData; AudioBuffer.prototype.getChannelData = function() { const results = getChannelData.apply(this, arguments); for (let i = 0; i < results.length; ++i) { results[i] = results[i] + 0.0000001; } return results; }")
        except Exception as e:
            logger.warning(f"Stealth patch failed: {e}")
    
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
    
    async def navigate_to_url(self, url: str, wait_for_selector: Optional[str] = None, min_delay: float = 1.0, max_delay: float = 3.0) -> bool:
        """
        Navigate to a URL and optionally wait for a selector.
        
        Args:
            url: URL to navigate to
            wait_for_selector: CSS selector to wait for (optional)
            min_delay: Minimum random delay after navigation (seconds)
            max_delay: Maximum random delay after navigation (seconds)
        
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
            
            # Add random delay to ensure content is loaded and evade bot detection
            delay = random.uniform(min_delay, max_delay)
            await asyncio.sleep(delay)
            logger.debug(f"Randomized delay after navigation: {delay:.2f}s")
            
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
                except Exception:
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
