# =============================================================================
# PYDANTIC SCHEMAS
# =============================================================================
# Request and response models for the API endpoints.
# Uses Pydantic for validation, serialization, and OpenAPI documentation.
# =============================================================================

"""
Pydantic Schema Definitions

This module defines all request and response models for the API:
- AnalyzeRequest/Response: Main analysis endpoint
- PIIExtractRequest/Response: PII extraction endpoint
- UsernameAnalyzeRequest/Response: Username analysis endpoint
- HealthResponse: Health check endpoint

Each model includes:
- Field validation rules
- Documentation for OpenAPI schema
- Example values for documentation
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Literal
from enum import Enum
import re


# =============================================================================
# ENUMS
# =============================================================================

class IdentifierType(str, Enum):
    """
    Enum for identifier types that can be searched.
    """
    USERNAME = "username"
    EMAIL = "email"
    PHONE = "phone"
    NAME = "name"


# =============================================================================
# HEALTH CHECK MODELS
# =============================================================================

class HealthResponse(BaseModel):
    """
    Response model for health check endpoint.
    
    Used by monitoring systems and load balancers to verify
    the API is operational.
    
    Attributes:
        status: Current health status ("healthy" or "unhealthy")
        version: API version string
        services: Dict of service names and their statuses
    
    Example:
        {
            "status": "healthy",
            "version": "1.0.0",
            "services": {
                "pii_extractor": "operational",
                "ner_engine": "operational"
            }
        }
    """
    status: str = Field(
        ...,
        description="Current health status",
        examples=["healthy"]
    )
    version: str = Field(
        ...,
        description="API version",
        examples=["1.0.0"]
    )
    services: Dict[str, str] = Field(
        default_factory=dict,
        description="Status of individual services"
    )


# =============================================================================
# MAIN ANALYSIS MODELS
# =============================================================================

class AnalyzeRequest(BaseModel):
    """
    Request model for the main analysis endpoint.
    
    Contains a single identifier for digital footprint analysis.
    The system auto-detects the type (username, email, phone, or name).
    
    Attributes:
        identifier: The value to search/analyze (required)
        identifier_type: Optional - if not provided, will be auto-detected
    
    Example:
        {
            "identifier": "john_doe"
        }
    """
    identifier: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="The identifier value to analyze",
        examples=["john_doe", "john@example.com", "0771234567", "John Perera"]
    )
    identifier_type: Optional[IdentifierType] = Field(
        default=None,
        description="Type of identifier - auto-detected if not provided",
        examples=["username", "email", "phone", "name"]
    )
    
    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        """
        Validate and clean the identifier.
        
        Rules:
        - Cannot be empty or whitespace only
        - Trims whitespace
        """
        if not v or not v.strip():
            raise ValueError("Identifier cannot be empty")
        return v.strip()
    
    def get_as_username(self) -> Optional[str]:
        """Get the identifier as username if type is username."""
        if self.identifier_type == IdentifierType.USERNAME:
            return self.identifier.lstrip('@')
        return None
    
    def get_as_email(self) -> Optional[str]:
        """Get the identifier as email if type is email."""
        if self.identifier_type == IdentifierType.EMAIL:
            return self.identifier.lower()
        return None
    
    def get_as_phone(self) -> Optional[str]:
        """Get the identifier as phone if type is phone."""
        if self.identifier_type == IdentifierType.PHONE:
            return self.identifier
        return None
    
    def get_as_name(self) -> Optional[str]:
        """Get the identifier as name if type is name."""
        if self.identifier_type == IdentifierType.NAME:
            return self.identifier
        return None


class PlatformUrl(BaseModel):
    """
    Model for a single platform URL.
    
    Attributes:
        name: Platform display name
        url: Direct URL to the profile
        icon: Icon identifier for UI display
    """
    name: str
    url: str
    icon: str


class PatternAnalysis(BaseModel):
    """
    Model for username pattern analysis results.
    
    Attributes:
        length: Username length
        has_numbers: Whether username contains digits
        has_underscores: Whether username contains underscores
        has_dots: Whether username contains dots
        number_density: Ratio of digits to total characters
        detected_patterns: List of suspicious patterns found
        has_suspicious_patterns: Whether any suspicious patterns detected
    """
    length: int
    has_numbers: bool
    has_underscores: bool
    has_dots: bool
    number_density: float
    letter_count: Optional[int] = None
    digit_count: Optional[int] = None
    detected_patterns: List[Dict[str, str]] = []
    has_suspicious_patterns: bool


class NEREntities(BaseModel):
    """
    Model for NER extraction results.
    
    Attributes:
        persons: List of person names found
        locations: List of locations found
        organizations: List of organizations found
    """
    persons: List[str] = []
    locations: List[str] = []
    organizations: List[str] = []


class AnalyzeResponse(BaseModel):
    """
    Response model for the main analysis endpoint.
    
    Contains comprehensive analysis results including platform URLs,
    username variations, PII extraction, NER results, and risk assessment.
    
    Attributes:
        identifier: The analyzed identifier value
        identifier_type: Detected/provided identifier type
        platform_urls: Dict of platform URLs
        variations: List of username variations
        pattern_analysis: Analysis of username patterns
        extracted_pii: Extracted PII from inputs
        ner_entities: Named entities found
        risk_score: Calculated risk score (0-100)
        risk_level: Risk level (low/medium/high)
        recommendations: List of security recommendations
        processing_time_ms: Time taken to process (milliseconds)
    
    Example:
        {
            "identifier": "0771234567",
            "identifier_type": "phone",
            "risk_score": 45,
            "risk_level": "medium",
            ...
        }
    """
    identifier: str = Field(
        ...,
        description="The analyzed identifier"
    )
    identifier_type: str = Field(
        ...,
        description="Type of identifier (username, email, phone, name)"
    )
    platform_urls: Dict[str, Dict[str, str]] = Field(
        ...,
        description="URLs for each supported platform"
    )
    variations: List[str] = Field(
        ...,
        description="Generated username variations"
    )
    pattern_analysis: Dict[str, Any] = Field(
        ...,
        description="Username pattern analysis results"
    )
    extracted_pii: Dict[str, Any] = Field(
        ...,
        description="Extracted PII from provided inputs"
    )
    potential_exposures: List[Dict[str, Any]] = Field(
        default=[],
        description="List of potential exposure points where identifier may be found"
    )
    ner_entities: Dict[str, List[str]] = Field(
        ...,
        description="Named entities found (persons, locations, organizations)"
    )
    risk_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Risk score from 0 (low) to 100 (high)"
    )
    risk_level: str = Field(
        ...,
        description="Risk level category (low/medium/high)"
    )
    recommendations: List[str] = Field(
        ...,
        description="Security and privacy recommendations"
    )
    processing_time_ms: float = Field(
        ...,
        description="Processing time in milliseconds"
    )


# =============================================================================
# PII EXTRACTION MODELS
# =============================================================================

class PIIExtractRequest(BaseModel):
    """
    Request model for PII extraction endpoint.
    
    Attributes:
        text: Text to analyze for PII
    
    Example:
        {
            "text": "Contact me at john@example.com or call 0771234567"
        }
    """
    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Text to analyze for PII extraction",
        examples=["Contact me at john@example.com or call 0771234567"]
    )
    
    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate that text is not empty."""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        return v


