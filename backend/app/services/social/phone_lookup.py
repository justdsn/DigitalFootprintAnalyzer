# =============================================================================
# PHONE NUMBER LOOKUP SERVICE
# =============================================================================
# Sri Lankan phone number validation and carrier identification.
# Supports mobile numbers (07X) and landline formats.
# =============================================================================

"""
Phone Number Lookup Service

This module provides Sri Lankan phone number analysis:
- Validate mobile and landline number formats
- Identify mobile carriers (Dialog, Mobitel, Airtel, Hutch)
- Identify landline area codes (Colombo, Kandy, Galle, etc.)
- Normalize to E.164 format (+94XXXXXXXXX)
- Format for display (local and international)

Example Usage:
    lookup = PhoneNumberLookup()
    result = lookup.lookup("0771234567")
    # Returns: {
    #     "valid": True,
    #     "type": "mobile",
    #     "carrier": "Dialog",
    #     "e164_format": "+94771234567",
    #     ...
    # }
"""

import re
from typing import Dict, Optional, Any


class PhoneNumberLookup:
    """
    Sri Lankan phone number validation and carrier lookup.
    
    This class provides methods to:
    1. Validate Sri Lankan phone number formats
    2. Identify mobile carriers from prefix
    3. Identify landline area codes
    4. Normalize numbers to E.164 format
    5. Format numbers for display
    
    Attributes:
        MOBILE_PREFIXES: Dict mapping mobile prefixes to carriers
        LANDLINE_CODES: Dict mapping area codes to cities/regions
    """
    
    # -------------------------------------------------------------------------
    # MOBILE CARRIER PREFIXES
    # -------------------------------------------------------------------------
    # Sri Lankan mobile prefixes and their carriers
    # All mobile numbers start with 07X
    # -------------------------------------------------------------------------
    MOBILE_PREFIXES = {
        "070": "Dialog",
        "074": "Dialog",
        "076": "Dialog",
        "077": "Dialog",
        "071": "Mobitel",
        "075": "Airtel",
        "072": "Hutch",
        "078": "Hutch"
    }
    
    # -------------------------------------------------------------------------
    # LANDLINE AREA CODES
    # -------------------------------------------------------------------------
    # Sri Lankan landline area codes and their regions
    # -------------------------------------------------------------------------
    LANDLINE_CODES = {
        "011": "Colombo",
        "021": "Jaffna",
        "023": "Mannar",
        "024": "Vavuniya",
        "025": "Anuradhapura",
        "026": "Trincomalee",
        "027": "Polonnaruwa",
        "031": "Negombo",
        "032": "Chilaw",
        "033": "Gampaha",
        "034": "Kalutara",
        "035": "Kegalle",
        "036": "Avissawella",
        "037": "Kurunegala",
        "038": "Panadura",
        "041": "Matara",
        "045": "Ratnapura",
        "047": "Hambantota",
        "051": "Hatton",
        "052": "Nuwara Eliya",
        "054": "Nawalapitiya",
        "055": "Badulla",
        "057": "Bandarawela",
        "063": "Ampara",
        "065": "Batticaloa",
        "066": "Matale",
        "067": "Kalmunai",
        "081": "Kandy",
        "091": "Galle"
    }
    
    def __init__(self):
        """Initialize the Phone Number Lookup service."""
        pass
    
    def _clean_number(self, phone: str) -> str:
        """
        Clean a phone number by removing non-digit characters.
        
        Preserves the leading + if present.
        
        Args:
            phone: Raw phone number input
        
        Returns:
            str: Cleaned phone number with only digits and optional +
        
        Example:
            >>> lookup._clean_number("+94 77-123 4567")
            '+94771234567'
        """
        if not phone:
            return ""
        
        # Preserve + at the start
        has_plus = phone.strip().startswith('+')
        
        # Remove all non-digit characters
        cleaned = re.sub(r'[^\d]', '', phone)
        
        # Add back + if it was there
        if has_plus:
            cleaned = '+' + cleaned
        
        return cleaned
    
    def _validate(self, phone: str) -> Dict[str, Any]:
        """
        Validate a Sri Lankan phone number format.
        
        Checks if the number matches valid mobile or landline patterns.
        
        Args:
            phone: Cleaned phone number
        
        Returns:
            Dict with validation results:
                - valid: Boolean
                - type: "mobile", "landline", or None
                - prefix: The identified prefix
                - error: Error message if invalid
        """
        if not phone:
            return {
                "valid": False,
                "type": None,
                "prefix": None,
                "error": "Phone number is required"
            }
        
        # Clean the number
        cleaned = self._clean_number(phone)
        
        # Remove country code if present
        if cleaned.startswith('+94'):
            cleaned = '0' + cleaned[3:]
        elif cleaned.startswith('0094'):
            cleaned = '0' + cleaned[4:]
        elif cleaned.startswith('94') and len(cleaned) == 11:
            cleaned = '0' + cleaned[2:]
        
        # Check mobile format: 07XXXXXXXX (10 digits starting with 07)
        if re.match(r'^07[0-8]\d{7}$', cleaned):
            prefix = cleaned[:3]
            if prefix in self.MOBILE_PREFIXES:
                return {
                    "valid": True,
                    "type": "mobile",
                    "prefix": prefix,
                    "error": None,
                    "normalized": cleaned
                }
            else:
                return {
                    "valid": False,
                    "type": "mobile",
                    "prefix": prefix,
                    "error": f"Unknown mobile prefix: {prefix}"
                }
        
        # Check landline format: 0XXXXXXXX (9-10 digits starting with 0)
        if re.match(r'^0[1-9]\d{7,8}$', cleaned):
            prefix = cleaned[:3]
            if prefix in self.LANDLINE_CODES:
                return {
                    "valid": True,
                    "type": "landline",
                    "prefix": prefix,
                    "error": None,
                    "normalized": cleaned
                }
            else:
                # Could still be valid landline with unknown area code
                return {
                    "valid": True,
                    "type": "landline",
                    "prefix": prefix,
                    "error": None,
                    "normalized": cleaned
                }
        
        return {
            "valid": False,
            "type": None,
            "prefix": None,
            "error": "Invalid Sri Lankan phone number format"
        }
    
    def _normalize_e164(self, phone: str) -> Optional[str]:
        """
        Normalize a phone number to E.164 format.
        
        E.164 format: +94XXXXXXXXX
        
        Args:
            phone: Phone number in any format
        
        Returns:
            str: E.164 formatted number or None if invalid
        
        Example:
            >>> lookup._normalize_e164("0771234567")
            '+94771234567'
        """
        validation = self._validate(phone)
        
        if not validation.get("valid"):
            return None
        
        normalized = validation.get("normalized", "")
        
        # Remove leading 0 and add +94
        if normalized.startswith('0'):
            return '+94' + normalized[1:]
        
        return None
    
    def _identify_carrier(self, phone: str) -> Dict[str, Any]:
        """
        Identify the carrier/region for a phone number.
        
        Args:
            phone: Phone number
        
        Returns:
            Dict with carrier/region information:
                - carrier: Carrier name for mobile, region for landline
                - prefix: The identified prefix
        """
        validation = self._validate(phone)
        
        if not validation.get("valid"):
            return {
                "carrier": None,
                "prefix": None
            }
        
        prefix = validation.get("prefix")
        phone_type = validation.get("type")
        
        if phone_type == "mobile":
            carrier = self.MOBILE_PREFIXES.get(prefix)
            return {
                "carrier": carrier,
                "prefix": prefix
            }
        elif phone_type == "landline":
            region = self.LANDLINE_CODES.get(prefix)
            return {
                "carrier": region,  # For landlines, "carrier" is the region
                "prefix": prefix
            }
        
        return {
            "carrier": None,
            "prefix": prefix
        }
    
    def lookup(self, phone: str) -> Dict[str, Any]:
        """
        Perform a complete lookup on a Sri Lankan phone number.
        
        Validates the number, identifies carrier/region, and formats
        for display.
        
        Args:
            phone: Phone number in any format
        
        Returns:
            Dict containing:
                - original: Original input
                - valid: Boolean indicating validity
                - type: "mobile" or "landline" or None
                - carrier: Carrier name (mobile) or region (landline)
                - e164_format: E.164 formatted number
                - local_format: Local display format (0XX-XXX-XXXX)
                - international_format: International format (+94 XX XXX XXXX)
                - error: Error message if invalid
        
        Example:
            >>> lookup.lookup("0771234567")
            {
                'original': '0771234567',
                'valid': True,
                'type': 'mobile',
                'carrier': 'Dialog',
                'e164_format': '+94771234567',
                'local_format': '077-123-4567',
                'international_format': '+94 77 123 4567',
                'error': None
            }
        """
        result = {
            "original": phone,
            "valid": False,
            "type": None,
            "carrier": None,
            "e164_format": None,
            "local_format": None,
            "international_format": None,
            "error": None
        }
        
        if not phone:
            result["error"] = "Phone number is required"
            return result
        
        # Validate
        validation = self._validate(phone)
        
        if not validation.get("valid"):
            result["error"] = validation.get("error")
            return result
        
        result["valid"] = True
        result["type"] = validation.get("type")
        
        # Identify carrier/region
        carrier_info = self._identify_carrier(phone)
        result["carrier"] = carrier_info.get("carrier")
        
        # Format numbers
        normalized = validation.get("normalized", "")
        
        # E.164 format
        result["e164_format"] = self._normalize_e164(phone)
        
        # Local format: 0XX-XXX-XXXX for mobile, varies for landline
        if result["type"] == "mobile" and len(normalized) == 10:
            result["local_format"] = f"{normalized[:3]}-{normalized[3:6]}-{normalized[6:]}"
        elif result["type"] == "landline" and len(normalized) >= 9:
            if len(normalized) == 9:
                result["local_format"] = f"{normalized[:3]}-{normalized[3:6]}-{normalized[6:]}"
            else:
                result["local_format"] = f"{normalized[:3]}-{normalized[3:6]}-{normalized[6:]}"
        
        # International format: +94 XX XXX XXXX
        if result["e164_format"]:
            e164 = result["e164_format"]
            if len(e164) == 12:  # +94 + 9 digits
                result["international_format"] = f"{e164[:3]} {e164[3:5]} {e164[5:8]} {e164[8:]}"
        
        return result
    
    def get_all_carriers(self) -> Dict[str, str]:
        """
        Get all known mobile carrier prefixes.
        
        Returns:
            Dict mapping prefixes to carrier names
        """
        return dict(self.MOBILE_PREFIXES)
    
    def get_all_area_codes(self) -> Dict[str, str]:
        """
        Get all known landline area codes.
        
        Returns:
            Dict mapping area codes to region names
        """
        return dict(self.LANDLINE_CODES)


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

_default_lookup = PhoneNumberLookup()


def lookup(phone: str) -> Dict[str, Any]:
    """Module-level convenience function for phone lookup."""
    return _default_lookup.lookup(phone)


def validate(phone: str) -> Dict[str, Any]:
    """Module-level convenience function for phone validation."""
    return _default_lookup._validate(phone)


def normalize_e164(phone: str) -> Optional[str]:
    """Module-level convenience function for E.164 normalization."""
    return _default_lookup._normalize_e164(phone)
