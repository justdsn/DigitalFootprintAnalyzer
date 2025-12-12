# =============================================================================
# OSINT SCHEMAS TESTS
# =============================================================================
# Unit tests for Pydantic schemas.
# =============================================================================

"""
OSINT Schemas Tests

Test suite for OSINT Pydantic models:
- Model validation
- Field constraints
- Serialization/deserialization
- Error handling

Run with: pytest tests/test_osint_schemas.py -v
"""

import pytest
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.osint.schemas import (
    IdentifierType,
    Platform,
    RiskLevel,
    CollectionResult,
    SessionInfo,
    PIIData,
    ParsedProfile,
    ProfileAnalysis,
    AnalyzedProfile,
    OverallRisk,
    OSINTAnalyzeRequest,
    OSINTAnalyzeResponse,
    SessionStatus,
    SessionsStatusResponse,
)


# =============================================================================
# ENUM TESTS
# =============================================================================

def test_identifier_type_enum():
    """Test IdentifierType enum values."""
    assert IdentifierType.USERNAME.value == "username"
    assert IdentifierType.EMAIL.value == "email"
    assert IdentifierType.PHONE.value == "phone"
    assert IdentifierType.NAME.value == "name"


def test_platform_enum():
    """Test Platform enum values."""
    assert Platform.INSTAGRAM.value == "instagram"
    assert Platform.FACEBOOK.value == "facebook"
    assert Platform.LINKEDIN.value == "linkedin"
    assert Platform.TWITTER.value == "twitter"


def test_risk_level_enum():
    """Test RiskLevel enum values."""
    assert RiskLevel.LOW.value == "low"
    assert RiskLevel.MEDIUM.value == "medium"
    assert RiskLevel.HIGH.value == "high"
    assert RiskLevel.CRITICAL.value == "critical"


# =============================================================================
# COLLECTION RESULT TESTS
# =============================================================================

def test_collection_result_success():
    """Test successful collection result."""
    result = CollectionResult(
        success=True,
        platform="instagram",
        url="https://instagram.com/testuser",
        html="<html></html>",
        text_blocks={"bio": "Test bio"}
    )
    
    assert result.success is True
    assert result.platform == "instagram"
    assert result.url == "https://instagram.com/testuser"
    assert result.html == "<html></html>"
    assert result.text_blocks["bio"] == "Test bio"
    assert result.error is None


def test_collection_result_failure():
    """Test failed collection result."""
    result = CollectionResult(
        success=False,
        platform="instagram",
        url="https://instagram.com/testuser",
        error="Login wall detected"
    )
    
    assert result.success is False
    assert result.error == "Login wall detected"
    assert result.html is None


# =============================================================================
# PII DATA TESTS
# =============================================================================

def test_pii_data_creation():
    """Test PIIData model creation."""
    pii = PIIData(
        emails=["test@example.com"],
        phones=["+1234567890"],
        urls=["https://example.com"],
        addresses=["123 Main St"]
    )
    
    assert len(pii.emails) == 1
    assert pii.emails[0] == "test@example.com"
    assert len(pii.phones) == 1
    assert len(pii.urls) == 1
    assert len(pii.addresses) == 1


def test_pii_data_empty():
    """Test PIIData with empty lists."""
    pii = PIIData()
    
    assert pii.emails == []
    assert pii.phones == []
    assert pii.urls == []
    assert pii.addresses == []


# =============================================================================
# PARSED PROFILE TESTS
# =============================================================================

def test_parsed_profile_complete():
    """Test complete parsed profile."""
    profile = ParsedProfile(
        platform="instagram",
        url="https://instagram.com/testuser",
        username="testuser",
        name="Test User",
        bio="Software Developer",
        followers=1000,
        following=500,
        location="New York",
        job_title="Engineer",
        urls=["https://example.com"],
        collection_success=True
    )
    
    assert profile.platform == "instagram"
    assert profile.username == "testuser"
    assert profile.name == "Test User"
    assert profile.followers == 1000
    assert profile.collection_success is True


def test_parsed_profile_minimal():
    """Test minimal parsed profile with defaults."""
    profile = ParsedProfile(platform="instagram")
    
    assert profile.platform == "instagram"
    assert profile.username is None
    assert profile.name is None
    assert profile.urls == []
    assert profile.metadata == {}
    assert profile.collection_success is False


# =============================================================================
# PROFILE ANALYSIS TESTS
# =============================================================================

def test_profile_analysis_creation():
    """Test ProfileAnalysis model creation."""
    analysis = ProfileAnalysis(
        username_similarity=85,
        bio_similarity=70,
        pii_exposure_score=30,
        timeline_risk="medium",
        impersonation_score=45
    )
    
    assert analysis.username_similarity == 85
    assert analysis.bio_similarity == 70
    assert analysis.pii_exposure_score == 30
    assert analysis.timeline_risk == "medium"
    assert analysis.impersonation_score == 45


def test_profile_analysis_validation():
    """Test ProfileAnalysis field validation."""
    # Test valid ranges (0-100)
    analysis = ProfileAnalysis(
        username_similarity=0,
        bio_similarity=100,
        pii_exposure_score=50,
        timeline_risk="low",
        impersonation_score=75
    )
    assert analysis.username_similarity == 0
    assert analysis.bio_similarity == 100


# =============================================================================
# OVERALL RISK TESTS
# =============================================================================

