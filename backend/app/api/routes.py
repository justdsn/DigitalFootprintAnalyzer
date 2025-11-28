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

Each endpoint includes comprehensive error handling and validation.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import time
import logging

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
    CorrelateRequest,
    CorrelateResponse
)

# Import services
from app.services.pii_extractor import PIIExtractor
from app.services.ner_engine import NEREngine
from app.services.username_analyzer import UsernameAnalyzer
from app.services.transliteration import SinhalaTransliterator
from app.services.correlation import Correlator


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
correlator = Correlator()


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
        version="1.0.0",
        services={
            "pii_extractor": "operational",
            "ner_engine": "operational",
            "username_analyzer": "operational"
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
        identifier_type = request.identifier_type
        
        # ---------------------------------------------------------------------
        # Initialize Results
        # ---------------------------------------------------------------------
        platform_urls = []
        variations = []
        pattern_analysis = {}
        extracted_pii = {"emails": [], "phones": [], "urls": [], "mentions": []}
        ner_results = {"persons": [], "locations": [], "organizations": []}
        
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
                "has_suspicious_patterns": False
            }
            
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
            username=display_username,
            platform_urls=platform_urls,
            variations=variations,
            pattern_analysis=pattern_analysis,
            extracted_pii=extracted_pii,
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


# =============================================================================
# TRANSLITERATION ENDPOINT
# =============================================================================

@router.post(
    "/transliterate",
    response_model=TransliterateResponse,
    summary="Transliterate Sinhala Text",
    description="""
    Convert Sinhala Unicode text to romanized English spellings.
    
    This endpoint:
    1. Detects if the input contains Sinhala characters
    2. Converts Sinhala text to romanized English
    3. Generates multiple spelling variants
    
    Useful for searching Sri Lankan names and places that may be
    written in either Sinhala script or various English spellings.
    """
)
async def transliterate(request: TransliterateRequest) -> TransliterateResponse:
    """
    Transliterate Sinhala text to romanized English.
    
    Accepts Sinhala Unicode text and returns multiple possible
    romanized spellings. Also works with romanized input to
    generate spelling variants.
    
    Args:
        request: TransliterateRequest containing the text to transliterate
    
    Returns:
        TransliterateResponse: Original text, transliterations, and Sinhala flag
    
    Raises:
        HTTPException: 400 if text is empty
        HTTPException: 500 for internal processing errors
    
    Example:
        Input: {"text": "දුෂාන්"}
        Output: {
            "original": "දුෂාන්",
            "transliterations": ["dushan", "dushaan", "dusan"],
            "is_sinhala": true
        }
    """
    try:
        # Validate input
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text is required and cannot be empty"
            )
        
        text = request.text.strip()
        
        # Check if text contains Sinhala characters
        is_sinhala = sinhala_transliterator.is_sinhala(text)
        
        # Get transliterations/variants
        if is_sinhala:
            # Transliterate Sinhala to English
            transliterations = sinhala_transliterator.transliterate(text)
        else:
            # Generate variants for romanized input
            transliterations = sinhala_transliterator.generate_variants(text)
        
        # Ensure we have at least the original/cleaned text
        if not transliterations:
            transliterations = [text.lower()]
        
        return TransliterateResponse(
            original=text,
            transliterations=transliterations,
            is_sinhala=is_sinhala
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
# CORRELATION ENDPOINT
# =============================================================================

@router.post(
    "/correlate",
    response_model=CorrelateResponse,
    summary="Correlate Cross-Platform Profiles",
    description="""
    Analyze and correlate PII across multiple social media profiles.
    
    This endpoint:
    1. Compares profile information across platforms
    2. Identifies overlapping information (shared PII)
    3. Detects contradictions (conflicting information)
    4. Calculates an impersonation risk score (0-100)
    
    Useful for detecting potential impersonation accounts and
    verifying identity consistency across platforms.
    """
)
async def correlate(request: CorrelateRequest) -> CorrelateResponse:
    """
    Correlate PII across multiple social media profiles.
    
    Analyzes profiles from different platforms to find overlaps,
    contradictions, and calculate impersonation risk.
    
    Args:
        request: CorrelateRequest containing list of profiles
    
    Returns:
        CorrelateResponse: Overlaps, contradictions, score, and risk level
    
    Raises:
        HTTPException: 400 if profiles list is empty
        HTTPException: 500 for internal processing errors
    
    Example:
        Input: {
            "profiles": [
                {"platform": "facebook", "username": "john_doe", "name": "John"},
                {"platform": "instagram", "username": "johndoe", "name": "John D"}
            ]
        }
        Output: {
            "overlaps": [{"field": "username", "match_score": 0.85, ...}],
            "contradictions": [],
            "impersonation_score": 25,
            "risk_level": "low",
            "analysis_details": {...}
        }
    """
    try:
        # Validate input
        if not request.profiles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one profile is required"
            )
        
        # Convert Pydantic models to dictionaries for the correlator
        profiles_data = [p.model_dump() for p in request.profiles]
        
        # Run correlation analysis
        result = correlator.correlate_profiles(profiles_data)
        
        return CorrelateResponse(
            overlaps=result['overlaps'],
            contradictions=result['contradictions'],
            impersonation_score=result['impersonation_score'],
            risk_level=result['risk_level'],
            analysis_details=result['analysis_details']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in correlate endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during correlation: {str(e)}"
        )
