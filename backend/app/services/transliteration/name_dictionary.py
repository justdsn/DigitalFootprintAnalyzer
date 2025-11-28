# =============================================================================
# SRI LANKAN NAME DICTIONARY
# =============================================================================
# Dictionary of common Sri Lankan names with their transliteration variants.
# Used by the SinhalaTransliterator for accurate name transliteration.
# =============================================================================

"""
Sri Lankan Name Dictionary

This module contains a comprehensive dictionary of common Sri Lankan names
in Sinhala script along with their romanized variants.

The dictionary includes:
- First names (male and female)
- Family names/surnames
- Common name variations used in Sri Lanka

Each entry maps a Sinhala name to a list of common romanized spellings,
accounting for different transliteration conventions.

Example:
    >>> from name_dictionary import NAME_DICTIONARY
    >>> NAME_DICTIONARY.get('දුෂාන්')
    ['dushan', 'dushaan', 'dusan']
"""

# =============================================================================
# MALE FIRST NAMES
# =============================================================================

MALE_NAMES = {
    # Common male names - A
    'අමිල': ['amila', 'ameela'],
    'අසංක': ['asanka', 'asangka'],
    'අජිත්': ['ajith', 'ajit'],
    'අනුර': ['anura', 'anurah'],
    'අරුණ': ['aruna', 'arunah'],
    'අශාන්': ['ashan', 'ashaan'],
    
    # Common male names - B
    'බුද්ධික': ['buddhika', 'budhdika'],
    'බණ්ඩාර': ['bandara', 'bandarah'],
    
    # Common male names - C/Ch
    'චමින්ද': ['chaminda', 'chamintha'],
    'චන්දන': ['chandana', 'chandan'],
    'චතුර': ['chathura', 'chathurah'],
    'චාමර': ['chamara', 'chamarah'],
    
    # Common male names - D
    'දුෂාන්': ['dushan', 'dushaan', 'dusan'],
    'දිනේෂ්': ['dinesh', 'dineesh'],
    'දයාසිරි': ['dayasiri', 'dayasiree'],
    'දමිත්': ['damith', 'damit'],
    'දිලාන්': ['dilan', 'dilaan', 'dilhan'],
    'දිලීප': ['dilip', 'dileepa', 'dileepah'],
    
    # Common male names - G
    'ගාමිණි': ['gamini', 'gaminee'],
    'ගයාන්': ['gayan', 'gayaan'],
    
    # Common male names - H
    'හරීෂ්': ['harish', 'hareesh'],
    'හිරාන්': ['hiran', 'hiraan'],
    
    # Common male names - I
    'ඉන්දික': ['indika', 'indikah'],
    
    # Common male names - J
    'ජනක': ['janaka', 'janakah'],
    'ජයසිංහ': ['jayasinghe', 'jayasinha', 'jayasingha'],
    'ජීවන්': ['jeevan', 'jiwan', 'jeewan'],
    
    # Common male names - K
    'කමල්': ['kamal', 'kamaal'],
    'කසුන්': ['kasun', 'kasunn'],
    'කුමාර': ['kumara', 'kumarah', 'kumar'],
    'කිත්සිරි': ['kithsiri', 'kithsiree'],
    'කවින්ද': ['kavinda', 'kavindah'],
    
    # Common male names - L
    'ලක්ෂාන්': ['lakshan', 'lakshaan', 'laxan'],
    'ලසිත්': ['lasith', 'lasit'],
    'ලාහිරු': ['lahiru', 'lahiruh'],
    
    # Common male names - M
    'මහේෂ්': ['mahesh', 'maheesh'],
    'මලින්ද': ['malinda', 'malindah'],
    'මනෝජ්': ['manoj', 'manoja'],
    'මිලින්ද': ['milinda', 'milindah'],
    
    # Common male names - N
    'නිමල්': ['nimal', 'nimaal'],
    'නිරෝෂ්': ['nirosh', 'niroshan'],
    'නුවන්': ['nuwan', 'nuwaan'],
    'නිශාන්ත': ['nishantha', 'nishanta'],
    
    # Common male names - P
    'ප්‍රසාද්': ['prasad', 'prasaad'],
    'ප්‍රදීප්': ['pradeep', 'pradeepa'],
    'ප්‍රභාත්': ['prabath', 'prabhaath'],
    'පවිත්‍ර': ['pavithra', 'pavitra'],
    
    # Common male names - R
    'රුවන්': ['ruwan', 'ruwaan'],
    'රංජිත්': ['ranjith', 'ranjit'],
    'රොෂාන්': ['roshan', 'roshaan'],
    'රාජිත': ['rajitha', 'rajita'],
    
    # Common male names - S
    'සුනිල්': ['sunil', 'suneel'],
    'සමන්': ['saman', 'samaan'],
    'සංජය': ['sanjaya', 'sanjay'],
    'සනත්': ['sanath', 'sanat'],
    'සිසිර': ['sisira', 'sisirah'],
    'සම්පත්': ['sampath', 'sampat'],
    
    # Common male names - T
    'තරංග': ['tharanga', 'taranga'],
    'තිලක්': ['thilak', 'tilak'],
    'තුෂාර': ['thushara', 'tushara'],
    
    # Common male names - U
    'උදාර': ['udara', 'udarah'],
    'උපුල්': ['upul', 'upula'],
    
    # Common male names - V/W
    'විජිත': ['vijitha', 'wijitha', 'vijita'],
    'වරුණ': ['waruna', 'varuna'],
    'වසන්ත': ['wasantha', 'vasantha', 'wasanta'],
    
    # Common male names - Y
    'යසිත': ['yasitha', 'yashitha'],
}


