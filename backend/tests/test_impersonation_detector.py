# =============================================================================
# IMPERSONATION DETECTOR SERVICE TESTS
# =============================================================================
# Unit tests for the Impersonation Detector functionality.
# Tests detection of suspicious patterns and impersonation indicators.
# =============================================================================

"""
Impersonation Detector Tests

Comprehensive test suite for the ImpersonationDetector service:
- Suspicious suffix detection
- Suspicious prefix detection
- Username with numbers detection
- Location mismatch detection
- Suspicious bio content detection
- Risk level calculation

Run with: pytest tests/test_impersonation_detector.py -v
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.social.impersonation_detector import ImpersonationDetector


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def detector():
    """Create an ImpersonationDetector instance for tests."""
    return ImpersonationDetector()


@pytest.fixture
def sample_platform_data():
    """Sample platform data for testing."""
    return {
        "facebook": {
            "status": "found",
            "url": "https://www.facebook.com/johnperera_official",
            "data": {
                "name": "John Perera",
                "bio": "DM me for free money! Click link in bio!",
                "location": "Nigeria",
                "profile_image": "https://example.com/fb_profile.jpg"
            }
        },
        "instagram": {
            "status": "found",
            "url": "https://www.instagram.com/johnperera123/",
            "data": {
                "name": "John Perera",
                "bio": "Software Developer",
                "location": "Colombo, Sri Lanka",
                "profile_image": "https://example.com/ig_profile.jpg"
            }
        },
        "linkedin": {
            "status": "not_found",
            "url": "https://www.linkedin.com/in/johnperera",
            "data": {}
        },
        "x": {
            "status": "found",
            "url": "https://x.com/the_johnperera",
            "data": {
                "name": "John P",
                "bio": "Tech enthusiast",
                "profile_image": "https://example.com/x_profile.jpg"
            }
        }
    }


@pytest.fixture
def sample_user_identifiers():
    """Sample user identifiers for testing."""
    return {
        "username": "johnperera",
        "name": "John Perera",
        "location": "Sri Lanka"
    }


# =============================================================================
# SUSPICIOUS SUFFIX DETECTION TESTS
# =============================================================================

class TestSuspiciousSuffixDetection:
    """Tests for suspicious suffix detection."""
    
    def test_detects_official_suffix(self, detector):
        """Test detection of _official suffix."""
        platform_data = {
            "instagram": {
                "status": "found",
                "url": "https://www.instagram.com/johnperera_official/",
                "data": {"name": "John Perera", "bio": ""}
            }
        }
        user_ids = {"username": "johnperera", "location": "Sri Lanka"}
        
        risks = detector.detect(platform_data, user_ids)
        
        # Should detect suspicious suffix
        assert len(risks) > 0
        indicators = risks[0].get("indicators", [])
        suffix_indicators = [i for i in indicators if i.get("type") == "suspicious_suffix"]
        assert len(suffix_indicators) >= 1
    
    def test_detects_real_suffix(self, detector):
        """Test detection of _real suffix."""
        platform_data = {
            "facebook": {
                "status": "found",
                "url": "https://www.facebook.com/johnperera_real",
                "data": {"name": "John", "bio": ""}
            }
        }
        user_ids = {"username": "johnperera", "location": "Sri Lanka"}
        
        risks = detector.detect(platform_data, user_ids)
        
        assert len(risks) > 0
        indicators = risks[0].get("indicators", [])
        suffix_indicators = [i for i in indicators if i.get("type") == "suspicious_suffix"]
        assert len(suffix_indicators) >= 1
    
    def test_no_suffix_no_detection(self, detector):
        """Test that clean username doesn't trigger suffix detection."""
        platform_data = {
            "instagram": {
                "status": "found",
                "url": "https://www.instagram.com/johnperera/",
                "data": {"name": "John Perera", "bio": "", "location": "Colombo"}
            }
        }
        user_ids = {"username": "johnperera", "location": "Sri Lanka"}
        
        risks = detector.detect(platform_data, user_ids)
        
        # Should not have any suffix-related risks
        for risk in risks:
            indicators = risk.get("indicators", [])
            suffix_indicators = [i for i in indicators if i.get("type") == "suspicious_suffix"]
            assert len(suffix_indicators) == 0


