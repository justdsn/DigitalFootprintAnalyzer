# =============================================================================
# HYBRID PROFILE FINDER SERVICE
# =============================================================================
# Combines Google Dorking with direct URL checking for profile discovery.
# Supports multiple identifier types: name, email, username, phone.
# =============================================================================

"""
Hybrid Profile Finder Service

This module combines two methods for finding social media profiles:
1. Google Dorking - Searches Google with platform-specific dork queries
2. Direct URL Checking - Checks if profile URLs exist directly

Features:
- Search by any single identifier (name, email, username, phone)
- Generate username variations from name/email
- Sri Lanka focused (location filtering, phone formats)
- Deduplicate results from both methods
- No authentication needed

Example Usage:
    finder = HybridProfileFinder()
    
    # Search by username
    results = await finder.find_profiles("john_doe", "username")
    
    # Search by email (extracts username)
    results = await finder.find_profiles("john@gmail.com", "email")
    
    # Search by name (generates username variations)
    results = await finder.find_profiles("John Perera", "name")
    
    # Search by phone (Sri Lankan formats)
    results = await finder.find_profiles("0771234567", "phone")
"""

import asyncio
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import logging

from .google_dorker import GoogleDorkSearcher
from .profile_checker import ProfileExistenceChecker
from .profile_generator import ProfileURLGenerator

# Set up logger
logger = logging.getLogger(__name__)


