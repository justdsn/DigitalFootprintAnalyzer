# =============================================================================
# API ROUTES
# =============================================================================
# Defines all API endpoints for the Digital Footprint Analyzer.
# Includes analysis, PII extraction, username analysis, and health check.
# =============================================================================

"""
API Route Definitions

This module defines the following endpoints:
- POST /api/analyze - Main analysis combining all services
- POST /api/extract-pii - Extract PII from provided text
- POST /api/analyze-username - Analyze username and generate platform URLs
- GET /api/health - Health check for monitoring
- POST /api/generate-profile-urls - Generate profile URLs (Phase 3)
- POST /api/check-profiles - Check profile existence (Phase 3)
- POST /api/collect-profile-data - Collect profile data (Phase 3)
- POST /api/phone-lookup - Phone number lookup (Phase 3)
- POST /api/full-scan - Full scan analysis (Phase 3)
- POST /api/scan - Enhanced flexible scan (Phase 4)
- GET /api/report/{report_id}/pdf - Download PDF report (Phase 4)

Each endpoint includes comprehensive error handling and validation.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List
import time
import logging
import re
import io

# Set up logger
logger = logging.getLogger(__name__)

# Import request/response schemas
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    PIIExtractRequest,
    PIIExtractResponse,
    UsernameAnalyzeRequest,
    UsernameAnalyzeResponse,
    HealthResponse,
    IdentifierType,
    TransliterateRequest,
    TransliterateResponse,
    CorrelationRequest,
    CorrelationResponse,
    PlatformProfile,
    # Phase 3 schemas
    ProfileURLRequest,
    ProfileURLResponse,
    ProfileCheckRequest,
    ProfileCheckResponse,
    DataCollectionRequest,
    DataCollectionResponse,
    PhoneLookupRequest,
    PhoneLookupResponse,
    FullScanRequest,
    FullScanResponse,
    # Phase 3 Enhancement schemas
    ExposureScanRequest,
    ExposedPIIItem,
    PlatformExposure,
    ExposureScanResponse,
    # Flexible Scan schemas (Hybrid Profile Discovery)
    FlexibleScanRequest,
    FlexibleScanResponse,
    # Phase 4 - Enhanced Report schemas
    EnhancedScanRequest,
    AnalysisReportResponse,
    ImpersonationRisk,
    CompleteFindings,
    ReportSummary,
)

# Import services
from app.services.pii_extractor import PIIExtractor
from app.services.ner_engine import NEREngine
from app.services.username_analyzer import UsernameAnalyzer
from app.services.transliteration import SinhalaTransliterator
from app.services.correlation import CrossPlatformCorrelator
# Phase 3 services
from app.services.social import (
    ProfileURLGenerator,
    ProfileExistenceChecker,
    SocialMediaDataCollector,
    PhoneNumberLookup,
    PIIExposureAnalyzer,
    scrape_all_platforms,
    HybridProfileFinder,
    ImpersonationDetector,
)
# Phase 4 services - Report generation
from app.services.report import (
    ReportBuilder,
    PDFGenerator,
    SUPPORTED_PLATFORMS,
)


# =============================================================================
# ROUTER INITIALIZATION
# =============================================================================

router = APIRouter()

# Initialize service instances
# These are stateless services, so we can reuse single instances
pii_extractor = PIIExtractor()
ner_engine = NEREngine()
username_analyzer = UsernameAnalyzer()
sinhala_transliterator = SinhalaTransliterator()
cross_platform_correlator = CrossPlatformCorrelator()
# Phase 3 service instances
profile_url_generator = ProfileURLGenerator()
profile_checker = ProfileExistenceChecker()
data_collector = SocialMediaDataCollector()
phone_lookup = PhoneNumberLookup()
# Phase 3 Enhancement services
exposure_analyzer = PIIExposureAnalyzer()
# Hybrid Profile Discovery service
hybrid_profile_finder = HybridProfileFinder()
# Phase 4 service instances
impersonation_detector = ImpersonationDetector()
report_builder = ReportBuilder()
pdf_generator = PDFGenerator()

# In-memory report storage (for demo purposes - use database in production)
report_cache: Dict[str, Dict[str, Any]] = {}


# =============================================================================
# HEALTH CHECK ENDPOINT
# =============================================================================

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the API is running and healthy"
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        HealthResponse: Current health status of the API
        
    Example Response:
        {
            "status": "healthy",
            "version": "1.0.0",
            "services": {
                "pii_extractor": "operational",
                "ner_engine": "operational",
                "username_analyzer": "operational"
            }
        }
    """
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        services={
            "pii_extractor": "operational",
            "ner_engine": "operational",
            "username_analyzer": "operational",
            "sinhala_transliterator": "operational",
            "cross_platform_correlator": "operational",
            "profile_url_generator": "operational",
            "profile_checker": "operational",
            "data_collector": "operational",
            "phone_lookup": "operational"
        }
    )


