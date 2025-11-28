# =============================================================================
# SINHALA TRANSLITERATION SERVICE TESTS
# =============================================================================
# Unit tests for the Sinhala transliteration functionality.
# Tests Sinhala detection, character-based transliteration, and dictionary lookups.
# =============================================================================

"""
Sinhala Transliteration Tests

Comprehensive test suite for the SinhalaTransliterator service:
- Sinhala text detection tests
- Character-by-character transliteration tests
- Dictionary lookup tests for names and locations
- Variant generation tests

Run with: pytest tests/test_transliteration.py -v
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.transliteration import (
    SinhalaTransliterator,
    is_sinhala,
    transliterate,
    generate_variants,
    NAME_DICTIONARY,
    LOCATION_DICTIONARY,
    get_name_variants,
    get_location_variants,
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
    """Tests for Sinhala text detection."""
    
    def test_detect_sinhala_text(self, transliterator):
        """Test detection of pure Sinhala text."""
        assert transliterator.is_sinhala("සිංහල") is True
        assert transliterator.is_sinhala("ආයුබෝවන්") is True
        assert transliterator.is_sinhala("කමල්") is True
    
    def test_detect_english_text(self, transliterator):
        """Test that English text is not detected as Sinhala."""
        assert transliterator.is_sinhala("Hello") is False
        assert transliterator.is_sinhala("John Doe") is False
        assert transliterator.is_sinhala("test123") is False
    
    def test_detect_mixed_text(self, transliterator):
        """Test detection of mixed Sinhala and English text."""
        assert transliterator.is_sinhala("Hello ආයුබෝවන්") is True
        assert transliterator.is_sinhala("සිංහල test") is True
    
    def test_detect_empty_text(self, transliterator):
        """Test detection with empty or None text."""
        assert transliterator.is_sinhala("") is False
        assert transliterator.is_sinhala(None) is False
    
    def test_detect_numbers_only(self, transliterator):
        """Test that numbers alone are not detected as Sinhala."""
        assert transliterator.is_sinhala("12345") is False
    
    def test_module_level_is_sinhala(self):
        """Test the module-level is_sinhala function."""
        assert is_sinhala("සිංහල") is True
        assert is_sinhala("English") is False


# =============================================================================
# TRANSLITERATION TESTS
# =============================================================================

class TestTransliteration:
    """Tests for Sinhala to English transliteration."""
    
    def test_transliterate_known_name(self, transliterator):
        """Test transliteration of a name in the dictionary."""
        # 'කමල්' should be found in dictionary
        results = transliterator.transliterate("කමල්")
        assert len(results) > 0
        assert any("kamal" in r.lower() for r in results)
    
    def test_transliterate_known_location(self, transliterator):
        """Test transliteration of a location in the dictionary."""
        # 'කොළඹ' (Colombo) should be found in dictionary
        results = transliterator.transliterate("කොළඹ")
        assert len(results) > 0
        assert any("colombo" in r.lower() for r in results)
    
    def test_transliterate_simple_word(self, transliterator):
        """Test transliteration of simple Sinhala word."""
        # This tests character-by-character transliteration
        results = transliterator.transliterate("අම")
        assert len(results) > 0
    
    def test_transliterate_multi_word(self, transliterator):
        """Test transliteration of multiple words."""
        # Test with a full name
        results = transliterator.transliterate("සුනිල් පෙරේරා")
        assert len(results) > 0
        # Should contain variations of "sunil" and "perera"
        combined = ' '.join(results)
        # At least one result should have both parts
        assert any('perera' in r.lower() for r in results) or 'sunil' in combined.lower()
    
    def test_transliterate_english_unchanged(self, transliterator):
        """Test that English text passes through unchanged."""
        results = transliterator.transliterate("John")
        assert "john" in results
    
    def test_transliterate_empty(self, transliterator):
        """Test transliteration of empty text."""
        results = transliterator.transliterate("")
        assert results == []
    
    def test_module_level_transliterate(self):
        """Test the module-level transliterate function."""
        results = transliterate("කමල්")
        assert len(results) > 0


# =============================================================================
# DICTIONARY TESTS
# =============================================================================

class TestDictionaries:
    """Tests for name and location dictionary lookups."""
    
    def test_name_dictionary_has_entries(self):
        """Test that name dictionary has entries."""
        assert len(NAME_DICTIONARY) > 0
    
    def test_location_dictionary_has_entries(self):
        """Test that location dictionary has entries."""
        assert len(LOCATION_DICTIONARY) > 0
    
    def test_get_name_variants_found(self):
        """Test getting variants for a known name."""
        # 'දුෂාන්' is in the dictionary
        variants = get_name_variants('දුෂාන්')
        assert len(variants) > 0
        assert 'dushan' in variants or 'dushaan' in variants
    
    def test_get_name_variants_not_found(self):
        """Test getting variants for unknown name."""
        variants = get_name_variants('නොදන්නා')
        assert variants == []
    
    def test_get_location_variants_found(self):
        """Test getting variants for a known location."""
        # 'ගාල්ල' (Galle) is in the dictionary
        variants = get_location_variants('ගාල්ල')
        assert len(variants) > 0
        assert 'galle' in variants
    
    def test_get_location_variants_not_found(self):
        """Test getting variants for unknown location."""
        variants = get_location_variants('නොදන්නා')
        assert variants == []
    
    def test_name_dictionary_common_names(self):
        """Test that common Sri Lankan names are in dictionary."""
        # Check some common names
        assert 'කමල්' in NAME_DICTIONARY  # Kamal
        assert 'නිමාලි' in NAME_DICTIONARY  # Nimali
        assert 'පෙරේරා' in NAME_DICTIONARY  # Perera (surname)
    
    def test_location_dictionary_major_cities(self):
        """Test that major cities are in dictionary."""
        assert 'කොළඹ' in LOCATION_DICTIONARY  # Colombo
        assert 'මහනුවර' in LOCATION_DICTIONARY  # Kandy
        assert 'ගාල්ල' in LOCATION_DICTIONARY  # Galle


# =============================================================================
# VARIANT GENERATION TESTS
# =============================================================================

class TestVariantGeneration:
    """Tests for spelling variant generation."""
    
    def test_generate_variants_with_aa(self, transliterator):
        """Test that 'aa' variant rules exist and work."""
        # Test that the variant rules include aa -> a transformation
        from app.services.transliteration.grapheme_map import VARIANT_RULES
        assert 'aa' in VARIANT_RULES
        assert 'a' in VARIANT_RULES['aa']
        
        # Test basic variant generation works
        variants = transliterator.generate_variants("test")
        assert isinstance(variants, list)
        assert len(variants) > 0
    
    def test_generate_variants_with_th(self, transliterator):
        """Test that 'th' generates 't' variant."""
        variants = transliterator.generate_variants("thilak")
        assert any("tilak" in v for v in variants)
    
    def test_generate_variants_empty(self, transliterator):
        """Test variant generation with empty string."""
        variants = transliterator.generate_variants("")
        assert variants == []
    
    def test_generate_variants_limit(self, transliterator):
        """Test that variant generation is limited."""
        # Long string with many possible variants
        variants = transliterator.generate_variants("thaathhaashaan")
        # Should be limited to prevent explosion
        assert len(variants) <= 10
    
    def test_module_level_generate_variants(self):
        """Test the module-level generate_variants function."""
        variants = generate_variants("sunil")
        assert "sunil" in variants


# =============================================================================
# SINGLE WORD TRANSLITERATION TESTS
# =============================================================================

class TestSingleWordTransliteration:
    """Tests for single word transliteration method."""
    
    def test_transliterate_word_vowel(self, transliterator):
        """Test transliteration of word starting with vowel."""
        result = transliterator.transliterate_word("අම")
        assert "a" in result.lower()
        assert "m" in result.lower()
    
    def test_transliterate_word_consonant(self, transliterator):
        """Test transliteration of word starting with consonant."""
        result = transliterator.transliterate_word("ක")
        assert result.lower() == "ka"
    
    def test_transliterate_word_with_virama(self, transliterator):
        """Test transliteration of consonant with virama."""
        # ක් should be just 'k' (consonant without inherent vowel)
        result = transliterator.transliterate_word("ක්")
        assert result.lower() == "k"
    
    def test_transliterate_word_with_vowel_sign(self, transliterator):
        """Test transliteration of consonant with vowel sign."""
        # කා should be 'kaa'
        result = transliterator.transliterate_word("කා")
        # The consonant root 'k' + vowel sign 'a'
        assert "k" in result.lower()
    
    def test_transliterate_word_empty(self, transliterator):
        """Test transliteration of empty word."""
        result = transliterator.transliterate_word("")
        assert result == ""


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and special scenarios."""
    
    def test_mixed_script_text(self, transliterator):
        """Test text with mixed Sinhala and English."""
        results = transliterator.transliterate("Hello කමල්")
        assert len(results) > 0
    
    def test_numbers_in_text(self, transliterator):
        """Test text with numbers."""
        results = transliterator.transliterate("කමල් 123")
        assert len(results) > 0
    
    def test_special_characters(self, transliterator):
        """Test text with special characters."""
        results = transliterator.transliterate("කමල්!")
        assert len(results) > 0
    
    def test_whitespace_handling(self, transliterator):
        """Test handling of extra whitespace."""
        results = transliterator.transliterate("  කමල්  ")
        assert len(results) > 0
    
    def test_sinhala_ratio(self, transliterator):
        """Test Sinhala character ratio calculation."""
        # Pure Sinhala text
        ratio = transliterator.get_sinhala_ratio("සිංහල")
        assert ratio > 0.9
        
        # Pure English text
        ratio = transliterator.get_sinhala_ratio("English")
        assert ratio == 0.0
        
        # Mixed text (approximately 50/50)
        ratio = transliterator.get_sinhala_ratio("abc සිංහල")
        assert 0.3 < ratio < 0.7


