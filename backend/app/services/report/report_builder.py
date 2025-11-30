# =============================================================================
# REPORT BUILDER SERVICE
# =============================================================================
# Builds comprehensive analysis reports with risk assessment,
# impersonation detection, exposed PII, and complete findings.
# =============================================================================

"""
Report Builder Service

This module builds comprehensive analysis reports including:
- Risk assessment (score 0-100, level, summary)
- Impersonation risks (separate section)
- Exposed PII categorized by severity
- Platform breakdown
- Recommendations (prioritized)
- Complete findings section with all profile links and exposed PII details

Example Usage:
    builder = ReportBuilder()
    report = builder.build_report(scan_results, user_identifiers)
    # Returns AnalysisReportResponse compatible dictionary
"""

import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from .platform_config import SUPPORTED_PLATFORMS, get_platform_config


class ReportBuilder:
    """
    Build comprehensive analysis reports for digital footprint scans.
    """
    
    # -------------------------------------------------------------------------
    # RISK LEVEL CONFIGURATION
    # -------------------------------------------------------------------------
    
    RISK_LEVELS = {
        "critical": {"emoji": "🔴", "color": "#dc3545", "threshold": 75},
        "high": {"emoji": "🟠", "color": "#fd7e14", "threshold": 50},
        "medium": {"emoji": "🟡", "color": "#ffc107", "threshold": 25},
        "low": {"emoji": "🟢", "color": "#28a745", "threshold": 0}
    }
    
    PII_TYPE_CONFIG = {
        "phone": {"emoji": "📱", "label": "Phone Number", "severity": "critical"},
        "email": {"emoji": "📧", "label": "Email Address", "severity": "high"},
        "address": {"emoji": "🏠", "label": "Physical Address", "severity": "critical"},
        "birthdate": {"emoji": "🎂", "label": "Birth Date", "severity": "high"},
        "workplace": {"emoji": "🏢", "label": "Workplace", "severity": "medium"},
        "education": {"emoji": "🎓", "label": "Education", "severity": "low"},
        "location": {"emoji": "📍", "label": "Location", "severity": "medium"},
        "name": {"emoji": "👤", "label": "Full Name", "severity": "low"},
        "bio": {"emoji": "📝", "label": "Bio/About", "severity": "low"},
        "profile_image": {"emoji": "🖼️", "label": "Profile Image", "severity": "low"},
        "website": {"emoji": "🌐", "label": "Website", "severity": "low"}
    }
    
    def __init__(self):
        """Initialize the Report Builder."""
        pass
    
    def build_report(
        self,
        scan_results: Dict[str, Any],
        user_identifiers: Dict[str, str],
        impersonation_risks: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Build a comprehensive analysis report.
        
        Args:
            scan_results: Results from platform scanning
                Format: {
                    "platform_data": {...},
                    "exposed_pii": [...],
                    "exposure_score": int,
                    "risk_level": str,
                    ...
                }
            user_identifiers: User-provided identifiers
                Format: {"username": "...", "email": "...", "name": "..."}
            impersonation_risks: Optional list of impersonation risks
            
        Returns:
            AnalysisReportResponse compatible dictionary
        """
        # Generate report ID and timestamp
        report_id = str(uuid.uuid4())
        generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        # Extract components from scan results
        platform_data = scan_results.get("platform_breakdown", scan_results.get("platform_data", {}))
        exposed_pii_list = scan_results.get("exposed_pii", [])
        exposure_score = scan_results.get("exposure_score", 0)
        base_risk_level = scan_results.get("risk_level", "low")
        
        # Build risk assessment
        risk_assessment = self._build_risk_assessment(
            exposure_score=exposure_score,
            risk_level=base_risk_level,
            exposed_pii=exposed_pii_list,
            impersonation_risks=impersonation_risks or []
        )
        
        # Build exposed PII section (categorized by severity)
        exposed_pii_categorized = self._categorize_exposed_pii(exposed_pii_list)
        
        # Build platform breakdown
        platforms = self._build_platform_breakdown(platform_data, user_identifiers)
        
        # Build recommendations
        recommendations = self._build_recommendations(
            exposed_pii=exposed_pii_list,
            risk_level=risk_assessment["level"],
            impersonation_risks=impersonation_risks or []
        )
        
        # Build complete findings section
        complete_findings = self._build_complete_findings(
            platform_data=platform_data,
            exposed_pii=exposed_pii_list,
            user_identifiers=user_identifiers
        )
        
        # Build summary
        summary = self._build_summary(
            platform_data=platform_data,
            exposed_pii=exposed_pii_list,
            impersonation_risks=impersonation_risks or [],
            user_identifiers=user_identifiers
        )
        
        # Build export section
        export = {
            "pdf_url": f"/api/report/{report_id}/pdf",
            "json_url": f"/api/report/{report_id}/json"
        }
        
        return {
            "success": True,
            "report_id": report_id,
            "generated_at": generated_at,
            "identifier": {
                "type": self._detect_identifier_type(user_identifiers),
                "value": user_identifiers.get("username", user_identifiers.get("email", user_identifiers.get("name", "")))
            },
            "risk_assessment": risk_assessment,
            "impersonation_risks": impersonation_risks or [],
            "exposed_pii": exposed_pii_categorized,
            "platforms": platforms,
            "recommendations": recommendations,
            "cross_language": None,  # Reserved for Sinhala support
            "complete_findings": complete_findings,
            "summary": summary,
            "export": export
        }
    
    def _build_risk_assessment(
        self,
        exposure_score: int,
        risk_level: str,
        exposed_pii: List[Dict],
        impersonation_risks: List[Dict]
    ) -> Dict[str, Any]:
        """
        Build risk assessment section.
        
        Args:
            exposure_score: Calculated exposure score (0-100)
            risk_level: Base risk level from exposure analysis
            exposed_pii: List of exposed PII items
            impersonation_risks: List of impersonation risks
            
        Returns:
            Risk assessment dictionary
        """
        # Adjust risk level if impersonation risks are high
        high_impersonation = any(r.get("risk_level") == "high" for r in impersonation_risks)
        if high_impersonation and risk_level not in ["critical", "high"]:
            risk_level = "high"
        
        # Get risk level config
        level_config = self.RISK_LEVELS.get(risk_level, self.RISK_LEVELS["low"])
        
        # Count critical and high severity items
        critical_count = sum(1 for p in exposed_pii if p.get("risk_level") == "critical")
        high_count = sum(1 for p in exposed_pii if p.get("risk_level") == "high")
        
        # Generate summary
        if risk_level == "critical":
            summary = "Critical digital footprint exposure detected. Immediate action required to protect your privacy."
        elif risk_level == "high":
            summary = "High level of personal information exposure. Review and update privacy settings across all platforms."
        elif risk_level == "medium":
            summary = "Moderate digital footprint exposure. Consider reviewing what information is publicly visible."
        else:
            summary = "Low exposure detected. Your digital footprint appears relatively private."
        
        return {
            "score": exposure_score,
            "level": risk_level,
            "emoji": level_config["emoji"],
            "color": level_config["color"],
            "summary": summary,
            "critical_items": critical_count,
            "high_risk_items": high_count,
            "impersonation_count": len([r for r in impersonation_risks if r.get("risk_level") in ["high", "medium"]])
        }
    
    def _categorize_exposed_pii(self, exposed_pii: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize exposed PII by severity level.
        
        Args:
            exposed_pii: List of exposed PII items
            
        Returns:
            Dictionary with PII items categorized by severity
        """
        categorized = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for item in exposed_pii:
            risk_level = item.get("risk_level", "low")
            if risk_level not in categorized:
                risk_level = "low"
            
            # Enrich item with type configuration
            pii_type = item.get("type", "unknown")
            type_config = self.PII_TYPE_CONFIG.get(pii_type, {
                "emoji": "❓",
                "label": pii_type.capitalize(),
                "severity": "low"
            })
            
            enriched_item = {
                **item,
                "pii_emoji": type_config["emoji"],
                "pii_label": type_config["label"],
                "risk_emoji": self.RISK_LEVELS.get(risk_level, {}).get("emoji", "⚪")
            }
            
            categorized[risk_level].append(enriched_item)
        
        return categorized
    
    def _build_platform_breakdown(
        self,
        platform_data: Dict[str, Dict],
        user_identifiers: Dict[str, str]
    ) -> List[Dict]:
        """
        Build platform breakdown section.
        
        Args:
            platform_data: Data from each platform
            user_identifiers: User identifiers
            
        Returns:
            List of platform breakdown dictionaries
        """
        platforms = []
        username = user_identifiers.get("username", "")
        
        for platform_id, config in SUPPORTED_PLATFORMS.items():
            platform_info = platform_data.get(platform_id, {})
            status = platform_info.get("status", "not_checked")
            url = platform_info.get("url", config["url_template"].format(username=username) if username else "")
            
            exposed_count = 0
            if "exposed_items" in platform_info:
                exposed_count = len(platform_info.get("exposed_items", []))
            elif "exposed_count" in platform_info:
                exposed_count = platform_info.get("exposed_count", 0)
            
            platforms.append({
                "platform_id": platform_id,
                "platform_name": config["name"],
                "platform_emoji": config["emoji"],
                "platform_color": config["color"],
                "status": status,
                "profile_url": url,
                "privacy_settings_url": config["privacy_url"],
                "report_url": config["report_url"],
                "exposed_count": exposed_count
            })
        
        return platforms
    
    def _build_recommendations(
        self,
        exposed_pii: List[Dict],
        risk_level: str,
        impersonation_risks: List[Dict]
    ) -> List[Dict]:
        """
        Build prioritized recommendations.
        
        Args:
            exposed_pii: List of exposed PII items
            risk_level: Overall risk level
            impersonation_risks: List of impersonation risks
            
        Returns:
            List of recommendation dictionaries with priority
        """
        recommendations = []
        priority = 1
        
        # Critical: Impersonation alerts
        for risk in impersonation_risks:
            if risk.get("risk_level") == "high":
                recommendations.append({
                    "priority": priority,
                    "severity": "critical",
                    "emoji": "🚨",
                    "title": f"Report Suspicious Profile on {risk.get('platform', 'Unknown').capitalize()}",
                    "description": risk.get("recommendation", "Report this profile for impersonation"),
                    "action_url": risk.get("report_url", ""),
                    "action_label": "Report Profile"
                })
                priority += 1
        
        # Critical/High: Phone number exposure
        phone_items = [p for p in exposed_pii if p.get("type") == "phone"]
        if phone_items:
            platforms = set()
            for item in phone_items:
                platforms.update(item.get("platforms", []))
            
            recommendations.append({
                "priority": priority,
                "severity": "critical",
                "emoji": "📱",
                "title": "Remove Phone Number from Profiles",
                "description": f"Your phone number is exposed on {', '.join(platforms)}. Remove it to prevent spam calls and potential scams.",
                "action_url": "",
                "action_label": "Review Privacy Settings"
            })
            priority += 1
        
        # High: Email exposure
        email_items = [p for p in exposed_pii if p.get("type") == "email"]
        if email_items:
            recommendations.append({
                "priority": priority,
                "severity": "high",
                "emoji": "📧",
                "title": "Protect Your Email Address",
                "description": "Consider hiding your email or using a secondary address for public profiles.",
                "action_url": "",
                "action_label": "Update Email Settings"
            })
            priority += 1
        
        # Medium: Location exposure
        location_items = [p for p in exposed_pii if p.get("type") == "location"]
        if location_items:
            recommendations.append({
                "priority": priority,
                "severity": "medium",
                "emoji": "📍",
                "title": "Review Location Sharing",
                "description": "Consider whether you need to share your precise location publicly.",
                "action_url": "",
                "action_label": "Review Location Settings"
            })
            priority += 1
        
        # General recommendations based on risk level
        if risk_level in ["critical", "high"]:
            recommendations.append({
                "priority": priority,
                "severity": "high",
                "emoji": "🔐",
                "title": "Enable Two-Factor Authentication",
                "description": "Protect all accounts with 2FA to prevent unauthorized access.",
                "action_url": "",
                "action_label": "Enable 2FA"
            })
            priority += 1
            
            recommendations.append({
                "priority": priority,
                "severity": "high",
                "emoji": "🔍",
                "title": "Conduct Privacy Audit",
                "description": "Review all profile settings and remove unnecessary personal information.",
                "action_url": "",
                "action_label": "Start Audit"
            })
            priority += 1
        
        # Always recommend monitoring
        recommendations.append({
            "priority": priority,
            "severity": "low",
            "emoji": "👀",
            "title": "Monitor Your Digital Footprint",
            "description": "Regularly search for your name and identifiers to detect new exposures.",
            "action_url": "",
            "action_label": "Set Reminder"
        })
        
        return recommendations
    
    def _build_complete_findings(
        self,
        platform_data: Dict[str, Dict],
        exposed_pii: List[Dict],
        user_identifiers: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Build complete findings section with all discovered profiles and exposed PII.
        
        Args:
            platform_data: Data from each platform
            exposed_pii: List of exposed PII items
            user_identifiers: User identifiers
            
        Returns:
            Complete findings dictionary
        """
        username = user_identifiers.get("username", "")
        
        # Build discovered profiles
        discovered_profiles = []
        index = 1
        
        for platform_id, config in SUPPORTED_PLATFORMS.items():
            platform_info = platform_data.get(platform_id, {})
            status = platform_info.get("status", "not_checked")
            url = platform_info.get("url", config["url_template"].format(username=username) if username else "")
            
            found = status in ["found", "exists"]
            
            profile_detail = {
                "index": index,
                "platform": config["name"],
                "platform_emoji": config["emoji"],
                "found": found,
                "profile_name": platform_info.get("data", {}).get("name") if found else None,
                "username": username if found else None,
                "profile_url": url if found else None,
                "discovery_source": "Direct URL Check",
                "links": {
                    "view_profile": url if found else None,
                    "privacy_settings": config["privacy_url"],
                    "report_profile": config["report_url"]
                },
                "checked_urls": [url] if not found else None
            }
            discovered_profiles.append(profile_detail)
            index += 1
        
        # Build exposed PII details
        exposed_pii_details = []
        pii_index = 1
        
        for item in exposed_pii:
            pii_type = item.get("type", "unknown")
            type_config = self.PII_TYPE_CONFIG.get(pii_type, {
                "emoji": "❓",
                "label": pii_type.capitalize(),
                "severity": "low"
            })
            
            risk_level = item.get("risk_level", "low")
            risk_config = self.RISK_LEVELS.get(risk_level, self.RISK_LEVELS["low"])
            
            # Build found_on sources
            found_on = []
            for platform in item.get("platforms", []):
                platform_config = get_platform_config(platform)
                if platform_config:
                    platform_info = platform_data.get(platform, {})
                    found_on.append({
                        "platform": platform_config["name"],
                        "platform_emoji": platform_config["emoji"],
                        "location_in_profile": "Bio/Profile Info",
                        "profile_url": platform_info.get("url", platform_config["url_template"].format(username=username) if username else ""),
                        "direct_link": platform_info.get("url", platform_config["url_template"].format(username=username) if username else "")
                    })
            
            # Generate recommended action
            if risk_level == "critical":
                recommended_action = f"Remove this {type_config['label'].lower()} immediately from all profiles"
            elif risk_level == "high":
                recommended_action = f"Review and consider hiding this {type_config['label'].lower()}"
            else:
                recommended_action = f"Consider whether you need to display this {type_config['label'].lower()}"
            
            detail = {
                "index": pii_index,
                "pii_type": pii_type,
                "pii_emoji": type_config["emoji"],
                "pii_label": type_config["label"],
                "exposed_value": item.get("value", ""),
                "exposed_value_sinhala": None,  # Reserved for Sinhala translations
                "risk_level": risk_level,
                "risk_emoji": risk_config["emoji"],
                "risk_description": f"This is considered {risk_level} risk information",
                "matches_user_input": item.get("matches_user_input", False),
                "found_on": found_on,
                "recommended_action": recommended_action
            }
            exposed_pii_details.append(detail)
            pii_index += 1
        
        return {
            "discovered_profiles": discovered_profiles,
            "exposed_pii_details": exposed_pii_details
        }
    
    def _build_summary(
        self,
        platform_data: Dict[str, Dict],
        exposed_pii: List[Dict],
        impersonation_risks: List[Dict],
        user_identifiers: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Build summary statistics.
        
        Args:
            platform_data: Data from each platform
            exposed_pii: List of exposed PII items
            impersonation_risks: List of impersonation risks
            user_identifiers: User identifiers
            
        Returns:
            Summary statistics dictionary
        """
        # Count platforms
        total_platforms = len(SUPPORTED_PLATFORMS)
        profiles_found = sum(
            1 for p in platform_data.values()
            if p.get("status") in ["found", "exists"]
        )
        
        # Count PII by risk level
        critical_high = sum(
            1 for p in exposed_pii
            if p.get("risk_level") in ["critical", "high"]
        )
        medium = sum(1 for p in exposed_pii if p.get("risk_level") == "medium")
        low = sum(1 for p in exposed_pii if p.get("risk_level") == "low")
        
        # Count impersonation risks
        impersonation_count = len([
            r for r in impersonation_risks
            if r.get("risk_level") in ["high", "medium"]
        ])
        
        # Build profile links
        username = user_identifiers.get("username", "")
        profile_links = {}
        for platform_id, config in SUPPORTED_PLATFORMS.items():
            if username:
                profile_links[config["name"]] = config["url_template"].format(username=username)
        
        return {
            "total_platforms_checked": total_platforms,
            "total_profiles_found": profiles_found,
            "total_pii_exposed": len(exposed_pii),
            "critical_high_risk_items": critical_high,
            "medium_risk_items": medium,
            "low_risk_items": low,
            "impersonation_risks_detected": impersonation_count,
            "profile_links": profile_links
        }
    
    def _detect_identifier_type(self, user_identifiers: Dict[str, str]) -> str:
        """
        Detect the primary identifier type from user identifiers.
        
        Args:
            user_identifiers: User-provided identifiers
            
        Returns:
            Identifier type string
        """
        if user_identifiers.get("username"):
            return "username"
        elif user_identifiers.get("email"):
            return "email"
        elif user_identifiers.get("name"):
            return "name"
        return "unknown"


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

_default_builder = ReportBuilder()


def build_report(
    scan_results: Dict[str, Any],
    user_identifiers: Dict[str, str],
    impersonation_risks: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """Module-level convenience function for building reports."""
    return _default_builder.build_report(scan_results, user_identifiers, impersonation_risks)
