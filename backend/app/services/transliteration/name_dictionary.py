# =============================================================================
# SINHALA NAME DICTIONARY
# =============================================================================
# Contains common Sri Lankan names with their Sinhala Unicode representations
# and multiple romanized spelling variants. Used for name transliteration.
# =============================================================================

"""
Sri Lankan Name Dictionary

This module contains:
- SINHALA_FIRST_NAMES: 50+ common Sri Lankan first names with variants
- SINHALA_SURNAMES: 30+ common Sri Lankan surnames with variants
- get_name_variants(): Function to get all variants for a name

Each name entry includes:
- sinhala: The name in Sinhala script
- transliterations: List of common English spelling variants

The variants cover different romanization styles commonly used by
Sri Lankans when writing their names in English.

Example:
    SINHALA_FIRST_NAMES['dushan']
    # Returns: {'sinhala': 'දුෂාන්', 'transliterations': ['dushan', 'dushaan', ...]}
"""

from typing import Dict, List, Optional

# =============================================================================
# COMMON SRI LANKAN FIRST NAMES (MALE)
# =============================================================================
# 50+ common male first names used in Sri Lanka with their Sinhala forms
# and common English spelling variants
# =============================================================================

SINHALA_FIRST_NAMES_MALE: Dict[str, Dict[str, any]] = {
    # A names
    'amal': {
        'sinhala': 'අමල්',
        'transliterations': ['amal', 'amaal', 'amhal']
    },
    'arjuna': {
        'sinhala': 'අර්ජුන',
        'transliterations': ['arjuna', 'arjun', 'arjunah']
    },
    'asanka': {
        'sinhala': 'අසංක',
        'transliterations': ['asanka', 'asanga', 'asankha']
    },
    'asela': {
        'sinhala': 'අසේල',
        'transliterations': ['asela', 'aseela', 'aselah']
    },
    'ajith': {
        'sinhala': 'අජිත්',
        'transliterations': ['ajith', 'ajit', 'ajeeth', 'ajitha']
    },
    
    # B names
    'bandara': {
        'sinhala': 'බණ්ඩාර',
        'transliterations': ['bandara', 'bandarah', 'bendara']
    },
    'buddhika': {
        'sinhala': 'බුද්ධික',
        'transliterations': ['buddhika', 'budhika', 'budhdika', 'buddika']
    },
    
    # C names
    'chaminda': {
        'sinhala': 'චමින්ද',
        'transliterations': ['chaminda', 'chamindha', 'shaminda']
    },
    'chandana': {
        'sinhala': 'චන්දන',
        'transliterations': ['chandana', 'chandanah', 'chanden']
    },
    'chathura': {
        'sinhala': 'චතුර',
        'transliterations': ['chathura', 'chathurah', 'chatura', 'cathura']
    },
    
    # D names
    'dilshan': {
        'sinhala': 'දිල්ශාන්',
        'transliterations': ['dilshan', 'dilshaan', 'dilsaan', 'tilshan']
    },
    'dinesh': {
        'sinhala': 'දිනේෂ්',
        'transliterations': ['dinesh', 'dineesh', 'dinish', 'dhinesh']
    },
    'dushan': {
        'sinhala': 'දුෂාන්',
        'transliterations': ['dushan', 'dushaan', 'dusan', 'dusaan', 'dhushan']
    },
    'dasun': {
        'sinhala': 'දසුන්',
        'transliterations': ['dasun', 'dasoon', 'dhasun', 'dasunth']
    },
    'dimuthu': {
        'sinhala': 'දිමුතු',
        'transliterations': ['dimuthu', 'dimuthu', 'dimutu', 'dhimuthu']
    },
    
    # G names
    'gayan': {
        'sinhala': 'ගයාන්',
        'transliterations': ['gayan', 'gayaan', 'gayen', 'gahan']
    },
    'gehan': {
        'sinhala': 'ගේහාන්',
        'transliterations': ['gehan', 'gehaan', 'ghehan']
    },
    
    # H names
    'harsha': {
        'sinhala': 'හර්ෂ',
        'transliterations': ['harsha', 'harshaa', 'harsa', 'harshah']
    },
    'hasitha': {
        'sinhala': 'හසිත',
        'transliterations': ['hasitha', 'hasithah', 'hasita', 'hasetha']
    },
    
    # I names
    'isuru': {
        'sinhala': 'ඉසුරු',
        'transliterations': ['isuru', 'isuroo', 'issuru', 'isooru']
    },
    
    # J names
    'janaka': {
        'sinhala': 'ජනක',
        'transliterations': ['janaka', 'janakah', 'janeka']
    },
    
    # K names
    'kamal': {
        'sinhala': 'කමල්',
        'transliterations': ['kamal', 'kamaal', 'kemal']
    },
    'kasun': {
        'sinhala': 'කසුන්',
        'transliterations': ['kasun', 'kasoon', 'kassun', 'casun']
    },
    'kavinda': {
        'sinhala': 'කවින්ද',
        'transliterations': ['kavinda', 'kavindah', 'kawindha', 'kavindha']
    },
    'kumara': {
        'sinhala': 'කුමාර',
        'transliterations': ['kumara', 'kumarah', 'koomar', 'kumar']
    },
    
    # L names
    'lahiru': {
        'sinhala': 'ලහිරු',
        'transliterations': ['lahiru', 'lahiroo', 'laheeru', 'lahirue']
    },
    'lasantha': {
        'sinhala': 'ලසන්ත',
        'transliterations': ['lasantha', 'lasanthah', 'lasanthe', 'lassantha']
    },
    
    # M names
    'mahesh': {
        'sinhala': 'මහේෂ්',
        'transliterations': ['mahesh', 'maheesh', 'mahes', 'maheysh']
    },
    'malith': {
        'sinhala': 'මාලිත්',
        'transliterations': ['malith', 'malitha', 'maleeth', 'malit']
    },
    'manjula': {
        'sinhala': 'මංජුල',
        'transliterations': ['manjula', 'manjulah', 'menjula']
    },
    
    # N names
    'namal': {
        'sinhala': 'නාමල්',
        'transliterations': ['namal', 'naamaal', 'nemal', 'namel']
    },
    'nishan': {
        'sinhala': 'නිශාන්',
        'transliterations': ['nishan', 'nishaan', 'nishan', 'nissan']
    },
    'nuwan': {
        'sinhala': 'නුවන්',
        'transliterations': ['nuwan', 'nuwaan', 'noowan', 'nuwen']
    },
    
    # P names
    'prasad': {
        'sinhala': 'ප්‍රසාද්',
        'transliterations': ['prasad', 'prasaad', 'prasath', 'prasadh']
    },
    'pradeep': {
        'sinhala': 'ප්‍රදීප්',
        'transliterations': ['pradeep', 'pradip', 'pradheep', 'pradeeph']
    },
    'priyantha': {
        'sinhala': 'ප්‍රියන්ත',
        'transliterations': ['priyantha', 'priyanthah', 'priyanth', 'priyanthe']
    },
    
    # R names
    'rajitha': {
        'sinhala': 'රාජිත',
        'transliterations': ['rajitha', 'rajithah', 'rajetha', 'rajita']
    },
    'roshan': {
        'sinhala': 'රොෂාන්',
        'transliterations': ['roshan', 'roshaan', 'rohan', 'roshen']
    },
    'ruwan': {
        'sinhala': 'රුවන්',
        'transliterations': ['ruwan', 'ruwaan', 'ruwen', 'roowan']
    },
    
    # S names
    'sampath': {
        'sinhala': 'සම්පත්',
        'transliterations': ['sampath', 'sampat', 'sampth', 'sampaath']
    },
    'saman': {
        'sinhala': 'සමන්',
        'transliterations': ['saman', 'samaan', 'samen', 'samun']
    },
    'sanjeewa': {
        'sinhala': 'සංජීව',
        'transliterations': ['sanjeewa', 'sanjiva', 'sanjeev', 'sanjewa']
    },
    'sunil': {
        'sinhala': 'සුනිල්',
        'transliterations': ['sunil', 'suneel', 'sunill', 'soonil']
    },
    'supun': {
        'sinhala': 'සුපුන්',
        'transliterations': ['supun', 'supoon', 'supuun', 'soopun']
    },
    
    # T names
    'thilak': {
        'sinhala': 'තිලක්',
        'transliterations': ['thilak', 'tilak', 'thilaka', 'tilaka']
    },
    'thisara': {
        'sinhala': 'තිසර',
        'transliterations': ['thisara', 'tisara', 'thissara', 'thisarah']
    },
    
    # U names
    'udara': {
        'sinhala': 'උදාර',
        'transliterations': ['udara', 'udarah', 'oodhara', 'udaara']
    },
    'upul': {
        'sinhala': 'උපුල්',
        'transliterations': ['upul', 'upula', 'oopul', 'upuul']
    },
    
    # V names
    'viraj': {
        'sinhala': 'විරාජ්',
        'transliterations': ['viraj', 'viraaj', 'wiraj', 'veeraj']
    },
    
    # W names
    'wasantha': {
        'sinhala': 'වසන්ත',
        'transliterations': ['wasantha', 'vasantha', 'wasanthe', 'wasanthah']
    },
    'wijitha': {
        'sinhala': 'විජිත',
        'transliterations': ['wijitha', 'vijitha', 'wijita', 'vijita']
    },
}