class PIIExtractResponse(BaseModel):
    """
    Response model for PII extraction endpoint.
    
    Contains all extracted PII categorized by type.
    
    Attributes:
        text: Original input text (truncated if very long)
        emails: List of email addresses found
        phones: List of phone numbers found (E.164 format)
        urls: List of URLs found
        mentions: List of @mentions found
        ner_entities: Named entities found via NER
    
    Example:
        {
            "text": "Contact me at...",
            "emails": ["john@example.com"],
            "phones": ["+94771234567"],
            "urls": [],
            "mentions": [],
            "ner_entities": {...}
        }
    """
    text: str = Field(
        ...,
        description="Original input text"
    )
    emails: List[str] = Field(
        default_factory=list,
        description="Extracted email addresses"
    )
    phones: List[str] = Field(
        default_factory=list,
        description="Extracted phone numbers in E.164 format"
    )
    urls: List[str] = Field(
        default_factory=list,
        description="Extracted URLs"
    )
    mentions: List[str] = Field(
        default_factory=list,
        description="Extracted @mentions"
    )
    ner_entities: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Named entities from NER analysis"
    )


# =============================================================================
# USERNAME ANALYSIS MODELS
# =============================================================================

class UsernameAnalyzeRequest(BaseModel):
    """
    Request model for username analysis endpoint.
    
    Attributes:
        username: Username to analyze
    
    Example:
        {
            "username": "john_doe"
        }
    """
    username: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Username to analyze",
        examples=["john_doe"]
    )
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate and clean the username."""
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip().lstrip('@')


class UsernameAnalyzeResponse(BaseModel):
    """
    Response model for username analysis endpoint.
    
    Contains platform URLs, variations, and pattern analysis.
    
    Attributes:
        username: The analyzed username
        platform_urls: Dict of platform URLs
        variations: List of username variations
        pattern_analysis: Analysis of username patterns
    
    Example:
        {
            "username": "john_doe",
            "platform_urls": {...},
            "variations": ["john_doe", "johndoe", ...],
            "pattern_analysis": {...}
        }
    """
    username: str = Field(
        ...,
        description="The analyzed username"
    )
    platform_urls: Dict[str, Dict[str, str]] = Field(
        ...,
        description="URLs for each supported platform"
    )
    variations: List[str] = Field(
        ...,
        description="Generated username variations"
    )
    pattern_analysis: Dict[str, Any] = Field(
        ...,
        description="Username pattern analysis results"
    )


# =============================================================================
# TRANSLITERATION MODELS (Phase 2)
# =============================================================================

class TransliterateRequest(BaseModel):
    """
    Request model for Sinhala transliteration endpoint.
    
    Attributes:
        text: Sinhala text to transliterate
        include_variants: Whether to include spelling variants (default True)
    
    Example:
        {
            "text": "සුනිල් පෙරේරා",
            "include_variants": true
        }
    """
    text: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Sinhala text to transliterate",
        examples=["සුනිල් පෙරේරා", "කොළඹ"]
    )
    include_variants: bool = Field(
        default=True,
        description="Whether to include spelling variants"
    )
    
    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate that text is not empty."""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()


class TransliterateResponse(BaseModel):
    """
    Response model for Sinhala transliteration endpoint.
    
    Contains the original text, Sinhala detection result,
    and transliteration variants.
    
    Attributes:
        original: Original input text
        is_sinhala: Whether text contains Sinhala characters
        transliterations: Primary transliteration results
        variants: Spelling variants of transliterations
    
    Example:
        {
            "original": "සුනිල් පෙරේරා",
            "is_sinhala": true,
            "transliterations": ["sunil perera"],
            "variants": ["suneel perera", "sunil pereera"]
        }
    """
    original: str = Field(
        ...,
        description="Original input text"
    )
    is_sinhala: bool = Field(
        ...,
        description="Whether input contains Sinhala characters"
    )
    transliterations: List[str] = Field(
        default_factory=list,
        description="Primary transliteration results"
    )
    variants: List[str] = Field(
        default_factory=list,
        description="Spelling variants of transliterations"
    )


# =============================================================================
# CORRELATION MODELS (Phase 2)
# =============================================================================

class PlatformProfile(BaseModel):
    """
    Model for a social media platform profile.
    
    Contains profile information from a single platform
    for use in cross-platform correlation analysis.
    
    Attributes:
        platform: Platform name (e.g., "facebook", "twitter")
        username: Username on the platform
        name: Display name (optional)
        bio: Profile bio/description (optional)
        location: Location from profile (optional)
        email: Email address (optional)
        phone: Phone number (optional)
    
    Example:
        {
            "platform": "facebook",
            "username": "john_doe",
            "name": "John Doe",
            "bio": "Software developer",
            "location": "Colombo"
        }
    """
    platform: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Platform name (e.g., facebook, twitter, instagram)",
        examples=["facebook", "twitter", "instagram", "linkedin", "tiktok"]
    )
    username: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Username on the platform",
        examples=["john_doe", "@johndoe"]
    )
    name: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Display name on the platform"
    )
    bio: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Profile bio or description"
    )
    location: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Location from profile"
    )
    email: Optional[str] = Field(
        default=None,
        description="Email address if publicly visible"
    )
    phone: Optional[str] = Field(
        default=None,
        description="Phone number if publicly visible"
    )


class CorrelationRequest(BaseModel):
    """
    Request model for cross-platform correlation endpoint.
    
    Contains a list of profiles from different platforms
    to analyze for overlaps, contradictions, and impersonation.
    
    Attributes:
        profiles: List of platform profiles to correlate
    
    Example:
        {
            "profiles": [
                {"platform": "facebook", "username": "john_doe", "name": "John Doe"},
                {"platform": "twitter", "username": "johndoe", "name": "John D"}
            ]
        }
    """
    profiles: List[PlatformProfile] = Field(
        ...,
        min_length=2,
        max_length=10,
        description="List of platform profiles to correlate (2-10 profiles)"
    )
    
    @field_validator("profiles")
    @classmethod
    def validate_profiles(cls, v: List[PlatformProfile]) -> List[PlatformProfile]:
        """Validate that at least 2 profiles are provided."""
        if len(v) < 2:
            raise ValueError("At least 2 profiles are required for correlation")
        return v


