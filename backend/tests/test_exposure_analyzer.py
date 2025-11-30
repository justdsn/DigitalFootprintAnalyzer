# =============================================================================
# PII EXPOSURE ANALYZER SERVICE TESTS
# =============================================================================
# Unit tests for the PII Exposure Analyzer functionality.
# Tests PII consolidation, matching, scoring, and recommendations.
# =============================================================================

"""
PII Exposure Analyzer Tests

Comprehensive test suite for the PIIExposureAnalyzer service:
- PII consolidation from multiple platforms
- User identifier matching
- Exposure score calculation
- Risk level determination
- Recommendation generation
- PII extraction from text

Run with: pytest tests/test_exposure_analyzer.py -v
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.social.exposure_analyzer import PIIExposureAnalyzer, extract_pii_from_text


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def analyzer():
    """Create a PIIExposureAnalyzer instance for tests."""
    return PIIExposureAnalyzer()


@pytest.fixture
def sample_platform_data():
    """Sample platform data for testing."""
    return {
        "facebook": {
            "status": "found",
            "url": "https://www.facebook.com/johnperera",
            "data": {
                "name": "John Perera",
                "bio": "Software Developer | Contact: john@gmail.com | +94771234567",
                "location": "Colombo, Sri Lanka",
                "profile_image": "https://example.com/fb_profile.jpg"
            }
        },
        "instagram": {
            "status": "found",
            "url": "https://www.instagram.com/johnperera/",
            "data": {
                "name": "John Perera",
                "bio": "📧 john@gmail.com",
                "profile_image": "https://example.com/ig_profile.jpg"
            }
        },
        "x": {
            "status": "found",
            "url": "https://x.com/johnperera",
            "data": {
                "name": "John P",
                "bio": "Developer | Tech enthusiast",
                "profile_image": "https://example.com/x_profile.jpg"
            }
        },
        "linkedin": {
            "status": "not_found",
            "url": "https://www.linkedin.com/in/johnperera",
            "data": {}
        }
    }


@pytest.fixture
def sample_user_identifiers():
    """Sample user identifiers for testing."""
    return {
        "username": "johnperera",
        "phone": "0771234567",
        "email": "john@gmail.com",
        "name": "John Perera"
    }


# =============================================================================
# PII CONSOLIDATION TESTS
# =============================================================================

class TestPIIConsolidation:
    """Tests for PII consolidation functionality."""
    
    def test_consolidate_pii_extracts_names(self, analyzer, sample_platform_data):
        """Test that names are extracted from platform data."""
        pii = analyzer._consolidate_pii(sample_platform_data)
        names = [item for item in pii if item["type"] == "name"]
        
        assert len(names) >= 1
        assert any(item["value"] == "John Perera" for item in names)
    
    def test_consolidate_pii_extracts_emails(self, analyzer, sample_platform_data):
        """Test that emails are extracted from bio text."""
        pii = analyzer._consolidate_pii(sample_platform_data)
        emails = [item for item in pii if item["type"] == "email"]
        
        assert len(emails) >= 1
        assert any("john@gmail.com" in item["value"].lower() for item in emails)
    
    def test_consolidate_pii_extracts_phones(self, analyzer, sample_platform_data):
        """Test that phones are extracted from bio text."""
        pii = analyzer._consolidate_pii(sample_platform_data)
        phones = [item for item in pii if item["type"] == "phone"]
        
        assert len(phones) >= 1
    
    def test_consolidate_pii_tracks_platforms(self, analyzer, sample_platform_data):
        """Test that platforms are tracked for each PII item."""
        pii = analyzer._consolidate_pii(sample_platform_data)
        
        # Find email item
        emails = [item for item in pii if item["type"] == "email"]
        assert len(emails) >= 1
        
        # Should appear on multiple platforms
        email_item = emails[0]
        assert "platforms" in email_item
        assert len(email_item["platforms"]) >= 1
    
    def test_consolidate_pii_assigns_risk_levels(self, analyzer, sample_platform_data):
        """Test that risk levels are assigned to each PII item."""
        pii = analyzer._consolidate_pii(sample_platform_data)
        
        for item in pii:
            assert "risk_level" in item
            assert item["risk_level"] in ["critical", "high", "medium", "low"]
    
    def test_consolidate_pii_handles_empty_data(self, analyzer):
        """Test consolidation with empty platform data."""
        pii = analyzer._consolidate_pii({})
        
        assert isinstance(pii, list)
        assert len(pii) == 0
    
    def test_consolidate_pii_skips_not_found_profiles(self, analyzer):
        """Test that not_found profiles are skipped."""
        platform_data = {
            "facebook": {
                "status": "not_found",
                "url": "https://www.facebook.com/test",
                "data": {
                    "name": "Test User"  # Should be ignored
                }
            }
        }
        pii = analyzer._consolidate_pii(platform_data)
        
        assert len(pii) == 0


# =============================================================================
# USER IDENTIFIER MATCHING TESTS
# =============================================================================

class TestUserIdentifierMatching:
    """Tests for matching exposed PII to user identifiers."""
    
    def test_match_phone_number(self, analyzer):
        """Test matching phone numbers."""
        exposed_pii = [
            {"type": "phone", "value": "+94771234567", "platforms": ["facebook"], "platform_count": 1, "risk_level": "critical"}
        ]
        user_identifiers = {"phone": "0771234567"}
        
        matched = analyzer._match_to_user_identifiers(exposed_pii, user_identifiers)
        
        assert matched[0]["matches_user_input"] is True
    
    def test_match_email_case_insensitive(self, analyzer):
        """Test matching emails case-insensitively."""
        exposed_pii = [
            {"type": "email", "value": "John@Gmail.com", "platforms": ["facebook"], "platform_count": 1, "risk_level": "high"}
        ]
        user_identifiers = {"email": "john@gmail.com"}
        
        matched = analyzer._match_to_user_identifiers(exposed_pii, user_identifiers)
        
        assert matched[0]["matches_user_input"] is True
    
    def test_match_name_partial(self, analyzer):
        """Test partial name matching."""
        exposed_pii = [
            {"type": "name", "value": "John Perera", "platforms": ["facebook"], "platform_count": 1, "risk_level": "low"}
        ]
        user_identifiers = {"name": "John"}
        
        matched = analyzer._match_to_user_identifiers(exposed_pii, user_identifiers)
        
        assert matched[0]["matches_user_input"] is True
    
    def test_no_match_different_values(self, analyzer):
        """Test that different values don't match."""
        exposed_pii = [
            {"type": "email", "value": "other@example.com", "platforms": ["facebook"], "platform_count": 1, "risk_level": "high"}
        ]
        user_identifiers = {"email": "john@gmail.com"}
        
        matched = analyzer._match_to_user_identifiers(exposed_pii, user_identifiers)
        
        assert matched[0]["matches_user_input"] is False


