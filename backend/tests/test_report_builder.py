# =============================================================================
# REPORT BUILDER SERVICE TESTS
# =============================================================================
# Unit tests for the Report Builder functionality.
# Tests report generation with risk assessment and complete findings.
# =============================================================================

"""
Report Builder Tests

Comprehensive test suite for the ReportBuilder service:
- Report structure validation
- Risk assessment calculation
- PII categorization
- Recommendations generation
- Complete findings building

Run with: pytest tests/test_report_builder.py -v
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.report.report_builder import ReportBuilder


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def builder():
    """Create a ReportBuilder instance for tests."""
    return ReportBuilder()


@pytest.fixture
def sample_scan_results():
    """Sample scan results for testing."""
    return {
        "platform_breakdown": {
            "facebook": {
                "platform": "facebook",
                "status": "found",
                "url": "https://www.facebook.com/johnperera",
                "exposed_count": 2,
                "exposed_items": []
            },
            "instagram": {
                "platform": "instagram",
                "status": "found",
                "url": "https://www.instagram.com/johnperera/",
                "exposed_count": 1,
                "exposed_items": []
            },
            "linkedin": {
                "platform": "linkedin",
                "status": "not_found",
                "url": "https://www.linkedin.com/in/johnperera",
                "exposed_count": 0,
                "exposed_items": []
            },
            "x": {
                "platform": "x",
                "status": "found",
                "url": "https://x.com/johnperera",
                "exposed_count": 0,
                "exposed_items": []
            }
        },
        "exposed_pii": [
            {
                "type": "phone",
                "value": "+94771234567",
                "platforms": ["facebook"],
                "platform_count": 1,
                "risk_level": "critical"
            },
            {
                "type": "email",
                "value": "john@gmail.com",
                "platforms": ["facebook", "instagram"],
                "platform_count": 2,
                "risk_level": "high"
            },
            {
                "type": "location",
                "value": "Colombo, Sri Lanka",
                "platforms": ["facebook"],
                "platform_count": 1,
                "risk_level": "medium"
            },
            {
                "type": "name",
                "value": "John Perera",
                "platforms": ["facebook", "instagram", "x"],
                "platform_count": 3,
                "risk_level": "low"
            }
        ],
        "exposure_score": 65,
        "risk_level": "high"
    }


@pytest.fixture
def sample_user_identifiers():
    """Sample user identifiers for testing."""
    return {
        "username": "johnperera",
        "email": "john@gmail.com",
        "name": "John Perera",
        "location": "Sri Lanka"
    }


@pytest.fixture
def sample_impersonation_risks():
    """Sample impersonation risks for testing."""
    return [
        {
            "platform": "facebook",
            "profile_url": "https://www.facebook.com/johnperera_official",
            "profile_name": "John Perera Official",
            "risk_level": "high",
            "risk_emoji": "🔴",
            "confidence_score": 0.85,
            "indicators": [
                {"type": "suspicious_suffix", "severity": "high"}
            ],
            "recommendation": "Report this profile",
            "report_url": "https://www.facebook.com/help/contact/169486816475808"
        }
    ]


# =============================================================================
# REPORT STRUCTURE TESTS
# =============================================================================

class TestReportStructure:
    """Tests for report structure validation."""
    
    def test_report_has_required_fields(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that report contains all required fields."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        assert "success" in report
        assert "report_id" in report
        assert "generated_at" in report
        assert "identifier" in report
        assert "risk_assessment" in report
        assert "impersonation_risks" in report
        assert "exposed_pii" in report
        assert "platforms" in report
        assert "recommendations" in report
        assert "complete_findings" in report
        assert "summary" in report
        assert "export" in report
    
    def test_report_success_is_true(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that success is True for valid input."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        assert report["success"] is True
    
    def test_report_id_is_uuid(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that report_id is a valid UUID format."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        report_id = report["report_id"]
        assert len(report_id) == 36  # UUID length with hyphens
        assert report_id.count('-') == 4  # UUID format
    
    def test_generated_at_is_iso_format(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that generated_at is valid ISO 8601 format."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        generated_at = report["generated_at"]
        assert "T" in generated_at
        assert generated_at.endswith("Z")
    
    def test_export_urls_are_correct(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that export URLs contain report_id."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        report_id = report["report_id"]
        assert report["export"]["pdf_url"] == f"/api/report/{report_id}/pdf"
        assert report["export"]["json_url"] == f"/api/report/{report_id}/json"


# =============================================================================
# RISK ASSESSMENT TESTS
# =============================================================================

class TestRiskAssessment:
    """Tests for risk assessment calculation."""
    
    def test_risk_assessment_has_required_fields(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that risk_assessment contains all required fields."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        risk = report["risk_assessment"]
        assert "score" in risk
        assert "level" in risk
        assert "emoji" in risk
        assert "color" in risk
        assert "summary" in risk
    
    def test_risk_score_matches_input(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that risk score matches input exposure_score."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        assert report["risk_assessment"]["score"] == 65
    
    def test_high_risk_level(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that high risk level is correctly set."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        assert report["risk_assessment"]["level"] == "high"
    
    def test_risk_emoji_matches_level(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that emoji matches risk level."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        # High risk should have orange emoji
        assert report["risk_assessment"]["emoji"] == "🟠"
    
    def test_impersonation_affects_risk_level(self, builder, sample_scan_results, sample_user_identifiers, sample_impersonation_risks):
        """Test that high impersonation risk affects overall risk level."""
        # Set base risk to medium
        sample_scan_results["risk_level"] = "medium"
        sample_scan_results["exposure_score"] = 40
        
        report = builder.build_report(
            sample_scan_results,
            sample_user_identifiers,
            sample_impersonation_risks
        )
        
        # Should be elevated to high due to impersonation
        assert report["risk_assessment"]["level"] == "high"


# =============================================================================
# PII CATEGORIZATION TESTS
# =============================================================================

class TestPIICategorization:
    """Tests for PII categorization by severity."""
    
    def test_pii_categorized_by_severity(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that PII is categorized by severity level."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        exposed_pii = report["exposed_pii"]
        assert "critical" in exposed_pii
        assert "high" in exposed_pii
        assert "medium" in exposed_pii
        assert "low" in exposed_pii
    
    def test_critical_pii_contains_phone(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that phone is categorized as critical."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        critical_items = report["exposed_pii"]["critical"]
        phone_items = [i for i in critical_items if i.get("type") == "phone"]
        assert len(phone_items) >= 1
    
    def test_high_pii_contains_email(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that email is categorized as high."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        high_items = report["exposed_pii"]["high"]
        email_items = [i for i in high_items if i.get("type") == "email"]
        assert len(email_items) >= 1
    
    def test_pii_items_enriched_with_labels(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that PII items are enriched with labels and emojis."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        for severity in ["critical", "high", "medium", "low"]:
            for item in report["exposed_pii"][severity]:
                assert "pii_emoji" in item
                assert "pii_label" in item
                assert "risk_emoji" in item


# =============================================================================
# PLATFORM BREAKDOWN TESTS
# =============================================================================

class TestPlatformBreakdown:
    """Tests for platform breakdown generation."""
    
    def test_platforms_list_has_four_items(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that platforms list has all 4 supported platforms."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        assert len(report["platforms"]) == 4
    
    def test_platform_has_required_fields(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that each platform has required fields."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        for platform in report["platforms"]:
            assert "platform_id" in platform
            assert "platform_name" in platform
            assert "platform_emoji" in platform
            assert "status" in platform
            assert "profile_url" in platform
            assert "privacy_settings_url" in platform
            assert "report_url" in platform
    
    def test_platform_status_matches_input(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that platform status matches input data."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        fb_platform = next(p for p in report["platforms"] if p["platform_id"] == "facebook")
        assert fb_platform["status"] == "found"
        
        li_platform = next(p for p in report["platforms"] if p["platform_id"] == "linkedin")
        assert li_platform["status"] == "not_found"


# =============================================================================
# RECOMMENDATIONS TESTS
# =============================================================================

class TestRecommendations:
    """Tests for recommendations generation."""
    
    def test_recommendations_is_list(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that recommendations is a list."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        assert isinstance(report["recommendations"], list)
    
    def test_recommendations_have_priority(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that each recommendation has a priority."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        for rec in report["recommendations"]:
            assert "priority" in rec
            assert isinstance(rec["priority"], int)
    
    def test_phone_exposure_generates_recommendation(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that phone exposure generates a recommendation."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        phone_recs = [r for r in report["recommendations"] if "phone" in r.get("title", "").lower()]
        assert len(phone_recs) >= 1
    
    def test_impersonation_generates_recommendation(self, builder, sample_scan_results, sample_user_identifiers, sample_impersonation_risks):
        """Test that impersonation risk generates recommendation."""
        report = builder.build_report(
            sample_scan_results,
            sample_user_identifiers,
            sample_impersonation_risks
        )
        
        # Should have recommendation about suspicious profile
        suspicious_recs = [r for r in report["recommendations"] if "suspicious" in r.get("title", "").lower() or "report" in r.get("title", "").lower()]
        assert len(suspicious_recs) >= 1


# =============================================================================
# COMPLETE FINDINGS TESTS
# =============================================================================

class TestCompleteFindings:
    """Tests for complete findings section."""
    
    def test_complete_findings_has_discovered_profiles(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that complete_findings has discovered_profiles."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        assert "discovered_profiles" in report["complete_findings"]
        assert isinstance(report["complete_findings"]["discovered_profiles"], list)
    
    def test_complete_findings_has_exposed_pii_details(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that complete_findings has exposed_pii_details."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        assert "exposed_pii_details" in report["complete_findings"]
        assert isinstance(report["complete_findings"]["exposed_pii_details"], list)
    
    def test_discovered_profiles_have_links(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that discovered profiles have links."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        for profile in report["complete_findings"]["discovered_profiles"]:
            assert "links" in profile
            assert "view_profile" in profile["links"]
            assert "privacy_settings" in profile["links"]
            assert "report_profile" in profile["links"]
    
    def test_exposed_pii_details_have_found_on(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that exposed PII details have found_on sources."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        for pii in report["complete_findings"]["exposed_pii_details"]:
            assert "found_on" in pii
            assert isinstance(pii["found_on"], list)


# =============================================================================
# SUMMARY TESTS
# =============================================================================

class TestSummary:
    """Tests for summary statistics."""
    
    def test_summary_has_required_fields(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that summary has all required fields."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        summary = report["summary"]
        assert "total_platforms_checked" in summary
        assert "total_profiles_found" in summary
        assert "total_pii_exposed" in summary
        assert "critical_high_risk_items" in summary
        assert "medium_risk_items" in summary
        assert "low_risk_items" in summary
        assert "impersonation_risks_detected" in summary
        assert "profile_links" in summary
    
    def test_platform_counts_correct(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that platform counts are correct."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        summary = report["summary"]
        assert summary["total_platforms_checked"] == 4
        assert summary["total_profiles_found"] == 3  # facebook, instagram, x found
    
    def test_pii_counts_correct(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that PII counts are correct."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        summary = report["summary"]
        assert summary["total_pii_exposed"] == 4
        assert summary["critical_high_risk_items"] == 2  # phone + email
        assert summary["medium_risk_items"] == 1  # location
        assert summary["low_risk_items"] == 1  # name
    
    def test_profile_links_populated(self, builder, sample_scan_results, sample_user_identifiers):
        """Test that profile_links is populated."""
        report = builder.build_report(sample_scan_results, sample_user_identifiers)
        
        profile_links = report["summary"]["profile_links"]
        assert "Facebook" in profile_links
        assert "Instagram" in profile_links
        assert "LinkedIn" in profile_links
        assert "X (Twitter)" in profile_links