# =============================================================================
# MAIN ANALYSIS ENDPOINT
# =============================================================================

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze Digital Footprint",
    description="""
    Main analysis endpoint that combines all services to provide a comprehensive
    digital footprint analysis. Accepts an identifier (username, email, phone, or name)
    with its type for targeted analysis.
    """
)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Perform comprehensive digital footprint analysis.
    
    This endpoint:
    1. Analyzes the identifier based on its type
    2. Generates platform URLs for username searches
    3. Creates variations to check for impersonation
    4. Extracts PII from the provided identifier
    5. Runs NER analysis for name-based searches
    6. Calculates a risk score based on exposure level
    
    Args:
        request: AnalyzeRequest containing identifier and identifier_type
    
    Returns:
        AnalyzeResponse: Comprehensive analysis results including:
            - Platform URLs
            - Identifier variations
            - Extracted PII
            - NER entities
            - Risk assessment
            - Recommendations
    
    Raises:
        HTTPException: 400 if identifier is empty or invalid
        HTTPException: 500 for internal processing errors
    """
    start_time = time.time()
    
    try:
        # ---------------------------------------------------------------------
        # Input Validation
        # ---------------------------------------------------------------------
        if not request.identifier or not request.identifier.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Identifier is required and cannot be empty"
            )
        
        identifier = request.identifier.strip()
        
        # ---------------------------------------------------------------------
        # Auto-detect Identifier Type (if not provided)
        # ---------------------------------------------------------------------
        identifier_type = request.identifier_type
        if identifier_type is None:
            identifier_type = detect_identifier_type(identifier)
        
        # ---------------------------------------------------------------------
        # Initialize Results
        # ---------------------------------------------------------------------
        platform_urls = []
        variations = []
        pattern_analysis = {}
        extracted_pii = {"emails": [], "phones": [], "urls": [], "mentions": []}
        ner_results = {"persons": [], "locations": [], "organizations": []}
        potential_exposures = []
        
        # Determine the display username (for results)
        display_username = identifier
        
        # ---------------------------------------------------------------------
        # Type-Specific Analysis
        # ---------------------------------------------------------------------
        
        if identifier_type == IdentifierType.USERNAME:
            # Username analysis
            username = identifier.lstrip('@')
            display_username = username
            
            # Generate platform URLs
            platform_urls = username_analyzer.generate_platform_urls(username)
            
            # Generate variations
            variations = username_analyzer.generate_variations(username)
            
            # Analyze patterns
            pattern_analysis = username_analyzer.analyze_patterns(username)
            
            # Generate exposure points for username
            potential_exposures = generate_username_exposures(username, platform_urls)
            
        elif identifier_type == IdentifierType.EMAIL:
            # Email analysis
            email = identifier.lower()
            display_username = email.split('@')[0]  # Use email prefix as display
            
            # Extract username from email for platform search
            email_username = email.split('@')[0]
            platform_urls = username_analyzer.generate_platform_urls(email_username)
            variations = username_analyzer.generate_variations(email_username)
            pattern_analysis = username_analyzer.analyze_patterns(email_username)
            
            # Add the email to extracted PII
            extracted_pii["emails"].append(email)
            
            # Generate exposure points for email
            potential_exposures = generate_email_exposures(email, email_username, platform_urls)
            
        elif identifier_type == IdentifierType.PHONE:
            # Phone number analysis
            phone = identifier
            
            # Normalize phone for display
            cleaned_phone = phone.replace(" ", "").replace("-", "")
            display_username = cleaned_phone
            
            # Add phone to extracted PII
            normalized_phone = pii_extractor.normalize_phone(phone)
            if normalized_phone:
                extracted_pii["phones"].append(normalized_phone)
            else:
                extracted_pii["phones"].append(phone)
            
            # Try to extract potential username from phone (last digits)
            if len(cleaned_phone) >= 4:
                phone_suffix = cleaned_phone[-4:]
                # Generate minimal platform URLs (phone-based search is limited)
                platform_urls = username_analyzer.generate_platform_urls(phone_suffix)
            
            pattern_analysis = {
                "has_numbers": True,
                "has_letters": False,
                "number_density": 1.0,
                "has_suspicious_patterns": False,
                "length": len(cleaned_phone)
            }
            
            # Generate exposure points for phone
            potential_exposures = generate_phone_exposures(phone, normalized_phone or phone)
            
        elif identifier_type == IdentifierType.NAME:
            # Name-based analysis
            name = identifier
            display_username = name.replace(" ", "_").lower()
            
            # Run NER analysis on the name
            ner_results = ner_engine.extract_entities(name)
            
            # Generate potential username variations from name
            name_parts = name.lower().split()
            if len(name_parts) >= 2:
                # Common username patterns from names
                potential_usernames = [
                    name_parts[0],  # firstname
                    name_parts[-1],  # lastname
                    f"{name_parts[0]}{name_parts[-1]}",  # firstnamelastname
                    f"{name_parts[0]}_{name_parts[-1]}",  # firstname_lastname
                    f"{name_parts[0]}.{name_parts[-1]}",  # firstname.lastname
                    f"{name_parts[0][0]}{name_parts[-1]}",  # flastname
                ]
                variations = list(set(potential_usernames))
                
                # Use first name for primary platform search
                platform_urls = username_analyzer.generate_platform_urls(name_parts[0])
            else:
                platform_urls = username_analyzer.generate_platform_urls(name.lower().replace(" ", ""))
                variations = [name.lower().replace(" ", ""), name.lower().replace(" ", "_")]
            
            pattern_analysis = username_analyzer.analyze_patterns(display_username)
            
            # Generate exposure points for name
            potential_exposures = generate_name_exposures(name, variations, platform_urls)
        
        # ---------------------------------------------------------------------
        # Risk Assessment
        # ---------------------------------------------------------------------
        risk_score, risk_level = calculate_risk_score(
            username=display_username,
            email_provided=(identifier_type == IdentifierType.EMAIL),
            phone_provided=(identifier_type == IdentifierType.PHONE),
            pattern_analysis=pattern_analysis,
            pii_count=len(extracted_pii.get("emails", [])) + len(extracted_pii.get("phones", []))
        )
        
        # ---------------------------------------------------------------------
        # Generate Recommendations
        # ---------------------------------------------------------------------
        recommendations = generate_recommendations(
            risk_level=risk_level,
            pattern_analysis=pattern_analysis,
            email_provided=(identifier_type == IdentifierType.EMAIL),
            phone_provided=(identifier_type == IdentifierType.PHONE),
            identifier_type=identifier_type.value
        )
        
        # ---------------------------------------------------------------------
        # Calculate Processing Time
        # ---------------------------------------------------------------------
        processing_time = round((time.time() - start_time) * 1000, 2)  # in ms
        
        # ---------------------------------------------------------------------
        # Build Response
        # ---------------------------------------------------------------------
        return AnalyzeResponse(
            identifier=identifier,
            identifier_type=identifier_type.value,
            platform_urls=platform_urls,
            variations=variations,
            pattern_analysis=pattern_analysis,
            extracted_pii=extracted_pii,
            potential_exposures=potential_exposures,
            ner_entities=ner_results,
            risk_score=risk_score,
            risk_level=risk_level,
            recommendations=recommendations,
            processing_time_ms=processing_time
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the error (in production, use proper logging)
        logger.error(f"Error in analyze endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during analysis: {str(e)}"
        )


# =============================================================================
# PII EXTRACTION ENDPOINT
# =============================================================================

@router.post(
    "/extract-pii",
    response_model=PIIExtractResponse,
    summary="Extract PII from Text",
    description="Extract personally identifiable information from provided text"
)
async def extract_pii(request: PIIExtractRequest) -> PIIExtractResponse:
    """
    Extract PII (Personally Identifiable Information) from text.
    
    Extracts:
    - Email addresses (RFC 5322 compliant)
    - Phone numbers (Sri Lankan formats - 07X, +94)
    - URLs (general and social media specific)
    - @mentions (social media handles)
    
    Args:
        request: PIIExtractRequest containing the text to analyze
    
    Returns:
        PIIExtractResponse: Extracted PII categorized by type
    
    Raises:
        HTTPException: 400 if text is empty
        HTTPException: 500 for internal processing errors
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text is required and cannot be empty"
            )
        
        # Extract all PII from the text
        extracted_pii = pii_extractor.extract_all(request.text)
        
        # Also run NER for additional entity extraction
        ner_results = ner_engine.extract_entities(request.text)
        
        return PIIExtractResponse(
            text=request.text,
            emails=extracted_pii.get("emails", []),
            phones=extracted_pii.get("phones", []),
            urls=extracted_pii.get("urls", []),
            mentions=extracted_pii.get("mentions", []),
            ner_entities=ner_results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in extract_pii endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during PII extraction: {str(e)}"
        )


# =============================================================================
# USERNAME ANALYSIS ENDPOINT
# =============================================================================

