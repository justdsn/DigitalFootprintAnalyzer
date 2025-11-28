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
    
    Contains a single identifier with its type for digital footprint analysis.
    The identifier can be a username, email, phone number, or name.
    
    Attributes:
        identifier: The value to search/analyze (required)
        identifier_type: The type of identifier (username, email, phone, name)
    
    Example:
        {
            "identifier": "john_doe",
            "identifier_type": "username"
        }
    """
    identifier: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="The identifier value to analyze",
        examples=["john_doe", "john@example.com", "0771234567", "John Perera"]
    )
    identifier_type: IdentifierType = Field(
        ...,
        description="Type of identifier being searched",
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
        username: The analyzed username
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
            "username": "john_doe",
            "risk_score": 45,
            "risk_level": "medium",
            ...
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
    extracted_pii: Dict[str, Any] = Field(
        ...,
        description="Extracted PII from provided inputs"
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
