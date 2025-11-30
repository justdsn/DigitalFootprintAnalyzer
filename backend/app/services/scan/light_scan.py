# =============================================================================
# LIGHT SCAN SERVICE
# =============================================================================
# Google Dorking-based profile discovery for social media platforms.
# Finds potential profile matches for a given identifier.
# =============================================================================

"""
Light Scan Service

This module provides Google Dork-based profile discovery:
- Search by name with location filtering
- Search by email (extracts username)
- Search by username with variations

Supported Platforms:
- Facebook
- Instagram
- LinkedIn
- X (Twitter)

NO phone number support in Light Scan (as per requirements).

Note on Google Search Usage:
    This service uses Google Search to perform dork queries. Rate limiting
    is implemented (3 seconds between requests) to reduce the risk of being
    blocked. For production use, consider:
    - Using Google's Custom Search JSON API for proper authentication
    - Implementing exponential backoff for rate limiting
    - Using multiple IP addresses/proxies for higher volume

Example Usage:
    service = LightScanService()
    result = await service.scan(
        identifier_type="name",
        identifier_value="John Perera",
        location="Sri Lanka"
    )
"""

import asyncio
import logging
import re
import time
import uuid
from typing import Dict, List, Optional, Any, Set
from urllib.parse import quote_plus, urlparse, parse_qs

import httpx
from bs4 import BeautifulSoup

# Set up logger
logger = logging.getLogger(__name__)


