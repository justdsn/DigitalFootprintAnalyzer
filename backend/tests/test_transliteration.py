# =============================================================================
# TRANSLITERATION SERVICE TESTS
# =============================================================================
# Unit tests for the Sinhala transliteration functionality.
# Tests Sinhala detection, transliteration, and variant generation.
# =============================================================================

"""
Transliteration Service Tests

Comprehensive test suite for the SinhalaTransliterator service:
- Sinhala character detection tests
- Transliteration from Sinhala to English
- Variant generation for romanized names
- Dictionary-based name and location lookups

Run with: pytest tests/test_transliteration.py -v
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.transliteration import SinhalaTransliterator
from app.services.transliteration.name_dictionary import (
    get_name_variants,
    get_all_name_variants,
    is_known_name
)
from app.services.transliteration.location_dictionary import (
    get_location_variants,
    get_all_location_variants,
    is_known_location
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def transliterator():
    """Create a SinhalaTransliterator instance for tests."""
    return SinhalaTransliterator()


# =============================================================================
# SINHALA DETECTION TESTS
# =============================================================================

class TestSinhalaDetection:
    """Tests for Sinhala character detection."""
    
    def test_detects_sinhala_text(self, transliterator):
        """Test that pure Sinhala text is detected."""
        assert transliterator.is_sinhala("දුෂාන්") is True
    
    def test_detects_mixed_text(self, transliterator):
        """Test that mixed Sinhala/English text is detected as containing Sinhala."""
        assert transliterator.is_sinhala("Hello දුෂාන්") is True
    
    def test_english_text_not_sinhala(self, transliterator):
        """Test that pure English text is not detected as Sinhala."""
        assert transliterator.is_sinhala("Hello World") is False
    
    def test_empty_text_not_sinhala(self, transliterator):
        """Test that empty text returns False."""
        assert transliterator.is_sinhala("") is False
    
    def test_none_text_not_sinhala(self, transliterator):
        """Test that None text returns False."""
        assert transliterator.is_sinhala(None) is False
    
    def test_numbers_not_sinhala(self, transliterator):
        """Test that numbers are not detected as Sinhala."""
        assert transliterator.is_sinhala("12345") is False


# =============================================================================
# TRANSLITERATION TESTS
# =============================================================================

class TestTransliteration:
    """Tests for Sinhala to English transliteration."""
    
    def test_transliterate_known_name(self, transliterator):
        """Test transliteration of a known name from dictionary."""
        result = transliterator.transliterate("දුෂාන්")
        assert len(result) > 0
        # Check that common variants are included
        assert any('dushan' in r.lower() for r in result)
    
    def test_transliterate_known_location(self, transliterator):
        """Test transliteration of a known location from dictionary."""
        result = transliterator.transliterate("කොළඹ")
        assert len(result) > 0
        # Check that colombo variant is included
        assert any('colombo' in r.lower() or 'kolamba' in r.lower() for r in result)
    
    def test_transliterate_empty_returns_empty(self, transliterator):
        """Test that empty input returns empty list."""
        result = transliterator.transliterate("")
        assert result == []
    
    def test_transliterate_returns_list(self, transliterator):
        """Test that transliterate always returns a list."""
        result = transliterator.transliterate("දුෂාන්")
        assert isinstance(result, list)


# =============================================================================
# VARIANT GENERATION TESTS
# =============================================================================

class TestVariantGeneration:
    """Tests for romanized name variant generation."""
    
    def test_generate_variants_includes_original(self, transliterator):
        """Test that original name is included in variants."""
        result = transliterator.generate_variants("dushan")
        assert "dushan" in result
    
    def test_generate_variants_returns_multiple(self, transliterator):
        """Test that multiple variants are generated."""
        result = transliterator.generate_variants("dushan")
        assert len(result) > 1
    
    def test_generate_variants_empty_returns_empty(self, transliterator):
        """Test that empty input returns empty list."""
        result = transliterator.generate_variants("")
        assert result == []
    
    def test_generate_variants_includes_common_patterns(self, transliterator):
        """Test that common spelling patterns are generated."""
        result = transliterator.generate_variants("perera")
        # Should include the original and at least one variant
        assert len(result) >= 1
        assert "perera" in result


# =============================================================================
# NAME DICTIONARY TESTS
# =============================================================================

class TestNameDictionary:
    """Tests for the name dictionary functions."""
    
    def test_get_known_name_variants(self):
        """Test getting variants for a known name."""
        result = get_name_variants("dushan")
        assert result is not None
        assert "sinhala" in result
        assert "transliterations" in result
    
    def test_get_unknown_name_returns_none(self):
        """Test that unknown name returns None."""
        result = get_name_variants("unknownxyz123")
        assert result is None
    
    def test_is_known_name_true(self):
        """Test that known names are recognized."""
        assert is_known_name("perera") is True
        assert is_known_name("dushan") is True
    
    def test_is_known_name_false(self):
        """Test that unknown names return False."""
        assert is_known_name("unknownxyz123") is False
    
    def test_get_all_name_variants(self):
        """Test getting all variants for a name."""
        result = get_all_name_variants("perera")
        assert isinstance(result, list)
        assert len(result) > 0


# =============================================================================
# LOCATION DICTIONARY TESTS
# =============================================================================

class TestLocationDictionary:
    """Tests for the location dictionary functions."""
    
    def test_get_known_location_variants(self):
        """Test getting variants for a known location."""
        result = get_location_variants("colombo")
        assert result is not None
        assert "sinhala" in result
        assert "transliterations" in result
    
    def test_get_unknown_location_returns_none(self):
        """Test that unknown location returns None."""
        result = get_location_variants("unknownxyz123")
        assert result is None
    
    def test_is_known_location_true(self):
        """Test that known locations are recognized."""
        assert is_known_location("colombo") is True
        assert is_known_location("kandy") is True
    
    def test_is_known_location_false(self):
        """Test that unknown locations return False."""
        assert is_known_location("unknownxyz123") is False
    
    def test_get_all_location_variants(self):
        """Test getting all variants for a location."""
        result = get_all_location_variants("colombo")
        assert isinstance(result, list)
        assert len(result) > 0


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