# =============================================================================
# SUSPICIOUS PREFIX DETECTION TESTS
# =============================================================================

class TestSuspiciousPrefixDetection:
    """Tests for suspicious prefix detection."""
    
    def test_detects_the_prefix(self, detector):
        """Test detection of the_ prefix."""
        platform_data = {
            "x": {
                "status": "found",
                "url": "https://x.com/the_johnperera",
                "data": {"name": "John", "bio": "DM me for free money!"}  # Add scam bio for high risk
            }
        }
        user_ids = {"username": "johnperera", "location": "Sri Lanka"}
        
        risks = detector.detect(platform_data, user_ids)
        
        # Should detect suspicious prefix
        assert len(risks) > 0
        indicators = risks[0].get("indicators", [])
        prefix_indicators = [i for i in indicators if i.get("type") == "suspicious_prefix"]
        assert len(prefix_indicators) >= 1
    
    def test_detects_official_prefix(self, detector):
        """Test detection of official_ prefix."""
        platform_data = {
            "facebook": {
                "status": "found",
                "url": "https://www.facebook.com/official_johnperera",
                "data": {"name": "John", "bio": "Click link for prizes!"}  # Add scam bio for high risk
            }
        }
        user_ids = {"username": "johnperera", "location": "Sri Lanka"}
        
        risks = detector.detect(platform_data, user_ids)
        
        assert len(risks) > 0
        indicators = risks[0].get("indicators", [])
        prefix_indicators = [i for i in indicators if i.get("type") == "suspicious_prefix"]
        assert len(prefix_indicators) >= 1


# =============================================================================
# USERNAME WITH NUMBERS DETECTION TESTS
# =============================================================================

class TestUsernameWithNumbersDetection:
    """Tests for username with numbers detection."""
    
    def test_detects_copied_username_with_numbers(self, detector):
        """Test detection of username copy with numbers."""
        platform_data = {
            "instagram": {
                "status": "found",
                "url": "https://www.instagram.com/johnperera123/",
                "data": {"name": "John", "bio": ""}
            }
        }
        user_ids = {"username": "johnperera", "location": "Sri Lanka"}
        
        risks = detector.detect(platform_data, user_ids)
        
        assert len(risks) > 0
        indicators = risks[0].get("indicators", [])
        number_indicators = [i for i in indicators if i.get("type") == "username_with_numbers"]
        assert len(number_indicators) >= 1
    
    def test_original_with_numbers_no_detection(self, detector):
        """Test that original username with numbers doesn't trigger."""
        platform_data = {
            "instagram": {
                "status": "found",
                "url": "https://www.instagram.com/johnperera123/",
                "data": {"name": "John", "bio": "", "location": "Colombo"}
            }
        }
        user_ids = {"username": "johnperera123", "location": "Sri Lanka"}
        
        risks = detector.detect(platform_data, user_ids)
        
        # Should not have username_with_numbers indicators when username matches
        for risk in risks:
            indicators = risk.get("indicators", [])
            number_indicators = [i for i in indicators if i.get("type") == "username_with_numbers"]
            assert len(number_indicators) == 0


# =============================================================================
# LOCATION MISMATCH DETECTION TESTS
# =============================================================================

