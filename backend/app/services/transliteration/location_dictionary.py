# =============================================================================
# SRI LANKAN LOCATION DICTIONARY
# =============================================================================
# Dictionary of Sri Lankan locations with their transliteration variants.
# Used by the SinhalaTransliterator for accurate location transliteration.
# =============================================================================

"""
Sri Lankan Location Dictionary

This module contains a comprehensive dictionary of Sri Lankan locations
in Sinhala script along with their romanized variants.

The dictionary includes:
- Major cities
- Provincial capitals
- Towns and municipalities
- Districts
- Famous landmarks and areas

Each entry maps a Sinhala location name to a list of common romanized spellings,
accounting for different transliteration conventions and historical names.

Example:
    >>> from location_dictionary import LOCATION_DICTIONARY
    >>> LOCATION_DICTIONARY.get('කොළඹ')
    ['colombo', 'kolamba']
"""

# =============================================================================
# MAJOR CITIES
# =============================================================================

MAJOR_CITIES = {
    # Capital and major urban centers
    'කොළඹ': ['colombo', 'kolamba', 'kolomba'],
    'ශ්‍රී ජයවර්ධනපුර කෝට්ටේ': ['sri jayawardenepura kotte', 'kotte', 'jayawardenepura'],
    'දෙහිවල': ['dehiwala', 'dehiwela'],
    'මොරටුව': ['moratuwa', 'moratuwah'],
    'නුගේගොඩ': ['nugegoda', 'nugeegoda'],
    'රාජගිරිය': ['rajagiriya', 'rajagireeya'],
    'මහරගම': ['maharagama', 'maharagamah'],
    'බොරැල්ල': ['borella', 'borellah'],
    'කොල්ලුපිටිය': ['kollupitiya', 'colpetty'],
    'බම්බලපිටිය': ['bambalapitiya', 'bambalapitiyah'],
    'වැල්ලවත්ත': ['wellawatta', 'wellawatte', 'wellawaththa'],
    
    # North-Central cities
    'අනුරාධපුරය': ['anuradhapura', 'anuradapura'],
    'පොළොන්නරුව': ['polonnaruwa', 'polonnaru'],
    'මැදිරිගිරිය': ['medirigiriya', 'medirigiriyah'],
    
    # Central Province cities
    'මහනුවර': ['kandy', 'mahanuwara', 'maha nuwara'],
    'පේරාදෙණිය': ['peradeniya', 'peradeniyah'],
    'කටුගස්තොට': ['katugastota', 'katugastotah'],
    'ගම්පොල': ['gampola', 'gampolah'],
    'නුවර එළිය': ['nuwara eliya', 'nuwaraeliya', 'nuwara eliyah'],
    'හැටන්': ['hatton', 'hattan'],
    'මාතලේ': ['matale', 'mataleh'],
    'දඹුල්ල': ['dambulla', 'dambullah'],
    
    # Southern Province cities
    'ගාල්ල': ['galle', 'gaalla', 'galla'],
    'මාතර': ['matara', 'matarah'],
    'හම්බන්තොට': ['hambantota', 'hambantotah'],
    'තංගල්ල': ['tangalle', 'tangalla', 'tangallah'],
    'අම්බලන්ගොඩ': ['ambalangoda', 'ambalangodah'],
    'හික්කඩුව': ['hikkaduwa', 'hikkaduwah'],
    'උණවටුන': ['unawatuna', 'unawatunah'],
    'වැලිගම': ['weligama', 'weligamah'],
    'මිරිස්ස': ['mirissa', 'mirissah'],
    
    # Western Province cities
    'නිගම්බො': ['negombo', 'negomboh'],
    'ගම්පහ': ['gampaha', 'gampahah'],
    'කඳාන': ['kandana', 'kadana'],
    'කළුතර': ['kalutara', 'kaluturah'],
    'පානදුර': ['panadura', 'panadurah'],
    'හොරණ': ['horana', 'horanah'],
    
    # Northern Province cities
    'යාපනය': ['jaffna', 'yaapanaya', 'yalppanam'],
    'මන්නාරම': ['mannar', 'mannarama'],
    'වව්නියාව': ['vavuniya', 'vavuniyavah'],
    'කිලිනොච්චිය': ['kilinochchi', 'kilinochchiiyah'],
    'මුලතිව්': ['mullaitivu', 'mulathivu'],
    
    # Eastern Province cities
    'ත්‍රිකුණාමළය': ['trincomalee', 'trikunamalaya'],
    'බදුල්ල': ['badulla', 'badullah'],
    'මඩකලපුව': ['batticaloa', 'madakalapuva'],
    'අම්පාර': ['ampara', 'amparah'],
    'කල්මුනේ': ['kalmunai', 'kalmunaiy'],
    
    # Sabaragamuwa Province cities
    'රත්නපුර': ['ratnapura', 'ratnapurah'],
    'කෑගල්ල': ['kegalle', 'kaegalla'],
    
    # Uva Province cities
    'බණ්ඩාරවෙල': ['bandarawela', 'bandarawelah'],
    'එල්ල': ['ella', 'ellah'],
    'වැල්ලවාය': ['wellawaya', 'wellawayah'],
    'මොනරාගල': ['moneragala', 'monaragalah'],
    
    # North Western Province cities
    'කුරුණෑගල': ['kurunegala', 'kurunegalah'],
    'පුත්තලම': ['puttalam', 'puttalamah'],
    'චිලාව': ['chilaw', 'chilawh'],
}


