# =============================================================================
# SINHALA GRAPHEME TO ROMAN CHARACTER MAPPINGS
# =============================================================================
# Provides comprehensive mappings from Sinhala Unicode characters to their
# romanized English equivalents. Used by the transliteration engine.
# =============================================================================

"""
Grapheme Mappings for Sinhala Transliteration

This module contains:
- SINHALA_VOWELS: Independent vowel characters and their Roman equivalents
- SINHALA_CONSONANTS: Consonant characters and their Roman equivalents
- SINHALA_VOWEL_SIGNS: Dependent vowel signs (diacritics) mappings
- VARIANT_RULES: Common spelling variation patterns for transliteration

Sinhala Unicode Range: 0D80-0DFF (U+0D80 to U+0DFF)

The mappings follow standard Sri Lankan transliteration conventions while
also supporting common Western spelling variations used in English contexts.

References:
- Unicode Standard for Sinhala: https://unicode.org/charts/PDF/U0D80.pdf
- ISO 15919 transliteration standard
"""

from typing import Dict, List

# =============================================================================
# SINHALA INDEPENDENT VOWELS (ස්වර)
# =============================================================================
# Independent vowel characters that can stand alone at the beginning of a word
# or syllable. Each vowel maps to its romanized equivalent.
# Unicode range: U+0D85 - U+0D96
# =============================================================================

SINHALA_VOWELS: Dict[str, str] = {
    # Short vowels
    'අ': 'a',      # U+0D85 - SINHALA LETTER AYANNA (a)
    'ඉ': 'i',      # U+0D89 - SINHALA LETTER IYANNA (i)
    'උ': 'u',      # U+0D8B - SINHALA LETTER UYANNA (u)
    'එ': 'e',      # U+0D91 - SINHALA LETTER EYANNA (e)
    'ඔ': 'o',      # U+0D94 - SINHALA LETTER OYANNA (o)
    
    # Long vowels
    'ආ': 'aa',     # U+0D86 - SINHALA LETTER AAYANNA (long a)
    'ඈ': 'ae',     # U+0D88 - SINHALA LETTER AEYANNA (ae sound)
    'ඊ': 'ii',     # U+0D8A - SINHALA LETTER IIYANNA (long i)
    'ඌ': 'uu',     # U+0D8C - SINHALA LETTER UUYANNA (long u)
    'ඒ': 'ee',     # U+0D92 - SINHALA LETTER EEYANNA (long e)
    'ඕ': 'oo',     # U+0D95 - SINHALA LETTER OOYANNA (long o)
    'ඓ': 'ai',     # U+0D93 - SINHALA LETTER AIYANNA (ai diphthong)
    'ඖ': 'au',     # U+0D96 - SINHALA LETTER AUYANNA (au diphthong)
    
    # Vocalic consonants (rarely used)
    'ඍ': 'ru',     # U+0D8D - SINHALA LETTER IRUYANNA
    'ඎ': 'ruu',    # U+0D8E - SINHALA LETTER IRUUYANNA
    'ඏ': 'lu',     # U+0D8F - SINHALA LETTER ILUYANNA
    'ඐ': 'luu',    # U+0D90 - SINHALA LETTER ILUUYANNA
}

# =============================================================================
# SINHALA CONSONANTS (ව්‍යංජන)
# =============================================================================
# Consonant characters with inherent 'a' vowel. Each consonant maps to its
# romanized equivalent. The inherent vowel is handled separately.
# Unicode range: U+0D9A - U+0DC6
# =============================================================================

