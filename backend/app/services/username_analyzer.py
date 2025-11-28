# =============================================================================
# USERNAME ANALYZER SERVICE
# =============================================================================
# Analyzes usernames to generate platform URLs, variations, and detect patterns.
# Helps identify potential impersonation or fake accounts.
# =============================================================================

"""
Username Analyzer Service

This module provides username analysis capabilities:
- Generate platform-specific profile URLs (Facebook, Instagram, X, LinkedIn, TikTok, YouTube)
- Generate username variations for impersonation detection
- Analyze username patterns to identify suspicious characteristics

Example Usage:
    analyzer = UsernameAnalyzer()
    urls = analyzer.generate_platform_urls("john_doe")
    # Returns URLs for all supported platforms
    
    variations = analyzer.generate_variations("john_doe")
    # Returns: ["john_doe", "johndoe", "john_doe_", "_john_doe", "john_doe123", etc.]
"""

import re
from typing import List, Dict, Any


# =============================================================================
# USERNAME ANALYZER CLASS
# =============================================================================

class UsernameAnalyzer:
    """
    Analyze usernames for digital footprint tracking.
    
    This class provides methods to:
    1. Generate profile URLs for major social platforms
    2. Create username variations that might be used for impersonation
    3. Analyze username patterns for suspicious characteristics
    
    Attributes:
        PLATFORMS: Dictionary of supported platforms and their URL templates
        SUSPICIOUS_PATTERNS: List of regex patterns indicating suspicious usernames
    """
    
    # -------------------------------------------------------------------------
    # SUPPORTED PLATFORMS CONFIGURATION
    # -------------------------------------------------------------------------
    # URL templates for each supported social media platform
    # {username} placeholder is replaced with the actual username
    # -------------------------------------------------------------------------
    PLATFORMS = {
        "facebook": {
            "name": "Facebook",
            "url_template": "https://www.facebook.com/{username}",
            "icon": "facebook"
        },
        "instagram": {
            "name": "Instagram",
            "url_template": "https://www.instagram.com/{username}",
            "icon": "instagram"
        },
        "twitter": {
            "name": "X (Twitter)",
            "url_template": "https://twitter.com/{username}",
            "icon": "twitter"
        },
        "linkedin": {
            "name": "LinkedIn",
            "url_template": "https://www.linkedin.com/in/{username}",
            "icon": "linkedin"
        },
        "tiktok": {
            "name": "TikTok",
            "url_template": "https://www.tiktok.com/@{username}",
            "icon": "tiktok"
        },
        "youtube": {
            "name": "YouTube",
            "url_template": "https://www.youtube.com/@{username}",
            "icon": "youtube"
        }
    }
    
    # -------------------------------------------------------------------------
    # SUSPICIOUS PATTERN DEFINITIONS
    # -------------------------------------------------------------------------
    # Patterns that might indicate fake or impersonation accounts
    # Each pattern has a name and regex for detection
    # -------------------------------------------------------------------------
    SUSPICIOUS_PATTERNS = [
        {
            "name": "ends_with_numbers",
            "pattern": r".*\d{3,}$",
            "description": "Username ends with 3+ consecutive numbers"
        },
        {
            "name": "random_numbers_letters",
            "pattern": r"^[a-z]+\d+[a-z]+\d+",
            "description": "Alternating random letters and numbers"
        },
        {
            "name": "repeated_chars",
            "pattern": r"(.)\1{3,}",
            "description": "Character repeated 4+ times"
        },
        {
            "name": "excessive_underscores",
            "pattern": r"_{2,}",
            "description": "Multiple consecutive underscores"
        },
        {
            "name": "real_prefix",
            "pattern": r"^(real|official|the_?real)",
            "description": "Starts with 'real' or 'official' prefix"
        },
        {
            "name": "impersonation_suffix",
            "pattern": r"(_official|_real|\.official|\.real)$",
            "description": "Ends with 'official' or 'real' suffix"
        }
    ]
    
    def __init__(self):
        """
        Initialize the Username Analyzer.
        
        Compiles regex patterns for better performance on repeated use.
        """
        # Compile suspicious patterns for efficient matching
        self._compiled_patterns = [
            {
                "name": p["name"],
                "pattern": re.compile(p["pattern"], re.IGNORECASE),
                "description": p["description"]
            }
            for p in self.SUSPICIOUS_PATTERNS
        ]
    
    # =========================================================================
    # PLATFORM URL GENERATION
    # =========================================================================
    
    def generate_platform_urls(self, username: str) -> Dict[str, Dict[str, str]]:
        """
        Generate profile URLs for all supported platforms.
        
        Creates direct links to the user's potential profile on each
        major social media platform.
        
        Args:
            username: The username to generate URLs for
        
        Returns:
            Dict[str, Dict[str, str]]: Dictionary with platform IDs as keys,
                                       containing name, url, and icon
        
        Example:
            >>> analyzer.generate_platform_urls("john_doe")
            {
                'facebook': {
                    'name': 'Facebook',
                    'url': 'https://www.facebook.com/john_doe',
                    'icon': 'facebook'
                },
                ...
            }
        """
        if not username:
            return {}
        
        # Clean username - remove @ if present
        clean_username = username.lstrip('@').strip()
        
        urls = {}
        for platform_id, platform_info in self.PLATFORMS.items():
            urls[platform_id] = {
                "name": platform_info["name"],
                "url": platform_info["url_template"].format(username=clean_username),
                "icon": platform_info["icon"]
            }
        
        return urls
    
    def generate_platform_url(self, username: str, platform: str) -> str:
        """
        Generate profile URL for a specific platform.
        
        Args:
            username: The username to generate URL for
            platform: Platform ID (facebook, instagram, etc.)
        
        Returns:
            str: Profile URL or empty string if platform not supported
        
        Example:
            >>> analyzer.generate_platform_url("john_doe", "instagram")
            'https://www.instagram.com/john_doe'
        """
        if not username or platform not in self.PLATFORMS:
            return ""
        
        clean_username = username.lstrip('@').strip()
        return self.PLATFORMS[platform]["url_template"].format(username=clean_username)
    
    # =========================================================================
    # USERNAME VARIATION GENERATION
    # =========================================================================
    
    def generate_variations(self, username: str) -> List[str]:
        """
        Generate common variations of a username.
        
        Creates variations that might be used by impersonators or
        that users might use across different platforms:
        - Original username
        - Without underscores/dots
        - With underscores replaced by dots and vice versa
        - With number suffixes (common birth years, random)
        - With leading/trailing underscores
        - With 'real' or 'official' prefixes/suffixes
        
        Args:
            username: The original username
        
        Returns:
            List[str]: List of unique username variations
        
        Example:
            >>> analyzer.generate_variations("john_doe")
            ['john_doe', 'johndoe', 'john.doe', '_john_doe', 
             'john_doe_', 'john_doe123', 'real_john_doe', ...]
        """
        if not username:
            return []
        
        # Clean and normalize username
        clean_username = username.lstrip('@').strip().lower()
        
        variations = set()
        
        # ---------------------------------------------------------------------
        # Original and basic variations
        # ---------------------------------------------------------------------
        variations.add(clean_username)
        
        # Remove all underscores
        no_underscore = clean_username.replace('_', '')
        variations.add(no_underscore)
        
        # Remove all dots
        no_dots = clean_username.replace('.', '')
        variations.add(no_dots)
        
        # Replace underscores with dots
        underscore_to_dot = clean_username.replace('_', '.')
        variations.add(underscore_to_dot)
        
        # Replace dots with underscores
        dot_to_underscore = clean_username.replace('.', '_')
        variations.add(dot_to_underscore)
        
        # ---------------------------------------------------------------------
        # Underscore position variations
        # ---------------------------------------------------------------------
        # Leading underscore
        variations.add(f"_{clean_username}")
        
        # Trailing underscore
        variations.add(f"{clean_username}_")
        
        # Both leading and trailing
        variations.add(f"_{clean_username}_")
        
        # Double leading underscore (common on some platforms)
        variations.add(f"__{clean_username}")
        
        # ---------------------------------------------------------------------
        # Number suffix variations
        # ---------------------------------------------------------------------
        # Common number suffixes (birth years 1990-2005 range)
        common_years = ["90", "91", "92", "93", "94", "95", "96", 
                       "97", "98", "99", "00", "01", "02", "03", "04", "05"]
        
        # Simple number suffixes
        for suffix in ["1", "2", "12", "123", "007", "69", "420"]:
            variations.add(f"{clean_username}{suffix}")
            variations.add(f"{no_underscore}{suffix}")
        
        # Year suffixes (just a few to keep list manageable)
        for year in common_years[:5]:  # First 5 years
            variations.add(f"{clean_username}{year}")
        
        # ---------------------------------------------------------------------
        # Impersonation-style variations
        # ---------------------------------------------------------------------
        # Real/Official prefixes (used by impersonators or verified accounts)
        variations.add(f"real_{clean_username}")
        variations.add(f"real{no_underscore}")
        variations.add(f"the_real_{clean_username}")
        variations.add(f"official_{clean_username}")
        
        # Real/Official suffixes
        variations.add(f"{clean_username}_real")
        variations.add(f"{clean_username}_official")
        variations.add(f"{clean_username}.official")
        
        # ---------------------------------------------------------------------
        # Clean up and return unique variations
        # ---------------------------------------------------------------------
        # Remove empty strings and the original if it somehow got modified
        return sorted(list(variations - {''}))
    
    # =========================================================================
    # PATTERN ANALYSIS
    # =========================================================================
    
    def analyze_patterns(self, username: str) -> Dict[str, Any]:
        """
        Analyze username for suspicious patterns.
        
        Examines the username for characteristics that might indicate
        a fake account, auto-generated username, or impersonation attempt.
        
        Analysis includes:
        - Detection of suspicious patterns (see SUSPICIOUS_PATTERNS)
        - Number density (ratio of digits to total characters)
        - Username length assessment
        - Character composition breakdown
        
        Args:
            username: The username to analyze
        
        Returns:
            Dict[str, Any]: Analysis results including:
                - length: Username length
                - has_numbers: Boolean indicating presence of digits
                - has_underscores: Boolean indicating presence of underscores
                - has_dots: Boolean indicating presence of dots
                - number_density: Ratio of digits to total chars (0.0-1.0)
                - detected_patterns: List of suspicious patterns found
                - has_suspicious_patterns: Boolean indicating any suspicious patterns
        
        Example:
            >>> analyzer.analyze_patterns("john_doe123456")
            {
                'length': 14,
                'has_numbers': True,
                'has_underscores': True,
                'has_dots': False,
                'number_density': 0.43,
                'detected_patterns': ['ends_with_numbers'],
                'has_suspicious_patterns': True
            }
        """
        if not username:
            return {
                "length": 0,
                "has_numbers": False,
                "has_underscores": False,
                "has_dots": False,
                "number_density": 0.0,
                "detected_patterns": [],
                "has_suspicious_patterns": False
            }
        
        clean_username = username.lstrip('@').strip()
        
        # ---------------------------------------------------------------------
        # Basic character analysis
        # ---------------------------------------------------------------------
        length = len(clean_username)
        digit_count = sum(1 for c in clean_username if c.isdigit())
        letter_count = sum(1 for c in clean_username if c.isalpha())
        
        # Calculate number density
        number_density = digit_count / length if length > 0 else 0.0
        
        # Check for specific characters
        has_numbers = digit_count > 0
        has_underscores = '_' in clean_username
        has_dots = '.' in clean_username
        
        # ---------------------------------------------------------------------
        # Suspicious pattern detection
        # ---------------------------------------------------------------------
        detected_patterns = []
        
        for pattern_info in self._compiled_patterns:
            if pattern_info["pattern"].search(clean_username):
                detected_patterns.append({
                    "name": pattern_info["name"],
                    "description": pattern_info["description"]
                })
        
        # ---------------------------------------------------------------------
        # Build and return results
        # ---------------------------------------------------------------------
        return {
            "length": length,
            "has_numbers": has_numbers,
            "has_underscores": has_underscores,
            "has_dots": has_dots,
            "number_density": round(number_density, 2),
            "letter_count": letter_count,
            "digit_count": digit_count,
            "detected_patterns": detected_patterns,
            "has_suspicious_patterns": len(detected_patterns) > 0
        }
    
    def is_likely_impersonation(self, original: str, candidate: str) -> bool:
        """
        Check if a candidate username might be impersonating the original.
        
        Compares two usernames to determine if the candidate might be
        attempting to impersonate the original through similar naming.
        
        Args:
            original: The original/authentic username
            candidate: The candidate username to check
        
        Returns:
            bool: True if candidate might be impersonating original
        
        Example:
            >>> analyzer.is_likely_impersonation("john_doe", "real_john_doe")
            True
        """
        if not original or not candidate:
            return False
        
        orig_clean = original.lstrip('@').strip().lower()
        cand_clean = candidate.lstrip('@').strip().lower()
        
        # Exact match isn't impersonation
        if orig_clean == cand_clean:
            return False
        
        # Check if candidate contains original
        if orig_clean in cand_clean:
            return True
        
        # Check if original contains candidate (opposite direction)
        if cand_clean in orig_clean:
            return True
        
        # Check stripped versions (no underscores/dots)
        orig_stripped = orig_clean.replace('_', '').replace('.', '')
        cand_stripped = cand_clean.replace('_', '').replace('.', '')
        
        if orig_stripped == cand_stripped:
            return True
        
        return False


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

_default_analyzer = UsernameAnalyzer()


def generate_platform_urls(username: str) -> Dict[str, Dict[str, str]]:
    """Module-level convenience function for URL generation."""
    return _default_analyzer.generate_platform_urls(username)


def generate_variations(username: str) -> List[str]:
    """Module-level convenience function for variation generation."""
    return _default_analyzer.generate_variations(username)


def analyze_patterns(username: str) -> Dict[str, Any]:
    """Module-level convenience function for pattern analysis."""
    return _default_analyzer.analyze_patterns(username)
