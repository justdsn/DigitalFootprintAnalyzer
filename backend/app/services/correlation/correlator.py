# =============================================================================
# CROSS-PLATFORM CORRELATOR
# =============================================================================
# Main correlation engine for analyzing profiles across social platforms.
# Detects overlaps, contradictions, and potential impersonation attempts.
# =============================================================================

"""
Cross-Platform Correlator

This module provides the main correlation engine for analyzing user profiles
across multiple social media platforms. It:

- Identifies matching information (overlaps)
- Detects conflicting information (contradictions)
- Calculates impersonation risk scores
- Generates warning flags and recommendations

Example:
    correlator = CrossPlatformCorrelator()
    result = correlator.correlate([
        {"platform": "facebook", "username": "john_doe", "name": "John Doe"},
        {"platform": "twitter", "username": "johndoe", "name": "John Doe"},
    ])
    print(result["impersonation_score"])  # 15
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from .fuzzy_matcher import FuzzyMatcher


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class PlatformProfile:
    """
    Represents a user profile from a social media platform.
    
    Attributes:
        platform: Platform name (e.g., "facebook", "twitter")
        username: Username on the platform
        name: Display name (optional)
        bio: Profile bio/description (optional)
        location: Location from profile (optional)
        email: Email address (optional)
        phone: Phone number (optional)
    """
    platform: str
    username: str
    name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "platform": self.platform,
            "username": self.username,
            "name": self.name,
            "bio": self.bio,
            "location": self.location,
            "email": self.email,
            "phone": self.phone,
        }


@dataclass
class CorrelationResult:
    """
    Result of cross-platform correlation analysis.
    
    Attributes:
        overlaps: List of matching information across platforms
        contradictions: List of conflicting information
        impersonation_score: Risk score 0-100
        impersonation_level: Risk level (low/medium/high/critical)
        flags: Warning flags identified
        recommendations: Suggested actions
    """
    overlaps: List[Dict[str, Any]] = field(default_factory=list)
    contradictions: List[Dict[str, Any]] = field(default_factory=list)
    impersonation_score: int = 0
    impersonation_level: str = "low"
    flags: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "overlaps": self.overlaps,
            "contradictions": self.contradictions,
            "impersonation_score": self.impersonation_score,
            "impersonation_level": self.impersonation_level,
            "flags": self.flags,
            "recommendations": self.recommendations,
        }


# =============================================================================
# CROSS-PLATFORM CORRELATOR CLASS
# =============================================================================

class CrossPlatformCorrelator:
    """
    Cross-platform profile correlation engine.
    
    Analyzes profiles from multiple platforms to identify:
    - Consistent information (overlaps) suggesting same person
    - Contradictory information suggesting different people
    - Potential impersonation attempts
    
    Attributes:
        matcher: FuzzyMatcher instance for string comparison
        name_threshold: Similarity threshold for name matching (0-100)
        username_threshold: Similarity threshold for username matching
        bio_threshold: Similarity threshold for bio matching
        
    Example:
        >>> correlator = CrossPlatformCorrelator()
        >>> profiles = [
        ...     PlatformProfile("facebook", "john_doe", name="John Doe"),
        ...     PlatformProfile("twitter", "johndoe", name="John D"),
        ... ]
        >>> result = correlator.correlate(profiles)
        >>> print(result.impersonation_level)
        'low'
    """
    
    def __init__(
        self,
        name_threshold: float = 75.0,
        username_threshold: float = 80.0,
        bio_threshold: float = 60.0
    ):
        """
        Initialize the correlator with matching thresholds.
        
        Args:
            name_threshold: Min similarity for name matches (0-100)
            username_threshold: Min similarity for username matches
            bio_threshold: Min similarity for bio matches
        """
        self.matcher = FuzzyMatcher()
        self.name_threshold = name_threshold
        self.username_threshold = username_threshold
        self.bio_threshold = bio_threshold
    
    # =========================================================================
    # MAIN CORRELATION
    # =========================================================================
    
    def correlate(
        self,
        profiles: List[Dict[str, Any]]
    ) -> CorrelationResult:
        """
        Correlate profiles across platforms for impersonation detection.
        
        This is the main entry point for correlation analysis. It:
        1. Converts dicts to PlatformProfile objects
        2. Finds overlapping information
        3. Finds contradictory information
        4. Calculates impersonation score
        5. Generates flags and recommendations
        
        Args:
            profiles: List of profile dictionaries with platform data
            
        Returns:
            CorrelationResult: Complete analysis results
            
        Example:
            >>> result = correlator.correlate([
            ...     {"platform": "facebook", "username": "john"},
            ...     {"platform": "twitter", "username": "john_official"}
            ... ])
        """
        if not profiles or len(profiles) < 2:
            return CorrelationResult(
                recommendations=["Add more profiles for correlation analysis"]
            )
        
        # Convert to PlatformProfile objects
        profile_objects = self._parse_profiles(profiles)
        
        if len(profile_objects) < 2:
            return CorrelationResult(
                recommendations=["Add more profiles for correlation analysis"]
            )
        
        # Perform correlation analysis
        overlaps = self.find_overlaps(profile_objects)
        contradictions = self.find_contradictions(profile_objects)
        
        # Build analysis context
        analysis = {
            "profiles": profile_objects,
            "overlaps": overlaps,
            "contradictions": contradictions,
        }
        
        # Calculate impersonation score
        score = self.calculate_impersonation_score(analysis)
        level = self._score_to_level(score)
        
        # Generate flags and recommendations
        flags = self.generate_flags(analysis)
        recommendations = self.generate_recommendations(analysis)
        
        return CorrelationResult(
            overlaps=overlaps,
            contradictions=contradictions,
            impersonation_score=score,
            impersonation_level=level,
            flags=flags,
            recommendations=recommendations,
        )
    
    def _parse_profiles(self, profiles: List[Dict[str, Any]]) -> List[PlatformProfile]:
        """
        Parse profile dictionaries into PlatformProfile objects.
        
        Args:
            profiles: List of profile dictionaries
            
        Returns:
            List[PlatformProfile]: Parsed profile objects
        """
        result = []
        for p in profiles:
            if isinstance(p, PlatformProfile):
                result.append(p)
            elif isinstance(p, dict) and "platform" in p and "username" in p:
                result.append(PlatformProfile(
                    platform=p.get("platform", ""),
                    username=p.get("username", ""),
                    name=p.get("name"),
                    bio=p.get("bio"),
                    location=p.get("location"),
                    email=p.get("email"),
                    phone=p.get("phone"),
                ))
        return result
    
    # =========================================================================
    # OVERLAP DETECTION
    # =========================================================================
    
    def find_overlaps(self, profiles: List[PlatformProfile]) -> List[Dict[str, Any]]:
        """
        Find matching information across platforms.
        
        Checks for matches in:
        - Usernames (similar or identical)
        - Display names
        - Bios/descriptions
        - Locations
        - Email addresses
        - Phone numbers
        
        Args:
            profiles: List of profile objects
            
        Returns:
            List of overlap dictionaries with field, platforms, values, and score
        """
        overlaps = []
        
        # Compare each pair of profiles
        for i, p1 in enumerate(profiles):
            for p2 in profiles[i+1:]:
                pair_overlaps = self._compare_profiles(p1, p2)
                overlaps.extend(pair_overlaps)
        
        return overlaps
    
    def _compare_profiles(
        self,
        p1: PlatformProfile,
        p2: PlatformProfile
    ) -> List[Dict[str, Any]]:
        """
        Compare two profiles for matching information.
        
        Args:
            p1: First profile
            p2: Second profile
            
        Returns:
            List of overlap dictionaries
        """
        overlaps = []
        platforms = [p1.platform, p2.platform]
        
        # Compare usernames
        if p1.username and p2.username:
            score = self.matcher.match_usernames(p1.username, p2.username)
            if score >= self.username_threshold:
                overlaps.append({
                    "field": "username",
                    "platforms": platforms,
                    "values": [p1.username, p2.username],
                    "score": round(score, 1),
                    "match_type": "exact" if score >= 99 else "similar"
                })
        
        # Compare names
        if p1.name and p2.name:
            score = self.matcher.match_names(p1.name, p2.name)
            if score >= self.name_threshold:
                overlaps.append({
                    "field": "name",
                    "platforms": platforms,
                    "values": [p1.name, p2.name],
                    "score": round(score, 1),
                    "match_type": "exact" if score >= 99 else "similar"
                })
        
        # Compare bios
        if p1.bio and p2.bio:
            score = self.matcher.match_bios(p1.bio, p2.bio)
            if score >= self.bio_threshold:
                overlaps.append({
                    "field": "bio",
                    "platforms": platforms,
                    "values": [p1.bio[:100], p2.bio[:100]],  # Truncate for display
                    "score": round(score, 1),
                    "match_type": "similar"
                })
        
        # Compare locations (exact match)
        if p1.location and p2.location:
            loc1 = p1.location.lower().strip()
            loc2 = p2.location.lower().strip()
            if loc1 == loc2:
                overlaps.append({
                    "field": "location",
                    "platforms": platforms,
                    "values": [p1.location, p2.location],
                    "score": 100.0,
                    "match_type": "exact"
                })
        
        # Compare emails (exact match)
        if p1.email and p2.email:
            email1 = p1.email.lower().strip()
            email2 = p2.email.lower().strip()
            if email1 == email2:
                overlaps.append({
                    "field": "email",
                    "platforms": platforms,
                    "values": [p1.email, p2.email],
                    "score": 100.0,
                    "match_type": "exact"
                })
        
        # Compare phones (normalized comparison)
        if p1.phone and p2.phone:
            phone1 = self._normalize_phone(p1.phone)
            phone2 = self._normalize_phone(p2.phone)
            if phone1 == phone2:
                overlaps.append({
                    "field": "phone",
                    "platforms": platforms,
                    "values": [p1.phone, p2.phone],
                    "score": 100.0,
                    "match_type": "exact"
                })
        
        return overlaps
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number for comparison."""
        if not phone:
            return ""
        # Remove all non-digit characters
        return ''.join(c for c in phone if c.isdigit())
    
    # =========================================================================
    # CONTRADICTION DETECTION
    # =========================================================================
    
    def find_contradictions(
        self,
        profiles: List[PlatformProfile]
    ) -> List[Dict[str, Any]]:
        """
        Find conflicting information across platforms.
        
        Contradictions indicate potential impersonation or data inconsistency:
        - Different names with similar usernames
        - Different locations with same name
        - Conflicting contact information
        
        Args:
            profiles: List of profile objects
            
        Returns:
            List of contradiction dictionaries
        """
        contradictions = []
        
        # Compare each pair of profiles
        for i, p1 in enumerate(profiles):
            for p2 in profiles[i+1:]:
                pair_contradictions = self._find_contradictions_pair(p1, p2)
                contradictions.extend(pair_contradictions)
        
        return contradictions
    
    def _find_contradictions_pair(
        self,
        p1: PlatformProfile,
        p2: PlatformProfile
    ) -> List[Dict[str, Any]]:
        """
        Find contradictions between two profiles.
        
        Args:
            p1: First profile
            p2: Second profile
            
        Returns:
            List of contradiction dictionaries
        """
        contradictions = []
        platforms = [p1.platform, p2.platform]
        
        # Check for username similarity with name mismatch
        if p1.username and p2.username and p1.name and p2.name:
            username_score = self.matcher.match_usernames(p1.username, p2.username)
            name_score = self.matcher.match_names(p1.name, p2.name)
            
            # Similar usernames but different names
            if username_score >= 85 and name_score < 50:
                contradictions.append({
                    "type": "name_mismatch",
                    "description": "Similar usernames but different display names",
                    "platforms": platforms,
                    "details": {
                        "usernames": [p1.username, p2.username],
                        "username_similarity": round(username_score, 1),
                        "names": [p1.name, p2.name],
                        "name_similarity": round(name_score, 1),
                    },
                    "severity": "high"
                })
        
        # Check for name match with location mismatch
        if p1.name and p2.name and p1.location and p2.location:
            name_score = self.matcher.match_names(p1.name, p2.name)
            loc1 = p1.location.lower().strip()
            loc2 = p2.location.lower().strip()
            
            # Same name but different locations
            if name_score >= 90 and loc1 != loc2:
                contradictions.append({
                    "type": "location_mismatch",
                    "description": "Same name but different locations",
                    "platforms": platforms,
                    "details": {
                        "name": p1.name,
                        "locations": [p1.location, p2.location],
                    },
                    "severity": "medium"
                })
        
        # Check for different emails with same name
        if p1.name and p2.name and p1.email and p2.email:
            name_score = self.matcher.match_names(p1.name, p2.name)
            email1 = p1.email.lower().strip()
            email2 = p2.email.lower().strip()
            
            if name_score >= 90 and email1 != email2:
                contradictions.append({
                    "type": "email_mismatch",
                    "description": "Same name but different email addresses",
                    "platforms": platforms,
                    "details": {
                        "name": p1.name,
                        "emails": [p1.email, p2.email],
                    },
                    "severity": "low"  # Different emails are common
                })
        
        return contradictions
    
    # =========================================================================
    # IMPERSONATION SCORING
    # =========================================================================
    
    def calculate_impersonation_score(self, analysis: Dict[str, Any]) -> int:
        """
        Calculate impersonation risk score from analysis results.
        
        Score factors:
        - Number of profiles (more = higher risk potential)
        - Contradictions (weighted by severity)
        - Overlap patterns (suspicious vs. normal)
        
        Args:
            analysis: Analysis context with profiles, overlaps, contradictions
            
        Returns:
            int: Risk score 0-100
        """
        score = 0
        
        profiles = analysis.get("profiles", [])
        overlaps = analysis.get("overlaps", [])
        contradictions = analysis.get("contradictions", [])
        
        # Base score from contradictions
        for c in contradictions:
            severity = c.get("severity", "low")
            if severity == "critical":
                score += 30
            elif severity == "high":
                score += 20
            elif severity == "medium":
                score += 10
            else:
                score += 5
        
        # Check for suspicious patterns
        
        # Many profiles with no overlaps = suspicious
        if len(profiles) >= 3 and len(overlaps) == 0:
            score += 15
        
        # Username similarity without other matches
        username_overlaps = [o for o in overlaps if o["field"] == "username"]
        name_overlaps = [o for o in overlaps if o["field"] == "name"]
        
        if username_overlaps and not name_overlaps:
            # Similar usernames but no name matches
            score += 25
        
        # Check for typosquatting indicators
        for i, p1 in enumerate(profiles):
            for p2 in profiles[i+1:]:
                is_typo, typo_score, techniques = self.matcher.detect_typosquatting(
                    p1.username, p2.username
                )
                if is_typo and techniques:
                    score += 30
        
        # Cap score at 100
        return min(score, 100)
    
    def _score_to_level(self, score: int) -> str:
        """
        Convert numeric score to risk level.
        
        Args:
            score: Risk score 0-100
            
        Returns:
            str: Risk level (low/medium/high/critical)
        """
        if score >= 70:
            return "critical"
        elif score >= 50:
            return "high"
        elif score >= 30:
            return "medium"
        else:
            return "low"
    
    # =========================================================================
    # FLAGS AND RECOMMENDATIONS
    # =========================================================================
    
    def generate_flags(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate warning flags from analysis results.
        
        Args:
            analysis: Analysis context
            
        Returns:
            List[str]: Warning flag messages
        """
        flags = []
        
        contradictions = analysis.get("contradictions", [])
        profiles = analysis.get("profiles", [])
        
        # Flag critical contradictions
        for c in contradictions:
            if c.get("severity") == "high":
                flags.append(f"⚠️ {c['description']} on {', '.join(c['platforms'])}")
        
        # Flag typosquatting detection
        for i, p1 in enumerate(profiles):
            for p2 in profiles[i+1:]:
                is_typo, _, techniques = self.matcher.detect_typosquatting(
                    p1.username, p2.username
                )
                if is_typo and techniques:
                    flags.append(
                        f"🚨 Potential typosquatting detected between "
                        f"@{p1.username} ({p1.platform}) and "
                        f"@{p2.username} ({p2.platform}): {', '.join(techniques)}"
                    )
        
        # Flag many profiles with no overlaps
        overlaps = analysis.get("overlaps", [])
        if len(profiles) >= 3 and len(overlaps) == 0:
            flags.append(
                "⚠️ Multiple profiles found with no matching information - "
                "verify ownership"
            )
        
        return flags
    
    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on analysis results.
        
        Args:
            analysis: Analysis context
            
        Returns:
            List[str]: Recommendation messages
        """
        recommendations = []
        
        contradictions = analysis.get("contradictions", [])
        overlaps = analysis.get("overlaps", [])
        profiles = analysis.get("profiles", [])
        
        # Recommendations based on contradictions
        if contradictions:
            recommendations.append(
                "Review the conflicting information across platforms and update "
                "profiles to maintain consistency"
            )
        
        # Recommendations for name mismatches
        name_mismatches = [
            c for c in contradictions
            if c.get("type") == "name_mismatch"
        ]
        if name_mismatches:
            recommendations.append(
                "Consider using consistent display names across platforms to "
                "establish your authentic identity"
            )
        
        # Recommendations for typosquatting
        for i, p1 in enumerate(profiles):
            for p2 in profiles[i+1:]:
                is_typo, _, _ = self.matcher.detect_typosquatting(
                    p1.username, p2.username
                )
                if is_typo:
                    recommendations.append(
                        f"Report the suspicious account @{p2.username} on {p2.platform} "
                        "if you believe it's impersonating you"
                    )
                    break
        
        # General recommendations
        if len(profiles) >= 2:
            recommendations.append(
                "Enable two-factor authentication on all accounts to prevent "
                "unauthorized access"
            )
            
            if not any(p.email for p in profiles):
                recommendations.append(
                    "Consider adding verified email addresses to your profiles "
                    "for better account recovery options"
                )
        
        # If no major issues found
        if not contradictions and len(profiles) >= 2:
            recommendations.append(
                "Your profiles appear consistent. Continue monitoring for "
                "potential impersonation accounts periodically"
            )
        
        return recommendations


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

_default_correlator = CrossPlatformCorrelator()


def correlate(profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Module-level convenience function for correlation."""
    result = _default_correlator.correlate(profiles)
    return result.to_dict()


def find_overlaps(profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Module-level convenience function for finding overlaps."""
    profile_objects = _default_correlator._parse_profiles(profiles)
    return _default_correlator.find_overlaps(profile_objects)


def find_contradictions(profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Module-level convenience function for finding contradictions."""
    profile_objects = _default_correlator._parse_profiles(profiles)
    return _default_correlator.find_contradictions(profile_objects)