# =============================================================================
# EXPOSURE SCORE CALCULATION TESTS
# =============================================================================

class TestExposureScoreCalculation:
    """Tests for exposure score calculation."""
    
    def test_empty_pii_returns_zero(self, analyzer):
        """Test that empty PII list returns score of 0."""
        score = analyzer._calculate_exposure_score([])
        
        assert score == 0
    
    def test_critical_items_increase_score(self, analyzer):
        """Test that critical items significantly increase score."""
        exposed_pii = [
            {"type": "phone", "risk_level": "critical", "matches_user_input": True, "platform_count": 1}
        ]
        score = analyzer._calculate_exposure_score(exposed_pii)
        
        assert score > 0
    
    def test_matched_items_score_higher(self, analyzer):
        """Test that matched items score higher."""
        unmatched = [
            {"type": "email", "risk_level": "high", "matches_user_input": False, "platform_count": 1}
        ]
        matched = [
            {"type": "email", "risk_level": "high", "matches_user_input": True, "platform_count": 1}
        ]
        
        score_unmatched = analyzer._calculate_exposure_score(unmatched)
        score_matched = analyzer._calculate_exposure_score(matched)
        
        assert score_matched > score_unmatched
    
    def test_multi_platform_exposure_increases_score(self, analyzer):
        """Test that exposure on multiple platforms increases score."""
        single_platform = [
            {"type": "email", "risk_level": "high", "matches_user_input": False, "platform_count": 1}
        ]
        multi_platform = [
            {"type": "email", "risk_level": "high", "matches_user_input": False, "platform_count": 3}
        ]
        
        score_single = analyzer._calculate_exposure_score(single_platform)
        score_multi = analyzer._calculate_exposure_score(multi_platform)
        
        assert score_multi > score_single
    
    def test_score_capped_at_100(self, analyzer):
        """Test that score is capped at 100."""
        # Create many high-risk items
        exposed_pii = [
            {"type": "phone", "risk_level": "critical", "matches_user_input": True, "platform_count": 4}
            for _ in range(10)
        ]
        score = analyzer._calculate_exposure_score(exposed_pii)
        
        assert score <= 100


