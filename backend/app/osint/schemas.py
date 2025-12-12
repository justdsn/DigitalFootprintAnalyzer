# =============================================================================
# OSINT SCHEMAS
# =============================================================================
# Pydantic models for OSINT data structures.
# =============================================================================

"""
OSINT Schemas

Pydantic models for all OSINT data structures:
- Collection results
- Parsed profile data
- Analysis results
- Session information
- API request/response models

These models provide type safety, validation, and OpenAPI documentation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class IdentifierType(str, Enum):
    """Types of identifiers that can be analyzed."""
    USERNAME = "username"
    EMAIL = "email"
    PHONE = "phone"
    NAME = "name"
    UNKNOWN = "unknown"


class Platform(str, Enum):
    """Supported social media platforms."""
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"


class RiskLevel(str, Enum):
    """Risk level classifications."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# =============================================================================
# COLLECTION MODELS
# =============================================================================

class CollectionResult(BaseModel):
    """Result from a platform collector."""
    success: bool = Field(..., description="Whether collection succeeded")
    platform: str = Field(..., description="Platform name")
    url: str = Field(..., description="Profile URL")
    html: Optional[str] = Field(None, description="Collected HTML content")
    text_blocks: Dict[str, str] = Field(default_factory=dict, description="Extracted text blocks")
    error: Optional[str] = Field(None, description="Error message if failed")
    timestamp: Optional[str] = Field(None, description="Collection timestamp")


class SessionInfo(BaseModel):
    """Session metadata and storage state."""
    platform: str = Field(..., description="Platform name")
    created_at: str = Field(..., description="Session creation timestamp")
    version: str = Field(default="1.0", description="Session format version")


class StorageState(BaseModel):
    """Playwright storage state structure."""
    cookies: List[Dict[str, Any]] = Field(default_factory=list, description="Browser cookies")
    origins: List[Dict[str, Any]] = Field(default_factory=list, description="Origin storage")


class SessionData(BaseModel):
    """Complete session file structure."""
    metadata: SessionInfo = Field(..., description="Session metadata")
    storageState: StorageState = Field(..., description="Playwright storage state")


# =============================================================================
# PARSED PROFILE MODELS
# =============================================================================

class PIIData(BaseModel):
    """Personally Identifiable Information extracted from profile."""
    emails: List[str] = Field(default_factory=list, description="Email addresses")
    phones: List[str] = Field(default_factory=list, description="Phone numbers")
    urls: List[str] = Field(default_factory=list, description="External URLs")
    addresses: List[str] = Field(default_factory=list, description="Physical addresses")


class NEREntities(BaseModel):
    """Named Entity Recognition results."""
    persons: List[str] = Field(default_factory=list, description="Person names")
    organizations: List[str] = Field(default_factory=list, description="Organization names")
    locations: List[str] = Field(default_factory=list, description="Locations")
    dates: List[str] = Field(default_factory=list, description="Dates")


