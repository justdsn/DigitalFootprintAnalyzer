# =============================================================================
# PROFILE EXISTENCE CHECKER SERVICE
# =============================================================================
# Checks if social media profiles exist using HTTP requests.
# Handles rate limiting and various response codes gracefully.
# =============================================================================

"""
Profile Existence Checker Service

This module checks if social media profiles exist on various platforms:
- HTTP HEAD/GET requests to check profile pages
- Analyze response codes and content for existence
- Handle rate limiting gracefully
- Return detailed status information

Features:
- Check individual profiles on specific platforms
- Check all platforms for a username
- Return status: exists, not_found, private, error

Example Usage:
    checker = ProfileExistenceChecker()
    result = await checker.check_profile("john_doe", "instagram")
    # Returns: {"status": "exists", "url": "...", ...}
    
    results = await checker.check_all_platforms("john_doe")
    # Returns results for all platforms
"""

import asyncio
from typing import Dict, List, Optional, Any
import logging

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

from .profile_generator import ProfileURLGenerator

# Set up logger
logger = logging.getLogger(__name__)


class ProfileExistenceChecker:
    """
    Check if social media profiles exist.
    
    This class provides methods to:
    1. Check if a profile exists on a specific platform
    2. Check all supported platforms for a username
    3. Analyze HTTP responses to determine profile status
    
    Status values:
    - exists: Profile was found and is accessible
    - not_found: Profile does not exist (404)
    - private: Profile exists but is private/restricted
    - rate_limited: Request was rate limited
    - error: An error occurred during the check
    """
    
    # -------------------------------------------------------------------------
    # PLATFORM-SPECIFIC CONFIGURATION
    # -------------------------------------------------------------------------
    PLATFORM_CONFIG = {
        "facebook": {
            "not_found_indicators": ["page not found", "content isn't available"],
            "private_indicators": ["this content isn't available"],
            "user_agent_required": True
        },
        "instagram": {
            "not_found_indicators": ["page not found", "sorry, this page isn't available"],
            "private_indicators": ["this account is private"],
            "user_agent_required": True
        },
        "linkedin": {
            "not_found_indicators": ["page not found", "this page doesn't exist"],
            "private_indicators": [],
            "user_agent_required": True
        },
        "x": {
            "not_found_indicators": ["this account doesn't exist", "hmm...this page doesn't exist"],
            "private_indicators": ["these tweets are protected"],
            "user_agent_required": True
        }
    }
    
    # Default User-Agent to mimic a browser
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    
    # Request timeout in seconds
    REQUEST_TIMEOUT = 10.0
    
    # Delay between requests to avoid rate limiting (seconds)
    REQUEST_DELAY = 1.0
    
    def __init__(self):
        """Initialize the Profile Existence Checker."""
        self.url_generator = ProfileURLGenerator()
    
    async def check_profile(
        self,
        username: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Check if a profile exists on a specific platform.
        
        Makes an HTTP request to the profile URL and analyzes the response
        to determine if the profile exists.
        
        Args:
            username: The username to check
            platform: Platform ID (facebook, instagram, linkedin, x)
        
        Returns:
            Dict containing:
                - status: exists, not_found, private, rate_limited, error
                - url: The profile URL checked
                - platform: Platform name
                - message: Human-readable status message
        
        Example:
            >>> await checker.check_profile("john_doe", "instagram")
            {
                'status': 'exists',
                'url': 'https://www.instagram.com/john_doe/',
                'platform': 'Instagram',
                'message': 'Profile found on Instagram'
            }
        """
        if not HTTPX_AVAILABLE:
            return {
                "status": "error",
                "url": None,
                "platform": platform,
                "message": "httpx library not available"
            }
        
        url = self.url_generator.generate_url(username, platform)
        
        if not url:
            return {
                "status": "error",
                "url": None,
                "platform": platform,
                "message": f"Invalid username or unsupported platform: {platform}"
            }
        
        platform_name = self.url_generator.PLATFORMS.get(platform, {}).get("name", platform)
        
        try:
            async with httpx.AsyncClient(
                timeout=self.REQUEST_TIMEOUT,
                follow_redirects=True
            ) as client:
                headers = {
                    "User-Agent": self.DEFAULT_USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "en-US,en;q=0.9"
                }
                
                response = await client.get(url, headers=headers)
                
                return self._analyze_response(
                    response=response,
                    url=url,
                    platform=platform,
                    platform_name=platform_name
                )
                
        except httpx.TimeoutException:
            return {
                "status": "error",
                "url": url,
                "platform": platform_name,
                "message": "Request timed out"
            }
        except httpx.RequestError as e:
            logger.warning(f"Request error for {platform} profile {username}: {e}")
            return {
                "status": "error",
                "url": url,
                "platform": platform_name,
                "message": f"Request error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error checking {platform} profile {username}: {e}")
            return {
                "status": "error",
                "url": url,
                "platform": platform_name,
                "message": f"Unexpected error: {str(e)}"
            }
    
    def _analyze_response(
        self,
        response: Any,
        url: str,
        platform: str,
        platform_name: str
    ) -> Dict[str, Any]:
        """
        Analyze HTTP response to determine profile status.
        
        Args:
            response: httpx Response object
            url: The URL that was checked
            platform: Platform ID
            platform_name: Human-readable platform name
        
        Returns:
            Dict with status information
        """
        status_code = response.status_code
        
        # Check for rate limiting
        if status_code == 429:
            return {
                "status": "rate_limited",
                "url": url,
                "platform": platform_name,
                "message": "Rate limited - please try again later"
            }
        
        # Check for not found
        if status_code == 404:
            return {
                "status": "not_found",
                "url": url,
                "platform": platform_name,
                "message": f"Profile not found on {platform_name}"
            }
        
        # Check for successful response
        if status_code == 200:
            # Get response content for deeper analysis
            content = response.text.lower() if response.text else ""
            
            # Check for platform-specific not found indicators
            config = self.PLATFORM_CONFIG.get(platform, {})
            
            for indicator in config.get("not_found_indicators", []):
                if indicator.lower() in content:
                    return {
                        "status": "not_found",
                        "url": url,
                        "platform": platform_name,
                        "message": f"Profile not found on {platform_name}"
                    }
            
            # Check for private indicators
            for indicator in config.get("private_indicators", []):
                if indicator.lower() in content:
                    return {
                        "status": "private",
                        "url": url,
                        "platform": platform_name,
                        "message": f"Profile is private on {platform_name}"
                    }
            
            # If we got here, profile likely exists
            return {
                "status": "exists",
                "url": url,
                "platform": platform_name,
                "message": f"Profile found on {platform_name}"
            }
        
        # Handle other status codes
        if status_code in [401, 403]:
            return {
                "status": "private",
                "url": url,
                "platform": platform_name,
                "message": f"Profile may be private or restricted on {platform_name}"
            }
        
        # Unknown status
        return {
            "status": "error",
            "url": url,
            "platform": platform_name,
            "message": f"Unexpected response code: {status_code}"
        }
    
    async def check_all_platforms(
        self,
        username: str,
        platforms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Check all supported platforms for a username.
        
        Checks each platform with a delay between requests to avoid
        rate limiting.
        
        Args:
            username: The username to check
            platforms: Optional list of platform IDs to check.
                      If None, checks all supported platforms.
        
        Returns:
            Dict containing:
                - username: The checked username
                - results: Dict of results per platform
                - summary: Count of each status type
        
        Example:
            >>> await checker.check_all_platforms("john_doe")
            {
                'username': 'john_doe',
                'results': {
                    'facebook': {...},
                    'instagram': {...},
                    ...
                },
                'summary': {
                    'exists': 2,
                    'not_found': 1,
                    'private': 0,
                    'error': 1
                }
            }
        """
        if platforms is None:
            platforms = self.url_generator.get_supported_platforms()
        
        results = {}
        summary = {
            "exists": 0,
            "not_found": 0,
            "private": 0,
            "rate_limited": 0,
            "error": 0
        }
        
        for i, platform in enumerate(platforms):
            # Add delay between requests (except for first request)
            if i > 0:
                await asyncio.sleep(self.REQUEST_DELAY)
            
            result = await self.check_profile(username, platform)
            results[platform] = result
            
            # Update summary
            status = result.get("status", "error")
            if status in summary:
                summary[status] += 1
        
        return {
            "username": username,
            "results": results,
            "summary": summary
        }


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

_default_checker = ProfileExistenceChecker()


async def check_profile(username: str, platform: str) -> Dict[str, Any]:
    """Module-level convenience function for single profile check."""
    return await _default_checker.check_profile(username, platform)


async def check_all_platforms(
    username: str,
    platforms: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Module-level convenience function for checking all platforms."""
    return await _default_checker.check_all_platforms(username, platforms)