class LightScanService:
    """
    Light scan service using Google Dorking for profile discovery.
    
    This service generates Google Dork queries for supported platforms
    and extracts potential profile URLs from search results.
    
    Attributes:
        PLATFORMS: Platform configuration including dork base and exclude paths
        DEFAULT_LOCATION: Default location filter for searches
    """
    
    # -------------------------------------------------------------------------
    # PLATFORM CONFIGURATION
    # -------------------------------------------------------------------------
    PLATFORMS = {
        "facebook": {
            "emoji": "📘",
            "dork_base": "site:facebook.com",
            "exclude_paths": ["/search", "/help", "/pages", "/groups", "/events",
                             "/login", "/signup", "/register", "/settings",
                             "/privacy", "/terms", "/policy", "/support",
                             "/about", "/directory"],
            "profile_pattern": r"facebook\.com/([a-zA-Z0-9._]+)/?$"
        },
        "instagram": {
            "emoji": "📷",
            "dork_base": "site:instagram.com",
            "exclude_paths": ["/explore", "/p/", "/reel/", "/stories/",
                             "/search", "/help", "/about", "/legal",
                             "/login", "/signup", "/accounts/"],
            "profile_pattern": r"instagram\.com/([a-zA-Z0-9._]+)/?$"
        },
        "linkedin": {
            "emoji": "💼",
            "dork_base": "site:linkedin.com/in",
            "exclude_paths": ["/search", "/jobs", "/company", "/pulse",
                             "/help", "/legal", "/login", "/signup"],
            "profile_pattern": r"linkedin\.com/in/([a-zA-Z0-9-]+)/?$"
        },
        "x": {
            "emoji": "𝕏",
            "dork_base": "(site:x.com OR site:twitter.com)",
            "exclude_paths": ["/search", "/explore", "/i/", "/hashtag/",
                             "/help", "/settings", "/login", "/signup",
                             "/tos", "/privacy"],
            "profile_pattern": r"(?:x\.com|twitter\.com)/([a-zA-Z0-9_]+)/?$"
        }
    }
    
    DEFAULT_LOCATION = "Sri Lanka"
    
    # Google search URL template
    GOOGLE_SEARCH_URL = "https://www.google.com/search"
    
    # Request configuration
    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    REQUEST_TIMEOUT = 15.0
    
    # Rate limiting configuration
    # Using 3 seconds between requests to reduce risk of being rate limited
    DELAY_BETWEEN_REQUESTS = 3.0  # seconds
    
    def __init__(self):
        """Initialize the Light Scan Service."""
        self._compiled_exclude_patterns: Dict[str, List[re.Pattern]] = {}
        for platform_id, config in self.PLATFORMS.items():
            self._compiled_exclude_patterns[platform_id] = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in config["exclude_paths"]
            ]
    
    # -------------------------------------------------------------------------
    # PUBLIC SCAN METHOD
    # -------------------------------------------------------------------------
    
    async def scan(
        self,
        identifier_type: str,
        identifier_value: str,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform a light scan using Google Dorking.
        
        Args:
            identifier_type: Type of identifier ('name', 'email', 'username')
            identifier_value: The identifier value to search for
            location: Optional location filter (default: Sri Lanka)
        
        Returns:
            Dict containing scan results with structure:
                - success: bool
                - scan_type: "light"
                - scan_id: unique identifier
                - identifier: {type, value}
                - location: applied location filter
                - scan_duration_seconds: float
                - total_results: int
                - platforms: list of PlatformDorkResults
                - summary: dict of platform -> result count
                - all_urls: list of all found URLs
                - deep_scan_available: bool
                - deep_scan_message: str
        
        Raises:
            ValueError: If identifier_type is not supported
        """
        start_time = time.time()
        
        # Validate identifier type
        valid_types = ["name", "email", "username"]
        if identifier_type not in valid_types:
            raise ValueError(
                f"Invalid identifier_type: {identifier_type}. "
                f"Must be one of: {valid_types}"
            )
        
        # Clean identifier value
        identifier_value = identifier_value.strip()
        if not identifier_value:
            raise ValueError("identifier_value cannot be empty")
        
        # Set location
        location = location or self.DEFAULT_LOCATION
        
        # Generate scan ID
        scan_id = f"LS-{uuid.uuid4().hex[:8].upper()}"
        
        # Generate dork queries based on identifier type
        queries_by_platform = self._generate_queries(
            identifier_type, identifier_value, location
        )
        
        # Execute searches and collect results
        platform_results = await self._execute_searches(queries_by_platform)
        
        # Build response
        platforms = []
        all_urls = []
        summary = {}
        total_results = 0
        
        for platform_id, results in platform_results.items():
            config = self.PLATFORMS[platform_id]
            
            # Deduplicate results by URL
            seen_urls: Set[str] = set()
            unique_results = []
            for result in results:
                if result["url"] not in seen_urls:
                    seen_urls.add(result["url"])
                    unique_results.append(result)
            
            platform_data = {
                "platform": platform_id,
                "platform_emoji": config["emoji"],
                "results_count": len(unique_results),
                "results": unique_results,
                "queries_used": queries_by_platform[platform_id]
            }
            platforms.append(platform_data)
            
            summary[platform_id] = len(unique_results)
            total_results += len(unique_results)
            
            # Add to all_urls
            for result in unique_results:
                all_urls.append({
                    "platform": platform_id,
                    "url": result["url"],
                    "title": result["title"]
                })
        
        scan_duration = time.time() - start_time
        
        return {
            "success": True,
            "scan_type": "light",
            "scan_id": scan_id,
            "identifier": {
                "type": identifier_type,
                "value": identifier_value
            },
            "location": location,
            "scan_duration_seconds": round(scan_duration, 2),
            "total_results": total_results,
            "platforms": platforms,
            "summary": summary,
            "all_urls": all_urls,
            "deep_scan_available": True,
            "deep_scan_message": (
                "Want more detailed analysis? "
                "Try Deep Scan with our browser extension."
            )
        }
    
    # -------------------------------------------------------------------------
    # QUERY GENERATION METHODS
    # -------------------------------------------------------------------------
    
    def _generate_queries(
        self,
        identifier_type: str,
        identifier_value: str,
        location: str
    ) -> Dict[str, List[str]]:
        """
        Generate Google Dork queries for each platform.
        
        Args:
            identifier_type: Type of identifier
            identifier_value: The identifier value
            location: Location filter
        
        Returns:
            Dict mapping platform_id to list of dork queries
        """
        queries_by_platform: Dict[str, List[str]] = {}
        
        for platform_id, config in self.PLATFORMS.items():
            dork_base = config["dork_base"]
            queries = []
            
            if identifier_type == "name":
                # Name-based queries
                queries.extend(self._generate_name_queries(
                    dork_base, identifier_value, location
                ))
            
            elif identifier_type == "email":
                # Email-based queries
                queries.extend(self._generate_email_queries(
                    dork_base, identifier_value
                ))
            
            elif identifier_type == "username":
                # Username-based queries
                queries.extend(self._generate_username_queries(
                    dork_base, identifier_value
                ))
            
            queries_by_platform[platform_id] = queries
        
        return queries_by_platform
    
    def _generate_name_queries(
        self,
        dork_base: str,
        name: str,
        location: str
    ) -> List[str]:
        """Generate queries for name-based search."""
        queries = []
        
        # Basic name search
        queries.append(f'{dork_base} "{name}"')
        
        # Name with location
        if location:
            queries.append(f'{dork_base} "{name}" "{location}"')
        
        return queries
    
    def _generate_email_queries(
        self,
        dork_base: str,
        email: str
    ) -> List[str]:
        """Generate queries for email-based search."""
        queries = []
        
        # Full email search
        queries.append(f'{dork_base} "{email}"')
        
        # Extract username from email and search that
        if "@" in email:
            username = email.split("@")[0]
            queries.append(f'{dork_base} "{username}"')
            
            # Remove dots and underscores for variation
            clean_username = re.sub(r'[._]', '', username)
            if clean_username != username:
                queries.append(f'{dork_base} "{clean_username}"')
        
        return queries
    
    def _generate_username_queries(
        self,
        dork_base: str,
        username: str
    ) -> List[str]:
        """Generate queries for username-based search."""
        queries = []
        
        # Strip @ if present
        username = username.lstrip("@")
        
        # Basic username search
        queries.append(f'{dork_base} "{username}"')
        
        # Generate variations
        variations = self._generate_username_variations(username)
        for variation in variations:
            if variation != username:
                queries.append(f'{dork_base} "{variation}"')
        
        return queries
    
    def _generate_username_variations(self, username: str) -> List[str]:
        """
        Generate common username variations.
        
        Args:
            username: Base username
        
        Returns:
            List of username variations (including original)
        """
        username = username.lower()
        variations = set()
        
        # Original
        variations.add(username)
        
        # Remove underscores
        variations.add(username.replace('_', ''))
        
        # Remove dots
        variations.add(username.replace('.', ''))
        
        # Replace underscores with dots
        variations.add(username.replace('_', '.'))
        
        # Replace dots with underscores
        variations.add(username.replace('.', '_'))
        
        # Remove all special characters
        clean = re.sub(r'[^a-z0-9]', '', username)
        variations.add(clean)
        
        # Filter out empty strings
        variations.discard('')
        
        return list(variations)
    
    # -------------------------------------------------------------------------
    # SEARCH EXECUTION METHODS
    # -------------------------------------------------------------------------
    
    async def _execute_searches(
        self,
        queries_by_platform: Dict[str, List[str]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Execute Google searches for all queries.
        
        Args:
            queries_by_platform: Dict mapping platform_id to list of queries
        
        Returns:
            Dict mapping platform_id to list of results
        """
        results_by_platform: Dict[str, List[Dict[str, Any]]] = {}
        
        async with httpx.AsyncClient(
            headers=self.DEFAULT_HEADERS,
            timeout=self.REQUEST_TIMEOUT,
            follow_redirects=True
        ) as client:
            for platform_id, queries in queries_by_platform.items():
                platform_results = []
                
                for query in queries:
                    try:
                        # Execute search
                        search_results = await self._execute_single_search(
                            client, query, platform_id
                        )
                        
                        # Tag results with the query used
                        for result in search_results:
                            result["query_used"] = query
                        
                        platform_results.extend(search_results)
                        
                        # Rate limiting delay
                        await asyncio.sleep(self.DELAY_BETWEEN_REQUESTS)
                        
                    except Exception as e:
                        logger.warning(
                            f"Search failed for platform {platform_id}, "
                            f"query '{query}': {str(e)}"
                        )
                        continue
                
                results_by_platform[platform_id] = platform_results
        
        return results_by_platform
    
    async def _execute_single_search(
        self,
        client: httpx.AsyncClient,
        query: str,
        platform_id: str
    ) -> List[Dict[str, Any]]:
        """
        Execute a single Google search and parse results.
        
        Args:
            client: httpx AsyncClient
            query: Google dork query
            platform_id: Platform identifier for filtering
        
        Returns:
            List of result dictionaries with title, url, snippet
        """
        results = []
        
        try:
            # Build search URL
            params = {
                "q": query,
                "num": 10,  # Number of results
            }
            
            response = await client.get(
                self.GOOGLE_SEARCH_URL,
                params=params
            )
            
            if response.status_code != 200:
                logger.warning(
                    f"Google search returned status {response.status_code}"
                )
                return results
            
            # Parse HTML response using lxml parser (included in requirements.txt)
            # lxml is faster and more robust than html.parser
            soup = BeautifulSoup(response.text, "lxml")
            
            # Extract search results
            # Google search results are in different structures
            # We try multiple selectors for robustness
            result_items = self._extract_search_results(soup)
            
            for item in result_items:
                # Filter for valid profile URLs
                if self._is_valid_profile_url(item["url"], platform_id):
                    results.append(item)
        
        except httpx.HTTPError as e:
            logger.warning(f"HTTP error during search: {str(e)}")
        except Exception as e:
            logger.warning(f"Error parsing search results: {str(e)}")
        
        return results
    
    def _extract_search_results(
        self,
        soup: BeautifulSoup
    ) -> List[Dict[str, Any]]:
        """
        Extract search results from Google HTML.
        
        Args:
            soup: BeautifulSoup parsed HTML
        
        Returns:
            List of result dictionaries with title, url, snippet
        """
        results = []
        
        # Try finding results using various selectors
        # Google's HTML structure can vary
        
        # Method 1: Look for main search result divs
        for div in soup.find_all("div", class_="g"):
            try:
                # Find link
                link = div.find("a", href=True)
                if not link:
                    continue
                
                url = link.get("href", "")
                
                # Skip Google redirect URLs
                if url.startswith("/url?"):
                    parsed = urlparse(url)
                    params = parse_qs(parsed.query)
                    url = params.get("q", [""])[0]
                
                # Skip empty or Google internal URLs
                if not url or url.startswith("/"):
                    continue
                
                # Get title
                title_elem = link.find("h3")
                title = title_elem.get_text(strip=True) if title_elem else ""
                
                # Get snippet
                snippet_elem = div.find("div", class_=re.compile(r"VwiC3b|IsZvec"))
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else None
                
                if url:
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet
                    })
            except Exception:
                continue
        
        # Method 2: Look for all links with valid structure
        if not results:
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                
                # Check if this looks like a search result
                if "/url?" in href:
                    parsed = urlparse(href)
                    params = parse_qs(parsed.query)
                    url = params.get("q", [""])[0]
                    
                    if url and not url.startswith("/"):
                        title = link.get_text(strip=True)
                        if title and len(title) > 5:
                            results.append({
                                "title": title,
                                "url": url,
                                "snippet": None
                            })
        
        return results
    
    def _is_valid_profile_url(self, url: str, platform_id: str) -> bool:
        """
        Check if a URL is a valid profile URL for the platform.
        
        Args:
            url: URL to check
            platform_id: Platform identifier
        
        Returns:
            bool: True if URL is a valid profile URL
        """
        if not url or platform_id not in self.PLATFORMS:
            return False
        
        config = self.PLATFORMS[platform_id]
        
        # Parse the URL to extract the hostname
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname or ""
            hostname_lower = hostname.lower()
            path = parsed.path.strip("/")
        except Exception:
            return False
        
        # Check if URL belongs to the correct platform using hostname parsing
        # This prevents substring matching vulnerabilities (e.g., "fakex.com")
        if platform_id == "x":
            # X can be either x.com or twitter.com
            valid_hosts = ["x.com", "www.x.com", "twitter.com", "www.twitter.com"]
            if hostname_lower not in valid_hosts:
                return False
        elif platform_id == "linkedin":
            # LinkedIn must be linkedin.com domain and have /in/ path
            valid_hosts = ["linkedin.com", "www.linkedin.com"]
            if hostname_lower not in valid_hosts:
                return False
            if not path.startswith("in/"):
                return False
        else:
            # Other platforms - check exact domain
            valid_hosts = [f"{platform_id}.com", f"www.{platform_id}.com"]
            if hostname_lower not in valid_hosts:
                return False
        
        # Check against exclude patterns
        url_lower = url.lower()
        for pattern in self._compiled_exclude_patterns[platform_id]:
            if pattern.search(url_lower):
                return False
        
        # Must have a path (username)
        if not path:
            return False
        
        # Path should be relatively short (usernames aren't usually long paths)
        if path.count("/") > 2:
            return False
        
        # If we have a profile pattern, use it for additional validation
        # but don't require it to match (allows for URL variations)
        profile_pattern = config.get("profile_pattern")
        if profile_pattern and re.search(profile_pattern, url):
            return True
        
        # If no pattern match, still accept if basic validation passed
        return True
    
    # -------------------------------------------------------------------------
    # UTILITY METHODS
    # -------------------------------------------------------------------------
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platform IDs."""
        return list(self.PLATFORMS.keys())
    
    def get_platform_config(self, platform_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific platform."""
        return self.PLATFORMS.get(platform_id)


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTION
# =============================================================================

_default_service = None


def get_light_scan_service() -> LightScanService:
    """Get or create the default LightScanService instance."""
    global _default_service
    if _default_service is None:
        _default_service = LightScanService()
    return _default_service
