# =============================================================================
# COLLECTORS MODULE
# =============================================================================
# Platform-specific Playwright collectors for OSINT data collection.
# =============================================================================

"""
Collectors Module

Platform-specific collectors that use Playwright to collect public data
from social media profiles.

Components:
- BaseCollector: Abstract base class for all collectors
- InstagramCollector: Instagram profile data collector
- FacebookCollector: Facebook profile data collector
- LinkedInCollector: LinkedIn profile data collector
- TwitterCollector: X/Twitter profile data collector
"""

from .base_collector import BaseCollector
from .instagram_collector import InstagramCollector
from .facebook_collector import FacebookCollector
from .linkedin_collector import LinkedInCollector
from .twitter_collector import TwitterCollector

__all__ = [
    "BaseCollector",
    "InstagramCollector",
    "FacebookCollector",
    "LinkedInCollector",
    "TwitterCollector",
]