class HybridProfileFinder:
    """
    Hybrid profile finder combining Google Dorking and direct URL checking.
    
    This class provides a comprehensive approach to finding social media
    profiles using multiple discovery methods and identifier types.
    
    Methods:
    1. Google Dorking: Generates search queries for profile discovery
    2. Direct URL Checking: Verifies if profiles exist at predicted URLs
    
    Attributes:
        google_dorker: GoogleDorkSearcher instance
        profile_checker: ProfileExistenceChecker instance
        url_generator: ProfileURLGenerator instance
    """
    
    # -------------------------------------------------------------------------
    # COMMON NAME PATTERNS FOR USERNAME GENERATION
    # -------------------------------------------------------------------------
    COMMON_SUFFIXES = ["1", "2", "123", "007", "99", "lk", "_lk"]
    
    def __init__(self):
        """Initialize the Hybrid Profile Finder."""
        self.google_dorker = GoogleDorkSearcher()
        self.profile_checker = ProfileExistenceChecker()
        self.url_generator = ProfileURLGenerator()
    
    # -------------------------------------------------------------------------
    # MAIN PUBLIC METHOD
    # -------------------------------------------------------------------------
    
    async def find_profiles(
        self,
        identifier: str,
        identifier_type: str,
        location: Optional[str] = "Sri Lanka",
        check_existence: bool = True
    ) -> Dict[str, Any]:
        """
        Find social media profiles using hybrid approach.
        
        Combines Google Dorking and direct URL checking to discover
        profiles for the given identifier.
        
        Args:
            identifier: The identifier value (name, email, username, or phone)
            identifier_type: Type of identifier ('name', 'email', 'username', 'phone')
            location: Optional location filter for name searches (default: "Sri Lanka")
            check_existence: Whether to verify profile existence (default: True)
        
        Returns:
            Dict containing:
                - identifier: The original identifier
                - identifier_type: Type of identifier
                - timestamp: Scan timestamp
                - dork_results: Results from Google Dorking
                - direct_check_results: Results from direct URL checking
                - combined_results: Deduplicated combined results
                - username_variations: Generated username variations
                - platforms_checked: List of platforms checked
                - summary: Summary statistics
        
        Example:
            >>> await finder.find_profiles("john_doe", "username")
            {
                'identifier': 'john_doe',
                'identifier_type': 'username',
                'combined_results': {...},
                'summary': {'total_found': 3, 'platforms_with_profiles': 2}
            }
        """
        if not identifier or not identifier.strip():
            return self._empty_result(identifier, identifier_type)
        
        identifier = identifier.strip()
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        # Step 1: Generate usernames to check based on identifier type
        usernames_to_check = self._get_usernames_to_check(
            identifier, identifier_type
        )
        
        # Step 2: Get Google Dork results
        dork_results = self._get_dork_results(
            identifier, identifier_type, location
        )
        
        # Step 3: Direct URL checking (if enabled)
        direct_check_results = {}
        if check_existence and usernames_to_check:
            direct_check_results = await self._check_profiles_directly(
                usernames_to_check
            )
        
        # Step 4: Combine and deduplicate results
        combined_results = self._combine_results(
            dork_results, direct_check_results, usernames_to_check
        )
        
        # Step 5: Build summary
        summary = self._build_summary(combined_results, direct_check_results)
        
        return {
            "identifier": identifier,
            "identifier_type": identifier_type,
            "timestamp": timestamp,
            "location_filter": location if identifier_type == "name" else None,
            "dork_results": dork_results,
            "direct_check_results": direct_check_results,
            "combined_results": combined_results,
            "username_variations": usernames_to_check,
            "platforms_checked": self.google_dorker.get_supported_platforms(),
            "summary": summary
        }
    
    # -------------------------------------------------------------------------
    # USERNAME GENERATION METHODS
    # -------------------------------------------------------------------------
    
    def _get_usernames_to_check(
        self, 
        identifier: str, 
        identifier_type: str
    ) -> List[str]:
        """
        Get list of usernames to check based on identifier type.
        
        Args:
            identifier: The identifier value
            identifier_type: Type of identifier
        
        Returns:
            List of usernames to check
        """
        if identifier_type == "username":
            return self._generate_username_variations(identifier)
        elif identifier_type == "email":
            return self._generate_usernames_from_email(identifier)
        elif identifier_type == "name":
            return self._generate_usernames_from_name(identifier)
        elif identifier_type == "phone":
            # Phone numbers don't typically map to usernames directly
            # Return empty list for direct checking
            return []
        else:
            return []
    
    def _generate_username_variations(self, username: str) -> List[str]:
        """
        Generate common variations of a username.
        
        Args:
            username: Base username
        
        Returns:
            List of username variations
        """
        username = username.strip().lstrip('@').lower()
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
        
        # Leading/trailing underscore
        variations.add(f"_{username}")
        variations.add(f"{username}_")
        
        # Clean version (no special chars)
        clean = re.sub(r'[^a-z0-9]', '', username)
        variations.add(clean)
        
        # Common suffixes on clean version
        for suffix in self.COMMON_SUFFIXES:
            variations.add(f"{clean}{suffix}")
        
        # Filter out empty strings
        variations.discard('')
        
        return list(variations)
    
    def _generate_usernames_from_email(self, email: str) -> List[str]:
        """
        Generate potential usernames from an email address.
        
        Args:
            email: Email address
        
        Returns:
            List of potential usernames
        """
        email = email.strip().lower()
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return []
        
        # Extract username from email
        email_username = email.split('@')[0]
        
        # Generate variations from email username
        return self._generate_username_variations(email_username)
    
    def _generate_usernames_from_name(self, name: str) -> List[str]:
        """
        Generate potential usernames from a full name.
        
        Common patterns:
        - firstname (john)
        - lastname (perera)
        - firstnamelastname (johnperera)
        - firstname_lastname (john_perera)
        - firstname.lastname (john.perera)
        - flastname (jperera)
        - firstnamel (johnp)
        
        Args:
            name: Full name
        
        Returns:
            List of potential usernames
        """
        name = name.strip()
        
        if not name:
            return []
        
        variations = set()
        
        # Split name into parts
        parts = name.lower().split()
        
        if len(parts) == 0:
            return []
        
        # Single name
        if len(parts) == 1:
            base = parts[0]
            base = re.sub(r'[^a-z0-9]', '', base)
            variations.add(base)
            for suffix in self.COMMON_SUFFIXES:
                variations.add(f"{base}{suffix}")
            return list(filter(None, variations))
        
        # Two or more parts
        first = re.sub(r'[^a-z]', '', parts[0])
        last = re.sub(r'[^a-z]', '', parts[-1])
        
        if not first or not last:
            return []
        
        # Common username patterns
        variations.add(first)  # john
        variations.add(last)   # perera
        variations.add(f"{first}{last}")  # johnperera
        variations.add(f"{first}_{last}")  # john_perera
        variations.add(f"{first}.{last}")  # john.perera
        variations.add(f"{first[0]}{last}")  # jperera
        variations.add(f"{first}{last[0]}")  # johnp
        variations.add(f"{last}{first}")  # pererajohn
        variations.add(f"{last}_{first}")  # perera_john
        variations.add(f"{last}.{first}")  # perera.john
        
        # With common suffixes
        base = f"{first}{last}"
        for suffix in self.COMMON_SUFFIXES:
            variations.add(f"{base}{suffix}")
        
        # Filter out empty strings
        variations.discard('')
        
        return list(variations)
    
    # -------------------------------------------------------------------------
    # DORK SEARCH METHODS
    # -------------------------------------------------------------------------
    
    def _get_dork_results(
        self,
        identifier: str,
        identifier_type: str,
        location: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Get Google Dork search results based on identifier type.
        
        Args:
            identifier: The identifier value
            identifier_type: Type of identifier
            location: Optional location filter
        
        Returns:
            List of dork search results
        """
        if identifier_type == "name":
            return self.google_dorker.search_by_name(identifier, location)
        elif identifier_type == "email":
            return self.google_dorker.search_by_email(identifier)
        elif identifier_type == "username":
            return self.google_dorker.search_by_username(identifier)
        elif identifier_type == "phone":
            return self.google_dorker.search_by_phone(identifier)
        else:
            return []
    
    # -------------------------------------------------------------------------
    # DIRECT URL CHECKING METHODS
    # -------------------------------------------------------------------------
    
    async def _check_profiles_directly(
        self,
        usernames: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Check profile existence directly for usernames.
        
        Args:
            usernames: List of usernames to check
        
        Returns:
            Dict of check results by username
        """
        results = {}
        
        # Limit to first 5 variations to avoid too many requests
        usernames_to_check = usernames[:5] if len(usernames) > 5 else usernames
        
        for username in usernames_to_check:
            check_result = await self.profile_checker.check_all_platforms(username)
            results[username] = check_result
        
        return results
    
    # -------------------------------------------------------------------------
    # RESULT COMBINATION AND DEDUPLICATION
    # -------------------------------------------------------------------------
    
    def _combine_results(
        self,
        dork_results: List[Dict[str, Any]],
        direct_results: Dict[str, Dict[str, Any]],
        usernames: List[str]
    ) -> Dict[str, Any]:
        """
        Combine and deduplicate results from both methods.
        
        Args:
            dork_results: Results from Google Dorking
            direct_results: Results from direct URL checking
            usernames: List of usernames checked
        
        Returns:
            Combined results dictionary
        """
        combined = {
            "by_platform": {},
            "found_profiles": [],
            "search_queries": []
        }
        
        # Initialize platforms
        for platform_id in self.google_dorker.get_supported_platforms():
            platform_name = self.google_dorker.PLATFORM_DORKS[platform_id]["name"]
            combined["by_platform"][platform_id] = {
                "name": platform_name,
                "status": "unknown",
                "found_usernames": [],
                "search_urls": [],
                "direct_check_url": None
            }
        
        # Add dork search URLs
        for dork in dork_results:
            platform_id = dork.get("platform_id")
            if platform_id and platform_id in combined["by_platform"]:
                combined["by_platform"][platform_id]["search_urls"].append({
                    "query": dork.get("query"),
                    "url": dork.get("search_url"),
                    "search_type": dork.get("search_type")
                })
                combined["search_queries"].append({
                    "platform": dork.get("platform"),
                    "query": dork.get("query"),
                    "search_url": dork.get("search_url")
                })
        
        # Add direct check results
        for username, check_data in direct_results.items():
            results = check_data.get("results", {})
            for platform_id, result in results.items():
                if platform_id in combined["by_platform"]:
                    status = result.get("status")
                    url = result.get("url")
                    
                    if status == "exists":
                        combined["by_platform"][platform_id]["status"] = "found"
                        combined["by_platform"][platform_id]["found_usernames"].append(username)
                        combined["by_platform"][platform_id]["direct_check_url"] = url
                        
                        # Add to found profiles list (deduplicated)
                        profile_entry = {
                            "platform": result.get("platform"),
                            "platform_id": platform_id,
                            "username": username,
                            "url": url,
                            "status": status,
                            "method": "direct_check"
                        }
                        
                        # Check if already in list
                        if not any(
                            p["platform_id"] == platform_id and p["username"] == username 
                            for p in combined["found_profiles"]
                        ):
                            combined["found_profiles"].append(profile_entry)
                    
                    elif status == "private":
                        if combined["by_platform"][platform_id]["status"] != "found":
                            combined["by_platform"][platform_id]["status"] = "private"
                    
                    elif status == "not_found":
                        if combined["by_platform"][platform_id]["status"] == "unknown":
                            combined["by_platform"][platform_id]["status"] = "not_found"
        
        return combined
    
    def _build_summary(
        self,
        combined_results: Dict[str, Any],
        direct_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build summary statistics from results.
        
        Args:
            combined_results: Combined results
            direct_results: Direct check results
        
        Returns:
            Summary dictionary
        """
        found_count = len(combined_results.get("found_profiles", []))
        platforms_with_profiles = sum(
            1 for p in combined_results.get("by_platform", {}).values()
            if p.get("status") == "found"
        )
        total_search_queries = len(combined_results.get("search_queries", []))
        usernames_checked = len(direct_results)
        
        return {
            "total_profiles_found": found_count,
            "platforms_with_profiles": platforms_with_profiles,
            "total_platforms_checked": len(combined_results.get("by_platform", {})),
            "total_search_queries": total_search_queries,
            "usernames_checked": usernames_checked
        }
    
    def _empty_result(
        self, 
        identifier: str, 
        identifier_type: str
    ) -> Dict[str, Any]:
        """
        Return an empty result structure.
        
        Args:
            identifier: The identifier value
            identifier_type: Type of identifier
        
        Returns:
            Empty result dictionary
        """
        return {
            "identifier": identifier,
            "identifier_type": identifier_type,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "location_filter": None,
            "dork_results": [],
            "direct_check_results": {},
            "combined_results": {
                "by_platform": {},
                "found_profiles": [],
                "search_queries": []
            },
            "username_variations": [],
            "platforms_checked": [],
            "summary": {
                "total_profiles_found": 0,
                "platforms_with_profiles": 0,
                "total_platforms_checked": 0,
                "total_search_queries": 0,
                "usernames_checked": 0
            }
        }


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

_default_finder = HybridProfileFinder()


async def find_profiles(
    identifier: str,
    identifier_type: str,
    location: Optional[str] = "Sri Lanka",
    check_existence: bool = True
) -> Dict[str, Any]:
    """Module-level convenience function for finding profiles."""
    return await _default_finder.find_profiles(
        identifier, identifier_type, location, check_existence
    )


def generate_usernames_from_name(name: str) -> List[str]:
    """Module-level convenience function for generating usernames from name."""
    return _default_finder._generate_usernames_from_name(name)


def generate_usernames_from_email(email: str) -> List[str]:
    """Module-level convenience function for generating usernames from email."""
    return _default_finder._generate_usernames_from_email(email)