SINHALA_CONSONANTS: Dict[str, str] = {
    # Velar consonants (කවර්ග)
    'ක': 'k',      # U+0D9A - SINHALA LETTER KAYANNA (k)
    'ඛ': 'kh',     # U+0D9B - SINHALA LETTER MAHA KAYANNA (aspirated k)
    'ග': 'g',      # U+0D9C - SINHALA LETTER GAYANNA (g)
    'ඝ': 'gh',     # U+0D9D - SINHALA LETTER MAHA GAYANNA (aspirated g)
    'ඞ': 'ng',     # U+0D9E - SINHALA LETTER KANTAJA NAASIKYAYA (velar nasal)
    'ඟ': 'nng',    # U+0D9F - SINHALA LETTER SANYAKA GAYANNA
    
    # Palatal consonants (චවර්ග)
    'ච': 'ch',     # U+0DA0 - SINHALA LETTER CAYANNA (ch)
    'ඡ': 'chh',    # U+0DA1 - SINHALA LETTER MAHA CAYANNA (aspirated ch)
    'ජ': 'j',      # U+0DA2 - SINHALA LETTER JAYANNA (j)
    'ඣ': 'jh',     # U+0DA3 - SINHALA LETTER MAHA JAYANNA (aspirated j)
    'ඤ': 'ny',     # U+0DA4 - SINHALA LETTER TAALUJA NAASIKYAYA (palatal nasal)
    'ඥ': 'gn',     # U+0DA5 - SINHALA LETTER TAALUJA SANYOOGA NAAYANNA
    'ඦ': 'nj',     # U+0DA6 - SINHALA LETTER SANYAKA JAYANNA
    
    # Retroflex consonants (ටවර්ග)
    'ට': 't',      # U+0DA7 - SINHALA LETTER TAYANNA (retroflex t)
    'ඨ': 'th',     # U+0DA8 - SINHALA LETTER MAHA TAYANNA (aspirated retroflex t)
    'ඩ': 'd',      # U+0DA9 - SINHALA LETTER DAYANNA (retroflex d)
    'ඪ': 'dh',     # U+0DAA - SINHALA LETTER MAHA DAYANNA (aspirated retroflex d)
    'ණ': 'n',      # U+0DAB - SINHALA LETTER MUURDHAJA NAYANNA (retroflex n)
    'ඬ': 'nd',     # U+0DAC - SINHALA LETTER SANYAKA DAYANNA
    
    # Dental consonants (තවර්ග)
    'ත': 'th',     # U+0DAD - SINHALA LETTER TAYANNA (dental t - often 'th')
    'ථ': 'th',     # U+0DAE - SINHALA LETTER MAHA TAYANNA (aspirated dental t)
    'ද': 'd',      # U+0DAF - SINHALA LETTER DAYANNA (dental d)
    'ධ': 'dh',     # U+0DB0 - SINHALA LETTER MAHA DAYANNA (aspirated dental d)
    'න': 'n',      # U+0DB1 - SINHALA LETTER DANTAJA NAYANNA (dental n)
    'ඳ': 'nd',     # U+0DB3 - SINHALA LETTER SANYAKA DAYANNA
    
    # Labial consonants (පවර්ග)
    'ප': 'p',      # U+0DB4 - SINHALA LETTER PAYANNA (p)
    'ඵ': 'ph',     # U+0DB5 - SINHALA LETTER MAHA PAYANNA (aspirated p)
    'බ': 'b',      # U+0DB6 - SINHALA LETTER BAYANNA (b)
    'භ': 'bh',     # U+0DB7 - SINHALA LETTER MAHA BAYANNA (aspirated b)
    'ම': 'm',      # U+0DB8 - SINHALA LETTER MAYANNA (m)
    'ඹ': 'mb',     # U+0DB9 - SINHALA LETTER AMBA BAYANNA
    
    # Semi-vowels and approximants
    'ය': 'y',      # U+0DBA - SINHALA LETTER YAYANNA (y)
    'ර': 'r',      # U+0DBB - SINHALA LETTER RAYANNA (r)
    'ල': 'l',      # U+0DBD - SINHALA LETTER LAYANNA (l)
    'ළ': 'l',      # U+0DC5 - SINHALA LETTER MUURDHAJA LAYANNA (retroflex l)
    'ව': 'w',      # U+0DC0 - SINHALA LETTER WAYANNA (w/v)
    
    # Sibilants and fricatives
    'ශ': 'sh',     # U+0DC1 - SINHALA LETTER TAALUJA SAYANNA (palatal sh)
    'ෂ': 'sh',     # U+0DC2 - SINHALA LETTER MUURDHAJA SAYANNA (retroflex sh)
    'ස': 's',      # U+0DC3 - SINHALA LETTER DANTAJA SAYANNA (dental s)
    'හ': 'h',      # U+0DC4 - SINHALA LETTER HAYANNA (h)
    
    # Aspirate and special consonants
    'ෆ': 'f',      # U+0DC6 - SINHALA LETTER FAYANNA (f - borrowed)
}

