# =============================================================================
# SINHALA GRAPHEME MAPPINGS
# =============================================================================
# Complete mapping of Sinhala Unicode characters to romanized English.
# Used by the SinhalaTransliterator for converting Sinhala text to English.
# =============================================================================

"""
Sinhala Grapheme Mappings

This module contains comprehensive mappings of Sinhala Unicode characters
(U+0D80-U+0DFF range) to their romanized English equivalents.

Mappings include:
- VOWELS: Independent vowel characters (අ, ආ, ඇ, etc.)
- CONSONANTS: Base consonant characters (ක, ඛ, ග, etc.)
- VOWEL_SIGNS: Dependent vowel marks (◌ා, ◌ැ, ◌ෑ, etc.)
- VARIANT_RULES: Rules for generating spelling alternatives

The transliteration follows common Sri Lankan romanization conventions
with support for multiple spelling variants.

Example:
    >>> from grapheme_map import VOWELS, CONSONANTS
    >>> VOWELS.get('අ')
    'a'
"""

# =============================================================================
# SINHALA VOWELS (Independent)
# =============================================================================
# Unicode range: U+0D85 - U+0D96
# These are standalone vowel characters that can begin a syllable.
# =============================================================================

VOWELS = {
    # Short vowels
    'අ': 'a',      # U+0D85 - SINHALA LETTER AYANNA
    'ඉ': 'i',      # U+0D89 - SINHALA LETTER IYANNA
    'උ': 'u',      # U+0D8B - SINHALA LETTER UYANNA
    'එ': 'e',      # U+0D91 - SINHALA LETTER EYANNA
    'ඔ': 'o',      # U+0D94 - SINHALA LETTER OYANNA
    
    # Long vowels
    'ආ': 'aa',     # U+0D86 - SINHALA LETTER AAYANNA
    'ඊ': 'ii',     # U+0D8A - SINHALA LETTER IIYANNA
    'ඌ': 'uu',     # U+0D8C - SINHALA LETTER UUYANNA
    'ඒ': 'ee',     # U+0D92 - SINHALA LETTER EEYANNA
    'ඕ': 'oo',     # U+0D95 - SINHALA LETTER OOYANNA
    
    # Special vowels
    'ඇ': 'ae',     # U+0D87 - SINHALA LETTER AEYANNA
    'ඈ': 'aee',    # U+0D88 - SINHALA LETTER AEEYANNA
    'ඖ': 'au',     # U+0D96 - SINHALA LETTER AUYANNA
    
    # Sanskrit vowels (rarely used in modern Sinhala)
    'ඍ': 'ru',     # U+0D8D - SINHALA LETTER IRUYANNA
    'ඎ': 'ruu',    # U+0D8E - SINHALA LETTER IRUUYANNA
    'ඏ': 'lu',     # U+0D8F - SINHALA LETTER ILUYANNA
    'ඐ': 'luu',    # U+0D90 - SINHALA LETTER ILUUYANNA
}


# =============================================================================
# SINHALA CONSONANTS (Base Form)
# =============================================================================
# Unicode range: U+0D9A - U+0DC6
# Base consonant characters with inherent 'a' sound.
# The romanization includes the inherent vowel for readability.
# =============================================================================

