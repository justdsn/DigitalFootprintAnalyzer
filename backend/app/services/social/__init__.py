# =============================================================================
# SOCIAL MEDIA SERVICES MODULE
# =============================================================================
# Phase 3: Social Media Data Collection & Profile Checking
# =============================================================================

"""
Social Media Services Module

This module provides services for social media profile analysis:
- ProfileURLGenerator: Generate profile URLs for multiple platforms
- ProfileExistenceChecker: Check if profiles exist on platforms
- SocialMediaDataCollector: Extract public data from profile pages
- PhoneNumberLookup: Sri Lankan phone validation and carrier ID
- PIIExposureAnalyzer: Analyze PII exposure across platforms
- Platform Scrapers: Specialized scrapers for each platform

Example Usage:
    from app.services.social import (
        ProfileURLGenerator,
        ProfileExistenceChecker,
        SocialMediaDataCollector,
        PhoneNumberLookup,
        PIIExposureAnalyzer,
    )
    
    # Generate profile URLs
    generator = ProfileURLGenerator()
    urls = generator.generate_urls("john_doe")
    
    # Check profile existence
    checker = ProfileExistenceChecker()
    result = await checker.check_profile("john_doe", "instagram")
    
    # Collect profile data
    collector = SocialMediaDataCollector()
    data = await collector.collect_profile_data(url, "instagram")
    
    # Phone lookup
    lookup = PhoneNumberLookup()
    info = lookup.lookup("0771234567")
    
    # Analyze PII exposure
    analyzer = PIIExposureAnalyzer()
    report = analyzer.analyze(platform_data, user_identifiers)
"""

from .profile_generator import ProfileURLGenerator
from .profile_checker import ProfileExistenceChecker
from .data_collector import SocialMediaDataCollector
from .phone_lookup import PhoneNumberLookup
from .exposure_analyzer import PIIExposureAnalyzer
from .platform_scrapers import (
    BasePlatformScraper,
    FacebookScraper,
    InstagramScraper,
    TwitterXScraper,
    LinkedInScraper,
    get_scraper,
    scrape_all_platforms,
)

__all__ = [
    "ProfileURLGenerator",
    "ProfileExistenceChecker",
    "SocialMediaDataCollector",
    "PhoneNumberLookup",
    "PIIExposureAnalyzer",
    "BasePlatformScraper",
    "FacebookScraper",
    "InstagramScraper",
    "TwitterXScraper",
    "LinkedInScraper",
    "get_scraper",
    "scrape_all_platforms",
]