@router.post(
    "/analyze-username",
    response_model=UsernameAnalyzeResponse,
    summary="Analyze Username",
    description="Generate platform URLs and variations for a username"
)
async def analyze_username(request: UsernameAnalyzeRequest) -> UsernameAnalyzeResponse:
    """
    Analyze a username to generate platform URLs and variations.
    
    Generates:
    - Platform URLs for Facebook, Instagram, X, LinkedIn, TikTok, YouTube
    - Username variations (underscores, numbers, prefixes, suffixes)
    - Pattern analysis (suspicious patterns, number density)
    
    Args:
        request: UsernameAnalyzeRequest containing the username to analyze
    
    Returns:
        UsernameAnalyzeResponse: Platform URLs, variations, and pattern analysis
    
    Raises:
        HTTPException: 400 if username is empty or invalid
        HTTPException: 500 for internal processing errors
    """
    try:
        if not request.username or not request.username.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is required and cannot be empty"
            )
        
        username = request.username.strip()
        
        # Generate platform URLs
        platform_urls = username_analyzer.generate_platform_urls(username)
        
        # Generate variations
        variations = username_analyzer.generate_variations(username)
        
        # Analyze patterns
        pattern_analysis = username_analyzer.analyze_patterns(username)
        
        return UsernameAnalyzeResponse(
            username=username,
            platform_urls=platform_urls,
            variations=variations,
            pattern_analysis=pattern_analysis
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_username endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during username analysis: {str(e)}"
        )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def detect_identifier_type(identifier: str) -> IdentifierType:
    """
    Auto-detect the type of identifier based on its format.
    
    Detection rules (in order of priority):
    1. Email: Contains @ and valid domain pattern
    2. Phone: Mostly digits, matches phone patterns (Sri Lankan or international)
    3. Name: Contains spaces and mostly letters (likely a full name)
    4. Username: Default fallback
    
    Args:
        identifier: The identifier string to analyze
    
    Returns:
        IdentifierType: Detected type (EMAIL, PHONE, NAME, or USERNAME)
    """
    identifier = identifier.strip()
    
    # Email detection: contains @ with domain pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, identifier):
        return IdentifierType.EMAIL
    
    # Phone detection: Sri Lankan and international formats
    # Remove common separators for analysis
    cleaned = identifier.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Sri Lankan phone patterns
    # - 07XXXXXXXX (10 digits starting with 07)
    # - +947XXXXXXXX (12 chars starting with +94)
    # - 947XXXXXXXX (11 digits starting with 94)
    # - 00947XXXXXXXX (13 digits starting with 0094)
    sri_lankan_patterns = [
        r'^07\d{8}$',           # 07XXXXXXXX
        r'^\+947\d{8}$',        # +947XXXXXXXX
        r'^947\d{8}$',          # 947XXXXXXXX  
        r'^00947\d{8}$',        # 00947XXXXXXXX
        r'^0\d{9}$',            # 0XXXXXXXXX (other local)
    ]
    
    for pattern in sri_lankan_patterns:
        if re.match(pattern, cleaned):
            return IdentifierType.PHONE
    
    # International phone: mostly digits (at least 70% digits, 7+ digits)
    digit_count = sum(1 for c in cleaned if c.isdigit())
    if len(cleaned) >= 7 and digit_count / len(cleaned) >= 0.7:
        # Additional check: starts with + or digit
        if cleaned.startswith('+') or cleaned[0].isdigit():
            return IdentifierType.PHONE
    
    # Name detection: contains space(s) and mostly letters
    if ' ' in identifier:
        letter_count = sum(1 for c in identifier if c.isalpha() or c.isspace())
        if letter_count / len(identifier) >= 0.8:
            # Check if it looks like a name (2+ parts, each starting with letter)
            parts = identifier.split()
            if len(parts) >= 2 and all(part[0].isalpha() for part in parts if part):
                return IdentifierType.NAME
    
    # Default to username
    return IdentifierType.USERNAME


def calculate_risk_score(
    username: str,
    email_provided: bool,
    phone_provided: bool,
    pattern_analysis: Dict[str, Any],
    pii_count: int
) -> tuple:
    """
    Calculate risk score based on exposure factors.
    
    Risk factors considered:
    - Amount of PII provided/detected
    - Username patterns (suspicious patterns increase risk)
    - Number of platforms where username might exist
    
    Args:
        username: The username being analyzed
        email_provided: Whether email was provided
        phone_provided: Whether phone was provided
        pattern_analysis: Results from username pattern analysis
        pii_count: Total count of detected PII elements
    
    Returns:
        tuple: (risk_score: int 0-100, risk_level: str)
    """
    score = 0
    
    # Base score for having a username
    score += 10
    
    # Add points for each type of PII provided
    if email_provided:
        score += 15
    if phone_provided:
        score += 20
    
    # Add points based on detected PII count
    score += min(pii_count * 5, 20)
    
    # Add points for suspicious username patterns
    if pattern_analysis.get("has_suspicious_patterns", False):
        score += 10
    
    # Higher number density might indicate auto-generated username
    number_density = pattern_analysis.get("number_density", 0)
    if number_density > 0.3:
        score += 5
    
    # Username length affects uniqueness
    if len(username) < 5:
        score += 10  # Short usernames are more common, higher collision risk
    elif len(username) > 15:
        score -= 5  # Longer usernames are more unique
    
    # Cap score at 100
    score = min(max(score, 0), 100)
    
    # Determine risk level
    if score >= 70:
        risk_level = "high"
    elif score >= 40:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return score, risk_level


def generate_recommendations(
    risk_level: str,
    pattern_analysis: Dict[str, Any],
    email_provided: bool,
    phone_provided: bool,
    identifier_type: str = "username"
) -> list:
    """
    Generate personalized recommendations based on analysis results.
    
    Args:
        risk_level: Calculated risk level (low/medium/high)
        pattern_analysis: Results from username pattern analysis
        email_provided: Whether email was provided
        phone_provided: Whether phone was provided
        identifier_type: Type of identifier searched (username/email/phone/name)
    
    Returns:
        list: List of recommendation strings
    """
    recommendations = []
    
    # General recommendations
    recommendations.append(
        "Review privacy settings on all social media platforms"
    )
    
    # Risk-level specific recommendations
    if risk_level == "high":
        recommendations.append(
            "Consider using different usernames across platforms to reduce traceability"
        )
        recommendations.append(
            "Enable two-factor authentication on all accounts"
        )
    elif risk_level == "medium":
        recommendations.append(
            "Regularly search for your username to monitor for impersonation"
        )
    
    # Identifier-type specific recommendations
    if identifier_type == "email" or email_provided:
        recommendations.append(
            "Check if your email has been involved in data breaches at haveibeenpwned.com"
        )
        recommendations.append(
            "Consider using email aliases for different services"
        )
    
    if identifier_type == "phone" or phone_provided:
        recommendations.append(
            "Be cautious about sharing your phone number publicly"
        )
        recommendations.append(
            "Consider using a secondary number for online registrations"
        )
    
    if identifier_type == "name":
        recommendations.append(
            "Search for your name in quotes on search engines to find mentions"
        )
        recommendations.append(
            "Set up Google Alerts for your name to monitor new mentions"
        )
    
    # Pattern-specific recommendations
    if pattern_analysis.get("has_suspicious_patterns", False):
        recommendations.append(
            "Your username contains patterns often used by fake accounts - "
            "ensure you can prove account ownership"
        )
    
    # Always recommend privacy audit
    recommendations.append(
        "Conduct a periodic audit of what personal information is visible on your profiles"
    )
    
    return recommendations


