# =============================================================================
# PII EXPOSURE ANALYZER SERVICE
# =============================================================================
# Analyzes scraped data to identify and list all exposed PII.
# Shows users exactly what personal data is publicly visible.
# =============================================================================

"""
PII Exposure Analyzer Service

This module analyzes PII exposure across social media platforms:
- Consolidate ALL exposed PII across platforms
- Match exposed data to user's provided identifiers
- Calculate exposure risk scores
- Generate actionable recommendations

Example Usage:
    analyzer = PIIExposureAnalyzer()
    report = analyzer.analyze(platform_data, user_identifiers)
    # Returns comprehensive exposure report with clear PII listing
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone


class PIIExposureAnalyzer:
    """
    Analyze scraped data to identify and list all exposed PII.
    Shows users exactly what personal data is publicly visible.
    """
    
    # -------------------------------------------------------------------------
    # PII RISK LEVELS CONFIGURATION
    # -------------------------------------------------------------------------
    PII_RISK_LEVELS = {
        "phone": "critical",
        "email": "high",
        "address": "critical",
        "birthdate": "high",
        "workplace": "medium",
        "education": "low",
        "location": "medium",
        "name": "low",
        "bio": "low",
        "profile_image": "low",
        "website": "low",
    }
    
    # Risk level weights for score calculation
    RISK_WEIGHTS = {
        "critical": 30,
        "high": 20,
        "medium": 10,
        "low": 5
    }
    
    def __init__(self):
        """Initialize the PII Exposure Analyzer."""
        pass
    
    def analyze(
        self,
        platform_data: Dict[str, Dict],
        user_identifiers: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Analyze PII exposure across all platforms.
        
        Args:
            platform_data: Scraped data from each platform
                Format: {
                    "facebook": {"status": "found", "data": {...}},
                    "instagram": {"status": "not_found", "data": {...}},
                    ...
                }
            user_identifiers: User-provided identifiers to match against
                Format: {"username": "...", "phone": "...", "email": "...", "name": "..."}
                
        Returns:
            Comprehensive exposure report with clear PII listing
        """
        # Get current timestamp (timezone-aware UTC)
        scan_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        # Extract platform status lists
        platforms_checked = list(platform_data.keys())
        profiles_found = []
        profiles_not_found = []
        
        for platform, data in platform_data.items():
            status = data.get("status", "unknown")
            if status in ["found", "exists"]:
                profiles_found.append(platform)
            elif status in ["not_found"]:
                profiles_not_found.append(platform)
        
        # Consolidate PII from all platforms
        exposed_pii = self._consolidate_pii(platform_data)
        
        # Match exposed PII to user's provided identifiers
        matched_pii = self._match_to_user_identifiers(exposed_pii, user_identifiers)
        
        # Calculate exposure score
        exposure_score = self._calculate_exposure_score(matched_pii)
        
        # Determine risk level
        risk_level = self._determine_risk_level(exposure_score)
        
        # Generate platform breakdown
        platform_breakdown = self._generate_platform_breakdown(platform_data, matched_pii)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(matched_pii, risk_level)
        
        return {
            "user_identifiers": user_identifiers,
            "scan_timestamp": scan_timestamp,
            "platforms_checked": platforms_checked,
            "profiles_found": profiles_found,
            "profiles_not_found": profiles_not_found,
            "exposure_score": exposure_score,
            "risk_level": risk_level,
            "total_exposed_items": len(matched_pii),
            "exposed_pii": matched_pii,
            "platform_breakdown": platform_breakdown,
            "recommendations": recommendations
        }
    
    def _consolidate_pii(self, platform_data: Dict[str, Dict]) -> List[Dict]:
        """
        Consolidate PII from all platforms into unified list.
        
        Args:
            platform_data: Scraped data from each platform
            
        Returns:
            List of exposed PII items with platform sources
        """
        # Dictionary to track unique PII items by type and value
        pii_map: Dict[str, Dict] = {}
        
        for platform, data in platform_data.items():
            status = data.get("status", "unknown")
            
            # Only process found profiles
            if status not in ["found", "exists"]:
                continue
            
            scraped = data.get("data", {})
            url = data.get("url", "")
            
            # Extract name
            if scraped.get("name"):
                name = scraped["name"].strip()
                if name:
                    key = f"name:{name.lower()}"
                    if key not in pii_map:
                        pii_map[key] = {
                            "type": "name",
                            "value": name,
                            "platforms": [platform],
                        }
                    elif platform not in pii_map[key]["platforms"]:
                        pii_map[key]["platforms"].append(platform)
            
            # Extract bio
            if scraped.get("bio"):
                bio = scraped["bio"].strip()
                if bio:
                    # Also extract PII from bio text
                    bio_pii = self.extract_pii_from_text(bio)
                    
                    # Add extracted emails
                    for email in bio_pii.get("emails", []):
                        key = f"email:{email.lower()}"
                        if key not in pii_map:
                            pii_map[key] = {
                                "type": "email",
                                "value": email,
                                "platforms": [platform],
                            }
                        elif platform not in pii_map[key]["platforms"]:
                            pii_map[key]["platforms"].append(platform)
                    
                    # Add extracted phones
                    for phone in bio_pii.get("phones", []):
                        key = f"phone:{self._normalize_phone(phone)}"
                        if key not in pii_map:
                            pii_map[key] = {
                                "type": "phone",
                                "value": phone,
                                "platforms": [platform],
                            }
                        elif platform not in pii_map[key]["platforms"]:
                            pii_map[key]["platforms"].append(platform)
                    
                    # Add bio as its own item
                    key = f"bio:{bio[:50].lower()}"
                    if key not in pii_map:
                        pii_map[key] = {
                            "type": "bio",
                            "value": bio[:200] + "..." if len(bio) > 200 else bio,
                            "platforms": [platform],
                        }
                    elif platform not in pii_map[key]["platforms"]:
                        pii_map[key]["platforms"].append(platform)
            
            # Extract location
            if scraped.get("location"):
                location = scraped["location"].strip()
                if location:
                    key = f"location:{location.lower()}"
                    if key not in pii_map:
                        pii_map[key] = {
                            "type": "location",
                            "value": location,
                            "platforms": [platform],
                        }
                    elif platform not in pii_map[key]["platforms"]:
                        pii_map[key]["platforms"].append(platform)
            
            # Extract workplace
            if scraped.get("workplace"):
                workplace = scraped["workplace"].strip()
                if workplace:
                    key = f"workplace:{workplace.lower()}"
                    if key not in pii_map:
                        pii_map[key] = {
                            "type": "workplace",
                            "value": workplace,
                            "platforms": [platform],
                        }
                    elif platform not in pii_map[key]["platforms"]:
                        pii_map[key]["platforms"].append(platform)
            
            # Extract email if directly available
            if scraped.get("email"):
                email = scraped["email"].strip().lower()
                if email:
                    key = f"email:{email}"
                    if key not in pii_map:
                        pii_map[key] = {
                            "type": "email",
                            "value": email,
                            "platforms": [platform],
                        }
                    elif platform not in pii_map[key]["platforms"]:
                        pii_map[key]["platforms"].append(platform)
            
            # Extract phone if directly available
            if scraped.get("phone"):
                phone = scraped["phone"].strip()
                if phone:
                    key = f"phone:{self._normalize_phone(phone)}"
                    if key not in pii_map:
                        pii_map[key] = {
                            "type": "phone",
                            "value": phone,
                            "platforms": [platform],
                        }
                    elif platform not in pii_map[key]["platforms"]:
                        pii_map[key]["platforms"].append(platform)
            
            # Extract profile image
            if scraped.get("profile_image"):
                profile_image = scraped["profile_image"].strip()
                if profile_image:
                    key = f"profile_image:{platform}"  # Unique per platform
                    pii_map[key] = {
                        "type": "profile_image",
                        "value": profile_image,
                        "platforms": [platform],
                    }
            
            # Extract website
            if scraped.get("website"):
                website = scraped["website"].strip()
                if website:
                    key = f"website:{website.lower()}"
                    if key not in pii_map:
                        pii_map[key] = {
                            "type": "website",
                            "value": website,
                            "platforms": [platform],
                        }
                    elif platform not in pii_map[key]["platforms"]:
                        pii_map[key]["platforms"].append(platform)
        
        # Convert to list format
        result = []
        for item in pii_map.values():
            result.append({
                "type": item["type"],
                "value": item["value"],
                "platforms": item["platforms"],
                "platform_count": len(item["platforms"]),
                "risk_level": self.PII_RISK_LEVELS.get(item["type"], "low"),
            })
        
        return result
    
    def _match_to_user_identifiers(
        self,
        exposed_pii: List[Dict],
        user_identifiers: Dict[str, str]
    ) -> List[Dict]:
        """
        Match exposed PII to user's provided identifiers.
        
        Args:
            exposed_pii: List of exposed PII items
            user_identifiers: User-provided identifiers
            
        Returns:
            Updated list with matches_user_input flag
        """
        result = []
        
        # Normalize user identifiers for matching
        normalized_identifiers = {}
        for key, value in user_identifiers.items():
            if value:
                if key == "phone":
                    normalized_identifiers[key] = self._normalize_phone(value)
                elif key == "email":
                    normalized_identifiers[key] = value.strip().lower()
                elif key == "name":
                    normalized_identifiers[key] = value.strip().lower()
                elif key == "username":
                    normalized_identifiers[key] = value.strip().lower().lstrip('@')
        
        for item in exposed_pii:
            matches = False
            pii_type = item["type"]
            pii_value = item["value"]
            
            # Check for matches based on type
            if pii_type == "phone" and "phone" in normalized_identifiers:
                normalized_pii_phone = self._normalize_phone(pii_value)
                if normalized_pii_phone == normalized_identifiers["phone"]:
                    matches = True
            
            elif pii_type == "email" and "email" in normalized_identifiers:
                if pii_value.strip().lower() == normalized_identifiers["email"]:
                    matches = True
            
            elif pii_type == "name" and "name" in normalized_identifiers:
                # Fuzzy match for names
                pii_name = pii_value.strip().lower()
                user_name = normalized_identifiers["name"]
                if pii_name == user_name or user_name in pii_name or pii_name in user_name:
                    matches = True
            
            # Check if username appears in name or bio
            if "username" in normalized_identifiers:
                username = normalized_identifiers["username"]
                if pii_type == "name":
                    if username in pii_value.lower().replace(" ", ""):
                        matches = True
            
            result.append({
                **item,
                "matches_user_input": matches
            })
        
        return result
    
    def _calculate_exposure_score(self, exposed_pii: List[Dict]) -> int:
        """
        Calculate exposure score 0-100.
        
        Args:
            exposed_pii: List of exposed PII items with risk levels
            
        Returns:
            Exposure score from 0 (low) to 100 (high)
        """
        if not exposed_pii:
            return 0
        
        total_weight = 0
        
        for item in exposed_pii:
            risk_level = item.get("risk_level", "low")
            base_weight = self.RISK_WEIGHTS.get(risk_level, 5)
            
            # Increase weight for items that match user input
            if item.get("matches_user_input", False):
                base_weight = int(base_weight * 1.5)
            
            # Increase weight for items exposed on multiple platforms
            platform_count = item.get("platform_count", 1)
            if platform_count > 1:
                base_weight += (platform_count - 1) * 3
            
            total_weight += base_weight
        
        # Normalize to 0-100 scale (cap at 100)
        score = min(total_weight, 100)
        
        return score
    
    def _determine_risk_level(self, score: int) -> str:
        """
        Determine overall risk level from score.
        
        Args:
            score: Exposure score 0-100
            
        Returns:
            Risk level: low, medium, high, or critical
        """
        if score >= 70:
            return "critical"
        elif score >= 50:
            return "high"
        elif score >= 25:
            return "medium"
        else:
            return "low"
    
    def _generate_platform_breakdown(
        self,
        platform_data: Dict[str, Dict],
        exposed_pii: List[Dict]
    ) -> Dict[str, Dict]:
        """
        Generate per-platform exposure breakdown.
        
        Args:
            platform_data: Original platform data
            exposed_pii: List of exposed PII items
            
        Returns:
            Dictionary with platform-specific exposure details
        """
        breakdown = {}
        
        for platform, data in platform_data.items():
            status = data.get("status", "unknown")
            url = data.get("url", "")
            
            # Get items exposed on this platform
            platform_items = [
                item for item in exposed_pii
                if platform in item.get("platforms", [])
            ]
            
            breakdown[platform] = {
                "platform": platform,
                "status": status,
                "url": url,
                "exposed_count": len(platform_items),
                "exposed_items": platform_items
            }
        
        return breakdown
    
    def _generate_recommendations(
        self,
        exposed_pii: List[Dict],
        risk_level: str
    ) -> List[str]:
        """
        Generate actionable recommendations.
        
        Args:
            exposed_pii: List of exposed PII items
            risk_level: Overall risk level
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Find critical and high risk items
        critical_items = [item for item in exposed_pii if item.get("risk_level") == "critical"]
        high_items = [item for item in exposed_pii if item.get("risk_level") == "high"]
        matched_items = [item for item in exposed_pii if item.get("matches_user_input", False)]
        
        # Phone exposure recommendations
        phone_items = [item for item in exposed_pii if item.get("type") == "phone"]
        for item in phone_items:
            platforms = ", ".join(item.get("platforms", []))
            recommendations.append(
                f"⚠️ CRITICAL: Your phone number ({item['value']}) is publicly visible on {platforms}. "
                f"Remove it from your profile to prevent spam calls and potential scams."
            )
        
        # Email exposure recommendations
        email_items = [item for item in exposed_pii if item.get("type") == "email"]
        for item in email_items:
            platform_count = item.get("platform_count", 1)
            if platform_count > 1:
                recommendations.append(
                    f"⚠️ HIGH: Your email ({item['value']}) is exposed on {platform_count} platforms. "
                    f"Consider using a separate email address for social media accounts."
                )
            else:
                platforms = ", ".join(item.get("platforms", []))
                recommendations.append(
                    f"⚠️ HIGH: Your email ({item['value']}) is visible on {platforms}. "
                    f"Review your privacy settings to hide it."
                )
        
        # Location exposure recommendations
        location_items = [item for item in exposed_pii if item.get("type") == "location"]
        if location_items:
            recommendations.append(
                "📍 MEDIUM: Your location information is visible. "
                "Consider whether you need to share precise location details publicly."
            )
        
        # Workplace exposure recommendations
        workplace_items = [item for item in exposed_pii if item.get("type") == "workplace"]
        if workplace_items:
            recommendations.append(
                "🏢 MEDIUM: Your workplace information is publicly visible. "
                "This could be used for targeted phishing attacks. Review your privacy settings."
            )
        
        # General recommendations based on risk level
        if risk_level == "critical":
            recommendations.append(
                "🔴 Your digital footprint shows critical exposure. "
                "Conduct an immediate privacy audit across all platforms."
            )
            recommendations.append(
                "Enable two-factor authentication on all accounts to prevent unauthorized access."
            )
        elif risk_level == "high":
            recommendations.append(
                "🟠 Your digital footprint has high exposure. "
                "Review and update privacy settings on all social media platforms."
            )
        elif risk_level == "medium":
            recommendations.append(
                "🟡 Your digital footprint has moderate exposure. "
                "Consider tightening privacy settings to reduce public visibility."
            )
        
        # General best practices
        if not recommendations:
            recommendations.append(
                "✅ No critical PII exposure detected. Continue to monitor your digital footprint regularly."
            )
        
        recommendations.append(
            "🔒 Regularly search for your name and identifiers to monitor for new exposures."
        )
        
        return recommendations
    
    def extract_pii_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Extract PII from bio/about text using regex.
        
        Args:
            text: Text to extract PII from
            
        Returns:
            Dictionary with extracted emails, phones, and urls
        """
        pii: Dict[str, List[str]] = {"emails": [], "phones": [], "urls": []}
        
        if not text:
            return pii
        
        # Email pattern
        emails = re.findall(
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            text
        )
        pii["emails"] = list(set(emails))
        
        # Sri Lankan phone patterns
        # Matches: +94 77 123 4567, 0771234567, 077-123-4567, etc.
        phones = re.findall(
            r'(?:\+94|0)?[0-9]{2}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
            text
        )
        pii["phones"] = list(set(phones))
        
        # URLs
        urls = re.findall(
            r'https?://[^\s<>"{}|\\^`\[\]]+',
            text
        )
        pii["urls"] = list(set(urls))
        
        return pii
    
    def _normalize_phone(self, phone: str) -> str:
        """
        Normalize phone number for comparison.
        
        Args:
            phone: Phone number in any format
            
        Returns:
            Normalized phone number (digits only, with country code)
        """
        if not phone:
            return ""
        
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Convert to standard format
        if cleaned.startswith('+94'):
            return cleaned
        elif cleaned.startswith('0094'):
            return '+94' + cleaned[4:]
        elif cleaned.startswith('94') and len(cleaned) >= 11:
            return '+' + cleaned
        elif cleaned.startswith('0') and len(cleaned) >= 10:
            return '+94' + cleaned[1:]
        
        return cleaned


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

_default_analyzer = PIIExposureAnalyzer()


def analyze_exposure(
    platform_data: Dict[str, Dict],
    user_identifiers: Dict[str, str]
) -> Dict[str, Any]:
    """Module-level convenience function for exposure analysis."""
    return _default_analyzer.analyze(platform_data, user_identifiers)


def extract_pii_from_text(text: str) -> Dict[str, List[str]]:
    """Module-level convenience function for PII extraction from text."""
    return _default_analyzer.extract_pii_from_text(text)
