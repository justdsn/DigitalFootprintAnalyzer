# =============================================================================
# IDENTIFIER DETECTOR
# =============================================================================
# Detects the type of identifier (email, username, name, phone).
# =============================================================================

"""
Identifier Detector

Automatically detects whether an input string is:
- Email address
- Username
- Full name
- Phone number
"""

import re
from typing import Literal

IdentifierType = Literal["email", "username", "name", "phone"]


class IdentifierDetector:
    """
    Detect identifier type from input string.
    """
    
    @staticmethod
    def detect(identifier: str) -> IdentifierType:
        """
        Detect the type of identifier.
        
        Args:
            identifier: Input string
        
        Returns:
            Identifier type: "email", "username", "name", or "phone"
        """
        identifier = identifier.strip()
        
        # Email detection
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, identifier):
            return "email"
        
        # Phone detection (Sri Lankan and international formats)
        cleaned = identifier.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # Sri Lankan patterns
        sri_lankan_patterns = [
            r'^07\d{8}$',           # 07XXXXXXXX
            r'^\+947\d{8}$',        # +947XXXXXXXX
            r'^947\d{8}$',          # 947XXXXXXXX
            r'^00947\d{8}$',        # 00947XXXXXXXX
            r'^0\d{9}$',            # 0XXXXXXXXX
        ]
        
        for pattern in sri_lankan_patterns:
            if re.match(pattern, cleaned):
                return "phone"
        
        # International phone
        digit_count = sum(1 for c in cleaned if c.isdigit())
        if len(cleaned) >= 7 and digit_count / len(cleaned) >= 0.7:
            if cleaned.startswith('+') or cleaned[0].isdigit():
                return "phone"
        
        # Name detection (contains space and mostly letters)
        if ' ' in identifier:
            letter_count = sum(1 for c in identifier if c.isalpha() or c.isspace())
            if letter_count / len(identifier) >= 0.8:
                parts = [p for p in identifier.split() if p]  # Filter empty parts first
                if len(parts) >= 2 and all(part[0].isalpha() for part in parts):
                    return "name"
        
        # Default to username
        return "username"
