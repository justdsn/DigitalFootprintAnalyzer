# =============================================================================
# PLATFORM CONFIGURATION
# =============================================================================
# Configuration for supported social media platforms.
# Only 4 platforms supported: Facebook, Instagram, LinkedIn, X
# =============================================================================

"""
Platform Configuration

This module defines configuration for supported social media platforms:
- Facebook
- Instagram
- LinkedIn
- X (Twitter)

Each platform configuration includes:
- name: Display name
- emoji: Platform emoji/icon
- color: Brand color (hex)
- url_template: Profile URL template
- privacy_url: Link to privacy settings
- report_url: Link to report profile page
"""

from typing import Dict, Any, Optional


# =============================================================================
# SUPPORTED PLATFORMS CONFIGURATION
# =============================================================================

SUPPORTED_PLATFORMS: Dict[str, Dict[str, str]] = {
    "facebook": {
        "name": "Facebook",
        "emoji": "📘",
        "color": "#1877f2",
        "url_template": "https://www.facebook.com/{username}",
        "privacy_url": "https://www.facebook.com/settings?tab=privacy",
        "report_url": "https://www.facebook.com/help/contact/169486816475808"
    },
    "instagram": {
        "name": "Instagram",
        "emoji": "📷",
        "color": "#e4405f",
        "url_template": "https://www.instagram.com/{username}/",
        "privacy_url": "https://www.instagram.com/accounts/privacy_and_security/",
        "report_url": "https://help.instagram.com/contact/636276399721841"
    },
    "linkedin": {
        "name": "LinkedIn",
        "emoji": "💼",
        "color": "#0a66c2",
        "url_template": "https://www.linkedin.com/in/{username}",
        "privacy_url": "https://www.linkedin.com/psettings/privacy",
        "report_url": "https://www.linkedin.com/help/linkedin/solve/report-a-fake-profile"
    },
    "x": {
        "name": "X (Twitter)",
        "emoji": "𝕏",
        "color": "#000000",
        "url_template": "https://x.com/{username}",
        "privacy_url": "https://twitter.com/settings/privacy_and_safety",
        "report_url": "https://help.twitter.com/forms/impersonation"
    }
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_platform_config(platform: str) -> Optional[Dict[str, str]]:
    """
    Get configuration for a specific platform.
    
    Args:
        platform: Platform identifier (facebook, instagram, linkedin, x)
        
    Returns:
        Platform configuration dict or None if not found
    """
    return SUPPORTED_PLATFORMS.get(platform.lower())


def get_platform_url(platform: str, username: str) -> Optional[str]:
    """
    Generate profile URL for a platform.
    
    Args:
        platform: Platform identifier
        username: Username to insert into URL template
        
    Returns:
        Profile URL or None if platform not supported
    """
    config = get_platform_config(platform)
    if config:
        return config["url_template"].format(username=username)
    return None


def get_platform_emoji(platform: str) -> str:
    """
    Get emoji for a platform.
    
    Args:
        platform: Platform identifier
        
    Returns:
        Platform emoji or generic icon if not found
    """
    config = get_platform_config(platform)
    if config:
        return config.get("emoji", "🌐")
    return "🌐"


def get_platform_name(platform: str) -> str:
    """
    Get display name for a platform.
    
    Args:
        platform: Platform identifier
        
    Returns:
        Platform display name or capitalized platform ID if not found
    """
    config = get_platform_config(platform)
    if config:
        return config.get("name", platform.capitalize())
    return platform.capitalize()


def get_all_platform_ids() -> list:
    """
    Get list of all supported platform IDs.
    
    Returns:
        List of platform identifiers
    """
    return list(SUPPORTED_PLATFORMS.keys())
