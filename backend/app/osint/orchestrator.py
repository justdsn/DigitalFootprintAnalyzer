# =============================================================================
# OSINT ORCHESTRATOR
# =============================================================================
# Main OSINT flow controller that coordinates all components.
# =============================================================================

"""
OSINT Orchestrator

Main controller that orchestrates the entire OSINT workflow:
1. Accept input identifier (username, email, name, phone)
2. Detect identifier type
3. Generate possible profile URLs
4. Collect data using Playwright collectors
5. Parse HTML data
6. Integrate with existing analysis modules (NER, PII, correlation, etc.)
7. Calculate risk scores
8. Return structured JSON output
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.osint.session_manager import SessionManager
from app.osint.collectors import (
    InstagramCollector,
    FacebookCollector,
    LinkedInCollector,
    TwitterCollector
)
from app.osint.parsers import (
    InstagramParser,
    FacebookParser,
    LinkedInParser,
    TwitterParser
)
from app.osint.discovery import IdentifierDetector, URLGenerator, SearchEngine

# Import existing services
from app.services.ner_engine import NEREngine
from app.services.pii_extractor import PIIExtractor
from app.services.username_analyzer import UsernameAnalyzer
from app.services.correlation import CrossPlatformCorrelator

logger = logging.getLogger(__name__)


# =============================================================================
# OSINT ORCHESTRATOR CLASS
# =============================================================================

class OSINTOrchestrator:
    """
    Orchestrates the complete OSINT data collection and analysis workflow.
    """
    
    # Platform to collector mapping
    COLLECTORS = {
        "instagram": InstagramCollector,
        "facebook": FacebookCollector,
        "linkedin": LinkedInCollector,
        "twitter": TwitterCollector
    }
    
    # Platform to parser mapping
    PARSERS = {
        "instagram": InstagramParser,
        "facebook": FacebookParser,
        "linkedin": LinkedInParser,
        "twitter": TwitterParser
    }
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.session_manager = SessionManager()
        self.identifier_detector = IdentifierDetector()
        self.url_generator = URLGenerator()
        self.search_engine = SearchEngine()
        
        # Initialize existing services
        self.ner_engine = NEREngine()
        self.pii_extractor = PIIExtractor()
        self.username_analyzer = UsernameAnalyzer()
        self.correlator = CrossPlatformCorrelator()
    
    async def analyze(
        self,
        identifier: str,
        platforms: Optional[List[str]] = None,
        use_search: bool = False
    ) -> Dict[str, Any]:
        """
        Perform comprehensive OSINT analysis.
        
        Args:
            identifier: Input identifier (username, email, name, phone)
            platforms: List of platforms to check (None = all)
            use_search: Whether to use Google Custom Search
        
        Returns:
            Structured analysis results
        """
        start_time = datetime.now()
        
        # Step 1: Detect identifier type
        identifier_type = self.identifier_detector.detect(identifier)
        logger.info(f"Detected identifier type: {identifier_type} for '{identifier}'")
        
        # Step 2: Extract username from identifier
        username = self._extract_username(identifier, identifier_type)
        
        # Step 3: Generate profile URLs
        if platforms is None:
            platforms = list(self.COLLECTORS.keys())
        
        profile_urls = {}
        for platform in platforms:
            try:
                url = self.url_generator.generate_url(platform, username)
                profile_urls[platform] = url
            except ValueError:
                logger.warning(f"Could not generate URL for {platform}")
        
        # Step 4: Collect data from platforms (parallel)
        collection_results = await self._collect_from_platforms(profile_urls)
        
        # Step 5: Parse collected HTML
        parsed_profiles = self._parse_profiles(collection_results)
        
        # Step 6: Integrate with existing analysis modules
        analyzed_profiles = await self._analyze_profiles(parsed_profiles, identifier, identifier_type)
        
        # Step 7: Cross-platform correlation
        correlation_results = self._correlate_profiles(analyzed_profiles)
        
        # Step 8: Calculate overall risk
        overall_risk = self._calculate_overall_risk(analyzed_profiles, correlation_results)
        
        # Step 9: Build final output
        result = {
            "input": identifier,
            "identifier_type": identifier_type,
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "profiles_found": analyzed_profiles,
            "correlation": correlation_results,
            "overall_risk": overall_risk,
            "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000
        }
        
        return result
    
    async def _collect_from_platforms(self, profile_urls: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """
        Collect data from multiple platforms in parallel.
        
        Args:
            profile_urls: Dict mapping platform to URL
        
        Returns:
            Dict mapping platform to collection results
        
        Raises:
            RuntimeError: If ALL platforms fail to collect data
        """
        tasks = []
        platform_names = []
        
        for platform, url in profile_urls.items():
            collector_class = self.COLLECTORS.get(platform)
            if collector_class:
                tasks.append(self._collect_from_platform(platform, url, collector_class))
                platform_names.append(platform)
        
        # Run collections in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Map results to platforms
        collection_results = {}
        successful_collections = 0
        browser_init_failures = 0
        
        for platform, result in zip(platform_names, results):
            if isinstance(result, RuntimeError):
                # Browser initialization failed
                logger.error(f"❌ [{platform}] Browser initialization failed: {result}")
                collection_results[platform] = {
                    "success": False,
                    "error": str(result),
                    "error_type": "browser_init_failure"
                }
                browser_init_failures += 1
                
            elif isinstance(result, Exception):
                logger.error(f"❌ [{platform}] Collection error: {result}")
                collection_results[platform] = {
                    "success": False,
                    "error": str(result),
                    "error_type": type(result).__name__
                }
                
            else:
                collection_results[platform] = result
                if result.get("success"):
                    successful_collections += 1
        
        # If ALL platforms failed due to browser issues, raise error
        if browser_init_failures == len(platform_names):
            raise RuntimeError(
                "All platform data collection failed due to browser initialization errors.\n"
                "This is likely due to Playwright not being properly installed or Python 3.13 compatibility issues.\n\n"
                "Solutions:\n"
                "  1. Run 'playwright install chromium'\n"
                "  2. Use Python 3.11.x or 3.12.x instead of Python 3.13\n"
                "  3. Check logs for detailed error messages"
            )
        
        # If no platforms succeeded, log warning
        if successful_collections == 0:
            logger.warning(
                f"⚠️  No platforms collected data successfully. "
                f"Failures: {len(platform_names)}, Browser init failures: {browser_init_failures}"
            )
        else:
            logger.info(f"✅ Successfully collected data from {successful_collections}/{len(platform_names)} platforms")
        
        return collection_results
    
    async def _collect_from_platform(
        self,
        platform: str,
        url: str,
        collector_class: type
    ) -> Dict[str, Any]:
        """
        Collect data from a single platform.
        
        Args:
            platform: Platform name
            url: Profile URL
            collector_class: Collector class to use
        
        Returns:
            Collection result
        
        Raises:
            RuntimeError: If browser initialization fails (propagated to caller)
        """
        collector = collector_class(self.session_manager)
        
        try:
            logger.info(f"[{platform}] Starting data collection from {url}")
            await collector.initialize_browser()
            result = await collector.collect_with_retry(url)
            
            if not result.get("success"):
                logger.warning(f"[{platform}] Collection failed: {result.get('error')}")
            else:
                logger.info(f"✅ [{platform}] Data collected successfully")
            
            return result
            
        except RuntimeError as e:
            # Browser initialization failed - propagate to caller for fail-fast handling
            logger.error(f"❌ [{platform}] CRITICAL: {e}")
            raise
            
        except Exception as e:
            logger.error(f"❌ [{platform}] Collection error: {e}")
            return {
                "success": False,
                "platform": platform,
                "url": url,
                "error": str(e),
                "error_type": type(e).__name__
            }
            
        finally:
            await collector.close_browser()
    
    def _parse_profiles(self, collection_results: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse collected HTML data.
        
        Args:
            collection_results: Collection results from platforms
        
        Returns:
            List of parsed profile data
        """
        parsed_profiles = []
        
        for platform, result in collection_results.items():
            if not result.get("success") or not result.get("html"):
                continue
            
            parser_class = self.PARSERS.get(platform)
            if not parser_class:
                continue
            
            try:
                parser = parser_class()
                parsed_data = parser.parse(result["html"])
                parsed_data["url"] = result.get("url")
                parsed_data["collection_success"] = True
                parsed_profiles.append(parsed_data)
            except Exception as e:
                logger.error(f"Error parsing {platform} profile: {e}")
        
        return parsed_profiles
    
    async def _analyze_profiles(
        self,
        profiles: List[Dict[str, Any]],
        original_identifier: str,
        identifier_type: str
    ) -> List[Dict[str, Any]]:
        """
        Analyze profiles with existing services.
        
        Args:
            profiles: Parsed profile data
            original_identifier: Original input identifier
            identifier_type: Type of identifier
        
        Returns:
            Profiles with analysis data
        """
        analyzed_profiles = []
        
        for profile in profiles:
            try:
                # Extract PII from bio and text
                bio_text = profile.get("bio") or ""
                pii_data = self.pii_extractor.extract_all(bio_text)
                
                # Also check for URLs in bio
                if profile.get("urls"):
                    if "urls" not in pii_data:
                        pii_data["urls"] = []
                    pii_data["urls"].extend(profile.get("urls", []))
                    # Deduplicate
                    pii_data["urls"] = list(set(pii_data["urls"]))
                
                # Extract email/phone from bio if present (additional patterns)
                if bio_text:
                    # Email pattern - comprehensive (fixed character class)
                    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', bio_text)
                    if emails:
                        if "emails" not in pii_data:
                            pii_data["emails"] = []
                        pii_data["emails"].extend(emails)
                        pii_data["emails"] = list(set(pii_data["emails"]))
                    
                    # Phone pattern (international) - more specific to avoid false positives
                    # Matches: +1-555-123-4567, (555) 123-4567, +44 20 1234 5678
                    # Requires phone-like formatting (parentheses, hyphens, or plus signs)
                    phone_pattern = r'(?:\+\d{1,3}[\s\-\.]?)?\(?\d{2,4}\)?[\s\-\.]?\d{3,4}[\s\-\.]?\d{3,4}'
                    potential_phones = re.findall(phone_pattern, bio_text)
                    if potential_phones:
                        if "phones" not in pii_data:
                            pii_data["phones"] = []
                        # Clean and validate phone numbers (must have at least 10 digits)
                        for phone in potential_phones:
                            digits = re.sub(r'[^\d]', '', phone)
                            if len(digits) >= 10:
                                pii_data["phones"].append(phone.strip())
                        pii_data["phones"] = list(set(pii_data["phones"]))
                
                # Run NER on bio and name
                combined_text = f"{profile.get('name', '')} {bio_text}"
                ner_data = self.ner_engine.extract_entities(combined_text)
                
                # Calculate username similarity
                profile_username = profile.get("username") or ""
                username_similarity = self._calculate_similarity(
                    original_identifier.lower(),
                    profile_username.lower()
                )
                
                # Calculate bio similarity
                bio_similarity = self._calculate_bio_similarity(
                    original_identifier,
                    bio_text,
                    identifier_type
                )
                
                # Calculate PII exposure score
                pii_exposure_score = self._calculate_pii_exposure(pii_data)
                
                # Calculate impersonation score
                impersonation_score = self._calculate_impersonation_score(
                    username_similarity,
                    bio_similarity,
                    pii_exposure_score
                )
                
                # Add analysis to profile
                profile["pii"] = pii_data
                profile["ner_entities"] = ner_data
                profile["analysis"] = {
                    "username_similarity": username_similarity,
                    "bio_similarity": bio_similarity,
                    "pii_exposure_score": pii_exposure_score,
                    "timeline_risk": self._assess_timeline_risk(profile),
                    "impersonation_score": impersonation_score
                }
                
                analyzed_profiles.append(profile)
                
            except Exception as e:
                logger.error(f"Error analyzing profile: {e}")
                analyzed_profiles.append(profile)
        
        return analyzed_profiles
    
    def _correlate_profiles(self, profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform cross-platform correlation.
        
        Args:
            profiles: Analyzed profiles
        
        Returns:
            Correlation results
        """
        if len(profiles) < 2:
            return {
                "correlated": False,
                "reason": "Not enough profiles for correlation"
            }
        
        try:
            # Convert to format expected by correlator
            profiles_for_correlation = []
            for p in profiles:
                profiles_for_correlation.append({
                    "source": p.get("platform"),
                    "username": p.get("username"),
                    "name": p.get("name"),
                    "bio": p.get("bio"),
                    "location": p.get("location"),
                    "job_title": p.get("job_title")
                })
            
            result = self.correlator.correlate(profiles_for_correlation)
            return {
                "correlated": True,
                "overlaps": result.overlaps,
                "contradictions": result.contradictions,
                "impersonation_score": result.impersonation_score,
                "impersonation_level": result.impersonation_level,
                "flags": result.flags
            }
            
        except Exception as e:
            logger.error(f"Error in correlation: {e}")
            return {
                "correlated": False,
                "error": str(e)
            }
    
    def _calculate_overall_risk(
        self,
        profiles: List[Dict[str, Any]],
        correlation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate overall risk assessment.
        
        Args:
            profiles: Analyzed profiles
            correlation: Correlation results
        
        Returns:
            Overall risk assessment
        """
        if not profiles:
            return {
                "exposure": "Low",
                "impersonation": "Unknown",
                "score": 0
            }
        
        # Calculate average PII exposure
        avg_pii_exposure = sum(
            p.get("analysis", {}).get("pii_exposure_score", 0)
            for p in profiles
        ) / len(profiles)
        
        # Calculate average impersonation score
        avg_impersonation = sum(
            p.get("analysis", {}).get("impersonation_score", 0)
            for p in profiles
        ) / len(profiles)
        
        # Determine exposure level
        if avg_pii_exposure >= 70:
            exposure_level = "High"
        elif avg_pii_exposure >= 40:
            exposure_level = "Medium"
        else:
            exposure_level = "Low"
        
        # Determine impersonation level
        if avg_impersonation >= 70:
            impersonation_level = "High"
        elif avg_impersonation >= 40:
            impersonation_level = "Medium"
        else:
            impersonation_level = "Low"
        
        # Use correlation impersonation level if available
        if correlation.get("correlated"):
            impersonation_level = correlation.get("impersonation_level", impersonation_level).capitalize()
        
        return {
            "exposure": exposure_level,
            "impersonation": impersonation_level,
            "score": int((avg_pii_exposure + avg_impersonation) / 2),
            "profiles_analyzed": len(profiles)
        }
    
    def _extract_username(self, identifier: str, identifier_type: str) -> str:
        """Extract username from identifier based on type."""
        if identifier_type == "email":
            return identifier.split('@')[0]
        elif identifier_type == "name":
            # For names, use the full name for searching (keep spaces)
            # Platforms will handle name-to-username matching
            return identifier.strip()
        else:
            return identifier.lstrip('@').strip()
    
    def _calculate_similarity(self, str1: str, str2: str) -> int:
        """Calculate simple similarity score (0-100)."""
        if not str1 or not str2:
            return 0
        
        # Exact match
        if str1 == str2:
            return 100
        
        # Substring match
        if str1 in str2 or str2 in str1:
            return 75
        
        # Calculate character overlap
        set1 = set(str1)
        set2 = set(str2)
        overlap = len(set1 & set2)
        total = len(set1 | set2)
        
        return int((overlap / total) * 50) if total > 0 else 0
    
    def _calculate_bio_similarity(self, identifier: str, bio: str, identifier_type: str) -> int:
        """Calculate bio similarity score."""
        if not bio:
            return 0
        
        bio_lower = bio.lower()
        
        # Check if identifier appears in bio
        if identifier.lower() in bio_lower:
            return 100
        
        # For names, check individual parts
        if identifier_type == "name":
            parts = identifier.lower().split()
            matches = sum(1 for part in parts if part in bio_lower)
            if matches > 0:
                return int((matches / len(parts)) * 100)
        
        return 0
    
    def _calculate_pii_exposure(self, pii_data: Dict[str, List]) -> int:
        """Calculate PII exposure score based on found PII."""
        score = 0
        
        # Weight different PII types
        if pii_data.get("emails"):
            score += len(pii_data["emails"]) * 20
        if pii_data.get("phones"):
            score += len(pii_data["phones"]) * 25
        if pii_data.get("urls"):
            score += len(pii_data["urls"]) * 5
        if pii_data.get("mentions"):
            score += len(pii_data["mentions"]) * 3
        
        return min(score, 100)
    
    def _calculate_impersonation_score(
        self,
        username_sim: int,
        bio_sim: int,
        pii_exposure: int
    ) -> int:
        """Calculate impersonation risk score."""
        # Weighted average
        score = (username_sim * 0.4 + bio_sim * 0.3 + pii_exposure * 0.3)
        return int(score)
    
    def _assess_timeline_risk(self, profile: Dict[str, Any]) -> str:
        """
        Assess timeline/posting risk level.
        
        Note: This is a placeholder stub. Full implementation would require
        analyzing post frequency, content types, and engagement patterns.
        """
        # TODO: Implement timeline analysis based on:
        # - Post frequency
        # - Content sensitivity
        # - Engagement patterns
        # - Temporal patterns
        return "medium"