# =============================================================================
# FEMALE FIRST NAMES
# =============================================================================

FEMALE_NAMES = {
    # Common female names - A
    'අනෝමා': ['anoma', 'anomah'],
    'අයේෂා': ['ayesha', 'ayeshaa'],
    'අමාලි': ['amali', 'amalee'],
    'අශාන්ති': ['ashanthi', 'ashanti'],
    
    # Common female names - C/Ch
    'චමිලා': ['chamila', 'chamilah'],
    'චන්ද්‍රිකා': ['chandrika', 'chandrikah'],
    
    # Common female names - D
    'දිලානි': ['dilani', 'dilanee'],
    'දීපිකා': ['deepika', 'dipika'],
    'දමයන්ති': ['damayanthi', 'damayanti'],
    
    # Common female names - G
    'ගයනී': ['gayani', 'gayanee'],
    
    # Common female names - H
    'හිරුනි': ['hiruni', 'hirunee'],
    'හෂිනි': ['hashini', 'hashinee'],
    
    # Common female names - I
    'ඉෂානි': ['ishani', 'ishanee'],
    
    # Common female names - K
    'කමලා': ['kamala', 'kamalah'],
    'කුමාරි': ['kumari', 'kumaree'],
    
    # Common female names - L
    'ලක්ෂිකා': ['lakshika', 'laxika'],
    
    # Common female names - M
    'මධුෂා': ['madhusha', 'madushaa'],
    'මාලිනී': ['malini', 'malinee'],
    
    # Common female names - N
    'නිමාලි': ['nimali', 'nimalee'],
    'නදීෂා': ['nadeesha', 'nadisha'],
    'නයෝමි': ['nayomi', 'nayomee'],
    'නිරෝෂා': ['nirosha', 'niroshaa'],
    
    # Common female names - P
    'පියුමි': ['piyumi', 'piyumee'],
    'ප්‍රභාෂිණි': ['prabhashini', 'prabhashinee'],
    
    # Common female names - R
    'රේණුකා': ['renuka', 'renukah'],
    'රුමේෂා': ['rumesha', 'rumeshaa'],
    
    # Common female names - S
    'සදුනි': ['saduni', 'sadunee'],
    'සෙව්වන්දි': ['sewwandi', 'sevwandee'],
    'ශිරානි': ['shirani', 'sheerani'],
    'සුරේඛා': ['surekha', 'surekhaa'],
    'සුභාෂිණී': ['subhashini', 'subhashinee'],
    
    # Common female names - T
    'තරිඳු': ['tharindu', 'tarinduh'],
    
    # Common female names - U
    'උදේනි': ['udeni', 'udenee'],
    
    # Common female names - V/W
    'විශාඛා': ['vishakha', 'wishakha'],
}


# =============================================================================
# FAMILY NAMES / SURNAMES
# =============================================================================