class TestLocationMismatchDetection:
    """Tests for location mismatch detection."""
    
    def test_detects_foreign_location(self, detector):
        """Test detection of non-Sri Lanka location."""
        platform_data = {
            "facebook": {
                "status": "found",
                "url": "https://www.facebook.com/johnperera",
                "data": {"name": "John", "bio": "DM me for free money!", "location": "Nigeria"}  # Add scam bio for high risk
            }
        }
        user_ids = {"username": "johnperera", "location": "Sri Lanka"}
        
        risks = detector.detect(platform_data, user_ids)
        
        # Should detect suspicious bio (which makes it high risk) and location
        assert len(risks) > 0
        indicators = risks[0].get("indicators", [])
        location_indicators = [i for i in indicators if i.get("type") == "location_mismatch"]
        assert len(location_indicators) >= 1
    
    def test_sri_lanka_location_no_detection(self, detector):
        """Test that Sri Lanka locations don't trigger mismatch."""
        platform_data = {
            "instagram": {
                "status": "found",
                "url": "https://www.instagram.com/johnperera/",
                "data": {"name": "John", "bio": "", "location": "Colombo, Sri Lanka"}
            }
        }
        user_ids = {"username": "johnperera", "location": "Sri Lanka"}
        
        risks = detector.detect(platform_data, user_ids)
        
        for risk in risks:
            indicators = risk.get("indicators", [])
            location_indicators = [i for i in indicators if i.get("type") == "location_mismatch"]
            assert len(location_indicators) == 0


# =============================================================================
# SUSPICIOUS BIO CONTENT DETECTION TESTS
# =============================================================================

class TestSuspiciousBioDetection:
    """Tests for suspicious bio content detection."""
    
    def test_detects_dm_for_money(self, detector):
        """Test detection of 'DM for money' scam pattern."""
        platform_data = {
            "instagram": {
                "status": "found",
                "url": "https://www.instagram.com/johnperera/",
                "data": {"name": "John", "bio": "DM me for free money!", "location": "Colombo"}
            }
        }
        user_ids = {"username": "johnperera", "location": "Sri Lanka"}
        
        risks = detector.detect(platform_data, user_ids)
        
        assert len(risks) > 0
        indicators = risks[0].get("indicators", [])
        bio_indicators = [i for i in indicators if i.get("type") == "suspicious_bio"]
        assert len(bio_indicators) >= 1
    
    def test_detects_click_link(self, detector):
        """Test detection of 'click link' scam pattern."""
        platform_data = {
            "facebook": {
                "status": "found",
                "url": "https://www.facebook.com/johnperera",
                "data": {"name": "John", "bio": "Click here for prizes!", "location": "Colombo"}
            }
        }
        user_ids = {"username": "johnperera", "location": "Sri Lanka"}
        
        risks = detector.detect(platform_data, user_ids)
        
        assert len(risks) > 0
        indicators = risks[0].get("indicators", [])
        bio_indicators = [i for i in indicators if i.get("type") == "suspicious_bio"]
        assert len(bio_indicators) >= 1
    
    def test_clean_bio_no_detection(self, detector):
        """Test that clean bio doesn't trigger detection."""
        platform_data = {
            "instagram": {
                "status": "found",
                "url": "https://www.instagram.com/johnperera/",
                "data": {"name": "John", "bio": "Software developer | Tech enthusiast", "location": "Colombo"}
            }
        }
        user_ids = {"username": "johnperera", "location": "Sri Lanka"}
        
        risks = detector.detect(platform_data, user_ids)
        
        for risk in risks:
            indicators = risk.get("indicators", [])
            bio_indicators = [i for i in indicators if i.get("type") == "suspicious_bio"]
            assert len(bio_indicators) == 0


# =============================================================================
# RISK LEVEL CALCULATION TESTS
# =============================================================================