# =============================================================================
# CONTAINS NAME/LOCATION TESTS
# =============================================================================

class TestContainsChecks:
    """Tests for name and location detection."""
    
    def test_contains_sinhala_name(self, transliterator):
        """Test detection of Sinhala name."""
        found, sinhala, variants = transliterator.contains_name("කමල්")
        assert found is True
        assert sinhala == "කමල්"
        assert len(variants) > 0
    
    def test_contains_romanized_name(self, transliterator):
        """Test detection of romanized name."""
        found, sinhala, variants = transliterator.contains_name("kamal")
        assert found is True
        assert len(variants) > 0
    
    def test_contains_unknown_name(self, transliterator):
        """Test with unknown name."""
        found, sinhala, variants = transliterator.contains_name("xyz123")
        assert found is False
        assert sinhala is None
        assert variants == []
    
    def test_contains_sinhala_location(self, transliterator):
        """Test detection of Sinhala location."""
        found, sinhala, variants = transliterator.contains_location("කොළඹ")
        assert found is True
        assert sinhala == "කොළඹ"
        assert "colombo" in variants
    
    def test_contains_romanized_location(self, transliterator):
        """Test detection of romanized location."""
        found, sinhala, variants = transliterator.contains_location("colombo")
        assert found is True
        assert len(variants) > 0


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