class CorrelationResponse(BaseModel):
    """
    Response model for cross-platform correlation endpoint.
    
    Contains correlation analysis results including overlaps,
    contradictions, impersonation risk assessment, and recommendations.
    
    Attributes:
        overlaps: List of matching information across platforms
        contradictions: List of conflicting information
        impersonation_score: Risk score from 0 (low) to 100 (high)
        impersonation_level: Risk level category
        flags: Warning flags identified during analysis
        recommendations: Suggested actions based on findings
    
    Example:
        {
            "overlaps": [{"field": "name", "platforms": ["facebook", "twitter"], ...}],
            "contradictions": [],
            "impersonation_score": 15,
            "impersonation_level": "low",
            "flags": [],
            "recommendations": ["Enable two-factor authentication..."]
        }
    """
    overlaps: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Matching information found across platforms"
    )
    contradictions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Conflicting information found across platforms"
    )
    impersonation_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Impersonation risk score from 0 (low) to 100 (high)"
    )
    impersonation_level: str = Field(
        ...,
        description="Risk level category (low/medium/high/critical)"
    )
    flags: List[str] = Field(
        default_factory=list,
        description="Warning flags identified during analysis"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommended actions based on analysis"
    )


# =============================================================================
# PROFILE URL GENERATION MODELS (Phase 3)
# =============================================================================

class ProfileURLRequest(BaseModel):
    """
    Request model for profile URL generation endpoint.
    
    Attributes:
        username: Username to generate URLs for
        include_variations: Whether to include username variations
    
    Example:
        {
            "username": "john_doe",
            "include_variations": true
        }
    """
    username: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Username to generate profile URLs for",
        examples=["john_doe", "johndoe123"]
    )
    include_variations: bool = Field(
        default=False,
        description="Whether to include username variations in response"
    )
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate and clean the username."""
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip().lstrip('@')


class ProfileURLResponse(BaseModel):
    """
    Response model for profile URL generation endpoint.
    
    Attributes:
        username: The username used for URL generation
        urls: Dict of platform URLs
        variations: Optional list of username variations with their URLs
    
    Example:
        {
            "username": "john_doe",
            "urls": {
                "facebook": {"name": "Facebook", "url": "..."},
                ...
            },
            "variations": [...]
        }
    """
    username: str = Field(
        ...,
        description="The username used for URL generation"
    )
    urls: Dict[str, Dict[str, str]] = Field(
        ...,
        description="Platform URLs for the username"
    )
    variations: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Username variations with their URLs"
    )


# =============================================================================
# PROFILE CHECK MODELS (Phase 3)
# =============================================================================

class ProfileCheckRequest(BaseModel):
    """
    Request model for profile existence check endpoint.
    
    Attributes:
        username: Username to check
        platforms: Optional list of platforms to check (None = all)
    
    Example:
        {
            "username": "john_doe",
            "platforms": ["instagram", "facebook"]
        }
    """
    username: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Username to check for existence",
        examples=["john_doe"]
    )
    platforms: Optional[List[str]] = Field(
        default=None,
        description="List of platforms to check. If None, checks all supported platforms.",
        examples=[["facebook", "instagram", "linkedin", "x"]]
    )
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate and clean the username."""
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip().lstrip('@')


class ProfileCheckResponse(BaseModel):
    """
    Response model for profile existence check endpoint.
    
    Attributes:
        username: The username that was checked
        results: Dict of check results per platform
        summary: Summary counts by status
    
    Example:
        {
            "username": "john_doe",
            "results": {
                "facebook": {"status": "exists", "url": "...", ...},
                ...
            },
            "summary": {"exists": 2, "not_found": 1, ...}
        }
    """
    username: str = Field(
        ...,
        description="The username that was checked"
    )
    results: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Check results for each platform"
    )
    summary: Dict[str, int] = Field(
        ...,
        description="Summary counts by status (exists, not_found, private, error)"
    )


# =============================================================================
# DATA COLLECTION MODELS (Phase 3)
# =============================================================================

class DataCollectionRequest(BaseModel):
    """
    Request model for profile data collection endpoint.
    
    Attributes:
        url: Profile URL to collect data from
        platform: Platform identifier
    
    Example:
        {
            "url": "https://www.instagram.com/john_doe/",
            "platform": "instagram"
        }
    """
    url: str = Field(
        ...,
        min_length=10,
        description="Profile URL to collect data from",
        examples=["https://www.instagram.com/john_doe/"]
    )
    platform: str = Field(
        ...,
        min_length=1,
        description="Platform identifier (facebook, instagram, linkedin, x)",
        examples=["instagram", "facebook"]
    )


class DataCollectionResponse(BaseModel):
    """
    Response model for profile data collection endpoint.
    
    Attributes:
        url: The URL that was processed
        platform: Platform identifier
        name: Extracted display name
        bio: Extracted bio/description
        profile_image: Profile picture URL
        location: Extracted location
        success: Whether data collection was successful
        error: Error message if any
    
    Example:
        {
            "url": "https://www.instagram.com/john_doe/",
            "platform": "instagram",
            "name": "John Doe",
            "bio": "Software Developer",
            "profile_image": "https://...",
            "location": null,
            "success": true,
            "error": null
        }
    """
    url: str = Field(
        ...,
        description="The URL that was processed"
    )
    platform: str = Field(
        ...,
        description="Platform identifier"
    )
    name: Optional[str] = Field(
        default=None,
        description="Extracted display name"
    )
    bio: Optional[str] = Field(
        default=None,
        description="Extracted bio/description"
    )
    profile_image: Optional[str] = Field(
        default=None,
        description="Profile picture URL"
    )
    location: Optional[str] = Field(
        default=None,
        description="Extracted location"
    )
    success: bool = Field(
        ...,
        description="Whether data collection was successful"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if any"
    )


# =============================================================================
# PHONE LOOKUP MODELS (Phase 3)
# =============================================================================

class PhoneLookupRequest(BaseModel):
    """
    Request model for phone number lookup endpoint.
    
    Attributes:
        phone: Sri Lankan phone number to lookup
    
    Example:
        {
            "phone": "0771234567"
        }
    """
    phone: str = Field(
        ...,
        min_length=9,
        max_length=20,
        description="Sri Lankan phone number to lookup",
        examples=["0771234567", "+94771234567", "077-123-4567"]
    )
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate that phone is not empty."""
        if not v or not v.strip():
            raise ValueError("Phone number cannot be empty")
        return v.strip()


class PhoneLookupResponse(BaseModel):
    """
    Response model for phone number lookup endpoint.
    
    Attributes:
        original: Original phone input
        valid: Whether the number is valid
        type: "mobile" or "landline"
        carrier: Carrier name (mobile) or region (landline)
        e164_format: E.164 formatted number
        local_format: Local display format
        international_format: International display format
        error: Error message if invalid
    
    Example:
        {
            "original": "0771234567",
            "valid": true,
            "type": "mobile",
            "carrier": "Dialog",
            "e164_format": "+94771234567",
            "local_format": "077-123-4567",
            "international_format": "+94 77 123 4567",
            "error": null
        }
    """
    original: str = Field(
        ...,
        description="Original phone input"
    )
    valid: bool = Field(
        ...,
        description="Whether the number is valid"
    )
    type: Optional[str] = Field(
        default=None,
        description="Phone type: mobile or landline"
    )
    carrier: Optional[str] = Field(
        default=None,
        description="Carrier name (mobile) or region (landline)"
    )
    e164_format: Optional[str] = Field(
        default=None,
        description="E.164 formatted number (+94XXXXXXXXX)"
    )
    local_format: Optional[str] = Field(
        default=None,
        description="Local display format (0XX-XXX-XXXX)"
    )
    international_format: Optional[str] = Field(
        default=None,
        description="International display format (+94 XX XXX XXXX)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if invalid"
    )


# =============================================================================
# FULL SCAN MODELS (Phase 3)
# =============================================================================

class FullScanRequest(BaseModel):
    """
    Request model for full scan endpoint.
    
    Performs comprehensive analysis including profile URLs,
    existence checks, phone lookup, and PII analysis.
    
    Attributes:
        username: Username to scan
        phone: Optional phone number to analyze
        email: Optional email to analyze
        name: Optional name to analyze
    
    Example:
        {
            "username": "john_doe",
            "phone": "0771234567",
            "email": "john@example.com",
            "name": "John Perera"
        }
    """
    username: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Username to scan",
        examples=["john_doe"]
    )
    phone: Optional[str] = Field(
        default=None,
        description="Optional phone number to analyze"
    )
    email: Optional[str] = Field(
        default=None,
        description="Optional email to analyze"
    )
    name: Optional[str] = Field(
        default=None,
        description="Optional name to analyze"
    )
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate and clean the username."""
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip().lstrip('@')