class ParsedProfile(BaseModel):
    """Parsed profile data from a platform."""
    platform: str = Field(..., description="Platform name")
    url: Optional[str] = Field(None, description="Profile URL")
    username: Optional[str] = Field(None, description="Username/handle")
    name: Optional[str] = Field(None, description="Display name")
    bio: Optional[str] = Field(None, description="Bio/description")
    followers: Optional[int] = Field(None, description="Follower count")
    following: Optional[int] = Field(None, description="Following count")
    location: Optional[str] = Field(None, description="Location")
    job_title: Optional[str] = Field(None, description="Job title")
    urls: List[str] = Field(default_factory=list, description="External URLs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    collection_success: bool = Field(default=False, description="Whether collection succeeded")


# =============================================================================
# ANALYSIS MODELS
# =============================================================================

class ProfileAnalysis(BaseModel):
    """Analysis results for a single profile."""
    username_similarity: int = Field(..., ge=0, le=100, description="Username similarity score (0-100)")
    bio_similarity: int = Field(..., ge=0, le=100, description="Bio similarity score (0-100)")
    pii_exposure_score: int = Field(..., ge=0, le=100, description="PII exposure score (0-100)")
    timeline_risk: str = Field(..., description="Timeline risk level (low/medium/high)")
    impersonation_score: int = Field(..., ge=0, le=100, description="Impersonation risk score (0-100)")


class AnalyzedProfile(BaseModel):
    """Complete profile with analysis results."""
    platform: str = Field(..., description="Platform name")
    url: Optional[str] = Field(None, description="Profile URL")
    username: Optional[str] = Field(None, description="Username/handle")
    name: Optional[str] = Field(None, description="Display name")
    bio: Optional[str] = Field(None, description="Bio/description")
    pii: PIIData = Field(default_factory=PIIData, description="Extracted PII data")
    ner_entities: Optional[NEREntities] = Field(None, description="NER entities")
    followers: Optional[int] = Field(None, description="Follower count")
    following: Optional[int] = Field(None, description="Following count")
    location: Optional[str] = Field(None, description="Location")
    job_title: Optional[str] = Field(None, description="Job title")
    profile_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    analysis: ProfileAnalysis = Field(..., description="Analysis results")


class CorrelationResult(BaseModel):
    """Cross-platform correlation results."""
    correlated: bool = Field(..., description="Whether profiles are correlated")
    impersonation_score: int = Field(default=0, ge=0, le=100, description="Correlation-based impersonation score")
    impersonation_level: str = Field(default="unknown", description="Impersonation risk level")
    reason: Optional[str] = Field(None, description="Reason for correlation result")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Correlation confidence (0-1)")


class OverallRisk(BaseModel):
    """Overall risk assessment across all profiles."""
    exposure: str = Field(..., description="Overall exposure level (Low/Medium/High)")
    impersonation: str = Field(..., description="Overall impersonation risk (Low/Medium/High)")
    score: int = Field(default=0, ge=0, le=100, description="Overall risk score (0-100)")
    profiles_analyzed: int = Field(default=0, ge=0, description="Number of profiles analyzed")


# =============================================================================
# SESSION MANAGEMENT MODELS
# =============================================================================

class SessionStatus(BaseModel):
    """Status of a platform session."""
    platform: str = Field(..., description="Platform name")
    exists: bool = Field(..., description="Whether session file exists")
    valid: bool = Field(..., description="Whether session is valid/not expired")
    age_days: Optional[int] = Field(None, description="Session age in days")
    expires_in_days: Optional[int] = Field(None, description="Days until expiration")
    error: Optional[str] = Field(None, description="Error message if validation failed")


class SessionsStatusResponse(BaseModel):
    """Status of all platform sessions."""
    sessions: Dict[str, SessionStatus] = Field(..., description="Session status by platform")
    healthy_count: int = Field(..., ge=0, description="Number of healthy sessions")
    expired_count: int = Field(..., ge=0, description="Number of expired sessions")
    missing_count: int = Field(..., ge=0, description="Number of missing sessions")


# =============================================================================
# API REQUEST/RESPONSE MODELS
# =============================================================================

class OSINTAnalyzeRequest(BaseModel):
    """Request model for OSINT analysis."""
    identifier: str = Field(..., description="Username, email, name, or phone number", min_length=1)
    platforms: Optional[List[str]] = Field(
        None,
        description="List of platforms to check (default: all supported platforms)"
    )
    use_search: bool = Field(
        default=False,
        description="Use Google Custom Search for profile discovery"
    )

    @field_validator('identifier')
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        """Validate identifier is not empty."""
        if not v or not v.strip():
            raise ValueError("Identifier cannot be empty")
        return v.strip()


class OSINTAnalyzeResponse(BaseModel):
    """Response model for OSINT analysis."""
    input: str = Field(..., description="Original input identifier")
    identifier_type: str = Field(..., description="Detected identifier type")
    username: str = Field(..., description="Extracted username for search")
    timestamp: str = Field(..., description="Analysis timestamp (ISO format)")
    profiles_found: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of found profiles with analysis"
    )
    correlation: Dict[str, Any] = Field(
        default_factory=dict,
        description="Cross-platform correlation results"
    )
    overall_risk: OverallRisk = Field(..., description="Overall risk assessment")
    processing_time_ms: float = Field(..., ge=0, description="Processing time in milliseconds")


class SessionValidateRequest(BaseModel):
    """Request model for session validation."""
    platform: str = Field(..., description="Platform to validate (instagram/facebook/linkedin/twitter)")

    @field_validator('platform')
    @classmethod
    def validate_platform(cls, v: str) -> str:
        """Validate platform is supported."""
        supported = ["instagram", "facebook", "linkedin", "twitter"]
        if v.lower() not in supported:
            raise ValueError(f"Platform must be one of: {', '.join(supported)}")
        return v.lower()


# =============================================================================
# DISCOVERY MODELS
# =============================================================================

class IdentifierDetectionResult(BaseModel):
    """Result of identifier type detection."""
    type: IdentifierType = Field(..., description="Detected identifier type")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence (0-1)")
    normalized: str = Field(..., description="Normalized identifier value")


class ProfileURL(BaseModel):
    """Generated profile URL for a platform."""
    platform: str = Field(..., description="Platform name")
    url: str = Field(..., description="Generated profile URL")
    confidence: float = Field(default=1.0, ge=0, le=1, description="URL generation confidence")


class SearchResult(BaseModel):
    """Search engine result for profile discovery."""
    url: str = Field(..., description="Found URL")
    title: str = Field(..., description="Page title")
    snippet: str = Field(..., description="Search result snippet")
    platform: Optional[str] = Field(None, description="Detected platform")


# =============================================================================
# ERROR MODELS
# =============================================================================

class OSINTError(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Error timestamp")


__all__ = [
    # Enums
    "IdentifierType",
    "Platform",
    "RiskLevel",
    
    # Collection
    "CollectionResult",
    "SessionInfo",
    "StorageState",
    "SessionData",
    
    # Profiles
    "PIIData",
    "NEREntities",
    "ParsedProfile",
    
    # Analysis
    "ProfileAnalysis",
    "AnalyzedProfile",
    "CorrelationResult",
    "OverallRisk",
    
    # Sessions
    "SessionStatus",
    "SessionsStatusResponse",
    
    # API
    "OSINTAnalyzeRequest",
    "OSINTAnalyzeResponse",
    "SessionValidateRequest",
    
    # Discovery
    "IdentifierDetectionResult",
    "ProfileURL",
    "SearchResult",
    
    # Errors
    "OSINTError",
]