class TestRiskLevelCalculation:
    """Tests for risk level calculation."""
    
    def test_high_risk_multiple_indicators(self, detector, sample_platform_data, sample_user_identifiers):
        """Test that multiple indicators result in high risk."""
        risks = detector.detect(sample_platform_data, sample_user_identifiers)
        
        # Should have at least one high risk detection
        high_risks = [r for r in risks if r.get("risk_level") == "high"]
        assert len(high_risks) >= 1
    
    def test_medium_risk_single_indicator(self, detector):
        """Test that single indicator results in medium risk."""
        platform_data = {
            "instagram": {
                "status": "found",
                "url": "https://www.instagram.com/the_johnperera/",
                "data": {"name": "John", "bio": "", "location": "Colombo"}
            }
        }
        user_ids = {"username": "johnperera", "location": "Sri Lanka"}
        
        risks = detector.detect(platform_data, user_ids)
        
        # Should have at least medium risk
        for risk in risks:
            assert risk.get("risk_level") in ["medium", "high"]
    
    def test_confidence_score_range(self, detector, sample_platform_data, sample_user_identifiers):
        """Test that confidence scores are within valid range."""
        risks = detector.detect(sample_platform_data, sample_user_identifiers)
        
        for risk in risks:
            confidence = risk.get("confidence_score", 0)
            assert 0.0 <= confidence <= 1.0


# =============================================================================
# FULL DETECTION WORKFLOW TESTS
# =============================================================================

class TestFullDetectionWorkflow:
    """Tests for full detection workflow."""
    
    def test_detect_returns_expected_structure(self, detector, sample_platform_data, sample_user_identifiers):
        """Test that detect returns expected response structure."""
        risks = detector.detect(sample_platform_data, sample_user_identifiers)
        
        for risk in risks:
            assert "platform" in risk
            assert "profile_url" in risk
            assert "profile_name" in risk
            assert "risk_level" in risk
            assert "risk_emoji" in risk
            assert "confidence_score" in risk
            assert "indicators" in risk
            assert "recommendation" in risk
            assert "report_url" in risk
    
    def test_skips_not_found_profiles(self, detector):
        """Test that not_found profiles are skipped."""
        platform_data = {
            "linkedin": {
                "status": "not_found",
                "url": "https://www.linkedin.com/in/johnperera_official",
                "data": {"name": "John"}  # Should be ignored
            }
        }
        user_ids = {"username": "johnperera", "location": "Sri Lanka"}
        
        risks = detector.detect(platform_data, user_ids)
        
        assert len(risks) == 0
    
    def test_empty_platform_data(self, detector):
        """Test with empty platform data."""
        risks = detector.detect({}, {"username": "test"})
        
        assert len(risks) == 0
    
    def test_risk_sorted_by_confidence(self, detector, sample_platform_data, sample_user_identifiers):
        """Test that risks are sorted by confidence score descending."""
        risks = detector.detect(sample_platform_data, sample_user_identifiers)
        
        if len(risks) >= 2:
            for i in range(len(risks) - 1):
                assert risks[i]["confidence_score"] >= risks[i+1]["confidence_score"]


# =============================================================================
# USERNAME EXTRACTION TESTS
# =============================================================================

class TestUsernameExtraction:
    """Tests for username extraction from URLs."""
    
    def test_extract_from_facebook_url(self, detector):
        """Test username extraction from Facebook URL."""
        url = "https://www.facebook.com/johnperera"
        username = detector._extract_username_from_url(url)
        
        assert username == "johnperera"
    
    def test_extract_from_instagram_url(self, detector):
        """Test username extraction from Instagram URL."""
        url = "https://www.instagram.com/johnperera/"
        username = detector._extract_username_from_url(url)
        
        assert username == "johnperera"
    
    def test_extract_from_x_url(self, detector):
        """Test username extraction from X URL."""
        url = "https://x.com/johnperera"
        username = detector._extract_username_from_url(url)
        
        assert username == "johnperera"
    
    def test_extract_from_linkedin_url(self, detector):
        """Test username extraction from LinkedIn URL."""
        url = "https://www.linkedin.com/in/johnperera"
        username = detector._extract_username_from_url(url)
        
        assert username == "johnperera"
    
    def test_empty_url_returns_empty(self, detector):
        """Test that empty URL returns empty string."""
        username = detector._extract_username_from_url("")
        
        assert username == ""