# =============================================================================
# COMMON SRI LANKAN FIRST NAMES (FEMALE)
# =============================================================================

SINHALA_FIRST_NAMES_FEMALE: Dict[str, Dict[str, any]] = {
    # A names
    'achini': {
        'sinhala': 'අචිනි',
        'transliterations': ['achini', 'acheeni', 'achinee', 'achinie']
    },
    'anoma': {
        'sinhala': 'අනෝමා',
        'transliterations': ['anoma', 'anomah', 'anomaa', 'enoma']
    },
    'anusha': {
        'sinhala': 'අනුෂා',
        'transliterations': ['anusha', 'anushaa', 'anosha', 'anushah']
    },
    
    # C names
    'chamari': {
        'sinhala': 'චාමරි',
        'transliterations': ['chamari', 'chamaree', 'shamari', 'chamarei']
    },
    'chathurika': {
        'sinhala': 'චතුරිකා',
        'transliterations': ['chathurika', 'chaturika', 'chathurikah', 'chathureeka']
    },
    
    # D names
    'darshani': {
        'sinhala': 'දර්ශනි',
        'transliterations': ['darshani', 'darshanee', 'dharshani', 'darshanie']
    },
    'dilini': {
        'sinhala': 'දිලිනි',
        'transliterations': ['dilini', 'dilinee', 'dhilini', 'dilinie']
    },
    
    # H names
    'hansani': {
        'sinhala': 'හංසනි',
        'transliterations': ['hansani', 'hansanee', 'hansanie', 'hensani']
    },
    'hashini': {
        'sinhala': 'හෂිනි',
        'transliterations': ['hashini', 'hashinee', 'heshini', 'hashinie']
    },
    
    # I names
    'iresha': {
        'sinhala': 'ඉරේෂා',
        'transliterations': ['iresha', 'ireshaa', 'eresha', 'ireshah']
    },
    
    # K names
    'kamani': {
        'sinhala': 'කමනි',
        'transliterations': ['kamani', 'kamanee', 'kemani', 'kamanie']
    },
    'kavindi': {
        'sinhala': 'කවින්දි',
        'transliterations': ['kavindi', 'kawindhi', 'kavindee', 'kavindhi']
    },
    'kumari': {
        'sinhala': 'කුමාරි',
        'transliterations': ['kumari', 'kumaree', 'kumare', 'kumarie']
    },
    
    # L names
    'lakshani': {
        'sinhala': 'ලක්ෂාණි',
        'transliterations': ['lakshani', 'lakshanee', 'lakshanie', 'laxani']
    },
    
    # M names
    'madhavi': {
        'sinhala': 'මාධවී',
        'transliterations': ['madhavi', 'madavi', 'madhavee', 'madhawee']
    },
    'malini': {
        'sinhala': 'මාලිනි',
        'transliterations': ['malini', 'malinee', 'malinei', 'malinie']
    },
    
    # N names
    'nadeesha': {
        'sinhala': 'නදීෂා',
        'transliterations': ['nadeesha', 'nadesha', 'nadisha', 'nadeeshaa']
    },
    'nimali': {
        'sinhala': 'නිමාලි',
        'transliterations': ['nimali', 'nimalee', 'nimalie', 'nimalei']
    },
    
    # P names
    'pavithra': {
        'sinhala': 'පවිත්‍රා',
        'transliterations': ['pavithra', 'pavitra', 'pawithrah', 'pawithra']
    },
    'pooja': {
        'sinhala': 'පූජා',
        'transliterations': ['pooja', 'puja', 'poojah', 'pujah']
    },
    'primali': {
        'sinhala': 'ප්‍රිමාලි',
        'transliterations': ['primali', 'primalee', 'premalee', 'primalie']
    },
    
    # R names
    'rangi': {
        'sinhala': 'රංගි',
        'transliterations': ['rangi', 'rangee', 'rangie', 'rengee']
    },
    'rashmi': {
        'sinhala': 'රශ්මි',
        'transliterations': ['rashmi', 'rashmee', 'rasmi', 'reshmee']
    },
    
    # S names
    'sachini': {
        'sinhala': 'සචිනි',
        'transliterations': ['sachini', 'sachinee', 'sachinie', 'sacheeni']
    },
    'sanduni': {
        'sinhala': 'සඳුනි',
        'transliterations': ['sanduni', 'sandunee', 'sandunie', 'sendunee']
    },
    'sewwandi': {
        'sinhala': 'සෙව්වන්දි',
        'transliterations': ['sewwandi', 'sewandi', 'sevvandi', 'sevwandi']
    },
    'shashini': {
        'sinhala': 'ෂෂිනි',
        'transliterations': ['shashini', 'shashinee', 'sashini', 'shashinie']
    },
    
    # T names
    'tharushi': {
        'sinhala': 'තරුෂි',
        'transliterations': ['tharushi', 'tarushi', 'tharushee', 'therushi']
    },
    'thilini': {
        'sinhala': 'තිලිනි',
        'transliterations': ['thilini', 'tilini', 'thilinee', 'tiliney']
    },
    
    # U names
    'udeshika': {
        'sinhala': 'උදේශිකා',
        'transliterations': ['udeshika', 'udeshikah', 'oodeshika', 'udeshikaa']
    },
    
    # W names
    'wasana': {
        'sinhala': 'වාසනා',
        'transliterations': ['wasana', 'vasana', 'wasanah', 'wasanaa']
    },
    
    # Y names
    'yashoda': {
        'sinhala': 'යශෝදා',
        'transliterations': ['yashoda', 'yashodah', 'yasoda', 'yashodaa']
    },
}