# =============================================================================
# SINHALA DEPENDENT VOWEL SIGNS (පිලි)
# =============================================================================
# Vowel signs that modify consonants. These appear as diacritics attached
# to consonant characters and replace the inherent 'a' vowel.
# Unicode range: U+0DCA - U+0DDF
# =============================================================================

SINHALA_VOWEL_SIGNS: Dict[str, str] = {
    # Virama (hal kirima) - removes inherent vowel
    '්': '',       # U+0DCA - SINHALA SIGN AL-LAKUNA (virama)
    
    # Short vowel signs
    'ා': 'a',      # U+0DCF - SINHALA VOWEL SIGN AELA-PILLA (aa -> a for simpler names)
    'ැ': 'e',      # U+0DD0 - SINHALA VOWEL SIGN KETTI AEDA-PILLA (short ae)
    'ි': 'i',      # U+0DD2 - SINHALA VOWEL SIGN KETTI IS-PILLA (short i)
    'ු': 'u',      # U+0DD4 - SINHALA VOWEL SIGN KETTI PAA-PILLA (short u)
    'ෙ': 'e',      # U+0DD9 - SINHALA VOWEL SIGN KOMBUVA (e)
    'ො': 'o',      # U+0DDC - SINHALA VOWEL SIGN KOMBUVA HAA AELA-PILLA (o)
    
    # Long vowel signs
    'ෑ': 'ae',     # U+0DD1 - SINHALA VOWEL SIGN DIGA AEDA-PILLA (long ae)
    'ී': 'i',      # U+0DD3 - SINHALA VOWEL SIGN DIGA IS-PILLA (long i)
    'ූ': 'u',      # U+0DD6 - SINHALA VOWEL SIGN DIGA PAA-PILLA (long u)
    'ේ': 'e',      # U+0DDA - SINHALA VOWEL SIGN DIGA KOMBUVA (long e)
    'ෝ': 'o',      # U+0DDD - SINHALA VOWEL SIGN DIGA KOMBUVA HAA AELA-PILLA (long o)
    
    # Diphthong signs
    'ෛ': 'ai',     # U+0DDB - SINHALA VOWEL SIGN KOMBU DEKA (ai)
    'ෞ': 'au',     # U+0DDE - SINHALA VOWEL SIGN KOMBUVA HAA GAYANUKITTA (au)
    
    # Special signs
    'ෘ': 'ru',     # U+0DD8 - SINHALA VOWEL SIGN GAETTA-PILLA (vocalic r)
    'ෟ': 'lu',     # U+0DDF - SINHALA VOWEL SIGN GAYANUKITTA (vocalic l)
}

# =============================================================================
# VARIANT RULES
# =============================================================================
# Common spelling variations for transliterated Sinhala names and words.
# These rules help generate multiple plausible English spellings.
# Each rule maps a pattern to its possible alternatives.
# =============================================================================

VARIANT_RULES: Dict[str, List[str]] = {
    # Long vowel variations
    # 'aa' can be simplified to 'a' in casual English spelling
    'aa': ['a', 'ah'],
    'ee': ['e', 'i', 'ey'],
    'ii': ['i', 'ee'],
    'oo': ['o', 'u'],
    'uu': ['u', 'oo'],
    
    # Consonant variations
    # 'th' can be written as 't' (common simplification)
    'th': ['t', 'dh'],
    # 'sh' variations
    'sh': ['s', 'sch'],
    # 'ch' variations
    'ch': ['c', 'tch'],
    # 'ph' is often simplified to 'f'
    'ph': ['f', 'p'],
    # 'gh' is often simplified to 'g'
    'gh': ['g'],
    # 'kh' is often simplified to 'k'
    'kh': ['k'],
    # 'dh' is often simplified to 'd'
    'dh': ['d'],
    # 'bh' is often simplified to 'b'
    'bh': ['b'],
    
    # Vowel variations in names
    # 'u' can sometimes be written as 'oo'
    'u': ['oo'],
    # 'i' can sometimes be written as 'ee'
    'i': ['ee', 'y'],
    
    # Ending variations
    # Names ending in 'an' might have variations
    'an': ['en', 'un'],
    # Names ending in 'a' might have variations
    'a$': ['ah', 'e'],
    
    # Double consonant variations
    'nn': ['n'],
    'mm': ['m'],
    'ss': ['s'],
    'll': ['l'],
    'tt': ['t'],
    'dd': ['d'],
    'pp': ['p'],
    'kk': ['k'],
}