# =============================================================================
# DISTRICTS
# =============================================================================

DISTRICTS = {
    'කොළඹ දිස්ත්‍රික්කය': ['colombo district'],
    'ගම්පහ දිස්ත්‍රික්කය': ['gampaha district'],
    'කළුතර දිස්ත්‍රික්කය': ['kalutara district'],
    'මහනුවර දිස්ත්‍රික්කය': ['kandy district'],
    'මාතලේ දිස්ත්‍රික්කය': ['matale district'],
    'නුවර එළිය දිස්ත්‍රික්කය': ['nuwara eliya district'],
    'ගාල්ල දිස්ත්‍රික්කය': ['galle district'],
    'මාතර දිස්ත්‍රික්කය': ['matara district'],
    'හම්බන්තොට දිස්ත්‍රික්කය': ['hambantota district'],
    'යාපනය දිස්ත්‍රික්කය': ['jaffna district'],
    'කිලිනොච්චි දිස්ත්‍රික්කය': ['kilinochchi district'],
    'මන්නාරම දිස්ත්‍රික්කය': ['mannar district'],
    'වව්නියාව දිස්ත්‍රික්කය': ['vavuniya district'],
    'මුලතිව් දිස්ත්‍රික්කය': ['mullaitivu district'],
    'මඩකලපුව දිස්ත්‍රික්කය': ['batticaloa district'],
    'අම්පාර දිස්ත්‍රික්කය': ['ampara district'],
    'ත්‍රිකුණාමළය දිස්ත්‍රික්කය': ['trincomalee district'],
    'කුරුණෑගල දිස්ත්‍රික්කය': ['kurunegala district'],
    'පුත්තලම දිස්ත්‍රික්කය': ['puttalam district'],
    'අනුරාධපුර දිස්ත්‍රික්කය': ['anuradhapura district'],
    'පොළොන්නරුව දිස්ත්‍රික්කය': ['polonnaruwa district'],
    'බදුල්ල දිස්ත්‍රික්කය': ['badulla district'],
    'මොනරාගල දිස්ත්‍රික්කය': ['moneragala district'],
    'රත්නපුර දිස්ත්‍රික්කය': ['ratnapura district'],
    'කෑගල්ල දිස්ත්‍රික්කය': ['kegalle district'],
}


# =============================================================================
# PROVINCES
# =============================================================================

PROVINCES = {
    'බස්නාහිර පළාත': ['western province'],
    'මධ්‍යම පළාත': ['central province'],
    'දකුණු පළාත': ['southern province'],
    'උතුරු පළාත': ['northern province'],
    'නැගෙනහිර පළාත': ['eastern province'],
    'වයඹ පළාත': ['north western province', 'wayamba'],
    'උතුරු මැද පළාත': ['north central province'],
    'ඌව පළාත': ['uva province'],
    'සබරගමුව පළාත': ['sabaragamuwa province'],
}


# =============================================================================
# LANDMARKS AND FAMOUS PLACES
# =============================================================================