FAMILY_NAMES = {
    # Common Sinhalese surnames
    'පෙරේරා': ['perera', 'pereera', 'pereira'],
    'සිල්වා': ['silva', 'silvaa', 'de silva'],
    'ප්‍රනාන්දු': ['fernando', 'fernandoo'],
    'ගුණවර්ධන': ['gunawardena', 'gunawardana', 'gunawardene'],
    'ජයවර්ධන': ['jayawardena', 'jayawardana', 'jayawardene'],
    'විජේසිංහ': ['wijesinghe', 'wijesinha', 'wijesingha'],
    'රත්නායක': ['rathnayake', 'ratnayaka', 'ratnayake'],
    'සේනාරත්න': ['senaratne', 'senaratna', 'senarathna'],
    'බණ්ඩාරනායක': ['bandaranaike', 'bandaranayake', 'bandaranayaka'],
    'විජේරත්න': ['wijeratne', 'wijerathna', 'wijeratna'],
    'ද සොයිසා': ['de soysa', 'de soyza', 'de zoysa'],
    'ද මෙල්': ['de mel', 'demel'],
    'කරුණාරත්න': ['karunaratne', 'karunarathna', 'karunaratna'],
    'දිසානායක': ['dissanayake', 'dissanayaka', 'disanayake'],
    'එදිරිසිංහ': ['edirisinghe', 'edirisingha', 'edirisinha'],
    'අබේවර්ධන': ['abewardena', 'abewardana', 'abewardene'],
    'හේවාවිතාරණ': ['hewavitharana', 'hewavitarana'],
    'මුදලිගේ': ['mudalige', 'mudaligey'],
    'සමරසිංහ': ['samarasinghe', 'samarasinha', 'samarasingha'],
    'වික්‍රමසිංහ': ['wickramasinghe', 'wickramasinha', 'vikramasinghe'],
    'රණතුංග': ['ranatunga', 'ranatunge'],
    'කුමාරතුංග': ['kumaratunga', 'kumaratunge'],
    'ප්‍රේමදාස': ['premadasa', 'premadassa'],
    'ද සිල්වා': ['de silva', 'da silva', 'desilva'],
    'අමරසේකර': ['amarasekara', 'amarasekera'],
    'ජයතිලක': ['jayatilaka', 'jayathilaka', 'jayatilleke'],
    'ගමගේ': ['gamage', 'gamagey'],
    'රාජපක්ෂ': ['rajapaksa', 'rajapakse', 'rajapaksha'],
    'සේනාධීර': ['senadhira', 'senadheera'],
    'හේරත්': ['herath', 'herathh'],
    'පීරිස්': ['peiris', 'peeris', 'pieris'],
    'කරුණානායක': ['karunanayake', 'karunanayaka'],
    'ෆොන්සේකා': ['fonseka', 'fonsekah'],
    'ගුණසේකර': ['gunasekara', 'gunasekera'],
    'අතුකෝරාල': ['athukorala', 'athukorale'],
    'බෙල්ලන': ['bellana', 'bellanah'],
    'සිරිවර්ධන': ['siriwardena', 'siriwardana', 'siriwardene'],
    'ඉලංගකෝන්': ['ilangakoon', 'ilangakon'],
    'ලියනගේ': ['liyanage', 'liyanagey'],
    'පතිරණ': ['pathirana', 'pathiranah'],
    'මැදගම': ['medagama', 'medagamah'],
}


# =============================================================================
# COMBINED NAME DICTIONARY
# =============================================================================

NAME_DICTIONARY = {}
NAME_DICTIONARY.update(MALE_NAMES)
NAME_DICTIONARY.update(FEMALE_NAMES)
NAME_DICTIONARY.update(FAMILY_NAMES)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_name_variants(sinhala_name: str) -> list:
    """
    Get romanized variants for a Sinhala name.
    
    Args:
        sinhala_name: Name in Sinhala script
        
    Returns:
        list: List of romanized variants, or empty list if not found
        
    Example:
        >>> get_name_variants('දුෂාන්')
        ['dushan', 'dushaan', 'dusan']
    """
    return NAME_DICTIONARY.get(sinhala_name, [])


def search_by_romanized(romanized_name: str) -> list:
    """
    Search for Sinhala names by their romanized form.
    
    Args:
        romanized_name: Name in romanized English (case-insensitive)
        
    Returns:
        list: List of matching Sinhala names
        
    Example:
        >>> search_by_romanized('kamal')
        ['කමල්']
    """
    romanized_lower = romanized_name.lower()
    matches = []
    for sinhala, variants in NAME_DICTIONARY.items():
        if romanized_lower in [v.lower() for v in variants]:
            matches.append(sinhala)
    return matches


def get_all_names() -> dict:
    """
    Get the complete name dictionary.
    
    Returns:
        dict: Complete name dictionary with all entries
    """
    return NAME_DICTIONARY.copy()
