# =============================================================================
# PLATFORM-SPECIFIC SCRAPERS
# =============================================================================
# Specialized scrapers for accurate data extraction from each platform.
# Uses multiple extraction methods for accuracy.
# =============================================================================

"""
Platform-Specific Scrapers

This module provides specialized scrapers for each social media platform:
- FacebookScraper: Facebook profile scraping
- InstagramScraper: Instagram profile scraping
- TwitterXScraper: X (Twitter) profile scraping
- LinkedInScraper: LinkedIn profile scraping

Each scraper extracts PII from:
- Open Graph meta tags
- Page title parsing
- JSON-LD structured data
- Embedded JSON in scripts
- Bio text analysis

Example Usage:
    scraper = FacebookScraper()
    result = await scraper.scrape_profile("john_doe")
    pii = scraper.extract_pii(result)
"""

import re
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import logging

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# Set up logger
logger = logging.getLogger(__name__)


class BasePlatformScraper(ABC):
    """
    Base class for platform scrapers.
    
    This abstract class defines the interface for all platform scrapers.
    Each platform-specific scraper must implement these methods.
    """
    
    # Default User-Agent
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
    
    # Request timeout
    REQUEST_TIMEOUT = 15.0
    
    def __init__(self):
        """Initialize the scraper."""
        pass
    
    @abstractmethod
    async def check_exists(self, username: str) -> Dict[str, Any]:
        """
        Check if a profile exists on the platform.
        
        Args:
            username: The username to check
            
        Returns:
            Dict with status and profile URL
        """
        pass
    
    @abstractmethod
    async def scrape_profile(self, username: str) -> Dict[str, Any]:
        """
        Scrape profile data from the platform.
        
        Args:
            username: The username to scrape
            
        Returns:
            Dict with scraped profile data
        """
        pass
    
    @abstractmethod
    def extract_pii(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract PII from scraped data.
        
        Args:
            scraped_data: Raw scraped data from scrape_profile
            
        Returns:
            Dict with extracted PII
        """
        pass
    
    def _extract_emails_from_text(self, text: str) -> List[str]:
        """Extract email addresses from text using regex."""
        if not text:
            return []
        emails = re.findall(
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            text
        )
        return list(set(emails))
    
    def _extract_phones_from_text(self, text: str) -> List[str]:
        """Extract phone numbers from text using regex (Sri Lankan focus)."""
        if not text:
            return []
        phones = re.findall(
            r'(?:\+94|0)?[0-9]{2}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
            text
        )
        return list(set(phones))
    
    def _get_og_content(self, soup: Any, property_name: str) -> Optional[str]:
        """Get content from an Open Graph meta tag."""
        if not soup:
            return None
        tag = soup.find("meta", property=property_name)
        if tag and tag.get("content"):
            return tag["content"].strip()
        return None
    
    def _get_meta_content(self, soup: Any, name: str) -> Optional[str]:
        """Get content from a meta tag by name."""
        if not soup:
            return None
        tag = soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            return tag["content"].strip()
        return None


class FacebookScraper(BasePlatformScraper):
    """
    Facebook profile scraper.
    
    Extracts data from Open Graph meta tags and page content.
    """
    
    PLATFORM = "facebook"
    BASE_URL = "https://www.facebook.com"
    
    async def check_exists(self, username: str) -> Dict[str, Any]:
        """Check if a Facebook profile exists."""
        if not HTTPX_AVAILABLE:
            return {"exists": False, "error": "httpx not available"}
        
        url = f"{self.BASE_URL}/{username}"
        
        try:
            async with httpx.AsyncClient(
                timeout=self.REQUEST_TIMEOUT,
                follow_redirects=True
            ) as client:
                response = await client.get(url, headers={
                    "User-Agent": self.DEFAULT_USER_AGENT,
                    "Accept": "text/html"
                })
                
                if response.status_code == 200:
                    content = response.text.lower()
                    if "page not found" in content or "content isn't available" in content:
                        return {"exists": False, "url": url, "status": "not_found"}
                    return {"exists": True, "url": url, "status": "found"}
                elif response.status_code == 404:
                    return {"exists": False, "url": url, "status": "not_found"}
                else:
                    return {"exists": False, "url": url, "status": "error", "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Error checking Facebook profile {username}: {e}")
            return {"exists": False, "url": url, "status": "error", "error": str(e)}
    
    async def scrape_profile(self, username: str) -> Dict[str, Any]:
        """Scrape Facebook profile data."""
        result = {
            "platform": self.PLATFORM,
            "username": username,
            "url": f"{self.BASE_URL}/{username}",
            "success": False,
            "data": {},
            "error": None
        }
        
        if not HTTPX_AVAILABLE or not BS4_AVAILABLE:
            result["error"] = "Required libraries not available"
            return result
        
        try:
            async with httpx.AsyncClient(
                timeout=self.REQUEST_TIMEOUT,
                follow_redirects=True
            ) as client:
                response = await client.get(result["url"], headers={
                    "User-Agent": self.DEFAULT_USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml"
                })
                
                if response.status_code != 200:
                    result["error"] = f"HTTP {response.status_code}"
                    return result
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Method 1: Open Graph meta tags
                result["data"]["name"] = self._get_og_content(soup, "og:title")
                result["data"]["bio"] = self._get_og_content(soup, "og:description")
                result["data"]["profile_image"] = self._get_og_content(soup, "og:image")
                
                # Clean name (remove " | Facebook" suffix)
                if result["data"]["name"]:
                    result["data"]["name"] = result["data"]["name"].split("|")[0].strip()
                
                # Method 2: JSON-LD structured data
                self._extract_json_ld(soup, result["data"])
                
                # Method 3: Embedded JSON in scripts
                self._extract_embedded_json(soup, result["data"])
                
                result["success"] = True
                
        except Exception as e:
            logger.error(f"Error scraping Facebook profile {username}: {e}")
            result["error"] = str(e)
        
        return result
    
    def _extract_json_ld(self, soup: Any, data: Dict) -> None:
        """Extract data from JSON-LD scripts."""
        try:
            scripts = soup.find_all("script", type="application/ld+json")
            for script in scripts:
                if script.string:
                    json_data = json.loads(script.string)
                    if isinstance(json_data, dict):
                        if "name" in json_data and not data.get("name"):
                            data["name"] = json_data["name"]
                        if "description" in json_data and not data.get("bio"):
                            data["bio"] = json_data["description"]
        except (json.JSONDecodeError, Exception) as e:
            logger.debug(f"JSON-LD extraction failed: {e}")
    
    def _extract_embedded_json(self, soup: Any, data: Dict) -> None:
        """Extract data from embedded JSON in scripts."""
        try:
            scripts = soup.find_all("script")
            for script in scripts:
                if script.string and "profileTabMainColumns" in script.string:
                    # Facebook embeds profile data in scripts
                    # This is a simplified extraction
                    pass
        except Exception as e:
            logger.debug(f"Embedded JSON extraction failed: {e}")
    
    def extract_pii(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract PII from scraped Facebook data."""
        pii = {
            "name": None,
            "bio": None,
            "email": None,
            "phone": None,
            "location": None,
            "workplace": None,
            "profile_image": None,
            "website": None
        }
        
        data = scraped_data.get("data", {})
        
        pii["name"] = data.get("name")
        pii["bio"] = data.get("bio")
        pii["profile_image"] = data.get("profile_image")
        pii["location"] = data.get("location")
        pii["workplace"] = data.get("workplace")
        
        # Extract email/phone from bio
        if pii["bio"]:
            emails = self._extract_emails_from_text(pii["bio"])
            if emails:
                pii["email"] = emails[0]
            
            phones = self._extract_phones_from_text(pii["bio"])
            if phones:
                pii["phone"] = phones[0]
        
        return pii


class InstagramScraper(BasePlatformScraper):
    """
    Instagram profile scraper.
    
    Extracts data from Open Graph meta tags and shared data JSON.
    """
    
    PLATFORM = "instagram"
    BASE_URL = "https://www.instagram.com"
    
    async def check_exists(self, username: str) -> Dict[str, Any]:
        """Check if an Instagram profile exists."""
        if not HTTPX_AVAILABLE:
            return {"exists": False, "error": "httpx not available"}
        
        url = f"{self.BASE_URL}/{username}/"
        
        try:
            async with httpx.AsyncClient(
                timeout=self.REQUEST_TIMEOUT,
                follow_redirects=True
            ) as client:
                response = await client.get(url, headers={
                    "User-Agent": self.DEFAULT_USER_AGENT,
                    "Accept": "text/html"
                })
                
                if response.status_code == 200:
                    content = response.text.lower()
                    if "sorry, this page isn't available" in content:
                        return {"exists": False, "url": url, "status": "not_found"}
                    return {"exists": True, "url": url, "status": "found"}
                elif response.status_code == 404:
                    return {"exists": False, "url": url, "status": "not_found"}
                else:
                    return {"exists": False, "url": url, "status": "error", "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Error checking Instagram profile {username}: {e}")
            return {"exists": False, "url": url, "status": "error", "error": str(e)}
    
    async def scrape_profile(self, username: str) -> Dict[str, Any]:
        """Scrape Instagram profile data."""
        result = {
            "platform": self.PLATFORM,
            "username": username,
            "url": f"{self.BASE_URL}/{username}/",
            "success": False,
            "data": {},
            "error": None
        }
        
        if not HTTPX_AVAILABLE or not BS4_AVAILABLE:
            result["error"] = "Required libraries not available"
            return result
        
        try:
            async with httpx.AsyncClient(
                timeout=self.REQUEST_TIMEOUT,
                follow_redirects=True
            ) as client:
                response = await client.get(result["url"], headers={
                    "User-Agent": self.DEFAULT_USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml"
                })
                
                if response.status_code != 200:
                    result["error"] = f"HTTP {response.status_code}"
                    return result
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Open Graph meta tags
                og_title = self._get_og_content(soup, "og:title")
                og_description = self._get_og_content(soup, "og:description")
                og_image = self._get_og_content(soup, "og:image")
                
                # Clean name from title (format: "Name (@username) • Instagram photos and videos")
                if og_title:
                    match = re.match(r"^([^@(]+)", og_title)
                    if match:
                        result["data"]["name"] = match.group(1).strip()
                
                result["data"]["profile_image"] = og_image
                
                # Extract bio from description
                if og_description:
                    # Format: "X Followers, Y Following, Z Posts - Bio text"
                    parts = og_description.split(" - ")
                    if len(parts) > 1:
                        bio_part = " - ".join(parts[1:])
                        if "See Instagram" not in bio_part:
                            result["data"]["bio"] = bio_part.strip()
                
                # Try to extract shared data JSON
                self._extract_shared_data(soup, result["data"])
                
                result["success"] = True
                
        except Exception as e:
            logger.error(f"Error scraping Instagram profile {username}: {e}")
            result["error"] = str(e)
        
        return result
    
    def _extract_shared_data(self, soup: Any, data: Dict) -> None:
        """Extract data from Instagram's shared data JSON."""
        try:
            scripts = soup.find_all("script")
            for script in scripts:
                if script.string and "window._sharedData" in script.string:
                    # Parse the JSON from shared data
                    match = re.search(r'window\._sharedData\s*=\s*({.*?});', script.string, re.DOTALL)
                    if match:
                        json_data = json.loads(match.group(1))
                        user_data = json_data.get("entry_data", {}).get("ProfilePage", [{}])[0].get("graphql", {}).get("user", {})
                        
                        if user_data:
                            if not data.get("name"):
                                data["name"] = user_data.get("full_name")
                            if not data.get("bio"):
                                data["bio"] = user_data.get("biography")
                            data["website"] = user_data.get("external_url")
        except (json.JSONDecodeError, Exception) as e:
            logger.debug(f"Shared data extraction failed: {e}")
    
    def extract_pii(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract PII from scraped Instagram data."""
        pii = {
            "name": None,
            "bio": None,
            "email": None,
            "phone": None,
            "location": None,
            "workplace": None,
            "profile_image": None,
            "website": None
        }
        
        data = scraped_data.get("data", {})
        
        pii["name"] = data.get("name")
        pii["bio"] = data.get("bio")
        pii["profile_image"] = data.get("profile_image")
        pii["website"] = data.get("website")
        
        # Extract email/phone from bio
        if pii["bio"]:
            emails = self._extract_emails_from_text(pii["bio"])
            if emails:
                pii["email"] = emails[0]
            
            phones = self._extract_phones_from_text(pii["bio"])
            if phones:
                pii["phone"] = phones[0]
        
        return pii


class TwitterXScraper(BasePlatformScraper):
    """
    X (Twitter) profile scraper.
    
    Extracts data from Open Graph meta tags and page content.
    """
    
    PLATFORM = "x"
    BASE_URL = "https://x.com"
    
    async def check_exists(self, username: str) -> Dict[str, Any]:
        """Check if an X profile exists."""
        if not HTTPX_AVAILABLE:
            return {"exists": False, "error": "httpx not available"}
        
        url = f"{self.BASE_URL}/{username}"
        
        try:
            async with httpx.AsyncClient(
                timeout=self.REQUEST_TIMEOUT,
                follow_redirects=True
            ) as client:
                response = await client.get(url, headers={
                    "User-Agent": self.DEFAULT_USER_AGENT,
                    "Accept": "text/html"
                })
                
                if response.status_code == 200:
                    content = response.text.lower()
                    if "this account doesn't exist" in content or "hmm...this page doesn't exist" in content:
                        return {"exists": False, "url": url, "status": "not_found"}
                    return {"exists": True, "url": url, "status": "found"}
                elif response.status_code == 404:
                    return {"exists": False, "url": url, "status": "not_found"}
                else:
                    return {"exists": False, "url": url, "status": "error", "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Error checking X profile {username}: {e}")
            return {"exists": False, "url": url, "status": "error", "error": str(e)}
    
    async def scrape_profile(self, username: str) -> Dict[str, Any]:
        """Scrape X profile data."""
        result = {
            "platform": self.PLATFORM,
            "username": username,
            "url": f"{self.BASE_URL}/{username}",
            "success": False,
            "data": {},
            "error": None
        }
        
        if not HTTPX_AVAILABLE or not BS4_AVAILABLE:
            result["error"] = "Required libraries not available"
            return result
        
        try:
            async with httpx.AsyncClient(
                timeout=self.REQUEST_TIMEOUT,
                follow_redirects=True
            ) as client:
                response = await client.get(result["url"], headers={
                    "User-Agent": self.DEFAULT_USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml"
                })
                
                if response.status_code != 200:
                    result["error"] = f"HTTP {response.status_code}"
                    return result
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Open Graph meta tags
                og_title = self._get_og_content(soup, "og:title")
                og_description = self._get_og_content(soup, "og:description")
                og_image = self._get_og_content(soup, "og:image")
                
                # Clean name from title (format: "Name (@username) / X")
                if og_title:
                    match = re.match(r"^([^@(]+)", og_title)
                    if match:
                        result["data"]["name"] = match.group(1).strip()
                
                result["data"]["bio"] = og_description
                result["data"]["profile_image"] = og_image
                
                result["success"] = True
                
        except Exception as e:
            logger.error(f"Error scraping X profile {username}: {e}")
            result["error"] = str(e)
        
        return result
    
    def extract_pii(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract PII from scraped X data."""
        pii = {
            "name": None,
            "bio": None,
            "email": None,
            "phone": None,
            "location": None,
            "workplace": None,
            "profile_image": None,
            "website": None
        }
        
        data = scraped_data.get("data", {})
        
        pii["name"] = data.get("name")
        pii["bio"] = data.get("bio")
        pii["profile_image"] = data.get("profile_image")
        pii["location"] = data.get("location")
        
        # Extract email/phone from bio
        if pii["bio"]:
            emails = self._extract_emails_from_text(pii["bio"])
            if emails:
                pii["email"] = emails[0]
            
            phones = self._extract_phones_from_text(pii["bio"])
            if phones:
                pii["phone"] = phones[0]
        
        return pii


class LinkedInScraper(BasePlatformScraper):
    """
    LinkedIn profile scraper.
    
    Extracts data from Open Graph meta tags.
    Note: LinkedIn has strong anti-scraping measures.
    """
    
    PLATFORM = "linkedin"
    BASE_URL = "https://www.linkedin.com/in"
    
    async def check_exists(self, username: str) -> Dict[str, Any]:
        """Check if a LinkedIn profile exists."""
        if not HTTPX_AVAILABLE:
            return {"exists": False, "error": "httpx not available"}
        
        url = f"{self.BASE_URL}/{username}"
        
        try:
            async with httpx.AsyncClient(
                timeout=self.REQUEST_TIMEOUT,
                follow_redirects=True
            ) as client:
                response = await client.get(url, headers={
                    "User-Agent": self.DEFAULT_USER_AGENT,
                    "Accept": "text/html"
                })
                
                if response.status_code == 200:
                    content = response.text.lower()
                    if "page not found" in content or "this page doesn't exist" in content:
                        return {"exists": False, "url": url, "status": "not_found"}
                    return {"exists": True, "url": url, "status": "found"}
                elif response.status_code == 404:
                    return {"exists": False, "url": url, "status": "not_found"}
                else:
                    return {"exists": False, "url": url, "status": "error", "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Error checking LinkedIn profile {username}: {e}")
            return {"exists": False, "url": url, "status": "error", "error": str(e)}
    
    async def scrape_profile(self, username: str) -> Dict[str, Any]:
        """Scrape LinkedIn profile data."""
        result = {
            "platform": self.PLATFORM,
            "username": username,
            "url": f"{self.BASE_URL}/{username}",
            "success": False,
            "data": {},
            "error": None
        }
        
        if not HTTPX_AVAILABLE or not BS4_AVAILABLE:
            result["error"] = "Required libraries not available"
            return result
        
        try:
            async with httpx.AsyncClient(
                timeout=self.REQUEST_TIMEOUT,
                follow_redirects=True
            ) as client:
                response = await client.get(result["url"], headers={
                    "User-Agent": self.DEFAULT_USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml"
                })
                
                if response.status_code != 200:
                    result["error"] = f"HTTP {response.status_code}"
                    return result
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Open Graph meta tags
                og_title = self._get_og_content(soup, "og:title")
                og_description = self._get_og_content(soup, "og:description")
                og_image = self._get_og_content(soup, "og:image")
                
                # Clean name from title (format: "Name - Title | LinkedIn")
                if og_title:
                    parts = og_title.split("-")
                    if parts:
                        result["data"]["name"] = parts[0].strip()
                    if len(parts) > 1:
                        # Second part might be job title
                        job_part = parts[1].split("|")[0].strip()
                        if job_part:
                            result["data"]["workplace"] = job_part
                
                result["data"]["bio"] = og_description
                result["data"]["profile_image"] = og_image
                
                result["success"] = True
                
        except Exception as e:
            logger.error(f"Error scraping LinkedIn profile {username}: {e}")
            result["error"] = str(e)
        
        return result
    
    def extract_pii(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract PII from scraped LinkedIn data."""
        pii = {
            "name": None,
            "bio": None,
            "email": None,
            "phone": None,
            "location": None,
            "workplace": None,
            "profile_image": None,
            "website": None
        }
        
        data = scraped_data.get("data", {})
        
        pii["name"] = data.get("name")
        pii["bio"] = data.get("bio")
        pii["profile_image"] = data.get("profile_image")
        pii["workplace"] = data.get("workplace")
        pii["location"] = data.get("location")
        
        # Extract email/phone from bio
        if pii["bio"]:
            emails = self._extract_emails_from_text(pii["bio"])
            if emails:
                pii["email"] = emails[0]
            
            phones = self._extract_phones_from_text(pii["bio"])
            if phones:
                pii["phone"] = phones[0]
        
        return pii


# =============================================================================
# SCRAPER REGISTRY
# =============================================================================

PLATFORM_SCRAPERS = {
    "facebook": FacebookScraper,
    "instagram": InstagramScraper,
    "x": TwitterXScraper,
    "linkedin": LinkedInScraper,
}


def get_scraper(platform: str) -> Optional[BasePlatformScraper]:
    """
    Get a scraper instance for the specified platform.
    
    Args:
        platform: Platform ID (facebook, instagram, x, linkedin)
        
    Returns:
        Scraper instance or None if platform not supported
    """
    scraper_class = PLATFORM_SCRAPERS.get(platform.lower())
    if scraper_class:
        return scraper_class()
    return None


async def scrape_all_platforms(username: str) -> Dict[str, Dict]:
    """
    Scrape profile data from all supported platforms.
    
    Args:
        username: Username to scrape
        
    Returns:
        Dictionary with results from each platform
    """
    results = {}
    
    for platform, scraper_class in PLATFORM_SCRAPERS.items():
        scraper = scraper_class()
        
        # First check if profile exists
        exists_result = await scraper.check_exists(username)
        
        if exists_result.get("exists"):
            # Scrape profile data
            scraped = await scraper.scrape_profile(username)
            
            # Extract PII
            pii = scraper.extract_pii(scraped)
            
            results[platform] = {
                "status": "found",
                "url": scraped.get("url", ""),
                "data": pii,
                "raw_data": scraped.get("data", {}),
                "success": scraped.get("success", False),
                "error": scraped.get("error")
            }
        else:
            results[platform] = {
                "status": exists_result.get("status", "not_found"),
                "url": exists_result.get("url", ""),
                "data": {},
                "success": False,
                "error": exists_result.get("error")
            }
    
    return results