LANDMARKS = {
    # Religious sites
    'දළදා මාලිගාව': ['temple of the tooth', 'dalada maligawa'],
    'කැලණිය රජමහා විහාරය': ['kelaniya raja maha viharaya', 'kelaniya temple'],
    'ගංගාරාම පන්සල': ['gangaramaya temple', 'gangarama'],
    'ශ්‍රී පාදය': ['sri pada', 'adams peak', 'sri padaya'],
    'මිහින්තලේ': ['mihintale', 'mihintaleh'],
    'රුවන්වැලි සෑය': ['ruwanwelisaya', 'ruwanweli seya'],
    'ජේතවනාරාමය': ['jetavanaramaya', 'jethawanaramaya'],
    
    # Historical sites
    'සීගිරිය': ['sigiriya', 'sigireeya', 'lion rock'],
    'පොළොන්නරුව ගල් විහාරය': ['polonnaruwa gal viharaya', 'gal vihara'],
    'යාල ජාතික වනෝද්‍යානය': ['yala national park', 'yala'],
    'උඩවලව': ['udawalawe', 'udawalaweh'],
    'හෝර්ටන් තැන්න': ['horton plains', 'hortan thanna'],
    'සිංහරාජ': ['sinharaja', 'sinharajah'],
    
    # Beaches
    'අරුගම් බොක්ක': ['arugam bay', 'arugam bokka'],
    'මිරිස්ස වෙරළ': ['mirissa beach'],
    'හික්කඩුව වෙරළ': ['hikkaduwa beach'],
    'බෙන්තොට': ['bentota', 'bentotah'],
    'පාසිකුඩා': ['pasikuda', 'pasikudah'],
    
    # Other notable places
    'පිනවල අලි නිවාසය': ['pinnawala elephant orphanage', 'pinnawela'],
    'නුවර වැව': ['kandy lake', 'nuwara wewa'],
    'බෙයිරා වැව': ['beira lake', 'beira wewa'],
    'නෙළුම් කුලුන': ['lotus tower', 'nelum kuluna'],
    'ගෝල් ෆේස්': ['galle face', 'galle face green'],
}


# =============================================================================
# SUBURBS AND AREAS IN COLOMBO
# =============================================================================

COLOMBO_AREAS = {
    'ෆෝර්ට්': ['fort', 'colombo fort'],
    'පෙට්ටා': ['pettah', 'petta'],
    'කොම්පඤ්ඤ වීදිය': ['kompannaveediya', 'slave island'],
    'මරදාන': ['maradana', 'maradanah'],
    'නාරාහේන්පිට': ['narahenpita', 'narahenpitah'],
    'කිරුලපන': ['kirulapana', 'kirulapone'],
    'හවෙලොක් ටවුන්': ['havelock town'],
    'තිඹිරිගස්යාය': ['thimbirigasyaya', 'thimbirigasyayah'],
    'කිරිබත්ගොඩ': ['kiribathgoda', 'kiribathgodah'],
    'කඩුවෙල': ['kaduwela', 'kaduwelah'],
    'අතුරුගිරිය': ['athurugiriya', 'athurugiriyah'],
    'බත්තරමුල්ල': ['battaramulla', 'battaramullah'],
    'මාලබේ': ['malabe', 'malabeh'],
    'කොට්ටාව': ['kottawa', 'kottawah'],
    'පිළියන්දල': ['piliyandala', 'piliyandalah'],
    'කෝට්ටේ': ['kotte', 'kottey'],
}


# =============================================================================
# COMBINED LOCATION DICTIONARY
# =============================================================================

LOCATION_DICTIONARY = {}
LOCATION_DICTIONARY.update(MAJOR_CITIES)
LOCATION_DICTIONARY.update(DISTRICTS)
LOCATION_DICTIONARY.update(PROVINCES)
LOCATION_DICTIONARY.update(LANDMARKS)
LOCATION_DICTIONARY.update(COLOMBO_AREAS)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_location_variants(sinhala_location: str) -> list:
    """
    Get romanized variants for a Sinhala location name.
    
    Args:
        sinhala_location: Location name in Sinhala script
        
    Returns:
        list: List of romanized variants, or empty list if not found
        
    Example:
        >>> get_location_variants('කොළඹ')
        ['colombo', 'kolamba', 'kolomba']
    """
    return LOCATION_DICTIONARY.get(sinhala_location, [])


def search_by_romanized(romanized_location: str) -> list:
    """
    Search for Sinhala location names by their romanized form.
    
    Args:
        romanized_location: Location name in romanized English (case-insensitive)
        
    Returns:
        list: List of matching Sinhala location names
        
    Example:
        >>> search_by_romanized('colombo')
        ['කොළඹ']
    """
    romanized_lower = romanized_location.lower()
    matches = []
    for sinhala, variants in LOCATION_DICTIONARY.items():
        if romanized_lower in [v.lower() for v in variants]:
            matches.append(sinhala)
    return matches


def get_all_locations() -> dict:
    """
    Get the complete location dictionary.
    
    Returns:
        dict: Complete location dictionary with all entries
    """
    return LOCATION_DICTIONARY.copy()
