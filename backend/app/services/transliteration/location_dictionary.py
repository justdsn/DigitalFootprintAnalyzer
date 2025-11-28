# =============================================================================
# SRI LANKAN LOCATION DICTIONARY
# =============================================================================
# Contains Sri Lankan cities, towns, and places with their Sinhala Unicode
# representations and multiple romanized spelling variants.
# =============================================================================

"""
Sri Lankan Location Dictionary

This module contains:
- SINHALA_LOCATIONS: 50+ Sri Lankan places with their Sinhala forms and variants
- get_location_variants(): Function to get all variants for a location

Each location entry includes:
- sinhala: The location name in Sinhala script
- transliterations: List of common English spelling variants
- province: The administrative province (optional)

Example:
    SINHALA_LOCATIONS['colombo']
    # Returns: {'sinhala': 'කොළඹ', 'transliterations': ['colombo', 'kolamba', ...]}
"""

from typing import Dict, List, Optional

# =============================================================================
# SRI LANKAN LOCATIONS DICTIONARY
# =============================================================================
# 50+ major cities, towns, and places in Sri Lanka with their Sinhala forms
# and common English spelling variants
# =============================================================================

SINHALA_LOCATIONS: Dict[str, Dict[str, any]] = {
    # =========================================================================
    # WESTERN PROVINCE
    # =========================================================================
    
    'colombo': {
        'sinhala': 'කොළඹ',
        'transliterations': ['colombo', 'kolamba', 'kolomba', 'columbo'],
        'province': 'Western'
    },
    'gampaha': {
        'sinhala': 'ගම්පහ',
        'transliterations': ['gampaha', 'gampahah', 'gamphaha', 'gempaha'],
        'province': 'Western'
    },
    'kalutara': {
        'sinhala': 'කළුතර',
        'transliterations': ['kalutara', 'kalutura', 'kaluthara', 'kalutarah'],
        'province': 'Western'
    },
    'negombo': {
        'sinhala': 'මීගමුව',
        'transliterations': ['negombo', 'meegamuwa', 'migamuwa', 'negambo'],
        'province': 'Western'
    },
    'moratuwa': {
        'sinhala': 'මොරටුව',
        'transliterations': ['moratuwa', 'moratuwah', 'moratuva', 'morathuwah'],
        'province': 'Western'
    },
    'dehiwala': {
        'sinhala': 'දෙහිවල',
        'transliterations': ['dehiwala', 'dehiwela', 'dehiwalah', 'dehivala'],
        'province': 'Western'
    },
    'mount_lavinia': {
        'sinhala': 'ගල්කිස්ස',
        'transliterations': ['mount lavinia', 'galkissa', 'galkissah', 'ml'],
        'province': 'Western'
    },
    'kotte': {
        'sinhala': 'කෝට්ටේ',
        'transliterations': ['kotte', 'kotteh', 'kottes', 'sri jayawardenepura kotte'],
        'province': 'Western'
    },
    'ja_ela': {
        'sinhala': 'ජා ඇල',
        'transliterations': ['ja ela', 'ja-ela', 'jaela', 'ja ala'],
        'province': 'Western'
    },
    'panadura': {
        'sinhala': 'පානදුර',
        'transliterations': ['panadura', 'panadurah', 'pendura', 'panadure'],
        'province': 'Western'
    },
    
    # =========================================================================
    # CENTRAL PROVINCE
    # =========================================================================
    
    'kandy': {
        'sinhala': 'මහනුවර',
        'transliterations': ['kandy', 'mahanuwara', 'kandie', 'kandee'],
        'province': 'Central'
    },
    'matale': {
        'sinhala': 'මාතලේ',
        'transliterations': ['matale', 'mathale', 'mataleh', 'mathaley'],
        'province': 'Central'
    },
    'nuwara_eliya': {
        'sinhala': 'නුවරඑළිය',
        'transliterations': ['nuwara eliya', 'nuwaraeliya', 'nuwereliya', 'nuwara eliyah'],
        'province': 'Central'
    },
    'peradeniya': {
        'sinhala': 'පේරාදෙණිය',
        'transliterations': ['peradeniya', 'peradeniyah', 'peredeniya', 'peradenia'],
        'province': 'Central'
    },
    'dambulla': {
        'sinhala': 'දඹුල්ල',
        'transliterations': ['dambulla', 'dambullah', 'dambula', 'dhambulla'],
        'province': 'Central'
    },
    'sigiriya': {
        'sinhala': 'සීගිරිය',
        'transliterations': ['sigiriya', 'sigiria', 'seegiriya', 'sigiriyah'],
        'province': 'Central'
    },
    
    # =========================================================================
    # SOUTHERN PROVINCE
    # =========================================================================
    
    'galle': {
        'sinhala': 'ගාල්ල',
        'transliterations': ['galle', 'galla', 'galley', 'gaalle'],
        'province': 'Southern'
    },
    'matara': {
        'sinhala': 'මාතර',
        'transliterations': ['matara', 'mathara', 'matarah', 'matharah'],
        'province': 'Southern'
    },
    'hambantota': {
        'sinhala': 'හම්බන්තොට',
        'transliterations': ['hambantota', 'hambanthota', 'hambantotah', 'hambantotta'],
        'province': 'Southern'
    },
    'unawatuna': {
        'sinhala': 'උනවටුන',
        'transliterations': ['unawatuna', 'unawathuna', 'unawatunah', 'unavatuna'],
        'province': 'Southern'
    },
    'hikkaduwa': {
        'sinhala': 'හික්කඩුව',
        'transliterations': ['hikkaduwa', 'hikaduwa', 'hikaduwah', 'hikkaduwah'],
        'province': 'Southern'
    },
    'weligama': {
        'sinhala': 'වැලිගම',
        'transliterations': ['weligama', 'waligama', 'weligamah', 'welligama'],
        'province': 'Southern'
    },
    'mirissa': {
        'sinhala': 'මිරිස්ස',
        'transliterations': ['mirissa', 'mirissah', 'mirisa', 'mirisah'],
        'province': 'Southern'
    },
    'tangalle': {
        'sinhala': 'තංගල්ල',
        'transliterations': ['tangalle', 'tangalla', 'thangalla', 'tangallah'],
        'province': 'Southern'
    },
    
    # =========================================================================
    # NORTHERN PROVINCE
    # =========================================================================
    
    'jaffna': {
        'sinhala': 'යාපනය',
        'transliterations': ['jaffna', 'yapanaya', 'yalpanaya', 'jafna'],
        'province': 'Northern'
    },
    'kilinochchi': {
        'sinhala': 'කිලිනොච්චි',
        'transliterations': ['kilinochchi', 'kilinochchy', 'kilinochi', 'killinochchi'],
        'province': 'Northern'
    },
    'mannar': {
        'sinhala': 'මන්නාරම',
        'transliterations': ['mannar', 'mannaar', 'mannarama', 'mannerh'],
        'province': 'Northern'
    },
    'vavuniya': {
        'sinhala': 'වව්නියාව',
        'transliterations': ['vavuniya', 'wawuniya', 'wavuniya', 'vavuniyah'],
        'province': 'Northern'
    },
    'mullaitivu': {
        'sinhala': 'මුලතිව්',
        'transliterations': ['mullaitivu', 'mulativu', 'mullaithivu', 'mullativu'],
        'province': 'Northern'
    },
    
    # =========================================================================
    # EASTERN PROVINCE
    # =========================================================================
    
    'batticaloa': {
        'sinhala': 'මඩකලපුව',
        'transliterations': ['batticaloa', 'madakalapuwa', 'batticaloe', 'batticalo'],
        'province': 'Eastern'
    },
    'trincomalee': {
        'sinhala': 'ත්‍රිකුණාමලය',
        'transliterations': ['trincomalee', 'trinco', 'thirukonamalai', 'thirukonimalai'],
        'province': 'Eastern'
    },
    'ampara': {
        'sinhala': 'අම්පාර',
        'transliterations': ['ampara', 'amparah', 'ampaarah', 'emparah'],
        'province': 'Eastern'
    },
    'kalmunai': {
        'sinhala': 'කල්මුනේ',
        'transliterations': ['kalmunai', 'kalmune', 'kalmuney', 'kalmunei'],
        'province': 'Eastern'
    },
    
    # =========================================================================
    # NORTH WESTERN PROVINCE
    # =========================================================================
    
    'kurunegala': {
        'sinhala': 'කුරුණෑගල',
        'transliterations': ['kurunegala', 'kurunagala', 'kurunegalah', 'kurunaegala'],
        'province': 'North Western'
    },
    'puttalam': {
        'sinhala': 'පුත්තලම',
        'transliterations': ['puttalam', 'putlam', 'puttalama', 'puthalam'],
        'province': 'North Western'
    },
    'chilaw': {
        'sinhala': 'හලාවත',
        'transliterations': ['chilaw', 'halawatha', 'chilau', 'chillaw'],
        'province': 'North Western'
    },
    'kuliyapitiya': {
        'sinhala': 'කුළියාපිටිය',
        'transliterations': ['kuliyapitiya', 'kuliyapitiyah', 'kuliyapitia', 'kuliyapitiye'],
        'province': 'North Western'
    },
    
    # =========================================================================
    # NORTH CENTRAL PROVINCE
    # =========================================================================
    
    'anuradhapura': {
        'sinhala': 'අනුරාධපුරය',
        'transliterations': ['anuradhapura', 'anuradapura', 'anuradhapurah', 'anuradapurah'],
        'province': 'North Central'
    },
    'polonnaruwa': {
        'sinhala': 'පොළොන්නරුව',
        'transliterations': ['polonnaruwa', 'pollonaruwa', 'polonnaruwah', 'pollonnaruwa'],
        'province': 'North Central'
    },
    
    # =========================================================================
    # UVA PROVINCE
    # =========================================================================
    
    'badulla': {
        'sinhala': 'බදුල්ල',
        'transliterations': ['badulla', 'badulleh', 'badula', 'badullah'],
        'province': 'Uva'
    },
    'bandarawela': {
        'sinhala': 'බණ්ඩාරවෙල',
        'transliterations': ['bandarawela', 'bandarawelah', 'bandaravela', 'bandarawella'],
        'province': 'Uva'
    },
    'ella': {
        'sinhala': 'ඇල්ල',
        'transliterations': ['ella', 'ellah', 'aella', 'ella'],
        'province': 'Uva'
    },
    'monaragala': {
        'sinhala': 'මොණරාගල',
        'transliterations': ['monaragala', 'moneragala', 'monaragalah', 'monoragala'],
        'province': 'Uva'
    },
    'haputale': {
        'sinhala': 'හපුතලේ',
        'transliterations': ['haputale', 'haputhale', 'haputaleh', 'haputhale'],
        'province': 'Uva'
    },
    
    # =========================================================================
    # SABARAGAMUWA PROVINCE
    # =========================================================================
    
    'ratnapura': {
        'sinhala': 'රත්නපුර',
        'transliterations': ['ratnapura', 'rathnapura', 'ratnapurah', 'rathnapurah'],
        'province': 'Sabaragamuwa'
    },
    'kegalle': {
        'sinhala': 'කෑගල්ල',
        'transliterations': ['kegalle', 'kegalla', 'kaegalle', 'kegalleh'],
        'province': 'Sabaragamuwa'
    },
    'balangoda': {
        'sinhala': 'බලන්ගොඩ',
        'transliterations': ['balangoda', 'belangoda', 'balangodah', 'balengoda'],
        'province': 'Sabaragamuwa'
    },
    
    # =========================================================================
    # NOTABLE LANDMARKS AND TOURIST PLACES
    # =========================================================================
    
    'adams_peak': {
        'sinhala': 'ශ්‍රී පාද',
        'transliterations': ['adams peak', 'sri pada', 'sripada', 'adam peak'],
        'province': 'Central/Sabaragamuwa'
    },
    'horton_plains': {
        'sinhala': 'හෝර්ටන් තැන්න',
        'transliterations': ['horton plains', 'horton', 'hortan plains', 'hortonplains'],
        'province': 'Central'
    },
    'yala': {
        'sinhala': 'යාල',
        'transliterations': ['yala', 'yaala', 'yalah', 'yaale'],
        'province': 'Southern/Uva'
    },
    'bentota': {
        'sinhala': 'බේන්තොට',
        'transliterations': ['bentota', 'benthota', 'bentotah', 'bentotte'],
        'province': 'Southern'
    },
    'arugam_bay': {
        'sinhala': 'අරුගම් බොක්ක',
        'transliterations': ['arugam bay', 'arugambay', 'arugam', 'arugambokka'],
        'province': 'Eastern'
    },
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_location_variants(location: str) -> Optional[Dict[str, any]]:
    """
    Get all transliteration variants for a given location.
    
    The search is case-insensitive and checks all known transliterations.
    
    Args:
        location: The location name to look up (in any known transliteration)
    
    Returns:
        Dict with 'sinhala', 'transliterations', and 'province' if found,
        None otherwise
    
    Example:
        >>> get_location_variants('colombo')
        {'sinhala': 'කොළඹ', 'transliterations': ['colombo', 'kolamba', ...], ...}
        
        >>> get_location_variants('unknown')
        None
    """
    location_lower = location.lower().strip()
    
    # Search in locations
    for key, value in SINHALA_LOCATIONS.items():
        # Check the key (with underscores replaced by spaces)
        if location_lower == key.replace('_', ' '):
            return value
        # Check all transliterations
        if location_lower in [t.lower() for t in value['transliterations']]:
            return value
    
    return None


def get_all_location_variants(location: str) -> List[str]:
    """
    Get all possible transliteration variants for a location.
    
    Args:
        location: The location name to look up
    
    Returns:
        List of all known transliterations, or empty list if not found
    
    Example:
        >>> get_all_location_variants('colombo')
        ['colombo', 'kolamba', 'kolomba', 'columbo']
    """
    result = get_location_variants(location)
    if result:
        return result['transliterations']
    return []


def get_sinhala_location(location: str) -> Optional[str]:
    """
    Get the Sinhala Unicode form of a romanized location name.
    
    Args:
        location: The romanized location name to look up
    
    Returns:
        The location name in Sinhala script, or None if not found
    
    Example:
        >>> get_sinhala_location('colombo')
        'කොළඹ'
    """
    result = get_location_variants(location)
    if result:
        return result['sinhala']
    return None


def get_location_province(location: str) -> Optional[str]:
    """
    Get the province of a given location.
    
    Args:
        location: The location name to look up
    
    Returns:
        The province name, or None if not found
    
    Example:
        >>> get_location_province('colombo')
        'Western'
    """
    result = get_location_variants(location)
    if result and 'province' in result:
        return result['province']
    return None


def is_known_location(location: str) -> bool:
    """
    Check if a location is in the dictionary.
    
    Args:
        location: The location name to check
    
    Returns:
        True if the location is known, False otherwise
    
    Example:
        >>> is_known_location('colombo')
        True
        >>> is_known_location('unknown')
        False
    """
    return get_location_variants(location) is not None


def get_locations_by_province(province: str) -> List[str]:
    """
    Get all locations in a given province.
    
    Args:
        province: The province name to filter by
    
    Returns:
        List of location keys in the given province
    
    Example:
        >>> get_locations_by_province('Western')
        ['colombo', 'gampaha', 'kalutara', ...]
    """
    province_lower = province.lower().strip()
    return [
        key for key, value in SINHALA_LOCATIONS.items()
        if value.get('province', '').lower() == province_lower
    ]


def get_all_locations() -> List[str]:
    """
    Get a list of all known location names.
    
    Returns:
        List of all location keys in the dictionary
    """
    return list(SINHALA_LOCATIONS.keys())


def get_all_provinces() -> List[str]:
    """
    Get a list of all provinces.
    
    Returns:
        List of unique province names
    """
    provinces = set()
    for value in SINHALA_LOCATIONS.values():
        if 'province' in value:
            provinces.add(value['province'])
    return sorted(list(provinces))
