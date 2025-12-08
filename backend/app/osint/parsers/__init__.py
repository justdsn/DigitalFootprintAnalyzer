# =============================================================================
# PARSERS MODULE
# =============================================================================
# HTML parsers for extracting profile data from collected HTML.
# =============================================================================

"""
Parsers Module

Platform-specific HTML parsers that extract structured data from
collected profile pages using BeautifulSoup.
"""

from .profile_parser import ProfileParser
from .instagram_parser import InstagramParser
from .facebook_parser import FacebookParser
from .linkedin_parser import LinkedInParser
from .twitter_parser import TwitterParser

__all__ = [
    "ProfileParser",
    "InstagramParser",
    "FacebookParser",
    "LinkedInParser",
    "TwitterParser",
]
