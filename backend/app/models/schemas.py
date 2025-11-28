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
from typing import List, Dict, Any, Optional
import re


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
    
    Contains all input parameters for comprehensive digital footprint analysis.
    Username is required; other fields are optional but enhance the analysis.
    
    Attributes:
        username: Social media username to analyze (required)
        email: Email address for PII extraction (optional)
        phone: Phone number - Sri Lankan formats supported (optional)
        name: Full name for NER analysis (optional)
    
    Example:
        {
            "username": "john_doe",
            "email": "john@example.com",
            "phone": "0771234567",
            "name": "John Perera"
        }
    """
    username: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Social media username to analyze",
        examples=["john_doe"]
    )
    email: Optional[str] = Field(
        None,
        description="Email address for enhanced analysis",
        examples=["john@example.com"]
    )
    phone: Optional[str] = Field(
        None,
        description="Phone number (Sri Lankan formats: 07X-XXXXXXX, +94)",
        examples=["0771234567", "+94771234567"]
    )
    name: Optional[str] = Field(
        None,
        max_length=200,
        description="Full name for NER analysis",
        examples=["John Perera"]
    )
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        Validate and clean the username.
        
        Rules:
        - Cannot be empty or whitespace only
        - Strips leading @ symbol if present
        - Trims whitespace
        """
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")
        # Clean up the username
        cleaned = v.strip().lstrip('@')
        if not cleaned:
            raise ValueError("Username cannot be just '@'")
        return cleaned
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate email format if provided.
        
        Uses a simplified RFC 5322 pattern for validation.
        """
        if v is None or v == "":
            return None
        
        # Basic email validation pattern
        email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        v = v.strip().lower()
        if not email_pattern.match(v):
            raise ValueError("Invalid email format")
        
        return v
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate phone number if provided.
        
        Accepts Sri Lankan phone formats:
        - 07X XXXXXXX (local)
        - +94 7X XXXXXXX (international)
        - 0094 7X XXXXXXX (international)
        """
        if v is None or v == "":
            return None
        
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', v)
        
        # Validate it looks like a Sri Lankan number
        # Local: 07XXXXXXXX (10 digits)
        # International: +947XXXXXXXX (12 chars) or 00947XXXXXXXX (13 chars)
        if not (
            (len(cleaned) == 10 and cleaned.startswith('07')) or
            (len(cleaned) == 12 and cleaned.startswith('+947')) or
            (len(cleaned) == 13 and cleaned.startswith('00947'))
        ):
            # Be lenient - if it has digits, keep it
            if not cleaned.replace('+', '').isdigit():
                raise ValueError("Invalid phone number format")
        
        return v.strip()


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