CONSONANTS = {
    # Velar consonants (ක-වර්ගය)
    'ක': 'ka',     # U+0D9A - SINHALA LETTER ALPAPRAANA KAYANNA
    'ඛ': 'kha',    # U+0D9B - SINHALA LETTER MAHAAPRAANA KAYANNA
    'ග': 'ga',     # U+0D9C - SINHALA LETTER ALPAPRAANA GAYANNA
    'ඝ': 'gha',    # U+0D9D - SINHALA LETTER MAHAAPRAANA GAYANNA
    'ඞ': 'nga',    # U+0D9E - SINHALA LETTER KANTAJA NAASIKYAYA
    
    # Palatal consonants (ච-වර්ගය)
    'ච': 'cha',    # U+0DA0 - SINHALA LETTER ALPAPRAANA CAYANNA
    'ඡ': 'chha',   # U+0DA1 - SINHALA LETTER MAHAAPRAANA CAYANNA
    'ජ': 'ja',     # U+0DA2 - SINHALA LETTER ALPAPRAANA JAYANNA
    'ඣ': 'jha',    # U+0DA3 - SINHALA LETTER MAHAAPRAANA JAYANNA
    'ඤ': 'nya',    # U+0DA4 - SINHALA LETTER TAALUJA NAASIKYAYA
    
    # Retroflex consonants (ට-වර්ගය)
    'ට': 'ta',     # U+0DA7 - SINHALA LETTER ALPAPRAANA TTAYANNA
    'ඨ': 'tha',    # U+0DA8 - SINHALA LETTER MAHAAPRAANA TTAYANNA
    'ඩ': 'da',     # U+0DA9 - SINHALA LETTER ALPAPRAANA DDAYANNA
    'ඪ': 'dha',    # U+0DAA - SINHALA LETTER MAHAAPRAANA DDAYANNA
    'ණ': 'na',     # U+0DAB - SINHALA LETTER MUURDHAJA NAYANNA
    
    # Dental consonants (ත-වර්ගය)
    'ත': 'tha',    # U+0DAD - SINHALA LETTER ALPAPRAANA TAYANNA
    'ථ': 'thha',   # U+0DAE - SINHALA LETTER MAHAAPRAANA TAYANNA
    'ද': 'da',     # U+0DAF - SINHALA LETTER ALPAPRAANA DAYANNA
    'ධ': 'dha',    # U+0DB0 - SINHALA LETTER MAHAAPRAANA DAYANNA
    'න': 'na',     # U+0DB1 - SINHALA LETTER DANTAJA NAYANNA
    
    # Labial consonants (ප-වර්ගය)
    'ප': 'pa',     # U+0DB4 - SINHALA LETTER ALPAPRAANA PAYANNA
    'ඵ': 'pha',    # U+0DB5 - SINHALA LETTER MAHAAPRAANA PAYANNA
    'බ': 'ba',     # U+0DB6 - SINHALA LETTER ALPAPRAANA BAYANNA
    'භ': 'bha',    # U+0DB7 - SINHALA LETTER MAHAAPRAANA BAYANNA
    'ම': 'ma',     # U+0DB8 - SINHALA LETTER MAYANNA
    
    # Semi-vowels and sibilants
    'ය': 'ya',     # U+0DBA - SINHALA LETTER YAYANNA
    'ර': 'ra',     # U+0DBB - SINHALA LETTER RAYANNA
    'ල': 'la',     # U+0DBD - SINHALA LETTER DANTAJA LAYANNA
    'ව': 'va',     # U+0DC0 - SINHALA LETTER VAYANNA (also 'wa')
    
    # Sibilants
    'ශ': 'sha',    # U+0DC1 - SINHALA LETTER TAALUJA SAYANNA
    'ෂ': 'sha',    # U+0DC2 - SINHALA LETTER MUURDHAJA SAYANNA
    'ස': 'sa',     # U+0DC3 - SINHALA LETTER DANTAJA SAYANNA
    
    # Aspirate and special consonants
    'හ': 'ha',     # U+0DC4 - SINHALA LETTER HAYANNA
    'ළ': 'la',     # U+0DC5 - SINHALA LETTER MUURDHAJA LAYANNA
    'ෆ': 'fa',     # U+0DC6 - SINHALA LETTER FAYANNA
    
    # Additional consonants
    'ඟ': 'nga',    # U+0D9F - SINHALA LETTER SANYAKA GAYANNA
    'ඦ': 'nja',    # U+0DA6 - SINHALA LETTER SANYAKA JAYANNA
    'ඬ': 'nda',    # U+0DAC - SINHALA LETTER SANYAKA DDAYANNA
    'ඳ': 'nda',    # U+0DB3 - SINHALA LETTER SANYAKA DAYANNA
    'ඹ': 'mba',    # U+0DB9 - SINHALA LETTER AMBA BAYANNA
}


# =============================================================================
# CONSONANT ROOT FORMS (Without inherent vowel)
# =============================================================================
# Used when combining consonants with vowel signs.
# =============================================================================

CONSONANT_ROOTS = {
    'ක': 'k',
    'ඛ': 'kh',
    'ග': 'g',
    'ඝ': 'gh',
    'ඞ': 'ng',
    'ච': 'ch',
    'ඡ': 'chh',
    'ජ': 'j',
    'ඣ': 'jh',
    'ඤ': 'ny',
    'ට': 't',
    'ඨ': 'th',
    'ඩ': 'd',
    'ඪ': 'dh',
    'ණ': 'n',
    'ත': 'th',
    'ථ': 'thh',
    'ද': 'd',
    'ධ': 'dh',
    'න': 'n',
    'ප': 'p',
    'ඵ': 'ph',
    'බ': 'b',
    'භ': 'bh',
    'ම': 'm',
    'ය': 'y',
    'ර': 'r',
    'ල': 'l',
    'ව': 'v',
    'ශ': 'sh',
    'ෂ': 'sh',
    'ස': 's',
    'හ': 'h',
    'ළ': 'l',
    'ෆ': 'f',
    'ඟ': 'ng',
    'ඦ': 'nj',
    'ඬ': 'nd',
    'ඳ': 'nd',
    'ඹ': 'mb',
}


# =============================================================================
# VOWEL SIGNS (Dependent/Combining)
# =============================================================================
# Unicode range: U+0DCA, U+0DCF - U+0DDF, U+0DF2 - U+0DF3
# These combine with consonants to modify the inherent vowel.
# The virama (්) kills the inherent vowel.
# =============================================================================

