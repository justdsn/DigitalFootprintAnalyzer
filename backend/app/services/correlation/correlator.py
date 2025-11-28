# =============================================================================
# CROSS-PLATFORM CORRELATOR
# =============================================================================
# Main correlation engine for comparing PII across social media platforms.
# Detects overlaps, contradictions, and calculates impersonation risk score.
# =============================================================================

"""
Cross-Platform Correlator Module

This module provides the Correlator class which:
- Compares PII fields across multiple platform profiles
- Identifies overlapping information (shared PII)
- Detects contradictions (conflicting information)
- Calculates an impersonation risk score (0-100)

The correlator is designed to analyze profiles from different social
media platforms and determine if they likely belong to the same person
or if there's evidence of impersonation.

Example Usage:
    correlator = Correlator()
    
    profiles = [
        {'platform': 'facebook', 'username': 'john_doe', 'name': 'John Doe', ...},
        {'platform': 'instagram', 'username': 'johndoe', 'name': 'John D', ...},
    ]
    
    result = correlator.correlate_profiles(profiles)
    # Returns: {
    #     'overlaps': [{'field': 'name', 'match_score': 0.85, ...}],
    #     'contradictions': [],
    #     'impersonation_score': 25,
    #     'risk_level': 'low'
    # }
"""

from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import re

from app.services.correlation.similarity_scorer import SimilarityScorer
from app.services.correlation.fuzzy_matcher import FuzzyMatcher


# =============================================================================
# DATA CLASSES AND ENUMS
# =============================================================================