def generate_username_exposures(username: str, platform_urls: Dict) -> List[Dict[str, Any]]:
    """
    Generate potential exposure points for a username.
    
    Args:
        username: The username being analyzed
        platform_urls: Generated platform URLs
    
    Returns:
        List of exposure dictionaries
    """
    exposures = []
    
    # Social media exposures
    for platform, data in platform_urls.items():
        exposures.append({
            "type": "social_media",
            "source": data.get("name", platform.capitalize()),
            "risk": "medium",
            "description": f"Profile may exist on {data.get('name', platform.capitalize())}",
            "url": data.get("url", ""),
            "icon": platform
        })
    
    # Search engine exposure
    exposures.append({
        "type": "search_engine",
        "source": "Google",
        "risk": "low",
        "description": f"Username '{username}' may appear in search results",
        "url": f"https://www.google.com/search?q=%22{username}%22",
        "icon": "search"
    })
    
    # Data broker/people search sites
    exposures.append({
        "type": "data_broker",
        "source": "People Search Sites",
        "risk": "medium",
        "description": "Username may be indexed by people search services",
        "url": "",
        "icon": "database"
    })
    
    return exposures


def generate_email_exposures(email: str, email_username: str, platform_urls: Dict) -> List[Dict[str, Any]]:
    """
    Generate potential exposure points for an email address.
    
    Args:
        email: The full email address
        email_username: Username part of email
        platform_urls: Generated platform URLs
    
    Returns:
        List of exposure dictionaries
    """
    exposures = []
    
    # Data breach exposure - HIGH PRIORITY
    exposures.append({
        "type": "data_breach",
        "source": "Have I Been Pwned",
        "risk": "high",
        "description": "Check if email appears in known data breaches",
        "url": f"https://haveibeenpwned.com/account/{email}",
        "icon": "alert"
    })
    
    # Gravatar/profile picture lookup
    exposures.append({
        "type": "profile_image",
        "source": "Gravatar",
        "risk": "low",
        "description": "Profile picture may be linked to this email",
        "url": f"https://www.gravatar.com/{email}",
        "icon": "image"
    })
    
    # Social media (using email username)
    for platform, data in platform_urls.items():
        exposures.append({
            "type": "social_media",
            "source": data.get("name", platform.capitalize()),
            "risk": "medium",
            "description": f"Account may be registered with username '{email_username}'",
            "url": data.get("url", ""),
            "icon": platform
        })
    
    # Email search
    exposures.append({
        "type": "search_engine",
        "source": "Google",
        "risk": "medium",
        "description": f"Email '{email}' may appear in search results or leaked databases",
        "url": f"https://www.google.com/search?q=%22{email}%22",
        "icon": "search"
    })
    
    # Pastebin/paste sites
    exposures.append({
        "type": "paste_site",
        "source": "Paste Sites",
        "risk": "high",
        "description": "Email may appear in publicly shared data dumps",
        "url": "",
        "icon": "file"
    })
    
    return exposures


def generate_phone_exposures(phone: str, normalized_phone: str) -> List[Dict[str, Any]]:
    """
    Generate potential exposure points for a phone number.
    
    Args:
        phone: Original phone number input
        normalized_phone: Normalized phone number
    
    Returns:
        List of exposure dictionaries
    """
    exposures = []
    
    # WhatsApp lookup
    exposures.append({
        "type": "messaging",
        "source": "WhatsApp",
        "risk": "medium",
        "description": "Phone may be linked to a WhatsApp account",
        "url": f"https://wa.me/{normalized_phone.replace('+', '')}",
        "icon": "whatsapp"
    })
    
    # Viber (popular in Sri Lanka)
    exposures.append({
        "type": "messaging",
        "source": "Viber",
        "risk": "medium",
        "description": "Phone may be linked to a Viber account",
        "url": "",
        "icon": "viber"
    })
    
    # Telegram
    exposures.append({
        "type": "messaging",
        "source": "Telegram",
        "risk": "medium",
        "description": "Phone may be linked to a Telegram account",
        "url": "",
        "icon": "telegram"
    })
    
    # Truecaller lookup
    exposures.append({
        "type": "caller_id",
        "source": "Truecaller",
        "risk": "high",
        "description": "Name and details may be visible in Truecaller database",
        "url": f"https://www.truecaller.com/search/lk/{phone.replace('+', '')}",
        "icon": "phone"
    })
    
    # Search engine
    exposures.append({
        "type": "search_engine",
        "source": "Google",
        "risk": "medium",
        "description": f"Phone number may appear in search results or directories",
        "url": f"https://www.google.com/search?q=%22{phone}%22",
        "icon": "search"
    })
    
    # Classified ads / directories
    exposures.append({
        "type": "directory",
        "source": "Online Directories",
        "risk": "medium",
        "description": "Number may be listed in business directories or classified ads",
        "url": "",
        "icon": "directory"
    })
    
    # Social media phone lookup
    exposures.append({
        "type": "social_media",
        "source": "Facebook",
        "risk": "medium",
        "description": "Account may be discoverable via phone number",
        "url": "",
        "icon": "facebook"
    })
    
    return exposures


def generate_name_exposures(name: str, variations: List[str], platform_urls: Dict) -> List[Dict[str, Any]]:
    """
    Generate potential exposure points for a name.
    
    Args:
        name: The full name
        variations: Username variations from name
        platform_urls: Generated platform URLs
    
    Returns:
        List of exposure dictionaries
    """
    exposures = []
    
    # Google search
    exposures.append({
        "type": "search_engine",
        "source": "Google",
        "risk": "medium",
        "description": f"Search results for '{name}'",
        "url": f"https://www.google.com/search?q=%22{name.replace(' ', '+')}%22",
        "icon": "search"
    })
    
    # Social media profiles
    for platform, data in platform_urls.items():
        exposures.append({
            "type": "social_media",
            "source": data.get("name", platform.capitalize()),
            "risk": "medium",
            "description": f"Profile may exist with name-based username",
            "url": data.get("url", ""),
            "icon": platform
        })
    
    # LinkedIn (professional)
    exposures.append({
        "type": "professional",
        "source": "LinkedIn",
        "risk": "medium",
        "description": "Professional profile may exist",
        "url": f"https://www.linkedin.com/search/results/all/?keywords={name.replace(' ', '%20')}",
        "icon": "linkedin"
    })
    
    # News mentions
    exposures.append({
        "type": "news",
        "source": "Google News",
        "risk": "low",
        "description": "Name may appear in news articles",
        "url": f"https://news.google.com/search?q=%22{name.replace(' ', '+')}%22",
        "icon": "news"
    })
    
    # Academic/research
    exposures.append({
        "type": "academic",
        "source": "Google Scholar",
        "risk": "low",
        "description": "Name may appear in academic publications",
        "url": f"https://scholar.google.com/scholar?q=%22{name.replace(' ', '+')}%22",
        "icon": "academic"
    })
    
    # Public records
    exposures.append({
        "type": "public_records",
        "source": "Public Records",
        "risk": "medium",
        "description": "Name may appear in public government records",
        "url": "",
        "icon": "government"
    })
    
    return exposures