VOWEL_SIGNS = {
    # Virama (hal kirīma) - removes inherent vowel
    '්': '',       # U+0DCA - SINHALA SIGN AL-LAKUNA (virama)
    
    # Short vowel signs
    'ා': 'a',      # U+0DCF - SINHALA VOWEL SIGN AELA-PILLA (ā)
    'ි': 'i',      # U+0DD2 - SINHALA VOWEL SIGN KETTI IS-PILLA
    'ු': 'u',      # U+0DD4 - SINHALA VOWEL SIGN KETTI PAA-PILLA
    'ෙ': 'e',      # U+0DD9 - SINHALA VOWEL SIGN KOMBUVA
    'ො': 'o',      # U+0DDC - SINHALA VOWEL SIGN KOMBUVA HAA AELA-PILLA
    
    # Long vowel signs
    'ැ': 'ae',     # U+0DD0 - SINHALA VOWEL SIGN KETTI AEDA-PILLA
    'ෑ': 'aee',    # U+0DD1 - SINHALA VOWEL SIGN DIGA AEDA-PILLA
    'ී': 'ii',     # U+0DD3 - SINHALA VOWEL SIGN DIGA IS-PILLA
    'ූ': 'uu',     # U+0DD6 - SINHALA VOWEL SIGN DIGA PAA-PILLA
    'ේ': 'ee',     # U+0DDA - SINHALA VOWEL SIGN DIGA KOMBUVA
    'ෝ': 'oo',     # U+0DDD - SINHALA VOWEL SIGN KOMBUVA HAA DIGA AELA-PILLA
    
    # Diphthong signs
    'ෞ': 'au',     # U+0DDE - SINHALA VOWEL SIGN KOMBUVA HAA GAYANUKITTA
    'ෛ': 'ai',     # U+0DDB - SINHALA VOWEL SIGN KOMBU DEKA
    
    # Rare vowel signs
    'ෘ': 'ru',     # U+0DD8 - SINHALA VOWEL SIGN GAETTA-PILLA
    'ෲ': 'ruu',    # U+0DF2 - SINHALA VOWEL SIGN DIGA GAETTA-PILLA
    'ෳ': 'luu',    # U+0DF3 - SINHALA VOWEL SIGN DIGA GAYANUKITTA
}


# =============================================================================
# SPECIAL CHARACTERS
# =============================================================================
# Other Sinhala-specific characters and modifiers.
# =============================================================================

SPECIAL_CHARS = {
    'ං': 'ng',     # U+0D82 - SINHALA SIGN ANUSVARAYA (anusvara)
    'ඃ': 'h',      # U+0D83 - SINHALA SIGN VISARGAYA (visarga)
    'ඞ්': 'ng',    # Nasal ng
    '්‍ර': 'r',    # Rakaransaya (conjunct r)
    '්‍ය': 'y',    # Yansaya (conjunct y)
    '\u200d': '',  # Zero Width Joiner (used in conjuncts)
}


# =============================================================================
# VARIANT RULES
# =============================================================================
# Rules for generating common spelling alternatives.
# These account for different romanization conventions and common variations
# in Sri Lankan English spellings.
# =============================================================================

VARIANT_RULES = {
    # Vowel length variations (aa ↔ a)
    'aa': ['a', 'ah'],
    'ee': ['e', 'i', 'ey'],
    'ii': ['i', 'ee', 'y'],
    'oo': ['o', 'u'],
    'uu': ['u', 'oo'],
    
    # Consonant variations
    'th': ['t', 'd'],
    'dh': ['d', 'th'],
    'sh': ['s', 'ch'],
    'ch': ['c', 'tch'],
    'ph': ['p', 'f'],
    'bh': ['b'],
    'kh': ['k', 'c'],
    'gh': ['g'],
    
    # Name-specific variations
    'v': ['w'],
    'w': ['v'],
    'j': ['g', 'dj'],
    'y': ['i', 'ie'],
    
    # Common suffix variations
    'ka': ['ke', 'ga'],
    'na': ['ne'],
    'ra': ['re'],
    'la': ['le'],
    'ya': ['ia', 'iya'],
    
    # Common endings
    'an': ['en', 'on'],
    'am': ['em', 'um'],
    'ar': ['er', 'or'],
    'al': ['el', 'ol'],
}


# =============================================================================
# SINHALA UNICODE RANGE
# =============================================================================
# Constants for detecting Sinhala text
# =============================================================================

SINHALA_UNICODE_START = 0x0D80  # Start of Sinhala Unicode block
SINHALA_UNICODE_END = 0x0DFF    # End of Sinhala Unicode block


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def is_sinhala_char(char: str) -> bool:
    """
    Check if a single character is in the Sinhala Unicode range.
    
    Args:
        char: A single character to check
        
    Returns:
        bool: True if character is Sinhala, False otherwise
        
    Example:
        >>> is_sinhala_char('ක')
        True
        >>> is_sinhala_char('a')
        False
    """
    if not char:
        return False
    code_point = ord(char[0])
    return SINHALA_UNICODE_START <= code_point <= SINHALA_UNICODE_END


def get_all_mappings() -> dict:
    """
    Get a combined dictionary of all Sinhala character mappings.
    
    Returns:
        dict: Combined mappings of all Sinhala characters to romanized English
        
    Example:
        >>> mappings = get_all_mappings()
        >>> mappings.get('අ')
        'a'
    """
    combined = {}
    combined.update(VOWELS)
    combined.update(CONSONANTS)
    combined.update(VOWEL_SIGNS)
    combined.update(SPECIAL_CHARS)
    return combined