def test_overall_risk_creation():
    """Test OverallRisk model creation."""
    risk = OverallRisk(
        exposure="Medium",
        impersonation="Low",
        score=45,
        profiles_analyzed=3
    )
    
    assert risk.exposure == "Medium"
    assert risk.impersonation == "Low"
    assert risk.score == 45
    assert risk.profiles_analyzed == 3


def test_overall_risk_defaults():
    """Test OverallRisk with defaults."""
    risk = OverallRisk(
        exposure="Low",
        impersonation="Low"
    )
    
    assert risk.score == 0
    assert risk.profiles_analyzed == 0


# =============================================================================
# API REQUEST TESTS
# =============================================================================

def test_osint_analyze_request_basic():
    """Test basic OSINTAnalyzeRequest."""
    request = OSINTAnalyzeRequest(
        identifier="testuser"
    )
    
    assert request.identifier == "testuser"
    assert request.platforms is None
    assert request.use_search is False


def test_osint_analyze_request_with_platforms():
    """Test OSINTAnalyzeRequest with platforms."""
    request = OSINTAnalyzeRequest(
        identifier="testuser",
        platforms=["instagram", "facebook"],
        use_search=True
    )
    
    assert request.identifier == "testuser"
    assert len(request.platforms) == 2
    assert "instagram" in request.platforms
    assert request.use_search is True


def test_osint_analyze_request_validation():
    """Test OSINTAnalyzeRequest validation."""
    # Test empty identifier
    with pytest.raises(ValueError):
        OSINTAnalyzeRequest(identifier="")
    
    # Test whitespace-only identifier
    with pytest.raises(ValueError):
        OSINTAnalyzeRequest(identifier="   ")


def test_osint_analyze_request_strips_whitespace():
    """Test that identifier is stripped."""
    request = OSINTAnalyzeRequest(identifier="  testuser  ")
    assert request.identifier == "testuser"


# =============================================================================
# API RESPONSE TESTS
# =============================================================================

def test_osint_analyze_response_creation():
    """Test OSINTAnalyzeResponse creation."""
    response = OSINTAnalyzeResponse(
        input="testuser",
        identifier_type="username",
        username="testuser",
        timestamp="2024-01-01T00:00:00",
        profiles_found=[],
        correlation={},
        overall_risk=OverallRisk(
            exposure="Low",
            impersonation="Low",
            score=0,
            profiles_analyzed=0
        ),
        processing_time_ms=100.5
    )
    
    assert response.input == "testuser"
    assert response.identifier_type == "username"
    assert response.username == "testuser"
    assert len(response.profiles_found) == 0
    assert response.overall_risk.exposure == "Low"
    assert response.processing_time_ms == 100.5


def test_osint_analyze_response_with_profiles():
    """Test OSINTAnalyzeResponse with profiles."""
    profile_data = {
        "platform": "instagram",
        "username": "testuser",
        "name": "Test User",
        "bio": "Software Developer"
    }
    
    response = OSINTAnalyzeResponse(
        input="testuser",
        identifier_type="username",
        username="testuser",
        timestamp="2024-01-01T00:00:00",
        profiles_found=[profile_data],
        correlation={"correlated": True},
        overall_risk=OverallRisk(
            exposure="Medium",
            impersonation="Low",
            score=35,
            profiles_analyzed=1
        ),
        processing_time_ms=2500.0
    )
    
    assert len(response.profiles_found) == 1
    assert response.profiles_found[0]["platform"] == "instagram"
    assert response.overall_risk.profiles_analyzed == 1


# =============================================================================
# SESSION STATUS TESTS
# =============================================================================

def test_session_status_valid():
    """Test valid session status."""
    status = SessionStatus(
        platform="instagram",
        exists=True,
        valid=True,
        age_days=5,
        expires_in_days=25
    )
    
    assert status.platform == "instagram"
    assert status.exists is True
    assert status.valid is True
    assert status.age_days == 5
    assert status.expires_in_days == 25
    assert status.error is None


def test_session_status_expired():
    """Test expired session status."""
    status = SessionStatus(
        platform="facebook",
        exists=True,
        valid=False,
        age_days=35,
        expires_in_days=-5,
        error="Session expired"
    )
    
    assert status.exists is True
    assert status.valid is False
    assert status.error == "Session expired"


def test_sessions_status_response():
    """Test SessionsStatusResponse."""
    status1 = SessionStatus(
        platform="instagram",
        exists=True,
        valid=True
    )
    status2 = SessionStatus(
        platform="facebook",
        exists=False,
        valid=False
    )
    
    response = SessionsStatusResponse(
        sessions={"instagram": status1, "facebook": status2},
        healthy_count=1,
        expired_count=0,
        missing_count=1
    )
    
    assert len(response.sessions) == 2
    assert response.healthy_count == 1
    assert response.missing_count == 1


# =============================================================================
# SERIALIZATION TESTS
# =============================================================================

def test_model_to_dict():
    """Test model serialization to dict."""
    pii = PIIData(
        emails=["test@example.com"],
        phones=["+1234567890"]
    )
    
    data = pii.model_dump()
    assert isinstance(data, dict)
    assert "emails" in data
    assert "phones" in data
    assert data["emails"] == ["test@example.com"]


def test_model_from_dict():
    """Test model deserialization from dict."""
    data = {
        "emails": ["test@example.com"],
        "phones": ["+1234567890"],
        "urls": [],
        "addresses": []
    }
    
    pii = PIIData(**data)
    assert pii.emails[0] == "test@example.com"
    assert pii.phones[0] == "+1234567890"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