# =============================================================================
# TRANSLITERATION ENDPOINT (Phase 2)
# =============================================================================

@router.post(
    "/transliterate",
    response_model=TransliterateResponse,
    summary="Transliterate Sinhala Text",
    description="""
    Transliterate Sinhala text to romanized English variants.
    
    This endpoint:
    - Detects if the input contains Sinhala characters
    - Converts Sinhala text to romanized English
    - Generates spelling variants for fuzzy matching
    - Supports names and locations from Sri Lankan context
    """
)
async def transliterate(request: TransliterateRequest) -> TransliterateResponse:
    """
    Transliterate Sinhala text to English variants.
    
    The transliteration engine:
    1. Detects Sinhala Unicode characters (U+0D80-U+0DFF)
    2. Looks up known names and locations in dictionaries
    3. Performs character-by-character transliteration for unknown words
    4. Generates spelling variants based on common romanization patterns
    
    Args:
        request: TransliterateRequest containing Sinhala text
    
    Returns:
        TransliterateResponse: Original text, detection result, and transliterations
    
    Raises:
        HTTPException: 400 if text is empty
        HTTPException: 500 for internal processing errors
    
    Example:
        Input: {"text": "සුනිල් පෙරේරා", "include_variants": true}
        Output: {
            "original": "සුනිල් පෙරේරා",
            "is_sinhala": true,
            "transliterations": ["sunil perera"],
            "variants": ["suneel perera", "sunil pereera", ...]
        }
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text is required and cannot be empty"
            )
        
        text = request.text.strip()
        
        # Check if text contains Sinhala
        is_sinhala = sinhala_transliterator.is_sinhala(text)
        
        # Perform transliteration
        transliterations = sinhala_transliterator.transliterate(text)
        
        # Separate primary transliterations from variants
        if transliterations:
            primary = transliterations[:1]  # First result is primary
            variants = transliterations[1:] if request.include_variants else []
        else:
            primary = [text.lower()] if not is_sinhala else []
            variants = []
        
        return TransliterateResponse(
            original=text,
            is_sinhala=is_sinhala,
            transliterations=primary,
            variants=variants
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in transliterate endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during transliteration: {str(e)}"
        )


# =============================================================================
# CORRELATION ENDPOINT (Phase 2)
# =============================================================================

@router.post(
    "/correlate",
    response_model=CorrelationResponse,
    summary="Correlate Profiles Across Platforms",
    description="""
    Correlate profiles from multiple social media platforms to detect
    impersonation and analyze digital footprint consistency.
    
    This endpoint:
    - Compares profile information across platforms
    - Identifies matching information (overlaps)
    - Detects conflicting information (contradictions)
    - Calculates impersonation risk score
    - Provides warning flags and recommendations
    """
)
async def correlate_profiles(request: CorrelationRequest) -> CorrelationResponse:
    """
    Correlate profiles across platforms for impersonation detection.
    
    The correlation engine:
    1. Compares usernames using fuzzy matching for typosquatting detection
    2. Compares names, bios, locations, and contact information
    3. Identifies overlaps (matching info) and contradictions (conflicting info)
    4. Calculates an impersonation risk score based on findings
    5. Generates warning flags and actionable recommendations
    
    Args:
        request: CorrelationRequest containing list of platform profiles
    
    Returns:
        CorrelationResponse: Complete correlation analysis results
    
    Raises:
        HTTPException: 400 if fewer than 2 profiles provided
        HTTPException: 500 for internal processing errors
    
    Example:
        Input: {
            "profiles": [
                {"source": "facebook", "username": "john_doe", "name": "John Doe"},
                {"source": "twitter", "username": "johndoe", "name": "John Doe"}
            ]
        }
        Output: {
            "overlaps": [...],
            "contradictions": [...],
            "impersonation_score": 15,
            "impersonation_level": "low",
            "flags": [],
            "recommendations": [...]
        }
    """
    try:
        if not request.profiles or len(request.profiles) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least 2 profiles are required for correlation"
            )
        
        # Convert Pydantic models to dicts for the correlator
        profiles_dict = [p.model_dump() for p in request.profiles]
        
        # Perform correlation analysis
        result = cross_platform_correlator.correlate(profiles_dict)
        
        return CorrelationResponse(
            overlaps=result.overlaps,
            contradictions=result.contradictions,
            impersonation_score=result.impersonation_score,
            impersonation_level=result.impersonation_level,
            flags=result.flags,
            recommendations=result.recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in correlate_profiles endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during correlation: {str(e)}"
        )


# =============================================================================
# PROFILE URL GENERATION ENDPOINT (Phase 3)
# =============================================================================

@router.post(
    "/generate-profile-urls",
    response_model=ProfileURLResponse,
    summary="Generate Profile URLs",
    description="""
    Generate direct profile URLs for a username across all supported
    social media platforms (Facebook, Instagram, LinkedIn, X).
    
    Optionally includes username variations for comprehensive searching.
    """
)
async def generate_profile_urls(request: ProfileURLRequest) -> ProfileURLResponse:
    """
    Generate profile URLs for all supported platforms.
    
    Args:
        request: ProfileURLRequest containing username and options
    
    Returns:
        ProfileURLResponse: URLs for all platforms and optional variations
    
    Example:
        Input: {"username": "john_doe", "include_variations": true}
        Output: {"username": "john_doe", "urls": {...}, "variations": [...]}
    """
    try:
        username = request.username
        
        # Generate URLs for all platforms
        urls = profile_url_generator.generate_urls(username)
        
        # Generate variations if requested
        variations = None
        if request.include_variations:
            variations = profile_url_generator.generate_variations(username)
        
        return ProfileURLResponse(
            username=username,
            urls=urls,
            variations=variations
        )
        
    except Exception as e:
        logger.error(f"Error in generate_profile_urls endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during URL generation: {str(e)}"
        )


# =============================================================================
# PROFILE CHECK ENDPOINT (Phase 3)
# =============================================================================

@router.post(
    "/check-profiles",
    response_model=ProfileCheckResponse,
    summary="Check Profile Existence",
    description="""
    Check if profiles exist on specified or all supported platforms.
    
    Returns status for each platform: exists, not_found, private, or error.
    """
)
async def check_profiles(request: ProfileCheckRequest) -> ProfileCheckResponse:
    """
    Check if profiles exist on social media platforms.
    
    Args:
        request: ProfileCheckRequest containing username and optional platforms
    
    Returns:
        ProfileCheckResponse: Check results for each platform
    
    Example:
        Input: {"username": "john_doe", "platforms": ["instagram", "facebook"]}
        Output: {"username": "john_doe", "results": {...}, "summary": {...}}
    """
    try:
        result = await profile_checker.check_all_platforms(
            request.username,
            request.platforms
        )
        
        return ProfileCheckResponse(
            username=result["username"],
            results=result["results"],
            summary=result["summary"]
        )
        
    except Exception as e:
        logger.error(f"Error in check_profiles endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during profile checking: {str(e)}"
        )


# =============================================================================
# DATA COLLECTION ENDPOINT (Phase 3)
# =============================================================================

@router.post(
    "/collect-profile-data",
    response_model=DataCollectionResponse,
    summary="Collect Profile Data",
    description="""
    Collect public data from a social media profile page.
    
    Extracts name, bio, profile image, and location from Open Graph meta tags.
    """
)
async def collect_profile_data(request: DataCollectionRequest) -> DataCollectionResponse:
    """
    Collect public data from a profile URL.
    
    Args:
        request: DataCollectionRequest containing URL and platform
    
    Returns:
        DataCollectionResponse: Extracted profile data
    
    Example:
        Input: {"url": "https://instagram.com/john_doe/", "source": "instagram"}
        Output: {"name": "John Doe", "bio": "...", "profile_image": "...", ...}
    """
    try:
        result = await data_collector.collect_profile_data(
            request.url,
            request.platform
        )
        
        return DataCollectionResponse(
            url=result["url"],
            platform=result["platform"],
            name=result["name"],
            bio=result["bio"],
            profile_image=result["profile_image"],
            location=result["location"],
            success=result["success"],
            error=result["error"]
        )
        
    except Exception as e:
        logger.error(f"Error in collect_profile_data endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during data collection: {str(e)}"
        )


# =============================================================================
# PHONE LOOKUP ENDPOINT (Phase 3)
# =============================================================================

@router.post(
    "/phone-lookup",
    response_model=PhoneLookupResponse,
    summary="Phone Number Lookup",
    description="""
    Lookup Sri Lankan phone number information.
    
    Validates the number, identifies carrier/region, and provides
    formatted versions (E.164, local, international).
    """
)
async def phone_lookup_endpoint(request: PhoneLookupRequest) -> PhoneLookupResponse:
    """
    Perform Sri Lankan phone number lookup.
    
    Args:
        request: PhoneLookupRequest containing the phone number
    
    Returns:
        PhoneLookupResponse: Validation and carrier information
    
    Example:
        Input: {"phone": "0771234567"}
        Output: {
            "valid": true,
            "type": "mobile",
            "carrier": "Dialog",
            "e164_format": "+94771234567",
            ...
        }
    """
    try:
        result = phone_lookup.lookup(request.phone)
        
        return PhoneLookupResponse(
            original=result["original"],
            valid=result["valid"],
            type=result["type"],
            carrier=result["carrier"],
            e164_format=result["e164_format"],
            local_format=result["local_format"],
            international_format=result["international_format"],
            error=result["error"]
        )
        
    except Exception as e:
        logger.error(f"Error in phone_lookup endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during phone lookup: {str(e)}"
        )


# =============================================================================
# FULL SCAN ENDPOINT (Phase 3)
# =============================================================================

@router.post(
    "/full-scan",
    response_model=FullScanResponse,
    summary="Full Digital Footprint Scan",
    description="""
    Perform a comprehensive digital footprint scan including:
    - Profile URL generation for all platforms
    - Profile existence checking
    - Phone number analysis (if provided)
    - PII analysis from email/name (if provided)
    - Risk assessment and recommendations
    """
)
async def full_scan(request: FullScanRequest) -> FullScanResponse:
    """
    Perform comprehensive digital footprint scan.
    
    Combines all available analysis methods for a complete assessment.
    
    Args:
        request: FullScanRequest with username and optional phone/email/name
    
    Returns:
        FullScanResponse: Complete analysis results
    
    Example:
        Input: {
            "username": "john_doe",
            "phone": "0771234567",
            "email": "john@example.com"
        }
        Output: {
            "profile_urls": {...},
            "profile_existence": {...},
            "phone_analysis": {...},
            "risk_score": 45,
            "recommendations": [...]
        }
    """
    try:
        start_time = time.time()
        
        # Generate profile URLs
        profile_urls = profile_url_generator.generate_urls(request.username)
        
        # Check profile existence
        existence_result = await profile_checker.check_all_platforms(request.username)
        
        # Phone analysis if provided
        phone_analysis = None
        if request.phone:
            phone_analysis = phone_lookup.lookup(request.phone)
        
        # PII analysis if email or name provided
        pii_analysis = None
        if request.email or request.name:
            pii_text = ""
            if request.email:
                pii_text += f" {request.email}"
            if request.name:
                pii_text += f" {request.name}"
            
            pii_extracted = pii_extractor.extract_all(pii_text.strip())
            ner_results = ner_engine.extract_entities(pii_text.strip())
            
            pii_analysis = {
                "extracted_pii": pii_extracted,
                "ner_entities": ner_results
            }
        
        # Calculate risk score
        risk_score = _calculate_full_scan_risk(
            existence_result=existence_result,
            phone_analysis=phone_analysis,
            pii_analysis=pii_analysis
        )
        
        # Generate recommendations
        recommendations = _generate_full_scan_recommendations(
            existence_result=existence_result,
            phone_analysis=phone_analysis,
            pii_analysis=pii_analysis,
            risk_score=risk_score
        )
        
        return FullScanResponse(
            profile_urls=profile_urls,
            profile_existence=existence_result,
            phone_analysis=phone_analysis,
            pii_analysis=pii_analysis,
            risk_score=risk_score,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error in full_scan endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during full scan: {str(e)}"
        )


def _calculate_full_scan_risk(
    existence_result: Dict[str, Any],
    phone_analysis: Dict[str, Any] = None,
    pii_analysis: Dict[str, Any] = None
) -> int:
    """
    Calculate risk score for full scan.
    
    Factors:
    - Number of platforms where profile exists
    - Phone number validity and exposure
    - PII found in provided data
    """
    score = 10  # Base score
    
    # Add points for existing profiles
    if existence_result:
        summary = existence_result.get("summary", {})
        exists_count = summary.get("exists", 0)
        score += exists_count * 10  # 10 points per existing profile
    
    # Add points for phone number exposure
    if phone_analysis and phone_analysis.get("valid"):
        score += 15
    
    # Add points for PII
    if pii_analysis:
        extracted = pii_analysis.get("extracted_pii", {})
        if extracted.get("emails"):
            score += 10
        if extracted.get("phones"):
            score += 10
    
    return min(score, 100)


def _generate_full_scan_recommendations(
    existence_result: Dict[str, Any],
    phone_analysis: Dict[str, Any] = None,
    pii_analysis: Dict[str, Any] = None,
    risk_score: int = 0
) -> List[str]:
    """
    Generate recommendations based on full scan results.
    """
    recommendations = []
    
    # General recommendation
    recommendations.append(
        "Review privacy settings on all identified social media profiles"
    )
    
    # Profile-based recommendations
    if existence_result:
        summary = existence_result.get("summary", {})
        if summary.get("exists", 0) >= 3:
            recommendations.append(
                "Consider using unique usernames across platforms to reduce traceability"
            )
    
    # Phone-based recommendations
    if phone_analysis and phone_analysis.get("valid"):
        recommendations.append(
            "Be cautious about linking your phone number to social media accounts"
        )
        recommendations.append(
            "Consider using a secondary number for online registrations"
        )
    
    # Risk-based recommendations
    if risk_score >= 70:
        recommendations.append(
            "High exposure detected - enable two-factor authentication on all accounts"
        )
        recommendations.append(
            "Consider conducting a comprehensive privacy audit"
        )
    elif risk_score >= 40:
        recommendations.append(
            "Regularly search for your username to monitor for impersonation"
        )
    
    # Always recommend periodic audit
    recommendations.append(
        "Conduct periodic audits of what personal information is publicly visible"
    )
    
    return recommendations


# =============================================================================
# EXPOSURE SCAN ENDPOINT (Phase 3 Enhancement)
# =============================================================================

@router.post(
    "/exposure-scan",
    response_model=ExposureScanResponse,
    summary="PII Exposure Scan",
    description="""
    Perform a comprehensive PII exposure scan across social media platforms.
    
    This enhanced endpoint:
    1. Generates profile URLs for the provided username
    2. Checks profile existence on each platform
    3. Scrapes existing profiles for public data
    4. Extracts ALL PII from scraped data
    5. Matches exposed data to user's provided identifiers
    6. Returns a clear list of exactly what PII is exposed and where
    
    Returns detailed exposure report showing:
    - Exactly what PII is exposed
    - Which platforms expose each piece of PII
    - Risk levels for each exposed item
    - Whether exposed data matches user-provided identifiers
    - Actionable recommendations
    """
)
async def exposure_scan(request: ExposureScanRequest) -> ExposureScanResponse:
    """
    Perform comprehensive PII exposure scan.
    
    This endpoint analyzes a user's digital footprint across social media
    platforms and shows exactly what personal information is publicly exposed.
    
    Args:
        request: ExposureScanRequest with username and optional phone/email/name
    
    Returns:
        ExposureScanResponse: Complete exposure analysis with clear PII listing
    
    Example:
        Input: {
            "username": "johnperera",
            "phone": "0771234567",
            "email": "john@gmail.com"
        }
        Output: {
            "exposure_score": 72,
            "risk_level": "high",
            "exposed_pii": [
                {"type": "phone", "value": "+94 77 123 4567", ...},
                {"type": "email", "value": "john@gmail.com", ...}
            ],
            ...
        }
    """
    try:
        # Build user identifiers dict
        user_identifiers = {
            "username": request.username
        }
        if request.phone:
            user_identifiers["phone"] = request.phone
        if request.email:
            user_identifiers["email"] = request.email
        if request.name:
            user_identifiers["name"] = request.name
        
        # Scrape all platforms for the username
        platform_data = await scrape_all_platforms(request.username)
        
        # Analyze PII exposure
        exposure_report = exposure_analyzer.analyze(platform_data, user_identifiers)
        
        # Phone analysis if provided
        phone_analysis_result = None
        if request.phone:
            phone_analysis_result = phone_lookup.lookup(request.phone)
        
        # Convert exposed_pii to ExposedPIIItem models
        exposed_pii_items = [
            ExposedPIIItem(
                type=item["type"],
                value=item["value"],
                platforms=item["platforms"],
                platform_count=item["platform_count"],
                risk_level=item["risk_level"],
                matches_user_input=item["matches_user_input"]
            )
            for item in exposure_report.get("exposed_pii", [])
        ]
        
        # Convert platform_breakdown to PlatformExposure models
        platform_breakdown = {}
        for platform, breakdown in exposure_report.get("platform_breakdown", {}).items():
            platform_items = [
                ExposedPIIItem(
                    type=item["type"],
                    value=item["value"],
                    platforms=item["platforms"],
                    platform_count=item["platform_count"],
                    risk_level=item["risk_level"],
                    matches_user_input=item["matches_user_input"]
                )
                for item in breakdown.get("exposed_items", [])
            ]
            platform_breakdown[platform] = PlatformExposure(
                platform=breakdown["platform"],
                status=breakdown["status"],
                url=breakdown["url"],
                exposed_count=breakdown["exposed_count"],
                exposed_items=platform_items
            )
        
        return ExposureScanResponse(
            user_identifiers=user_identifiers,
            scan_timestamp=exposure_report["scan_timestamp"],
            platforms_checked=exposure_report["platforms_checked"],
            profiles_found=exposure_report["profiles_found"],
            profiles_not_found=exposure_report["profiles_not_found"],
            exposure_score=exposure_report["exposure_score"],
            risk_level=exposure_report["risk_level"],
            total_exposed_items=exposure_report["total_exposed_items"],
            exposed_pii=exposed_pii_items,
            platform_breakdown=platform_breakdown,
            phone_analysis=phone_analysis_result,
            recommendations=exposure_report["recommendations"]
        )
        
    except Exception as e:
        logger.error(f"Error in exposure_scan endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during exposure scan: {str(e)}"
        )


# =============================================================================
# FLEXIBLE SCAN ENDPOINT (Hybrid Profile Discovery)
# =============================================================================

@router.post(
    "/scan",
    response_model=FlexibleScanResponse,
    summary="Flexible Profile Scan",
    description="""
    Hybrid profile discovery endpoint that combines Google Dorking with 
    direct URL checking.
    
    Users can provide any single identifier:
    - **name**: Full name (e.g., "John Perera") - searches with location filter
    - **email**: Email address (e.g., "john@gmail.com") - extracts username
    - **username**: Social media handle (e.g., "john_doe") - generates variations
    - **phone**: Sri Lankan phone number (e.g., "0771234567") - various formats
    
    This endpoint performs:
    1. Google Dork query generation for each supported platform
    2. Username variation generation (from name/email)
    3. Direct URL checking to verify profile existence
    4. Result deduplication and combination
    
    No authentication needed - uses public Google search.
    Sri Lanka focused with location filtering.
    """
)
async def flexible_scan(request: FlexibleScanRequest) -> FlexibleScanResponse:
    """
    Perform hybrid profile discovery scan.
    
    Combines Google Dorking and direct URL checking to discover
    social media profiles for any identifier type.
    
    Args:
        request: FlexibleScanRequest containing identifier_type and identifier_value
    
    Returns:
        FlexibleScanResponse: Comprehensive profile discovery results
    
    Example:
        Input: {"identifier_type": "username", "identifier_value": "john_doe"}
        Output: {
            "identifier": "john_doe",
            "identifier_type": "username",
            "combined_results": {
                "found_profiles": [...],
                "by_platform": {...}
            },
            "summary": {
                "total_profiles_found": 3,
                "platforms_with_profiles": 2
            }
        }
    """
    try:
        # Perform hybrid profile discovery
        result = await hybrid_profile_finder.find_profiles(
            identifier=request.identifier_value,
            identifier_type=request.identifier_type.value,
            location=request.location,
            check_existence=request.check_existence
        )
        
        return FlexibleScanResponse(
            identifier=result["identifier"],
            identifier_type=result["identifier_type"],
            timestamp=result["timestamp"],
            location_filter=result["location_filter"],
            dork_results=result["dork_results"],
            direct_check_results=result["direct_check_results"],
            combined_results=result["combined_results"],
            username_variations=result["username_variations"],
            platforms_checked=result["platforms_checked"],
            summary=result["summary"]
        )
        
    except Exception as e:
        logger.error(f"Error in flexible_scan endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during profile scan: {str(e)}"
        )


# =============================================================================
# ENHANCED SCAN ENDPOINT (Phase 4 - Report Presentation & PDF Export)
# =============================================================================

@router.post(
    "/enhanced-scan",
    response_model=AnalysisReportResponse,
    summary="Enhanced Profile Scan with Report",
    description="""
    Comprehensive scan with enhanced report presentation.
    
    This endpoint performs:
    1. Profile discovery across Facebook, Instagram, LinkedIn, and X
    2. PII exposure analysis
    3. Impersonation detection
    4. Risk assessment
    5. Comprehensive report generation with PDF export
    
    Only supports 3 identifier types: name, email, username (NO phone).
    Only checks 4 platforms: Facebook, Instagram, LinkedIn, X (NO YouTube, TikTok).
    
    Returns a detailed report with complete findings and export URLs.
    """
)
async def enhanced_scan(request: EnhancedScanRequest) -> AnalysisReportResponse:
    """
    Perform enhanced scan with comprehensive report generation.
    
    Args:
        request: EnhancedScanRequest with identifier_type and identifier_value
        
    Returns:
        AnalysisReportResponse: Comprehensive report with all findings
    """
    try:
        # Build user identifiers dict
        user_identifiers = {
            "location": request.location or "Sri Lanka"
        }
        
        # Set identifier based on type
        if request.identifier_type.value == "username":
            user_identifiers["username"] = request.identifier_value.lstrip('@')
        elif request.identifier_type.value == "email":
            user_identifiers["email"] = request.identifier_value.lower()
            # Extract username from email
            user_identifiers["username"] = request.identifier_value.split('@')[0]
        elif request.identifier_type.value == "name":
            user_identifiers["name"] = request.identifier_value
            # Generate username from name
            name_parts = request.identifier_value.lower().split()
            if len(name_parts) >= 2:
                user_identifiers["username"] = f"{name_parts[0]}{name_parts[-1]}"
            else:
                user_identifiers["username"] = name_parts[0] if name_parts else request.identifier_value.lower().replace(" ", "")
        
        username = user_identifiers.get("username", "")
        
        # Step 1: Scrape all platforms for profile data
        platform_data = await scrape_all_platforms(username)
        
        # Step 2: Analyze PII exposure
        exposure_report = exposure_analyzer.analyze(platform_data, user_identifiers)
        
        # Step 3: Detect impersonation risks
        impersonation_risks = impersonation_detector.detect(platform_data, user_identifiers)
        
        # Step 4: Build comprehensive report
        report = report_builder.build_report(
            scan_results=exposure_report,
            user_identifiers=user_identifiers,
            impersonation_risks=impersonation_risks
        )
        
        # Store report in cache for PDF generation
        report_cache[report["report_id"]] = report
        
        # Convert to response model
        return AnalysisReportResponse(
            success=report["success"],
            report_id=report["report_id"],
            generated_at=report["generated_at"],
            identifier=report["identifier"],
            risk_assessment=report["risk_assessment"],
            impersonation_risks=[
                ImpersonationRisk(
                    platform=r["platform"],
                    profile_url=r["profile_url"],
                    profile_name=r["profile_name"],
                    risk_level=r["risk_level"],
                    risk_emoji=r["risk_emoji"],
                    confidence_score=r["confidence_score"],
                    indicators=r["indicators"],
                    recommendation=r["recommendation"],
                    report_url=r["report_url"]
                )
                for r in report.get("impersonation_risks", [])
            ],
            exposed_pii=report["exposed_pii"],
            platforms=report["platforms"],
            recommendations=report["recommendations"],
            cross_language=report.get("cross_language"),
            complete_findings=CompleteFindings(
                discovered_profiles=report["complete_findings"]["discovered_profiles"],
                exposed_pii_details=report["complete_findings"]["exposed_pii_details"]
            ),
            summary=ReportSummary(
                total_platforms_checked=report["summary"]["total_platforms_checked"],
                total_profiles_found=report["summary"]["total_profiles_found"],
                total_pii_exposed=report["summary"]["total_pii_exposed"],
                critical_high_risk_items=report["summary"]["critical_high_risk_items"],
                medium_risk_items=report["summary"]["medium_risk_items"],
                low_risk_items=report["summary"]["low_risk_items"],
                impersonation_risks_detected=report["summary"]["impersonation_risks_detected"],
                profile_links=report["summary"]["profile_links"]
            ),
            export=report["export"]
        )
        
    except Exception as e:
        logger.error(f"Error in enhanced_scan endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during enhanced scan: {str(e)}"
        )


# =============================================================================
# PDF REPORT DOWNLOAD ENDPOINT (Phase 4)
# =============================================================================

@router.get(
    "/report/{report_id}/pdf",
    summary="Download PDF Report",
    description="Download the analysis report as a PDF file."
)
async def download_pdf_report(report_id: str):
    """
    Download analysis report as PDF.
    
    Args:
        report_id: The unique report identifier
        
    Returns:
        StreamingResponse: PDF file download
        
    Raises:
        HTTPException: 404 if report not found
    """
    try:
        # Check if report exists in cache
        if report_id not in report_cache:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report with ID '{report_id}' not found. Reports are only available for a limited time after generation."
            )
        
        report_data = report_cache[report_id]
        
        # Generate PDF
        pdf_bytes = pdf_generator.generate(report_data)
        
        # Create streaming response
        buffer = io.BytesIO(pdf_bytes)
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=digital-footprint-report-{report_id[:8]}.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred generating the PDF report: {str(e)}"
        )


@router.get(
    "/report/{report_id}/json",
    summary="Download JSON Report",
    description="Download the analysis report as a JSON file."
)
async def download_json_report(report_id: str):
    """
    Download analysis report as JSON.
    
    Args:
        report_id: The unique report identifier
        
    Returns:
        StreamingResponse: JSON file download
        
    Raises:
        HTTPException: 404 if report not found
    """
    import json
    
    try:
        # Check if report exists in cache
        if report_id not in report_cache:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report with ID '{report_id}' not found. Reports are only available for a limited time after generation."
            )
        
        report_data = report_cache[report_id]
        
        # Convert to JSON
        json_str = json.dumps(report_data, indent=2, ensure_ascii=False)
        
        # Create streaming response
        buffer = io.BytesIO(json_str.encode('utf-8'))
        
        return StreamingResponse(
            buffer,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=digital-footprint-report-{report_id[:8]}.json"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating JSON report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred generating the JSON report: {str(e)}"
        )