# =============================================================================
# COMBINED FIRST NAMES DICTIONARY
# =============================================================================

SINHALA_FIRST_NAMES: Dict[str, Dict[str, any]] = {
    **SINHALA_FIRST_NAMES_MALE,
    **SINHALA_FIRST_NAMES_FEMALE
}

# =============================================================================
# COMMON SRI LANKAN SURNAMES
# =============================================================================
# 30+ common Sri Lankan surnames with their Sinhala forms and variants.
# These are typically inherited family names or caste-based surnames.
# =============================================================================

SINHALA_SURNAMES: Dict[str, Dict[str, any]] = {
    # A surnames
    'abeysekara': {
        'sinhala': 'අබේසේකර',
        'transliterations': ['abeysekara', 'abesekara', 'abeysekarah', 'abeysekera']
    },
    'amarasinghe': {
        'sinhala': 'අමරසිංහ',
        'transliterations': ['amarasinghe', 'amarasinge', 'amarasingha', 'amarasinha']
    },
    
    # B surnames
    'bandara': {
        'sinhala': 'බණ්ඩාර',
        'transliterations': ['bandara', 'bandarah', 'bendara', 'bandera']
    },
    
    # D surnames
    'de_silva': {
        'sinhala': 'ද සිල්වා',
        'transliterations': ['de silva', 'desilva', 'de sylva', 'desylva', 'silva']
    },
    'dharmasena': {
        'sinhala': 'ධර්මසේන',
        'transliterations': ['dharmasena', 'dharmasenah', 'darmasena', 'dharmsena']
    },
    'dissanayake': {
        'sinhala': 'දිසානායක',
        'transliterations': ['dissanayake', 'disanayake', 'dissanayaka', 'disanayaka']
    },
    
    # E surnames
    'ekanayake': {
        'sinhala': 'ඒකනායක',
        'transliterations': ['ekanayake', 'ekanayaka', 'ekenayake', 'ekaanayake']
    },
    
    # F surnames
    'fernando': {
        'sinhala': 'ප්‍රනාන්දු',
        'transliterations': ['fernando', 'fernandoh', 'frenando', 'fernandu']
    },
    'fonseka': {
        'sinhala': 'ෆොන්සේකා',
        'transliterations': ['fonseka', 'fonsekah', 'fonseca', 'fonsecca']
    },
    
    # G surnames
    'gunasekara': {
        'sinhala': 'ගුණසේකර',
        'transliterations': ['gunasekara', 'gunasekera', 'gunasekra', 'gunesekarah']
    },
    'gunawardena': {
        'sinhala': 'ගුණවර්ධන',
        'transliterations': ['gunawardena', 'gunawardana', 'gunewardene', 'gunawardene']
    },
    
    # H surnames
    'herath': {
        'sinhala': 'හේරත්',
        'transliterations': ['herath', 'herat', 'heraath', 'herrath']
    },
    
    # J surnames
    'jayasinghe': {
        'sinhala': 'ජයසිංහ',
        'transliterations': ['jayasinghe', 'jayasinha', 'jayasinge', 'jeyasinha']
    },
    'jayasuriya': {
        'sinhala': 'ජයසූරිය',
        'transliterations': ['jayasuriya', 'jayasooriya', 'jeyasuriya', 'jayasuryia']
    },
    'jayawardena': {
        'sinhala': 'ජයවර්ධන',
        'transliterations': ['jayawardena', 'jayawardana', 'jayewardene', 'jayawardene']
    },
    
    # K surnames
    'karunaratne': {
        'sinhala': 'කරුණාරත්න',
        'transliterations': ['karunaratne', 'karunaratna', 'karunaaratne', 'karunaratney']
    },
    'kumarasinghe': {
        'sinhala': 'කුමාරසිංහ',
        'transliterations': ['kumarasinghe', 'kumarasinga', 'kumarasinhe', 'kumarasinha']
    },
    
    # L surnames
    'liyanage': {
        'sinhala': 'ලියනගේ',
        'transliterations': ['liyanage', 'liyanagey', 'liyanagae', 'liyenage']
    },
    
    # M surnames
    'mendis': {
        'sinhala': 'මෙන්ඩිස්',
        'transliterations': ['mendis', 'mendes', 'mandis', 'mendiss']
    },
    'munasinghe': {
        'sinhala': 'මුණසිංහ',
        'transliterations': ['munasinghe', 'munasinga', 'munasinhge', 'munasingha']
    },
    
    # N surnames
    'nanayakkara': {
        'sinhala': 'නානායක්කාර',
        'transliterations': ['nanayakkara', 'nanayakara', 'nanayakkarah', 'nenayakkara']
    },
    
    # P surnames
    'perera': {
        'sinhala': 'පෙරේරා',
        'transliterations': ['perera', 'pererah', 'parera', 'perira']
    },
    'pieris': {
        'sinhala': 'පීරිස්',
        'transliterations': ['pieris', 'peiris', 'pieries', 'peeries']
    },
    
    # R surnames
    'rajakaruna': {
        'sinhala': 'රාජකරුණා',
        'transliterations': ['rajakaruna', 'rajekaruna', 'rajakrunah', 'rajakaruuna']
    },
    'rajapaksa': {
        'sinhala': 'රාජපක්ෂ',
        'transliterations': ['rajapaksa', 'rajapaksha', 'rajapakse', 'rajapaksha']
    },
    'ranasinghe': {
        'sinhala': 'රණසිංහ',
        'transliterations': ['ranasinghe', 'ranasinha', 'ranasingha', 'ranasinhe']
    },
    'rathnayake': {
        'sinhala': 'රත්නායක',
        'transliterations': ['rathnayake', 'ratnayaka', 'ratnayake', 'rathnaayake']
    },
    
    # S surnames
    'samarasinghe': {
        'sinhala': 'සමරසිංහ',
        'transliterations': ['samarasinghe', 'samarasinhe', 'samarasinha', 'samarasinge']
    },
    'senanayake': {
        'sinhala': 'සේනානායක',
        'transliterations': ['senanayake', 'senanayaka', 'sennanayake', 'senaanayake']
    },
    'silva': {
        'sinhala': 'සිල්වා',
        'transliterations': ['silva', 'sylva', 'silvah', 'silvaa']
    },
    
    # W surnames
    'wickramasinghe': {
        'sinhala': 'වික්‍රමසිංහ',
        'transliterations': ['wickramasinghe', 'wickremasinghe', 'wikramasinghe', 'wickramasinha']
    },
    'wijesinghe': {
        'sinhala': 'විජේසිංහ',
        'transliterations': ['wijesinghe', 'wijesinha', 'vijesinha', 'wijesinge']
    },
    'wijewardena': {
        'sinhala': 'විජේවර්ධන',
        'transliterations': ['wijewardena', 'wijewardana', 'vijewardena', 'wijewardene']
    },
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_name_variants(name: str) -> Optional[Dict[str, any]]:
    """
    Get all transliteration variants for a given name.
    
    Searches both first names and surnames for the given name.
    The search is case-insensitive and checks all known transliterations.
    
    Args:
        name: The name to look up (in any known transliteration)
    
    Returns:
        Dict with 'sinhala' and 'transliterations' if found, None otherwise
    
    Example:
        >>> get_name_variants('dushan')
        {'sinhala': 'දුෂාන්', 'transliterations': ['dushan', 'dushaan', ...]}
        
        >>> get_name_variants('unknown')
        None
    """
    name_lower = name.lower().strip()
    
    # Search in first names
    for key, value in SINHALA_FIRST_NAMES.items():
        if name_lower == key or name_lower in [t.lower() for t in value['transliterations']]:
            return value
    
    # Search in surnames
    for key, value in SINHALA_SURNAMES.items():
        if name_lower == key.replace('_', ' ') or name_lower in [t.lower() for t in value['transliterations']]:
            return value
    
    return None


def get_all_name_variants(name: str) -> List[str]:
    """
    Get all possible transliteration variants for a name.
    
    Args:
        name: The name to look up
    
    Returns:
        List of all known transliterations, or empty list if not found
    
    Example:
        >>> get_all_name_variants('perera')
        ['perera', 'pererah', 'parera', 'perira']
    """
    result = get_name_variants(name)
    if result:
        return result['transliterations']
    return []


def get_sinhala_form(name: str) -> Optional[str]:
    """
    Get the Sinhala Unicode form of a romanized name.
    
    Args:
        name: The romanized name to look up
    
    Returns:
        The name in Sinhala script, or None if not found
    
    Example:
        >>> get_sinhala_form('perera')
        'පෙරේරා'
    """
    result = get_name_variants(name)
    if result:
        return result['sinhala']
    return None


def is_known_name(name: str) -> bool:
    """
    Check if a name is in the dictionary.
    
    Args:
        name: The name to check
    
    Returns:
        True if the name is known, False otherwise
    
    Example:
        >>> is_known_name('perera')
        True
        >>> is_known_name('unknown')
        False
    """
    return get_name_variants(name) is not None


def get_all_first_names() -> List[str]:
    """
    Get a list of all known first names.
    
    Returns:
        List of all first name keys in the dictionary
    """
    return list(SINHALA_FIRST_NAMES.keys())


def get_all_surnames() -> List[str]:
    """
    Get a list of all known surnames.
    
    Returns:
        List of all surname keys in the dictionary
    """
    return list(SINHALA_SURNAMES.keys())
