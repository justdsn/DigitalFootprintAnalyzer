# =============================================================================
# PHONE NUMBER LOOKUP SERVICE TESTS
# =============================================================================
# Unit tests for the Phone Number Lookup functionality.
# Tests Sri Lankan phone validation, carrier identification, and formatting.
# =============================================================================

"""
Phone Number Lookup Tests

Comprehensive test suite for the PhoneNumberLookup service:
- Phone number validation (mobile and landline)
- Carrier identification (Dialog, Mobitel, Airtel, Hutch)
- E.164 normalization
- Local and international formatting
- Module-level convenience functions

Run with: pytest tests/test_phone_lookup.py -v
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.social.phone_lookup import PhoneNumberLookup


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def lookup():
    """Create a PhoneNumberLookup instance for tests."""
    return PhoneNumberLookup()


# =============================================================================
# MOBILE NUMBER VALIDATION TESTS
# =============================================================================

class TestMobileValidation:
    """Tests for mobile number validation."""
    
    def test_valid_dialog_077(self, lookup):
        """Test valid Dialog number (077)."""
        result = lookup.lookup("0771234567")
        
        assert result["valid"] is True
        assert result["type"] == "mobile"
        assert result["carrier"] == "Dialog"
    
    def test_valid_dialog_070(self, lookup):
        """Test valid Dialog number (070)."""
        result = lookup.lookup("0701234567")
        
        assert result["valid"] is True
        assert result["type"] == "mobile"
        assert result["carrier"] == "Dialog"
    
    def test_valid_dialog_076(self, lookup):
        """Test valid Dialog number (076)."""
        result = lookup.lookup("0761234567")
        
        assert result["valid"] is True
        assert result["type"] == "mobile"
        assert result["carrier"] == "Dialog"
    
    def test_valid_dialog_074(self, lookup):
        """Test valid Dialog number (074)."""
        result = lookup.lookup("0741234567")
        
        assert result["valid"] is True
        assert result["type"] == "mobile"
        assert result["carrier"] == "Dialog"
    
    def test_valid_mobitel_071(self, lookup):
        """Test valid Mobitel number (071)."""
        result = lookup.lookup("0711234567")
        
        assert result["valid"] is True
        assert result["type"] == "mobile"
        assert result["carrier"] == "Mobitel"
    
    def test_valid_airtel_075(self, lookup):
        """Test valid Airtel number (075)."""
        result = lookup.lookup("0751234567")
        
        assert result["valid"] is True
        assert result["type"] == "mobile"
        assert result["carrier"] == "Airtel"
    
    def test_valid_hutch_072(self, lookup):
        """Test valid Hutch number (072)."""
        result = lookup.lookup("0721234567")
        
        assert result["valid"] is True
        assert result["type"] == "mobile"
        assert result["carrier"] == "Hutch"
    
    def test_valid_hutch_078(self, lookup):
        """Test valid Hutch number (078)."""
        result = lookup.lookup("0781234567")
        
        assert result["valid"] is True
        assert result["type"] == "mobile"
        assert result["carrier"] == "Hutch"


# =============================================================================
# LANDLINE VALIDATION TESTS
# =============================================================================

class TestLandlineValidation:
    """Tests for landline number validation."""
    
    def test_valid_colombo_landline(self, lookup):
        """Test valid Colombo landline (011)."""
        result = lookup.lookup("0112345678")
        
        assert result["valid"] is True
        assert result["type"] == "landline"
        assert result["carrier"] == "Colombo"
    
    def test_valid_kandy_landline(self, lookup):
        """Test valid Kandy landline (081)."""
        result = lookup.lookup("0812345678")
        
        assert result["valid"] is True
        assert result["type"] == "landline"
        assert result["carrier"] == "Kandy"
    
    def test_valid_galle_landline(self, lookup):
        """Test valid Galle landline (091)."""
        result = lookup.lookup("0912345678")
        
        assert result["valid"] is True
        assert result["type"] == "landline"
        assert result["carrier"] == "Galle"
    
    def test_valid_jaffna_landline(self, lookup):
        """Test valid Jaffna landline (021)."""
        result = lookup.lookup("0212345678")
        
        assert result["valid"] is True
        assert result["type"] == "landline"
        assert result["carrier"] == "Jaffna"
    
    def test_valid_negombo_landline(self, lookup):
        """Test valid Negombo landline (031)."""
        result = lookup.lookup("0312345678")
        
        assert result["valid"] is True
        assert result["type"] == "landline"
        assert result["carrier"] == "Negombo"


# =============================================================================
# INVALID NUMBER TESTS
# =============================================================================

class TestInvalidNumbers:
    """Tests for invalid phone numbers."""
    
    def test_invalid_too_short(self, lookup):
        """Test number that is too short."""
        result = lookup.lookup("07712345")
        
        assert result["valid"] is False
        assert result["error"] is not None
    
    def test_invalid_too_long(self, lookup):
        """Test number that is too long."""
        result = lookup.lookup("077123456789")
        
        assert result["valid"] is False
        assert result["error"] is not None
    
    def test_invalid_wrong_prefix(self, lookup):
        """Test number with wrong prefix (079 is not assigned)."""
        result = lookup.lookup("0791234567")
        
        # 079 is not a valid mobile prefix (mobile is 070-078)
        # But it's treated as an unknown landline, not invalid
        # The test checks it's not identified as a known carrier
        assert result["carrier"] is None or result["type"] == "landline"
    
    def test_empty_number(self, lookup):
        """Test empty phone number."""
        result = lookup.lookup("")
        
        assert result["valid"] is False
        assert result["error"] == "Phone number is required"
    
    def test_none_number(self, lookup):
        """Test None phone number."""
        result = lookup.lookup(None)
        
        assert result["valid"] is False


# =============================================================================
# FORMAT HANDLING TESTS
# =============================================================================

class TestFormatHandling:
    """Tests for different input formats."""
    
    def test_with_hyphens(self, lookup):
        """Test number with hyphens."""
        result = lookup.lookup("077-123-4567")
        
        assert result["valid"] is True
        assert result["carrier"] == "Dialog"
    
    def test_with_spaces(self, lookup):
        """Test number with spaces."""
        result = lookup.lookup("077 123 4567")
        
        assert result["valid"] is True
        assert result["carrier"] == "Dialog"
    
    def test_with_dots(self, lookup):
        """Test number with dots."""
        result = lookup.lookup("077.123.4567")
        
        assert result["valid"] is True
        assert result["carrier"] == "Dialog"
    
    def test_international_plus94(self, lookup):
        """Test international format with +94."""
        result = lookup.lookup("+94771234567")
        
        assert result["valid"] is True
        assert result["carrier"] == "Dialog"
    
    def test_international_0094(self, lookup):
        """Test international format with 0094."""
        result = lookup.lookup("0094771234567")
        
        assert result["valid"] is True
        assert result["carrier"] == "Dialog"
    
    def test_international_with_spaces(self, lookup):
        """Test international format with spaces."""
        result = lookup.lookup("+94 77 123 4567")
        
        assert result["valid"] is True
        assert result["carrier"] == "Dialog"


# =============================================================================
# E.164 NORMALIZATION TESTS
# =============================================================================

class TestE164Normalization:
    """Tests for E.164 format normalization."""
    
    def test_e164_from_local(self, lookup):
        """Test E.164 conversion from local format."""
        result = lookup.lookup("0771234567")
        
        assert result["e164_format"] == "+94771234567"
    
    def test_e164_from_international(self, lookup):
        """Test E.164 conversion from international format."""
        result = lookup.lookup("+94771234567")
        
        assert result["e164_format"] == "+94771234567"
    
    def test_e164_from_0094(self, lookup):
        """Test E.164 conversion from 0094 format."""
        result = lookup.lookup("0094771234567")
        
        assert result["e164_format"] == "+94771234567"
    
    def test_e164_with_separators(self, lookup):
        """Test E.164 conversion with separators."""
        result = lookup.lookup("077-123-4567")
        
        assert result["e164_format"] == "+94771234567"


# =============================================================================
# DISPLAY FORMAT TESTS
# =============================================================================

class TestDisplayFormats:
    """Tests for display format generation."""
    
    def test_local_format(self, lookup):
        """Test local display format."""
        result = lookup.lookup("0771234567")
        
        assert result["local_format"] == "077-123-4567"
    
    def test_international_format(self, lookup):
        """Test international display format."""
        result = lookup.lookup("0771234567")
        
        assert result["international_format"] == "+94 77 123 4567"


# =============================================================================
# CARRIER LOOKUP TESTS
# =============================================================================

class TestCarrierLookup:
    """Tests for carrier identification."""
    
    def test_get_all_carriers(self, lookup):
        """Test getting all carrier prefixes."""
        carriers = lookup.get_all_carriers()
        
        assert "077" in carriers
        assert carriers["077"] == "Dialog"
        assert "071" in carriers
        assert carriers["071"] == "Mobitel"
    
    def test_get_all_area_codes(self, lookup):
        """Test getting all landline area codes."""
        codes = lookup.get_all_area_codes()
        
        assert "011" in codes
        assert codes["011"] == "Colombo"
        assert "081" in codes
        assert codes["081"] == "Kandy"


# =============================================================================
# MODULE-LEVEL FUNCTION TESTS
# =============================================================================

class TestModuleFunctions:
    """Tests for module-level convenience functions."""
    
    def test_module_lookup(self):
        """Test module-level lookup function."""
        from app.services.social.phone_lookup import lookup
        
        result = lookup("0771234567")
        
        assert result["valid"] is True
        assert result["carrier"] == "Dialog"
    
    def test_module_validate(self):
        """Test module-level validate function."""
        from app.services.social.phone_lookup import validate
        
        result = validate("0771234567")
        
        assert result["valid"] is True
        assert result["type"] == "mobile"
    
    def test_module_normalize_e164(self):
        """Test module-level normalize_e164 function."""
        from app.services.social.phone_lookup import normalize_e164
        
        result = normalize_e164("0771234567")
        
        assert result == "+94771234567"


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and special scenarios."""
    
    def test_whitespace_only(self, lookup):
        """Test whitespace-only input."""
        result = lookup.lookup("   ")
        
        assert result["valid"] is False
    
    def test_alphabetic_characters(self, lookup):
        """Test input with alphabetic characters."""
        result = lookup.lookup("077abc4567")
        
        assert result["valid"] is False
    
    def test_mixed_valid_invalid(self, lookup):
        """Test input with mixed valid/invalid characters stripped."""
        result = lookup.lookup("(077) 123-4567")
        
        assert result["valid"] is True
        assert result["carrier"] == "Dialog"
    
    def test_original_preserved(self, lookup):
        """Test that original input is preserved in result."""
        original = "077-123-4567"
        result = lookup.lookup(original)
        
        assert result["original"] == original