# =============================================================================
# RISK LEVEL DETERMINATION TESTS
# =============================================================================

class TestRiskLevelDetermination:
    """Tests for risk level determination."""
    
    def test_low_score_returns_low(self, analyzer):
        """Test that low score returns low risk level."""
        level = analyzer._determine_risk_level(10)
        
        assert level == "low"
    
    def test_medium_score_returns_medium(self, analyzer):
        """Test that medium score returns medium risk level."""
        level = analyzer._determine_risk_level(35)
        
        assert level == "medium"
    
    def test_high_score_returns_high(self, analyzer):
        """Test that high score returns high risk level."""
        level = analyzer._determine_risk_level(60)
        
        assert level == "high"
    
    def test_critical_score_returns_critical(self, analyzer):
        """Test that critical score returns critical risk level."""
        level = analyzer._determine_risk_level(85)
        
        assert level == "critical"


# =============================================================================
# RECOMMENDATION GENERATION TESTS
# =============================================================================

class TestRecommendationGeneration:
    """Tests for recommendation generation."""
    
    def test_phone_exposure_generates_recommendation(self, analyzer):
        """Test that phone exposure generates specific recommendation."""
        exposed_pii = [
            {"type": "phone", "value": "+94771234567", "platforms": ["facebook"], "risk_level": "critical", "matches_user_input": True, "platform_count": 1}
        ]
        recommendations = analyzer._generate_recommendations(exposed_pii, "high")
        
        assert any("phone" in rec.lower() for rec in recommendations)
    
    def test_email_exposure_generates_recommendation(self, analyzer):
        """Test that email exposure generates specific recommendation."""
        exposed_pii = [
            {"type": "email", "value": "john@gmail.com", "platforms": ["facebook", "instagram"], "risk_level": "high", "matches_user_input": True, "platform_count": 2}
        ]
        recommendations = analyzer._generate_recommendations(exposed_pii, "high")
        
        assert any("email" in rec.lower() for rec in recommendations)
    
    def test_critical_risk_generates_urgent_recommendations(self, analyzer):
        """Test that critical risk level generates urgent recommendations."""
        exposed_pii = []
        recommendations = analyzer._generate_recommendations(exposed_pii, "critical")
        
        assert any("critical" in rec.lower() or "immediate" in rec.lower() or "audit" in rec.lower() for rec in recommendations)
    
    def test_always_includes_monitoring_recommendation(self, analyzer):
        """Test that monitoring recommendation is always included."""
        recommendations = analyzer._generate_recommendations([], "low")
        
        assert any("search" in rec.lower() or "monitor" in rec.lower() for rec in recommendations)


# =============================================================================
# PII EXTRACTION FROM TEXT TESTS
# =============================================================================

class TestPIIExtractionFromText:
    """Tests for PII extraction from text using regex."""
    
    def test_extract_email_from_text(self, analyzer):
        """Test extracting email from text."""
        text = "Contact me at john@example.com for inquiries"
        result = analyzer.extract_pii_from_text(text)
        
        assert "john@example.com" in result["emails"]
    
    def test_extract_multiple_emails(self, analyzer):
        """Test extracting multiple emails."""
        text = "Email john@example.com or jane@test.org"
        result = analyzer.extract_pii_from_text(text)
        
        assert len(result["emails"]) == 2
    
    def test_extract_sri_lankan_phone(self, analyzer):
        """Test extracting Sri Lankan phone numbers."""
        text = "Call me at 0771234567"
        result = analyzer.extract_pii_from_text(text)
        
        assert len(result["phones"]) >= 1
    
    def test_extract_phone_with_spaces(self, analyzer):
        """Test extracting phone with spaces."""
        text = "My number is 077 123 4567"
        result = analyzer.extract_pii_from_text(text)
        
        assert len(result["phones"]) >= 1
    
    def test_extract_international_phone(self, analyzer):
        """Test extracting international format phone."""
        text = "Contact: +94771234567"
        result = analyzer.extract_pii_from_text(text)
        
        assert len(result["phones"]) >= 1
    
    def test_extract_url_from_text(self, analyzer):
        """Test extracting URLs from text."""
        text = "Visit https://example.com for more info"
        result = analyzer.extract_pii_from_text(text)
        
        assert "https://example.com" in result["urls"]
    
    def test_empty_text_returns_empty_lists(self, analyzer):
        """Test that empty text returns empty lists."""
        result = analyzer.extract_pii_from_text("")
        
        assert result["emails"] == []
        assert result["phones"] == []
        assert result["urls"] == []
    
    def test_none_text_returns_empty_lists(self, analyzer):
        """Test that None text returns empty lists."""
        result = analyzer.extract_pii_from_text(None)
        
        assert result["emails"] == []
        assert result["phones"] == []
        assert result["urls"] == []