class ExposureScanRequest(BaseModel):
    """
    Request model for PII exposure scan endpoint.
    
    Performs comprehensive PII exposure analysis across social media platforms.
    
    Attributes:
        username: Username to scan across platforms
        phone: Optional phone number to match against exposed PII
        email: Optional email to match against exposed PII
        name: Optional name to match against exposed PII
    
    Example:
        {
            "username": "johnperera",
            "phone": "0771234567",
            "email": "john@gmail.com",
            "name": "John Perera"
        }
    """
    username: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Username to scan across platforms",
        examples=["johnperera"]
    )
    phone: Optional[str] = Field(
        default=None,
        description="Optional phone number to match against exposed PII"
    )
    email: Optional[str] = Field(
        default=None,
        description="Optional email to match against exposed PII"
    )
    name: Optional[str] = Field(
        default=None,
        description="Optional name to match against exposed PII"
    )
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate and clean the username."""
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip().lstrip('@')


class FullScanResponse(BaseModel):
    """
    Response model for full scan endpoint.
    
    Contains comprehensive analysis results including profile URLs,
    existence status, phone analysis, PII analysis, and recommendations.
    
    Attributes:
        profile_urls: Generated profile URLs
        profile_existence: Profile existence check results
        phone_analysis: Phone number analysis (if provided)
        pii_analysis: PII analysis results (if email/name provided)
        risk_score: Overall risk score (0-100)
        recommendations: Security and privacy recommendations
    
    Example:
        {
            "profile_urls": {...},
            "profile_existence": {...},
            "phone_analysis": {...},
            "pii_analysis": {...},
            "risk_score": 45,
            "recommendations": [...]
        }
    """
    profile_urls: Dict[str, Any] = Field(
        ...,
        description="Generated profile URLs for all platforms"
    )
    profile_existence: Dict[str, Any] = Field(
        ...,
        description="Profile existence check results"
    )
    phone_analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Phone number analysis results"
    )
    pii_analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="PII analysis from email/name"
    )
    risk_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall risk score (0-100)"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Security and privacy recommendations"
    )


# =============================================================================
# EXPOSURE SCAN MODELS (Phase 3 Enhancement)
# =============================================================================

class ExposedPIIItem(BaseModel):
    """
    Single exposed PII item - shows exactly what's exposed.
    
    Attributes:
        type: Type of PII (email, phone, name, location, workplace, etc.)
        value: The actual exposed value
        platforms: Which platforms expose this
        platform_count: Number of platforms
        risk_level: Risk level (critical, high, medium, low)
        matches_user_input: Does this match user's provided identifier?
    
    Example:
        {
            "type": "phone",
            "value": "+94 77 123 4567",
            "platforms": ["facebook"],
            "platform_count": 1,
            "risk_level": "critical",
            "matches_user_input": true
        }
    """
    type: str = Field(
        ...,
        description="Type of PII (email, phone, name, location, workplace, etc.)"
    )
    value: str = Field(
        ...,
        description="The actual exposed value"
    )
    platforms: List[str] = Field(
        ...,
        description="Which platforms expose this PII"
    )
    platform_count: int = Field(
        ...,
        ge=0,
        description="Number of platforms exposing this PII"
    )
    risk_level: str = Field(
        ...,
        description="Risk level: critical, high, medium, low"
    )
    matches_user_input: bool = Field(
        ...,
        description="Does this match user's provided identifier?"
    )


class PlatformExposure(BaseModel):
    """
    Exposure details for a single platform.
    
    Attributes:
        platform: Platform name
        status: Profile status (found, not_found, error)
        url: Profile URL
        exposed_count: Number of exposed PII items
        exposed_items: List of exposed PII items on this platform
    
    Example:
        {
            "platform": "facebook",
            "status": "found",
            "url": "https://facebook.com/johnperera",
            "exposed_count": 4,
            "exposed_items": [...]
        }
    """
    platform: str = Field(
        ...,
        description="Platform name"
    )
    status: str = Field(
        ...,
        description="Profile status: found, not_found, error"
    )
    url: str = Field(
        ...,
        description="Profile URL"
    )
    exposed_count: int = Field(
        ...,
        ge=0,
        description="Number of exposed PII items"
    )
    exposed_items: List[ExposedPIIItem] = Field(
        default_factory=list,
        description="List of exposed PII items on this platform"
    )


class ExposureScanResponse(BaseModel):
    """
    Complete exposure scan response - clear PII listing for user.
    
    Shows users exactly what PII is exposed and where.
    
    Attributes:
        user_identifiers: User's provided identifiers
        scan_timestamp: When the scan was performed
        platforms_checked: List of platforms checked
        profiles_found: Platforms where profile was found
        profiles_not_found: Platforms where profile was not found
        exposure_score: Exposure risk score (0-100)
        risk_level: Overall risk level
        total_exposed_items: Total number of exposed PII items
        exposed_pii: Clear list of exactly what PII is exposed
        platform_breakdown: Per-platform exposure breakdown
        phone_analysis: Phone analysis if phone was provided
        recommendations: Actionable recommendations
    
    Example:
        {
            "user_identifiers": {"username": "johnperera", ...},
            "exposure_score": 72,
            "risk_level": "high",
            "total_exposed_items": 7,
            "exposed_pii": [...],
            ...
        }
    """
    user_identifiers: Dict[str, str] = Field(
        ...,
        description="User's provided identifiers"
    )
    scan_timestamp: str = Field(
        ...,
        description="ISO 8601 timestamp of when scan was performed"
    )
    platforms_checked: List[str] = Field(
        ...,
        description="List of platforms that were checked"
    )
    profiles_found: List[str] = Field(
        ...,
        description="Platforms where profile was found"
    )
    profiles_not_found: List[str] = Field(
        ...,
        description="Platforms where profile was not found"
    )
    exposure_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Exposure risk score from 0 (low) to 100 (high)"
    )
    risk_level: str = Field(
        ...,
        description="Overall risk level: low, medium, high, critical"
    )
    total_exposed_items: int = Field(
        ...,
        ge=0,
        description="Total number of exposed PII items"
    )
    exposed_pii: List[ExposedPIIItem] = Field(
        ...,
        description="Clear list of exactly what PII is exposed"
    )
    platform_breakdown: Dict[str, PlatformExposure] = Field(
        ...,
        description="Per-platform exposure breakdown"
    )
    phone_analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Phone number analysis if phone was provided"
    )
    recommendations: List[str] = Field(
        ...,
        description="Actionable recommendations specific to exposed data"
    )


# =============================================================================
# FLEXIBLE SCAN MODELS (Hybrid Profile Discovery)
# =============================================================================

class FlexibleScanRequest(BaseModel):
    """
    Request model for flexible scan endpoint using hybrid profile discovery.
    
    Users can provide any single identifier (name, email, username, or phone)
    and the system will use Google Dorking and direct URL checking to find
    social media profiles.
    
    Attributes:
        identifier_type: Type of identifier being provided
        identifier_value: The actual identifier value
        location: Optional location filter for name-based searches (default: Sri Lanka)
        check_existence: Whether to verify profile existence via HTTP (default: True)
    
    Example:
        {
            "identifier_type": "username",
            "identifier_value": "john_doe"
        }
        
        {
            "identifier_type": "email",
            "identifier_value": "john.perera@gmail.com"
        }
        
        {
            "identifier_type": "phone",
            "identifier_value": "0771234567"
        }
        
        {
            "identifier_type": "name",
            "identifier_value": "John Perera",
            "location": "Colombo"
        }
    """
    identifier_type: IdentifierType = Field(
        ...,
        description="Type of identifier: name, email, username, or phone"
    )
    identifier_value: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="The identifier value to search for",
        examples=["john_doe", "john@example.com", "0771234567", "John Perera"]
    )
    location: Optional[str] = Field(
        default="Sri Lanka",
        description="Location filter for name-based searches",
        examples=["Sri Lanka", "Colombo", "Kandy"]
    )
    check_existence: bool = Field(
        default=True,
        description="Whether to verify profile existence via HTTP requests"
    )
    
    @field_validator("identifier_value")
    @classmethod
    def validate_identifier_value(cls, v: str) -> str:
        """Validate and clean the identifier value."""
        if not v or not v.strip():
            raise ValueError("Identifier value cannot be empty")
        return v.strip()


class FlexibleScanResponse(BaseModel):
    """
    Response model for flexible scan endpoint.
    
    Contains hybrid profile discovery results combining Google Dorking
    and direct URL checking methods.
    
    Attributes:
        identifier: The searched identifier value
        identifier_type: Type of identifier used
        timestamp: When the scan was performed
        location_filter: Location filter applied (for name searches)
        dork_results: Google Dork search queries generated
        direct_check_results: Results from direct URL checking
        combined_results: Deduplicated combined results
        username_variations: Generated username variations
        platforms_checked: List of platforms checked
        summary: Summary statistics
    
    Example:
        {
            "identifier": "john_doe",
            "identifier_type": "username",
            "timestamp": "2024-01-15T10:30:00Z",
            "combined_results": {
                "by_platform": {...},
                "found_profiles": [...]
            },
            "summary": {
                "total_profiles_found": 3,
                "platforms_with_profiles": 2
            }
        }
    """
    identifier: str = Field(
        ...,
        description="The searched identifier value"
    )
    identifier_type: str = Field(
        ...,
        description="Type of identifier (name, email, username, phone)"
    )
    timestamp: str = Field(
        ...,
        description="ISO 8601 timestamp of when scan was performed"
    )
    location_filter: Optional[str] = Field(
        default=None,
        description="Location filter applied for name searches"
    )
    dork_results: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Google Dork search queries generated"
    )
    direct_check_results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Results from direct URL checking"
    )
    combined_results: Dict[str, Any] = Field(
        ...,
        description="Deduplicated combined results from both methods"
    )
    username_variations: List[str] = Field(
        default_factory=list,
        description="Generated username variations"
    )
    platforms_checked: List[str] = Field(
        default_factory=list,
        description="List of platforms checked"
    )
    summary: Dict[str, int] = Field(
        ...,
        description="Summary statistics"
    )


# =============================================================================
# ENHANCED REPORT MODELS (Phase 4 - Results Presentation & PDF Export)
# =============================================================================

class ProfileLinks(BaseModel):
    """
    Links for a discovered profile.
    
    Attributes:
        view_profile: Direct link to view the profile
        privacy_settings: Link to platform privacy settings
        report_profile: Link to report the profile
    """
    view_profile: Optional[str] = Field(
        default=None,
        description="Direct link to view the profile"
    )
    privacy_settings: Optional[str] = Field(
        default=None,
        description="Link to platform privacy settings"
    )
    report_profile: Optional[str] = Field(
        default=None,
        description="Link to report the profile"
    )


class DiscoveredProfileDetail(BaseModel):
    """
    Detailed information about a discovered profile.
    
    Attributes:
        index: Order/index of the profile
        platform: Platform name
        platform_emoji: Platform icon/emoji
        found: Whether profile was found
        profile_name: Name on the profile
        username: Username on the platform
        profile_url: Direct profile URL
        discovery_source: How the profile was discovered
        links: Related links for the profile
        checked_urls: URLs checked if profile not found
    """
    index: int = Field(..., description="Order/index of the profile")
    platform: str = Field(..., description="Platform name")
    platform_emoji: str = Field(..., description="Platform icon/emoji")
    found: bool = Field(..., description="Whether profile was found")
    profile_name: Optional[str] = Field(default=None, description="Name on the profile")
    username: Optional[str] = Field(default=None, description="Username on the platform")
    profile_url: Optional[str] = Field(default=None, description="Direct profile URL")
    discovery_source: str = Field(..., description="How the profile was discovered")
    links: ProfileLinks = Field(..., description="Related links for the profile")
    checked_urls: Optional[List[str]] = Field(
        default=None,
        description="URLs checked if profile not found"
    )


class PIISourceDetail(BaseModel):
    """
    Source details for exposed PII.
    
    Attributes:
        platform: Platform name where PII was found
        platform_emoji: Platform icon/emoji
        location_in_profile: Where in the profile the PII was found
        profile_url: URL to the profile
        direct_link: Direct link to the specific location
    """
    platform: str = Field(..., description="Platform name where PII was found")
    platform_emoji: str = Field(..., description="Platform icon/emoji")
    location_in_profile: str = Field(..., description="Where in the profile the PII was found")
    profile_url: str = Field(..., description="URL to the profile")
    direct_link: str = Field(..., description="Direct link to the specific location")


class ExposedPIIDetail(BaseModel):
    """
    Detailed information about an exposed PII item.
    
    Attributes:
        index: Order/index of the PII item
        pii_type: Type of PII (email, phone, name, etc.)
        pii_emoji: Emoji icon for the PII type
        pii_label: Human-readable label for the PII type
        exposed_value: The actual exposed value
        exposed_value_sinhala: Sinhala translation if applicable
        risk_level: Risk level (critical, high, medium, low)
        risk_emoji: Emoji for risk level
        risk_description: Description of the risk
        matches_user_input: Whether this matches user's provided identifier
        found_on: List of sources where PII was found
        recommended_action: Recommended action to take
    """
    index: int = Field(..., description="Order/index of the PII item")
    pii_type: str = Field(..., description="Type of PII")
    pii_emoji: str = Field(..., description="Emoji icon for the PII type")
    pii_label: str = Field(..., description="Human-readable label for the PII type")
    exposed_value: str = Field(..., description="The actual exposed value")
    exposed_value_sinhala: Optional[str] = Field(
        default=None,
        description="Sinhala translation if applicable"
    )
    risk_level: str = Field(..., description="Risk level (critical, high, medium, low)")
    risk_emoji: str = Field(..., description="Emoji for risk level")
    risk_description: str = Field(..., description="Description of the risk")
    matches_user_input: Optional[bool] = Field(
        default=None,
        description="Whether this matches user's provided identifier"
    )
    found_on: List[PIISourceDetail] = Field(
        default_factory=list,
        description="List of sources where PII was found"
    )
    recommended_action: str = Field(..., description="Recommended action to take")


class ImpersonationRisk(BaseModel):
    """
    Information about a detected impersonation risk.
    
    Attributes:
        platform: Platform where risk was detected
        profile_url: URL to the suspicious profile
        profile_name: Name on the suspicious profile
        risk_level: Risk level (high, medium, low)
        risk_emoji: Emoji for risk level
        confidence_score: Confidence score (0-1)
        indicators: List of indicator details
        recommendation: Recommended action
        report_url: URL to report the profile
    """
    platform: str = Field(..., description="Platform where risk was detected")
    profile_url: str = Field(..., description="URL to the suspicious profile")
    profile_name: str = Field(..., description="Name on the suspicious profile")
    risk_level: str = Field(..., description="Risk level (high, medium, low)")
    risk_emoji: str = Field(..., description="Emoji for risk level")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score")
    indicators: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of indicator details"
    )
    recommendation: str = Field(..., description="Recommended action")
    report_url: str = Field(..., description="URL to report the profile")


class CompleteFindings(BaseModel):
    """
    Complete findings section with all discovered profiles and exposed PII.
    
    Attributes:
        discovered_profiles: List of all discovered profile details
        exposed_pii_details: List of all exposed PII details
    """
    discovered_profiles: List[DiscoveredProfileDetail] = Field(
        default_factory=list,
        description="List of all discovered profile details"
    )
    exposed_pii_details: List[ExposedPIIDetail] = Field(
        default_factory=list,
        description="List of all exposed PII details"
    )


class ReportSummary(BaseModel):
    """
    Summary statistics for the analysis report.
    
    Attributes:
        total_platforms_checked: Number of platforms checked
        total_profiles_found: Number of profiles found
        total_pii_exposed: Total number of exposed PII items
        critical_high_risk_items: Count of critical and high risk items
        medium_risk_items: Count of medium risk items
        low_risk_items: Count of low risk items
        impersonation_risks_detected: Number of impersonation risks
        profile_links: Dictionary of platform to profile URL mappings
    """
    total_platforms_checked: int = Field(..., description="Number of platforms checked")
    total_profiles_found: int = Field(..., description="Number of profiles found")
    total_pii_exposed: int = Field(..., description="Total number of exposed PII items")
    critical_high_risk_items: int = Field(..., description="Count of critical and high risk items")
    medium_risk_items: int = Field(..., description="Count of medium risk items")
    low_risk_items: int = Field(..., description="Count of low risk items")
    impersonation_risks_detected: int = Field(..., description="Number of impersonation risks")
    profile_links: Dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary of platform to profile URL mappings"
    )


class AnalysisReportResponse(BaseModel):
    """
    Comprehensive analysis report response.
    
    Contains all analysis results including risk assessment,
    impersonation risks, exposed PII, platform breakdown,
    recommendations, and complete findings.
    
    Attributes:
        success: Whether the analysis was successful
        report_id: Unique report identifier
        generated_at: ISO 8601 timestamp
        identifier: Identifier information
        risk_assessment: Risk assessment details
        impersonation_risks: List of impersonation risks
        exposed_pii: Exposed PII categorized by severity
        platforms: Platform breakdown list
        recommendations: Prioritized recommendations
        cross_language: Cross-language support (Sinhala)
        complete_findings: Complete findings with all links
        summary: Summary statistics
        export: Export URLs for PDF/JSON
    """
    success: bool = Field(..., description="Whether the analysis was successful")
    report_id: str = Field(..., description="Unique report identifier")
    generated_at: str = Field(..., description="ISO 8601 timestamp")
    identifier: Dict[str, Any] = Field(..., description="Identifier information")
    risk_assessment: Dict[str, Any] = Field(..., description="Risk assessment details")
    impersonation_risks: List[ImpersonationRisk] = Field(
        default_factory=list,
        description="List of impersonation risks"
    )
    exposed_pii: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Exposed PII categorized by severity"
    )
    platforms: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Platform breakdown list"
    )
    recommendations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Prioritized recommendations"
    )
    cross_language: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Cross-language support (Sinhala)"
    )
    complete_findings: CompleteFindings = Field(
        ...,
        description="Complete findings with all links"
    )
    summary: ReportSummary = Field(..., description="Summary statistics")
    export: Dict[str, str] = Field(
        default_factory=dict,
        description="Export URLs for PDF/JSON"
    )


# =============================================================================
# ENHANCED FLEXIBLE SCAN REQUEST (Updated to support only 3 identifier types)
# =============================================================================

class EnhancedIdentifierType(str, Enum):
    """
    Enum for supported identifier types (NO phone).
    Only name, email, and username are supported.
    """
    NAME = "name"
    EMAIL = "email"
    USERNAME = "username"


class EnhancedScanRequest(BaseModel):
    """
    Request model for enhanced scan endpoint.
    
    Only supports 3 identifier types: name, email, username (NO phone).
    
    Attributes:
        identifier_type: Type of identifier (name, email, username only)
        identifier_value: The identifier value to search for
        location: Optional location filter (default: Sri Lanka)
    
    Example:
        {
            "identifier_type": "username",
            "identifier_value": "john_doe"
        }
        
        {
            "identifier_type": "email",
            "identifier_value": "john@example.com"
        }
        
        {
            "identifier_type": "name",
            "identifier_value": "John Perera",
            "location": "Colombo"
        }
    """
    identifier_type: EnhancedIdentifierType = Field(
        ...,
        description="Type of identifier: name, email, or username (NO phone)"
    )
    identifier_value: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="The identifier value to search for",
        examples=["john_doe", "john@example.com", "John Perera"]
    )
    location: Optional[str] = Field(
        default="Sri Lanka",
        description="Location filter for searches",
        examples=["Sri Lanka", "Colombo", "Kandy"]
    )
    platforms: Optional[List[str]] = Field(
        default=None,
        description="List of platforms to scan (facebook, instagram, linkedin, x)",
        examples=[["facebook", "instagram"]]
    )
    
    @field_validator("identifier_value")
    @classmethod
    def validate_identifier_value(cls, v: str) -> str:
        """Validate and clean the identifier value."""
        if not v or not v.strip():
            raise ValueError("Identifier value cannot be empty")
        return v.strip()


# =============================================================================
# LIGHT SCAN MODELS (Google Dorking Profile Discovery)
# =============================================================================

class ScanType(str, Enum):
    """
    Enum for scan types.
    """
    LIGHT = "light"
    DEEP = "deep"


class LightScanRequest(BaseModel):
    """
    Request model for light scan endpoint (Google Dorking).
    
    Only supports 3 identifier types: name, email, username (NO phone).
    
    Attributes:
        identifier_type: Type of identifier ('name', 'email', 'username')
        identifier_value: The identifier value to search for
        location: Optional location filter (default: Sri Lanka)
    
    Example:
        {
            "identifier_type": "name",
            "identifier_value": "John Perera",
            "location": "Sri Lanka"
        }
    """
    identifier_type: str = Field(
        ...,
        description="Type of identifier: 'name', 'email', or 'username' (NO phone)"
    )
    identifier_value: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="The identifier value to search for",
        examples=["john_doe", "john@example.com", "John Perera"]
    )
    location: Optional[str] = Field(
        default="Sri Lanka",
        description="Location filter for searches",
        examples=["Sri Lanka", "Colombo", "Kandy"]
    )
    
    @field_validator("identifier_type")
    @classmethod
    def validate_identifier_type(cls, v: str) -> str:
        """Validate identifier type is one of the supported types."""
        valid_types = ["name", "email", "username"]
        if v.lower() not in valid_types:
            raise ValueError(
                f"identifier_type must be one of: {valid_types}. "
                "Phone number is NOT supported for Light Scan."
            )
        return v.lower()
    
    @field_validator("identifier_value")
    @classmethod
    def validate_light_scan_identifier_value(cls, v: str) -> str:
        """Validate and clean the identifier value."""
        if not v or not v.strip():
            raise ValueError("Identifier value cannot be empty")
        return v.strip()


class DorkResult(BaseModel):
    """
    Model for a single Google Dork search result.
    
    Attributes:
        title: Page title from search result
        url: URL of the found profile
        snippet: Description snippet from search result (optional)
        query_used: The dork query that found this result
    
    Example:
        {
            "title": "John Perera - Colombo, Sri Lanka",
            "url": "https://www.facebook.com/john.perera.colombo",
            "snippet": "Software Engineer at ABC Tech...",
            "query_used": "site:facebook.com \"John Perera\" \"Sri Lanka\""
        }
    """
    title: str = Field(
        ...,
        description="Page title from search result"
    )
    url: str = Field(
        ...,
        description="URL of the found profile"
    )
    snippet: Optional[str] = Field(
        default=None,
        description="Description snippet from search result"
    )
    query_used: str = Field(
        ...,
        description="The dork query that found this result"
    )


class PlatformDorkResults(BaseModel):
    """
    Model for dork results from a single platform.
    
    Attributes:
        platform: Platform identifier (facebook, instagram, linkedin, x)
        platform_emoji: Emoji/icon for the platform
        results_count: Number of results found
        results: List of DorkResult items
        queries_used: List of dork queries used for this platform
    
    Example:
        {
            "platform": "facebook",
            "platform_emoji": "📘",
            "results_count": 4,
            "results": [...],
            "queries_used": ["site:facebook.com \"John Perera\"", ...]
        }
    """
    platform: str = Field(
        ...,
        description="Platform identifier"
    )
    platform_emoji: str = Field(
        ...,
        description="Emoji/icon for the platform"
    )
    results_count: int = Field(
        ...,
        ge=0,
        description="Number of results found"
    )
    results: List[DorkResult] = Field(
        default_factory=list,
        description="List of found results"
    )
    queries_used: List[str] = Field(
        default_factory=list,
        description="List of dork queries used"
    )


class LightScanResponse(BaseModel):
    """
    Response model for light scan endpoint.
    
    Contains all results from Google Dorking grouped by platform.
    
    Attributes:
        success: Whether the scan completed successfully
        scan_type: Always "light" for this response
        scan_id: Unique scan identifier (e.g., "LS-ABC12345")
        identifier: Dict with type and value of the searched identifier
        location: Location filter used
        scan_duration_seconds: Time taken to complete the scan
        total_results: Total number of results found across all platforms
        platforms: List of PlatformDorkResults for each platform
        summary: Dict mapping platform to result count
        all_urls: Flat list of all found URLs with platform and title
        deep_scan_available: Whether deep scan is available
        deep_scan_message: Message about deep scan availability
    
    Example:
        {
            "success": true,
            "scan_type": "light",
            "scan_id": "LS-ABC12345",
            "identifier": {"type": "name", "value": "John Perera"},
            "location": "Sri Lanka",
            "scan_duration_seconds": 28.5,
            "total_results": 12,
            "platforms": [...],
            "summary": {"facebook": 4, "instagram": 3, "linkedin": 3, "x": 2},
            "all_urls": [...],
            "deep_scan_available": true,
            "deep_scan_message": "Want more detailed analysis?..."
        }
    """
    success: bool = Field(
        ...,
        description="Whether the scan completed successfully"
    )
    scan_type: str = Field(
        default="light",
        description="Type of scan performed"
    )
    scan_id: str = Field(
        ...,
        description="Unique scan identifier"
    )
    identifier: Dict[str, str] = Field(
        ...,
        description="Searched identifier info with 'type' and 'value'"
    )
    location: str = Field(
        ...,
        description="Location filter used"
    )
    scan_duration_seconds: float = Field(
        ...,
        description="Time taken to complete the scan"
    )
    total_results: int = Field(
        ...,
        ge=0,
        description="Total number of results found"
    )
    platforms: List[PlatformDorkResults] = Field(
        ...,
        description="Results grouped by platform"
    )
    summary: Dict[str, int] = Field(
        ...,
        description="Summary of result counts per platform"
    )
    all_urls: List[Dict[str, str]] = Field(
        ...,
        description="Flat list of all found URLs"
    )
    deep_scan_available: bool = Field(
        default=True,
        description="Whether deep scan is available"
    )
    deep_scan_message: str = Field(
        ...,
        description="Message about deep scan availability"
    )


class ScanOptionsResponse(BaseModel):
    """
    Response model for scan options endpoint.
    
    Describes available scan types and their capabilities.
    
    Example:
        {
            "light_scan": {
                "name": "Light Scan",
                "description": "Fast Google Dorking...",
                "supported_identifiers": ["name", "email", "username"],
                "platforms": ["facebook", "instagram", "linkedin", "x"]
            },
            "deep_scan": {
                "name": "Deep Scan",
                "description": "Comprehensive analysis...",
                "requires_extension": true
            }
        }
    """
    light_scan: Dict[str, Any] = Field(
        ...,
        description="Light scan options and capabilities"
    )
    deep_scan: Dict[str, Any] = Field(
        ...,
        description="Deep scan options and capabilities"
    )


class DeepScanResponse(BaseModel):
    """
    Response model for deep scan placeholder endpoint.
    
    Indicates that deep scan requires the browser extension.
    
    Example:
        {
            "success": false,
            "message": "Deep Scan requires the browser extension...",
            "extension_required": true,
            "extension_info": {...}
        }
    """
    success: bool = Field(
        default=False,
        description="Whether the scan was performed"
    )
    message: str = Field(
        ...,
        description="Message explaining why deep scan wasn't performed"
    )
    extension_required: bool = Field(
        default=True,
        description="Whether the browser extension is required"
    )
    extension_info: Dict[str, str] = Field(
        ...,
        description="Information about the required extension"
    )


# =============================================================================
# DEEP SCAN ANALYZE MODELS (Browser Extension Integration)
# =============================================================================

class ExtractedProfileData(BaseModel):
    """
    Profile data extracted by the browser extension content scripts.
    
    Attributes:
        platform: Platform identifier (facebook, instagram, linkedin, x)
        name: Display name from profile
        username: Username/handle
        profileUrl: URL to the profile
        profileImage: Profile image URL
        bio: Profile bio/description
        location: Location if available
        email: Email if publicly visible
        phone: Phone if publicly visible
        website: Website link if available
        followers: Follower count
        following: Following count
        isVerified: Verified account status
        extractedPII: PII extracted from visible content
    """
    platform: str = Field(..., description="Platform identifier")
    name: Optional[str] = Field(default=None, description="Display name")
    username: Optional[str] = Field(default=None, description="Username/handle")
    profileUrl: Optional[str] = Field(default=None, description="Profile URL")
    profileImage: Optional[str] = Field(default=None, description="Profile image URL")
    bio: Optional[str] = Field(default=None, description="Profile bio")
    location: Optional[str] = Field(default=None, description="Location")
    email: Optional[str] = Field(default=None, description="Email if visible")
    phone: Optional[str] = Field(default=None, description="Phone if visible")
    website: Optional[str] = Field(default=None, description="Website link")
    followers: Optional[str] = Field(default=None, description="Follower count")
    following: Optional[str] = Field(default=None, description="Following count")
    isVerified: bool = Field(default=False, description="Verified status")
    extractedPII: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Extracted PII (emails, phones, urls, mentions)"
    )


class PlatformScanResult(BaseModel):
    """
    Scan results for a single platform.
    
    Attributes:
        platform: Platform display name
        emoji: Platform emoji icon
        status: Scan status (completed, error, timeout)
        profiles: List of extracted profile data
        searchResults: List of search result profiles
        errors: List of error messages
    """
    platform: str = Field(..., description="Platform display name")
    emoji: str = Field(..., description="Platform emoji icon")
    status: str = Field(..., description="Scan status")
    profiles: List[ExtractedProfileData] = Field(
        default_factory=list,
        description="Extracted profile data"
    )
    searchResults: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Search result profiles"
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Error messages"
    )


class DeepScanAnalyzeRequest(BaseModel):
    """
    Request model for deep scan analyze endpoint.
    
    Receives data collected by the browser extension and processes it
    for comprehensive analysis.
    
    Attributes:
        scan_id: Unique scan identifier from extension
        identifier_type: Type of identifier searched (name, email, username)
        identifier_value: The value that was searched
        platforms_scanned: List of platforms that were scanned
        results: Scan results grouped by platform
        scan_duration_ms: Time taken to complete scan
        generate_pdf: Whether to generate PDF report
    
    Example:
        {
            "scan_id": "DS-ABC12345",
            "identifier_type": "username",
            "identifier_value": "john_doe",
            "platforms_scanned": ["facebook", "instagram"],
            "results": {...},
            "scan_duration_ms": 15000
        }
    """
    scan_id: str = Field(
        ...,
        min_length=1,
        description="Unique scan identifier from extension"
    )
    identifier_type: str = Field(
        ...,
        description="Type of identifier (name, email, username)"
    )
    identifier_value: str = Field(
        ...,
        min_length=1,
        description="The value that was searched"
    )
    platforms_scanned: List[str] = Field(
        default_factory=list,
        description="List of platforms scanned"
    )
    results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Scan results grouped by platform"
    )
    scan_duration_ms: Optional[int] = Field(
        default=None,
        description="Time taken to complete scan in milliseconds"
    )
    generate_pdf: bool = Field(
        default=False,
        description="Whether to generate PDF report"
    )
    
    @field_validator("identifier_value")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        """Validate identifier is not empty."""
        if not v or not v.strip():
            raise ValueError("Identifier value cannot be empty")
        return v.strip()


class DeepScanAnalyzeResponse(BaseModel):
    """
    Response model for deep scan analyze endpoint.
    
    Returns comprehensive analysis of the extension-collected data.
    
    Attributes:
        success: Whether analysis was successful
        scan_id: Original scan ID
        report_id: Generated report ID for PDF download
        analysis_timestamp: When analysis was performed
        identifier: Analyzed identifier info
        platforms_analyzed: Number of platforms with data
        total_profiles_found: Total profiles discovered
        total_pii_exposed: Total PII items found
        risk_score: Overall risk score (0-100)
        risk_level: Risk level (low, medium, high, critical)
        exposed_pii: List of exposed PII items
        platform_summary: Summary per platform
        impersonation_risks: Detected impersonation risks
        recommendations: Privacy recommendations
        pdf_url: URL to download PDF report (if generated)
    """
    success: bool = Field(..., description="Whether analysis succeeded")
    scan_id: str = Field(..., description="Original scan ID")
    report_id: Optional[str] = Field(
        default=None,
        description="Report ID for PDF download"
    )
    analysis_timestamp: str = Field(
        ...,
        description="ISO 8601 timestamp of analysis"
    )
    identifier: Dict[str, str] = Field(
        ...,
        description="Analyzed identifier info"
    )
    platforms_analyzed: int = Field(
        ...,
        ge=0,
        description="Number of platforms with data"
    )
    total_profiles_found: int = Field(
        ...,
        ge=0,
        description="Total profiles discovered"
    )
    total_pii_exposed: int = Field(
        ...,
        ge=0,
        description="Total PII items found"
    )
    risk_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall risk score"
    )
    risk_level: str = Field(
        ...,
        description="Risk level category"
    )
    exposed_pii: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of exposed PII items"
    )
    pii_by_platform: Optional[Dict[str, Dict[str, Any]]] = Field(
        default=None,
        description="PII grouped by platform for detailed reporting"
    )
    platform_summary: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Summary per platform"
    )
    impersonation_risks: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Detected impersonation risks"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Privacy recommendations"
    )
    pdf_url: Optional[str] = Field(
        default=None,
        description="URL to download PDF report"
    )
