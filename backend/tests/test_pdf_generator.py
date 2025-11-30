# =============================================================================
# PDF GENERATOR SERVICE TESTS
# =============================================================================
# Unit tests for the PDF Generator functionality.
# Tests PDF generation from report data.
# =============================================================================

"""
PDF Generator Tests

Comprehensive test suite for the PDFGenerator service:
- PDF generation
- Content validation
- Error handling

Run with: pytest tests/test_pdf_generator.py -v
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.report.pdf_generator import PDFGenerator


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def generator():
    """Create a PDFGenerator instance for tests."""
    return PDFGenerator()


@pytest.fixture
def sample_report_data():
    """Sample report data for testing."""
    return {
        "success": True,
        "report_id": "test-report-1234-5678-abcd",
        "generated_at": "2024-01-15T10:30:00Z",
        "identifier": {
            "type": "username",
            "value": "johnperera"
        },
        "risk_assessment": {
            "score": 65,
            "level": "high",
            "emoji": "🟠",
            "color": "#fd7e14",
            "summary": "High level of personal information exposure.",
            "critical_items": 1,
            "high_risk_items": 1,
            "impersonation_count": 1
        },
        "impersonation_risks": [
            {
                "platform": "facebook",
                "profile_url": "https://www.facebook.com/johnperera_official",
                "profile_name": "John Perera Official",
                "risk_level": "high",
                "risk_emoji": "🔴",
                "confidence_score": 0.85,
                "indicators": [],
                "recommendation": "Report this profile for impersonation",
                "report_url": "https://www.facebook.com/help/contact/169486816475808"
            }
        ],
        "exposed_pii": {
            "critical": [
                {
                    "type": "phone",
                    "value": "+94771234567",
                    "platforms": ["facebook"],
                    "platform_count": 1,
                    "risk_level": "critical",
                    "pii_emoji": "📱",
                    "pii_label": "Phone Number",
                    "risk_emoji": "🔴"
                }
            ],
            "high": [
                {
                    "type": "email",
                    "value": "john@gmail.com",
                    "platforms": ["facebook", "instagram"],
                    "platform_count": 2,
                    "risk_level": "high",
                    "pii_emoji": "📧",
                    "pii_label": "Email Address",
                    "risk_emoji": "🟠"
                }
            ],
            "medium": [],
            "low": []
        },
        "platforms": [
            {
                "platform_id": "facebook",
                "platform_name": "Facebook",
                "platform_emoji": "📘",
                "status": "found",
                "profile_url": "https://www.facebook.com/johnperera",
                "privacy_settings_url": "https://www.facebook.com/settings?tab=privacy",
                "report_url": "https://www.facebook.com/help/contact/169486816475808",
                "exposed_count": 2
            },
            {
                "platform_id": "instagram",
                "platform_name": "Instagram",
                "platform_emoji": "📷",
                "status": "found",
                "profile_url": "https://www.instagram.com/johnperera/",
                "privacy_settings_url": "https://www.instagram.com/accounts/privacy_and_security/",
                "report_url": "https://help.instagram.com/contact/636276399721841",
                "exposed_count": 1
            }
        ],
        "recommendations": [
            {
                "priority": 1,
                "severity": "critical",
                "emoji": "📱",
                "title": "Remove Phone Number from Profiles",
                "description": "Your phone number is exposed. Remove it to prevent spam.",
                "action_url": "",
                "action_label": "Review Privacy Settings"
            }
        ],
        "complete_findings": {
            "discovered_profiles": [
                {
                    "index": 1,
                    "platform": "Facebook",
                    "platform_emoji": "📘",
                    "found": True,
                    "profile_name": "John Perera",
                    "username": "johnperera",
                    "profile_url": "https://www.facebook.com/johnperera",
                    "discovery_source": "Direct URL Check",
                    "links": {
                        "view_profile": "https://www.facebook.com/johnperera",
                        "privacy_settings": "https://www.facebook.com/settings?tab=privacy",
                        "report_profile": "https://www.facebook.com/help/contact/169486816475808"
                    },
                    "checked_urls": None
                }
            ],
            "exposed_pii_details": [
                {
                    "index": 1,
                    "pii_type": "phone",
                    "pii_emoji": "📱",
                    "pii_label": "Phone Number",
                    "exposed_value": "+94771234567",
                    "risk_level": "critical",
                    "risk_emoji": "🔴",
                    "risk_description": "This is considered critical risk information",
                    "matches_user_input": True,
                    "found_on": [
                        {
                            "platform": "Facebook",
                            "platform_emoji": "📘",
                            "location_in_profile": "Bio/Profile Info",
                            "profile_url": "https://www.facebook.com/johnperera",
                            "direct_link": "https://www.facebook.com/johnperera"
                        }
                    ],
                    "recommended_action": "Remove this phone number immediately from all profiles"
                }
            ]
        },
        "summary": {
            "total_platforms_checked": 4,
            "total_profiles_found": 2,
            "total_pii_exposed": 2,
            "critical_high_risk_items": 2,
            "medium_risk_items": 0,
            "low_risk_items": 0,
            "impersonation_risks_detected": 1,
            "profile_links": {
                "Facebook": "https://www.facebook.com/johnperera",
                "Instagram": "https://www.instagram.com/johnperera/"
            }
        }
    }


# =============================================================================
# PDF GENERATION TESTS
# =============================================================================

class TestPDFGeneration:
    """Tests for PDF generation."""
    
    def test_generate_returns_bytes(self, generator, sample_report_data):
        """Test that generate returns bytes."""
        pdf_bytes = generator.generate(sample_report_data)
        
        assert isinstance(pdf_bytes, bytes)
    
    def test_generate_returns_valid_pdf(self, generator, sample_report_data):
        """Test that generated PDF has valid PDF header."""
        pdf_bytes = generator.generate(sample_report_data)
        
        # PDF files start with %PDF-
        assert pdf_bytes.startswith(b'%PDF-')
    
    def test_generate_pdf_not_empty(self, generator, sample_report_data):
        """Test that generated PDF is not empty."""
        pdf_bytes = generator.generate(sample_report_data)
        
        # PDF should be at least a few KB
        assert len(pdf_bytes) > 1000
    
    def test_generate_with_empty_pii(self, generator, sample_report_data):
        """Test generation with empty PII lists."""
        sample_report_data["exposed_pii"] = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        pdf_bytes = generator.generate(sample_report_data)
        
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b'%PDF-')
    
    def test_generate_with_empty_impersonation_risks(self, generator, sample_report_data):
        """Test generation with empty impersonation risks."""
        sample_report_data["impersonation_risks"] = []
        
        pdf_bytes = generator.generate(sample_report_data)
        
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b'%PDF-')
    
    def test_generate_with_empty_platforms(self, generator, sample_report_data):
        """Test generation with empty platforms list."""
        sample_report_data["platforms"] = []
        
        pdf_bytes = generator.generate(sample_report_data)
        
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b'%PDF-')
    
    def test_generate_with_empty_recommendations(self, generator, sample_report_data):
        """Test generation with empty recommendations."""
        sample_report_data["recommendations"] = []
        
        pdf_bytes = generator.generate(sample_report_data)
        
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b'%PDF-')


# =============================================================================
# STYLING TESTS
# =============================================================================

class TestStyling:
    """Tests for PDF styling."""
    
    def test_custom_styles_created(self, generator):
        """Test that custom styles are created."""
        assert 'CustomTitle' in generator.styles
        assert 'SectionHeader' in generator.styles
        assert 'SubSection' in generator.styles
        assert 'NormalLink' in generator.styles
    
    def test_risk_color_styles_created(self, generator):
        """Test that risk color styles are created."""
        assert 'RiskCritical' in generator.styles
        assert 'RiskHigh' in generator.styles
        assert 'RiskMedium' in generator.styles
        assert 'RiskLow' in generator.styles
    
    def test_risk_colors_defined(self, generator):
        """Test that risk colors are defined."""
        assert "critical" in generator.RISK_COLORS
        assert "high" in generator.RISK_COLORS
        assert "medium" in generator.RISK_COLORS
        assert "low" in generator.RISK_COLORS


# =============================================================================
# SECTION BUILDING TESTS
# =============================================================================

class TestSectionBuilding:
    """Tests for individual section building."""
    
    def test_build_header(self, generator, sample_report_data):
        """Test header section building."""
        elements = generator._build_header(sample_report_data)
        
        assert isinstance(elements, list)
        assert len(elements) > 0
    
    def test_build_risk_section(self, generator, sample_report_data):
        """Test risk section building."""
        elements = generator._build_risk_section(sample_report_data)
        
        assert isinstance(elements, list)
        assert len(elements) > 0
    
    def test_build_impersonation_section(self, generator, sample_report_data):
        """Test impersonation section building."""
        elements = generator._build_impersonation_section(sample_report_data)
        
        assert isinstance(elements, list)
        # Should have content since impersonation_risks is not empty
        assert len(elements) > 0
    
    def test_build_impersonation_section_empty(self, generator, sample_report_data):
        """Test impersonation section building with no risks."""
        sample_report_data["impersonation_risks"] = []
        elements = generator._build_impersonation_section(sample_report_data)
        
        assert isinstance(elements, list)
        # Should be empty or minimal
        assert len(elements) == 0
    
    def test_build_pii_section(self, generator, sample_report_data):
        """Test PII section building."""
        elements = generator._build_pii_section(sample_report_data)
        
        assert isinstance(elements, list)
        assert len(elements) > 0
    
    def test_build_platform_section(self, generator, sample_report_data):
        """Test platform section building."""
        elements = generator._build_platform_section(sample_report_data)
        
        assert isinstance(elements, list)
        assert len(elements) > 0
    
    def test_build_recommendations_section(self, generator, sample_report_data):
        """Test recommendations section building."""
        elements = generator._build_recommendations_section(sample_report_data)
        
        assert isinstance(elements, list)
        assert len(elements) > 0
    
    def test_build_findings_section(self, generator, sample_report_data):
        """Test findings section building."""
        elements = generator._build_findings_section(sample_report_data)
        
        assert isinstance(elements, list)
        assert len(elements) > 0


# =============================================================================
# MODULE FUNCTION TESTS
# =============================================================================

class TestModuleFunctions:
    """Tests for module-level convenience functions."""
    
    def test_generate_pdf_function(self, sample_report_data):
        """Test module-level generate_pdf function."""
        from app.services.report.pdf_generator import generate_pdf
        
        pdf_bytes = generate_pdf(sample_report_data)
        
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b'%PDF-')