# =============================================================================
# FULL ANALYSIS TESTS
# =============================================================================

class TestFullAnalysis:
    """Tests for full analysis workflow."""
    
    def test_analyze_returns_expected_structure(self, analyzer, sample_platform_data, sample_user_identifiers):
        """Test that analyze returns expected response structure."""
        result = analyzer.analyze(sample_platform_data, sample_user_identifiers)
        
        assert "user_identifiers" in result
        assert "scan_timestamp" in result
        assert "platforms_checked" in result
        assert "profiles_found" in result
        assert "profiles_not_found" in result
        assert "exposure_score" in result
        assert "risk_level" in result
        assert "total_exposed_items" in result
        assert "exposed_pii" in result
        assert "platform_breakdown" in result
        assert "recommendations" in result
    
    def test_analyze_tracks_platforms_correctly(self, analyzer, sample_platform_data, sample_user_identifiers):
        """Test that platforms are tracked correctly."""
        result = analyzer.analyze(sample_platform_data, sample_user_identifiers)
        
        assert "facebook" in result["platforms_checked"]
        assert "instagram" in result["platforms_checked"]
        assert "x" in result["platforms_checked"]
        assert "linkedin" in result["platforms_checked"]
        
        assert "facebook" in result["profiles_found"]
        assert "linkedin" in result["profiles_not_found"]
    
    def test_analyze_generates_valid_timestamp(self, analyzer, sample_platform_data, sample_user_identifiers):
        """Test that timestamp is valid ISO format."""
        result = analyzer.analyze(sample_platform_data, sample_user_identifiers)
        
        assert result["scan_timestamp"].endswith("Z")
        assert "T" in result["scan_timestamp"]
    
    def test_analyze_empty_data(self, analyzer):
        """Test analysis with empty platform data."""
        result = analyzer.analyze({}, {"username": "test"})
        
        assert result["exposure_score"] == 0
        assert result["risk_level"] == "low"
        assert result["total_exposed_items"] == 0


# =============================================================================
# MODULE-LEVEL FUNCTION TESTS
# =============================================================================

class TestModuleFunctions:
    """Tests for module-level convenience functions."""
    
    def test_module_extract_pii_from_text(self):
        """Test module-level extract_pii_from_text function."""
        result = extract_pii_from_text("Contact: john@example.com")
        
        assert "john@example.com" in result["emails"]


# =============================================================================
# PHONE NORMALIZATION TESTS
# =============================================================================

class TestPhoneNormalization:
    """Tests for phone number normalization."""
    
    def test_normalize_local_format(self, analyzer):
        """Test normalizing local format phone."""
        result = analyzer._normalize_phone("0771234567")
        
        assert result == "+94771234567"
    
    def test_normalize_international_format(self, analyzer):
        """Test normalizing already international format."""
        result = analyzer._normalize_phone("+94771234567")
        
        assert result == "+94771234567"
    
    def test_normalize_with_spaces(self, analyzer):
        """Test normalizing phone with spaces."""
        result = analyzer._normalize_phone("077 123 4567")
        
        assert result == "+94771234567"
    
    def test_normalize_with_dashes(self, analyzer):
        """Test normalizing phone with dashes."""
        result = analyzer._normalize_phone("077-123-4567")
        
        assert result == "+94771234567"
    
    def test_normalize_empty_returns_empty(self, analyzer):
        """Test that empty input returns empty string."""
        result = analyzer._normalize_phone("")
        
        assert result == ""