class RiskLevel(str, Enum):
    """Risk level classifications for impersonation detection."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ProfileData:
    """
    Represents a social media profile's PII data.
    
    Attributes:
        platform: Social media platform name (e.g., 'facebook', 'instagram')
        username: Profile username/handle
        name: Display name or real name
        bio: Profile bio/description text
        location: Stated location
        email: Email address if public
        phone: Phone number if public
        profile_url: Direct URL to the profile
    """
    platform: str
    username: str
    name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    profile_url: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProfileData':
        """Create a ProfileData instance from a dictionary."""
        return cls(
            platform=data.get('platform', 'unknown'),
            username=data.get('username', ''),
            name=data.get('name'),
            bio=data.get('bio'),
            location=data.get('location'),
            email=data.get('email'),
            phone=data.get('phone'),
            profile_url=data.get('profile_url')
        )


@dataclass
class Overlap:
    """
    Represents an overlap (shared information) between profiles.
    
    Attributes:
        field: The PII field that overlaps (e.g., 'name', 'location')
        platforms: List of platform names where the overlap was found
        values: The matching values from each platform
        match_score: Similarity score (0.0 to 1.0)
        description: Human-readable description of the overlap
    """
    field: str
    platforms: List[str]
    values: List[str]
    match_score: float
    description: str


@dataclass
class Contradiction:
    """
    Represents a contradiction (conflicting information) between profiles.
    
    Attributes:
        field: The PII field that contradicts (e.g., 'location')
        platforms: The two platforms with conflicting info
        values: The conflicting values [platform1_value, platform2_value]
        severity: Severity level ('low', 'medium', 'high')
        description: Human-readable description of the contradiction
    """
    field: str
    platforms: List[str]
    values: List[str]
    severity: str
    description: str


# =============================================================================
# CORRELATOR CLASS
# =============================================================================

class Correlator:
    """
    Main correlation engine for cross-platform PII comparison.
    
    This class analyzes multiple social media profiles and determines:
    - What information is shared across platforms (overlaps)
    - What information conflicts between platforms (contradictions)
    - The overall impersonation risk score
    
    The impersonation score considers:
    - Username similarity across platforms
    - Name consistency
    - Location consistency
    - Bio content similarity
    - Presence of typosquatting patterns
    
    Attributes:
        scorer: SimilarityScorer for calculating similarity metrics
        matcher: FuzzyMatcher for name and text matching
        
    Example:
        >>> correlator = Correlator()
        >>> profiles = [
        ...     {'platform': 'facebook', 'username': 'john_doe', 'name': 'John Doe'},
        ...     {'platform': 'instagram', 'username': 'j0hn_d0e', 'name': 'John Doe'},
        ... ]
        >>> result = correlator.correlate_profiles(profiles)
        >>> print(f"Impersonation Score: {result['impersonation_score']}")
        Impersonation Score: 65
    """
    
    # Weights for impersonation score calculation
    # Higher weights mean more impact on the final score
    IMPERSONATION_WEIGHTS = {
        'username_typosquatting': 30,  # Very suspicious if detected
        'name_mismatch': 15,           # Names should match
        'location_mismatch': 10,       # Location can vary
        'bio_similarity': 10,          # Similar bios might indicate copying
        'email_mismatch': 20,          # Emails should be consistent
        'phone_mismatch': 15,          # Phones should be consistent
    }
    
    # Thresholds for matching
    NAME_MATCH_THRESHOLD = 0.7
    BIO_SIMILARITY_THRESHOLD = 0.6
    USERNAME_SIMILARITY_THRESHOLD = 0.8
    
    def __init__(self):
        """Initialize the Correlator with scoring and matching utilities."""
        self.scorer = SimilarityScorer()
        self.matcher = FuzzyMatcher()
    
    # =========================================================================
    # MAIN CORRELATION METHOD
    # =========================================================================
    
    def correlate_profiles(
        self,
        profiles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Correlate PII across multiple social media profiles.
        
        This is the main entry point for profile correlation. It analyzes
        the provided profiles and returns comprehensive correlation results.
        
        Args:
            profiles: List of profile dictionaries, each containing:
                - platform: str (required)
                - username: str (required)
                - name: str (optional)
                - bio: str (optional)
                - location: str (optional)
                - email: str (optional)
                - phone: str (optional)
        
        Returns:
            Dict containing:
                - overlaps: List of Overlap objects (as dicts)
                - contradictions: List of Contradiction objects (as dicts)
                - impersonation_score: int (0-100)
                - risk_level: str ('low', 'medium', 'high', 'critical')
                - analysis_details: Dict with detailed analysis
        
        Example:
            >>> correlator = Correlator()
            >>> result = correlator.correlate_profiles([
            ...     {'platform': 'facebook', 'username': 'john_doe', 'name': 'John'},
            ...     {'platform': 'instagram', 'username': 'johndoe', 'name': 'John D'}
            ... ])
        """
        if not profiles:
            return {
                'overlaps': [],
                'contradictions': [],
                'impersonation_score': 0,
                'risk_level': 'low',
                'analysis_details': {}
            }
        
        # Convert dictionaries to ProfileData objects
        profile_objects = [ProfileData.from_dict(p) for p in profiles]
        
        # Find overlaps between profiles
        overlaps = self._find_overlaps(profile_objects)
        
        # Find contradictions between profiles
        contradictions = self._find_contradictions(profile_objects)
        
        # Calculate impersonation score
        impersonation_score, risk_factors = self._calculate_impersonation_score(
            profile_objects, overlaps, contradictions
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(impersonation_score)
        
        # Compile analysis details
        analysis_details = {
            'profiles_analyzed': len(profile_objects),
            'platforms': [p.platform for p in profile_objects],
            'risk_factors': risk_factors
        }
        
        return {
            'overlaps': [self._overlap_to_dict(o) for o in overlaps],
            'contradictions': [self._contradiction_to_dict(c) for c in contradictions],
            'impersonation_score': impersonation_score,
            'risk_level': risk_level,
            'analysis_details': analysis_details
        }
    
    # =========================================================================
    # OVERLAP DETECTION METHODS
    # =========================================================================
    
    def _find_overlaps(self, profiles: List[ProfileData]) -> List[Overlap]:
        """
        Find overlapping (shared) information across profiles.
        
        Checks each PII field for matches across all profile pairs.
        
        Args:
            profiles: List of ProfileData objects
        
        Returns:
            List[Overlap]: List of detected overlaps
        """
        overlaps = []
        
        if len(profiles) < 2:
            return overlaps
        
        # Compare all pairs of profiles
        for i in range(len(profiles)):
            for j in range(i + 1, len(profiles)):
                p1, p2 = profiles[i], profiles[j]
                
                # Check username overlap
                username_overlap = self._check_username_overlap(p1, p2)
                if username_overlap:
                    overlaps.append(username_overlap)
                
                # Check name overlap
                name_overlap = self._check_name_overlap(p1, p2)
                if name_overlap:
                    overlaps.append(name_overlap)
                
                # Check location overlap
                location_overlap = self._check_location_overlap(p1, p2)
                if location_overlap:
                    overlaps.append(location_overlap)
                
                # Check bio similarity
                bio_overlap = self._check_bio_overlap(p1, p2)
                if bio_overlap:
                    overlaps.append(bio_overlap)
                
                # Check email overlap
                email_overlap = self._check_email_overlap(p1, p2)
                if email_overlap:
                    overlaps.append(email_overlap)
                
                # Check phone overlap
                phone_overlap = self._check_phone_overlap(p1, p2)
                if phone_overlap:
                    overlaps.append(phone_overlap)
        
        return overlaps
    
    def _check_username_overlap(
        self,
        p1: ProfileData,
        p2: ProfileData
    ) -> Optional[Overlap]:
        """Check for username similarity between two profiles."""
        if not p1.username or not p2.username:
            return None
        
        # Normalize usernames
        u1 = p1.username.lower().strip()
        u2 = p2.username.lower().strip()
        
        # Calculate similarity
        similarity = self.scorer.levenshtein_ratio(u1, u2)
        
        if similarity >= self.USERNAME_SIMILARITY_THRESHOLD:
            return Overlap(
                field='username',
                platforms=[p1.platform, p2.platform],
                values=[p1.username, p2.username],
                match_score=similarity,
                description=f"Similar usernames found: '{p1.username}' and '{p2.username}' "
                           f"({similarity*100:.0f}% similar)"
            )
        
        return None
    
    def _check_name_overlap(
        self,
        p1: ProfileData,
        p2: ProfileData
    ) -> Optional[Overlap]:
        """Check for name match between two profiles."""
        if not p1.name or not p2.name:
            return None
        
        is_match, score = self.matcher.match_names(p1.name, p2.name)
        
        if is_match:
            return Overlap(
                field='name',
                platforms=[p1.platform, p2.platform],
                values=[p1.name, p2.name],
                match_score=score,
                description=f"Matching names found: '{p1.name}' and '{p2.name}' "
                           f"({score*100:.0f}% match)"
            )
        
        return None
    
    def _check_location_overlap(
        self,
        p1: ProfileData,
        p2: ProfileData
    ) -> Optional[Overlap]:
        """Check for location match between two profiles."""
        if not p1.location or not p2.location:
            return None
        
        # Normalize locations
        loc1 = p1.location.lower().strip()
        loc2 = p2.location.lower().strip()
        
        # Check for substring match or high similarity
        if loc1 in loc2 or loc2 in loc1:
            return Overlap(
                field='location',
                platforms=[p1.platform, p2.platform],
                values=[p1.location, p2.location],
                match_score=1.0,
                description=f"Same location: '{p1.location}' and '{p2.location}'"
            )
        
        similarity = self.scorer.token_sort_ratio(loc1, loc2)
        
        if similarity >= 0.7:
            return Overlap(
                field='location',
                platforms=[p1.platform, p2.platform],
                values=[p1.location, p2.location],
                match_score=similarity,
                description=f"Similar locations found ({similarity*100:.0f}% match)"
            )
        
        return None
    
    def _check_bio_overlap(
        self,
        p1: ProfileData,
        p2: ProfileData
    ) -> Optional[Overlap]:
        """Check for bio similarity between two profiles."""
        if not p1.bio or not p2.bio:
            return None
        
        score, _ = self.matcher.compare_bios(p1.bio, p2.bio)
        
        if score >= self.BIO_SIMILARITY_THRESHOLD:
            return Overlap(
                field='bio',
                platforms=[p1.platform, p2.platform],
                values=[p1.bio[:50] + '...', p2.bio[:50] + '...'],
                match_score=score,
                description=f"Similar bio content found ({score*100:.0f}% similar)"
            )
        
        return None
    
    def _check_email_overlap(
        self,
        p1: ProfileData,
        p2: ProfileData
    ) -> Optional[Overlap]:
        """Check for email match between two profiles."""
        if not p1.email or not p2.email:
            return None
        
        # Normalize emails
        e1 = p1.email.lower().strip()
        e2 = p2.email.lower().strip()
        
        if e1 == e2:
            return Overlap(
                field='email',
                platforms=[p1.platform, p2.platform],
                values=[p1.email, p2.email],
                match_score=1.0,
                description=f"Same email address found on both platforms"
            )
        
        return None
    
    def _check_phone_overlap(
        self,
        p1: ProfileData,
        p2: ProfileData
    ) -> Optional[Overlap]:
        """Check for phone match between two profiles."""
        if not p1.phone or not p2.phone:
            return None
        
        # Normalize phones (remove non-digit characters)
        phone1 = re.sub(r'\D', '', p1.phone)
        phone2 = re.sub(r'\D', '', p2.phone)
        
        if phone1 == phone2 or phone1.endswith(phone2[-9:]) or phone2.endswith(phone1[-9:]):
            return Overlap(
                field='phone',
                platforms=[p1.platform, p2.platform],
                values=[p1.phone, p2.phone],
                match_score=1.0,
                description=f"Same phone number found on both platforms"
            )
        
        return None
    
    # =========================================================================
    # CONTRADICTION DETECTION METHODS
    # =========================================================================
    
    def _find_contradictions(
        self,
        profiles: List[ProfileData]
    ) -> List[Contradiction]:
        """
        Find contradictions (conflicting information) across profiles.
        
        Args:
            profiles: List of ProfileData objects
        
        Returns:
            List[Contradiction]: List of detected contradictions
        """
        contradictions = []
        
        if len(profiles) < 2:
            return contradictions
        
        # Compare all pairs of profiles
        for i in range(len(profiles)):
            for j in range(i + 1, len(profiles)):
                p1, p2 = profiles[i], profiles[j]
                
                # Check for name contradictions
                name_contradiction = self._check_name_contradiction(p1, p2)
                if name_contradiction:
                    contradictions.append(name_contradiction)
                
                # Check for location contradictions
                location_contradiction = self._check_location_contradiction(p1, p2)
                if location_contradiction:
                    contradictions.append(location_contradiction)
                
                # Check for email contradictions
                email_contradiction = self._check_email_contradiction(p1, p2)
                if email_contradiction:
                    contradictions.append(email_contradiction)
        
        return contradictions
    
    def _check_name_contradiction(
        self,
        p1: ProfileData,
        p2: ProfileData
    ) -> Optional[Contradiction]:
        """Check for name contradiction between two profiles."""
        if not p1.name or not p2.name:
            return None
        
        is_match, score = self.matcher.match_names(p1.name, p2.name)
        
        # If names don't match at all, that's a contradiction
        if not is_match and score < 0.4:
            severity = 'high' if score < 0.2 else 'medium'
            return Contradiction(
                field='name',
                platforms=[p1.platform, p2.platform],
                values=[p1.name, p2.name],
                severity=severity,
                description=f"Different names: '{p1.name}' vs '{p2.name}' "
                           f"(only {score*100:.0f}% similar)"
            )
        
        return None
    
    def _check_location_contradiction(
        self,
        p1: ProfileData,
        p2: ProfileData
    ) -> Optional[Contradiction]:
        """Check for location contradiction between two profiles."""
        if not p1.location or not p2.location:
            return None
        
        # Normalize locations
        loc1 = p1.location.lower().strip()
        loc2 = p2.location.lower().strip()
        
        # Check similarity
        similarity = self.scorer.token_sort_ratio(loc1, loc2)
        
        # Low similarity indicates contradiction
        if similarity < 0.3:
            return Contradiction(
                field='location',
                platforms=[p1.platform, p2.platform],
                values=[p1.location, p2.location],
                severity='low',
                description=f"Different locations: '{p1.location}' vs '{p2.location}'"
            )
        
        return None
    
    def _check_email_contradiction(
        self,
        p1: ProfileData,
        p2: ProfileData
    ) -> Optional[Contradiction]:
        """Check for email contradiction between two profiles."""
        if not p1.email or not p2.email:
            return None
        
        # Normalize emails
        e1 = p1.email.lower().strip()
        e2 = p2.email.lower().strip()
        
        # Different emails is a potential contradiction
        if e1 != e2:
            # Check if they might be related (same domain, similar local part)
            domain1 = e1.split('@')[-1] if '@' in e1 else ''
            domain2 = e2.split('@')[-1] if '@' in e2 else ''
            
            if domain1 != domain2:
                return Contradiction(
                    field='email',
                    platforms=[p1.platform, p2.platform],
                    values=[p1.email, p2.email],
                    severity='medium',
                    description=f"Different email addresses with different domains"
                )
        
        return None
    
    # =========================================================================
    # IMPERSONATION SCORE CALCULATION
    # =========================================================================
    
    def _calculate_impersonation_score(
        self,
        profiles: List[ProfileData],
        overlaps: List[Overlap],
        contradictions: List[Contradiction]
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Calculate the impersonation risk score (0-100).
        
        A higher score indicates higher likelihood of impersonation.
        
        Factors considered:
        - Typosquatting in usernames
        - Name mismatches
        - Location inconsistencies
        - Overly similar bios (copying)
        - Contact information mismatches
        
        Args:
            profiles: List of ProfileData objects
            overlaps: Detected overlaps
            contradictions: Detected contradictions
        
        Returns:
            Tuple[int, Dict]: (score 0-100, risk_factors dict)
        """
        score = 0
        risk_factors = {}
        
        # Check for typosquatting between usernames
        typosquat_detected = False
        for i in range(len(profiles)):
            for j in range(i + 1, len(profiles)):
                p1, p2 = profiles[i], profiles[j]
                if p1.username and p2.username:
                    is_squat, sim, techniques = self.matcher.is_typosquatting(
                        p1.username, p2.username
                    )
                    if is_squat:
                        typosquat_detected = True
                        score += self.IMPERSONATION_WEIGHTS['username_typosquatting']
                        risk_factors['typosquatting'] = {
                            'detected': True,
                            'usernames': [p1.username, p2.username],
                            'techniques': techniques
                        }
                        break
            if typosquat_detected:
                break
        
        # Score based on contradictions
        for contradiction in contradictions:
            if contradiction.field == 'name':
                if contradiction.severity == 'high':
                    score += self.IMPERSONATION_WEIGHTS['name_mismatch']
                else:
                    score += self.IMPERSONATION_WEIGHTS['name_mismatch'] // 2
                risk_factors['name_mismatch'] = {
                    'severity': contradiction.severity,
                    'values': contradiction.values
                }
            elif contradiction.field == 'location':
                score += self.IMPERSONATION_WEIGHTS['location_mismatch']
                risk_factors['location_mismatch'] = {
                    'values': contradiction.values
                }
            elif contradiction.field == 'email':
                score += self.IMPERSONATION_WEIGHTS['email_mismatch']
                risk_factors['email_mismatch'] = {
                    'values': contradiction.values
                }
        
        # Check for suspicious bio similarity (might indicate copying)
        for overlap in overlaps:
            if overlap.field == 'bio' and overlap.match_score > 0.9:
                # Very high bio similarity is suspicious
                score += self.IMPERSONATION_WEIGHTS['bio_similarity']
                risk_factors['suspicious_bio_similarity'] = {
                    'score': overlap.match_score
                }
        
        # Cap the score at 100
        score = min(score, 100)
        
        return (score, risk_factors)
    
    def _determine_risk_level(self, score: int) -> str:
        """
        Determine the risk level based on impersonation score.
        
        Args:
            score: Impersonation score (0-100)
        
        Returns:
            str: Risk level ('low', 'medium', 'high', 'critical')
        """
        if score >= 70:
            return RiskLevel.CRITICAL.value
        elif score >= 50:
            return RiskLevel.HIGH.value
        elif score >= 30:
            return RiskLevel.MEDIUM.value
        else:
            return RiskLevel.LOW.value
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def _overlap_to_dict(self, overlap: Overlap) -> Dict[str, Any]:
        """Convert an Overlap dataclass to a dictionary."""
        return {
            'field': overlap.field,
            'platforms': overlap.platforms,
            'values': overlap.values,
            'match_score': overlap.match_score,
            'description': overlap.description
        }
    
    def _contradiction_to_dict(self, contradiction: Contradiction) -> Dict[str, Any]:
        """Convert a Contradiction dataclass to a dictionary."""
        return {
            'field': contradiction.field,
            'platforms': contradiction.platforms,
            'values': contradiction.values,
            'severity': contradiction.severity,
            'description': contradiction.description
        }
    
    # =========================================================================
    # QUICK COMPARISON METHOD
    # =========================================================================
    
    def quick_compare(
        self,
        profile1: Dict[str, Any],
        profile2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Quick comparison between two profiles.
        
        A simplified version of correlate_profiles for comparing just two
        profiles.
        
        Args:
            profile1: First profile dictionary
            profile2: Second profile dictionary
        
        Returns:
            Dict with comparison results
        
        Example:
            >>> correlator = Correlator()
            >>> result = correlator.quick_compare(
            ...     {'platform': 'facebook', 'username': 'john_doe', 'name': 'John'},
            ...     {'platform': 'instagram', 'username': 'johndoe', 'name': 'John D'}
            ... )
        """
        return self.correlate_profiles([profile1, profile2])


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

# Create a default correlator instance for module-level usage
_default_correlator = Correlator()


def correlate_profiles(profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Module-level convenience function for profile correlation."""
    return _default_correlator.correlate_profiles(profiles)


def quick_compare(
    profile1: Dict[str, Any],
    profile2: Dict[str, Any]
) -> Dict[str, Any]:
    """Module-level convenience function for quick comparison."""
    return _default_correlator.quick_compare(profile1, profile2)
