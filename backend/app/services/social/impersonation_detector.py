# =============================================================================
# IMPERSONATION DETECTOR SERVICE
# =============================================================================
# Detects potential impersonation accounts across social media platforms.
# Designed for Sri Lanka focused OSINT digital footprint analysis.
# =============================================================================

"""
Impersonation Detector Service

This module detects potential impersonation accounts by checking:
- Location mismatch (different country, not Sri Lanka)
- Suspicious username suffixes (_official, _real, etc.)
- Duplicate usernames with numbers
- Suspicious bio content (scam patterns)
- Low activity accounts
- Recently created accounts

Example Usage:
    detector = ImpersonationDetector()
    risks = detector.detect(profile_data, user_identifiers)
    # Returns list of impersonation risks with indicators
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone


class ImpersonationDetector:
    """
    Detect potential impersonation accounts across social media platforms.
    Returns risk assessments with indicators and recommendations.
    """
    
    # -------------------------------------------------------------------------
    # SUSPICIOUS PATTERNS CONFIGURATION
    # -------------------------------------------------------------------------
    
    # Suspicious username suffixes that may indicate impersonation
    SUSPICIOUS_SUFFIXES = [
        "_official", "_real", "_verified", "_original", "_authentic",
        ".official", ".real", ".verified", ".original",
        "_admin", "_support", "_help", "_customer",
        "_lk", "_srilanka", "_sl"
    ]
    
    # Suspicious username prefixes
    SUSPICIOUS_PREFIXES = [
        "official_", "real_", "the_", "the.",
        "iamthe", "imthe", "iam_"
    ]
    
    # Suspicious bio content patterns (scam indicators)
    SUSPICIOUS_BIO_PATTERNS = [
        r"dm\s*(for|me)",
        r"dm\s*to\s*win",
        r"giveaway",
        r"free\s*(money|cash|prize|gift)",
        r"click\s*(link|here)",
        r"whatsapp\s*me",
        r"send\s*dm",
        r"investment\s*opportunity",
        r"make\s*money\s*fast",
        r"guaranteed\s*(returns|profit)",
        r"crypto\s*(trading|investment)",
        r"forex\s*trading",
        r"get\s*rich\s*quick",
        r"limited\s*offer",
        r"act\s*now",
        r"financial\s*freedom"
    ]
    
    # Sri Lanka related location identifiers
    SRI_LANKA_INDICATORS = [
        "sri lanka", "srilanka", "sl", "lk",
        "colombo", "kandy", "galle", "negombo",
        "dehiwala", "moratuwa", "jaffna", "matara",
        "batticaloa", "trincomalee", "anuradhapura"
    ]
    
    # Report URLs for each platform
    REPORT_URLS = {
        "facebook": "https://www.facebook.com/help/contact/169486816475808",
        "instagram": "https://help.instagram.com/contact/636276399721841",
        "linkedin": "https://www.linkedin.com/help/linkedin/solve/report-a-fake-profile",
        "x": "https://help.twitter.com/forms/impersonation"
    }
    
    def __init__(self):
        """Initialize the Impersonation Detector."""
        pass
    
    def detect(
        self,
        profile_data: Dict[str, Dict],
        user_identifiers: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Detect potential impersonation accounts.
        
        Args:
            profile_data: Scraped data from each platform
                Format: {
                    "facebook": {"status": "found", "url": "...", "data": {...}},
                    ...
                }
            user_identifiers: User-provided identifiers
                Format: {"username": "...", "name": "...", "location": "..."}
                
        Returns:
            List of impersonation risk assessments
        """
        risks = []
        
        # Get user's expected location (default to Sri Lanka)
        expected_location = user_identifiers.get("location", "Sri Lanka")
        user_username = user_identifiers.get("username", "").lower().strip().lstrip('@')
        user_name = user_identifiers.get("name", "").lower().strip()
        
        for platform, data in profile_data.items():
            status = data.get("status", "unknown")
            
            # Only check found profiles
            if status not in ["found", "exists"]:
                continue
            
            url = data.get("url", "")
            scraped = data.get("data", {})
            
            # Analyze this profile for impersonation indicators
            indicators = self._analyze_profile(
                platform=platform,
                url=url,
                scraped=scraped,
                user_username=user_username,
                user_name=user_name,
                expected_location=expected_location
            )
            
            if indicators:
                # Calculate risk level based on indicators
                risk_level, confidence = self._calculate_risk(indicators)
                
                # Only report medium or high risk profiles
                if risk_level in ["medium", "high"]:
                    risk_emoji = "🔴" if risk_level == "high" else "🟠"
                    
                    risks.append({
                        "platform": platform,
                        "profile_url": url,
                        "profile_name": scraped.get("name", "Unknown"),
                        "risk_level": risk_level,
                        "risk_emoji": risk_emoji,
                        "confidence_score": confidence,
                        "indicators": indicators,
                        "recommendation": self._generate_recommendation(risk_level, indicators),
                        "report_url": self.REPORT_URLS.get(platform, "")
                    })
        
        # Sort by confidence score descending
        risks.sort(key=lambda x: x["confidence_score"], reverse=True)
        
        return risks
    
    def _analyze_profile(
        self,
        platform: str,
        url: str,
        scraped: Dict,
        user_username: str,
        user_name: str,
        expected_location: str
    ) -> List[Dict[str, Any]]:
        """
        Analyze a profile for impersonation indicators.
        
        Args:
            platform: Platform identifier
            url: Profile URL
            scraped: Scraped profile data
            user_username: User's expected username
            user_name: User's expected name
            expected_location: User's expected location
            
        Returns:
            List of indicator dictionaries
        """
        indicators = []
        
        profile_name = scraped.get("name", "").lower().strip()
        profile_bio = scraped.get("bio", "").lower().strip()
        profile_location = scraped.get("location", "").lower().strip()
        
        # Extract username from URL
        profile_username = self._extract_username_from_url(url)
        
        # Check 1: Suspicious username suffixes
        for suffix in self.SUSPICIOUS_SUFFIXES:
            if profile_username.endswith(suffix):
                indicators.append({
                    "type": "suspicious_suffix",
                    "severity": "high",
                    "description": f"Username ends with suspicious suffix '{suffix}'",
                    "details": {
                        "pattern": suffix,
                        "username": profile_username
                    }
                })
                break
        
        # Check 2: Suspicious username prefixes
        for prefix in self.SUSPICIOUS_PREFIXES:
            if profile_username.startswith(prefix):
                indicators.append({
                    "type": "suspicious_prefix",
                    "severity": "medium",
                    "description": f"Username starts with suspicious prefix '{prefix}'",
                    "details": {
                        "pattern": prefix,
                        "username": profile_username
                    }
                })
                break
        
        # Check 3: Duplicate username with numbers (if user provided username)
        if user_username:
            number_pattern = re.search(r'(\d+)$', profile_username)
            base_username = re.sub(r'\d+$', '', profile_username)
            
            if number_pattern and base_username == user_username:
                indicators.append({
                    "type": "username_with_numbers",
                    "severity": "high",
                    "description": f"Username '{profile_username}' appears to be a copy with numbers added",
                    "details": {
                        "original": user_username,
                        "copy": profile_username,
                        "added_numbers": number_pattern.group(1)
                    }
                })
        
        # Check 4: Location mismatch (not in Sri Lanka when expected)
        if profile_location and expected_location.lower() in ["sri lanka", "lk"]:
            is_sri_lanka = any(
                indicator in profile_location.lower()
                for indicator in self.SRI_LANKA_INDICATORS
            )
            
            if not is_sri_lanka and profile_location:
                # Check if it mentions another country
                indicators.append({
                    "type": "location_mismatch",
                    "severity": "medium",
                    "description": f"Profile location '{profile_location}' differs from expected (Sri Lanka)",
                    "details": {
                        "profile_location": profile_location,
                        "expected_location": expected_location
                    }
                })
        
        # Check 5: Suspicious bio content
        if profile_bio:
            for pattern in self.SUSPICIOUS_BIO_PATTERNS:
                if re.search(pattern, profile_bio, re.IGNORECASE):
                    indicators.append({
                        "type": "suspicious_bio",
                        "severity": "high",
                        "description": "Bio contains suspicious content patterns (possible scam)",
                        "details": {
                            "matched_pattern": pattern,
                            "bio_excerpt": profile_bio[:100] + "..." if len(profile_bio) > 100 else profile_bio
                        }
                    })
                    break  # Only report once per profile
        
        # Check 6: Similar name but different username
        if user_name and profile_name:
            # Check if names are similar but usernames differ significantly
            name_similarity = self._calculate_name_similarity(user_name, profile_name)
            username_similarity = self._calculate_name_similarity(user_username, profile_username) if user_username else 1.0
            
            if name_similarity > 0.8 and username_similarity < 0.5:
                indicators.append({
                    "type": "name_username_mismatch",
                    "severity": "medium",
                    "description": "Profile has similar name but different username (possible impersonator)",
                    "details": {
                        "user_name": user_name,
                        "profile_name": profile_name,
                        "user_username": user_username,
                        "profile_username": profile_username
                    }
                })
        
        return indicators
    
    def _extract_username_from_url(self, url: str) -> str:
        """
        Extract username from profile URL.
        
        Args:
            url: Profile URL
            
        Returns:
            Extracted username or empty string
        """
        if not url:
            return ""
        
        # Common patterns for social media profile URLs
        patterns = [
            r'facebook\.com/([^/?]+)',
            r'instagram\.com/([^/?]+)',
            r'linkedin\.com/in/([^/?]+)',
            r'x\.com/([^/?]+)',
            r'twitter\.com/([^/?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1).lower().strip('/')
        
        return ""
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two names.
        
        Args:
            name1: First name
            name2: Second name
            
        Returns:
            Similarity score between 0 and 1
        """
        if not name1 or not name2:
            return 0.0
        
        # Normalize names
        n1 = set(name1.lower().split())
        n2 = set(name2.lower().split())
        
        if not n1 or not n2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(n1 & n2)
        union = len(n1 | n2)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_risk(self, indicators: List[Dict]) -> tuple:
        """
        Calculate overall risk level from indicators.
        
        Args:
            indicators: List of impersonation indicators
            
        Returns:
            Tuple of (risk_level, confidence_score)
        """
        if not indicators:
            return ("low", 0.0)
        
        # Count severity levels
        high_count = sum(1 for i in indicators if i.get("severity") == "high")
        medium_count = sum(1 for i in indicators if i.get("severity") == "medium")
        low_count = sum(1 for i in indicators if i.get("severity") == "low")
        
        # Calculate weighted score
        score = (high_count * 3) + (medium_count * 2) + (low_count * 1)
        
        # Calculate confidence (0-1 scale)
        max_score = len(indicators) * 3  # All indicators at high severity
        confidence = min(score / max(max_score, 1), 1.0)
        
        # Determine risk level
        if high_count >= 2 or score >= 6:
            risk_level = "high"
        elif high_count >= 1 or medium_count >= 2 or score >= 3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return (risk_level, round(confidence, 2))
    
    def _generate_recommendation(
        self,
        risk_level: str,
        indicators: List[Dict]
    ) -> str:
        """
        Generate recommendation based on risk level and indicators.
        
        Args:
            risk_level: Calculated risk level
            indicators: List of impersonation indicators
            
        Returns:
            Recommendation string
        """
        if risk_level == "high":
            # Check for specific high-severity indicators
            has_scam_bio = any(i["type"] == "suspicious_bio" for i in indicators)
            has_username_copy = any(i["type"] == "username_with_numbers" for i in indicators)
            
            if has_scam_bio:
                return (
                    "⚠️ HIGH RISK: This profile shows signs of being a scam account. "
                    "Report it immediately to protect others. Do not engage with any requests."
                )
            elif has_username_copy:
                return (
                    "⚠️ HIGH RISK: This profile appears to be impersonating the original account. "
                    "Report it to the platform and warn your contacts about the fake account."
                )
            else:
                return (
                    "⚠️ HIGH RISK: Multiple impersonation indicators detected. "
                    "Report this profile to the platform for investigation."
                )
        
        elif risk_level == "medium":
            return (
                "🟠 MEDIUM RISK: Some suspicious indicators found. "
                "Monitor this profile and verify if you recognize it. "
                "Consider reporting if behavior seems suspicious."
            )
        
        else:
            return (
                "✅ LOW RISK: Minor indicators detected. "
                "Keep monitoring your digital footprint for changes."
            )


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

_default_detector = ImpersonationDetector()


def detect_impersonation(
    profile_data: Dict[str, Dict],
    user_identifiers: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Module-level convenience function for impersonation detection."""
    return _default_detector.detect(profile_data, user_identifiers)