# =============================================================================
# SPECIAL COMBINATIONS
# =============================================================================
# Multi-character sequences that should be transliterated as units.
# These handle common Sinhala consonant clusters and special forms.
# =============================================================================

SPECIAL_COMBINATIONS: Dict[str, str] = {
    # Consonant + yansaya (යංශය) combinations
    'ක්‍ය': 'kya',   # k + yansaya
    'ග්‍ය': 'gya',   # g + yansaya
    'ප්‍ය': 'pya',   # p + yansaya
    'බ්‍ය': 'bya',   # b + yansaya
    'ම්‍ය': 'mya',   # m + yansaya
    'ව්‍ය': 'vya',   # v + yansaya
    
    # Consonant + rakaransaya (රකාරාංශය) combinations
    'ක්‍ර': 'kra',   # k + rakaransaya
    'ග්‍ර': 'gra',   # g + rakaransaya
    'ප්‍ර': 'pra',   # p + rakaransaya
    'බ්‍ර': 'bra',   # b + rakaransaya
    'ත්‍ර': 'tra',   # t + rakaransaya
    'ද්‍ර': 'dra',   # d + rakaransaya
    'ශ්‍ර': 'shra',  # sh + rakaransaya (as in Sri)
    
    # Common name patterns
    'ශ්‍රී': 'sri',  # Sri (as in Sri Lanka)
}

# =============================================================================
# ANUSVARA AND VISARGA
# =============================================================================
# Additional diacritical marks used in Sinhala
# =============================================================================

ANUSVARA_VISARGA: Dict[str, str] = {
    'ං': 'n',      # U+0D82 - SINHALA SIGN ANUSVARAYA (anusvara - nasal)
    'ඃ': 'h',      # U+0D83 - SINHALA SIGN VISARGAYA (visarga - aspiration)
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_all_mappings() -> Dict[str, str]:
    """
    Get a combined dictionary of all Sinhala to Roman mappings.
    
    This combines vowels, consonants, vowel signs, special combinations,
    and anusvara/visarga into a single lookup dictionary.
    
    Returns:
        Dict[str, str]: Combined mapping dictionary
    
    Example:
        >>> mappings = get_all_mappings()
        >>> mappings['ක']
        'k'
    """
    combined = {}
    combined.update(SINHALA_VOWELS)
    combined.update(SINHALA_CONSONANTS)
    combined.update(SINHALA_VOWEL_SIGNS)
    combined.update(SPECIAL_COMBINATIONS)
    combined.update(ANUSVARA_VISARGA)
    return combined


def is_sinhala_char(char: str) -> bool:
    """
    Check if a character is in the Sinhala Unicode range.
    
    Sinhala Unicode block: U+0D80 - U+0DFF
    
    Args:
        char: Single character to check
    
    Returns:
        bool: True if character is Sinhala, False otherwise
    
    Example:
        >>> is_sinhala_char('ක')
        True
        >>> is_sinhala_char('a')
        False
    """
    if not char or len(char) != 1:
        return False
    code_point = ord(char)
    # Sinhala Unicode range: 0x0D80 - 0x0DFF
    return 0x0D80 <= code_point <= 0x0DFF


def get_character_type(char: str) -> str:
    """
    Determine the type of a Sinhala character.
    
    Args:
        char: Single Sinhala character
    
    Returns:
        str: Character type - 'vowel', 'consonant', 'vowel_sign', 
             'special', or 'unknown'
    
    Example:
        >>> get_character_type('අ')
        'vowel'
        >>> get_character_type('ක')
        'consonant'
    """
    if char in SINHALA_VOWELS:
        return 'vowel'
    elif char in SINHALA_CONSONANTS:
        return 'consonant'
    elif char in SINHALA_VOWEL_SIGNS:
        return 'vowel_sign'
    elif char in ANUSVARA_VISARGA:
        return 'special'
    return 'unknown'
