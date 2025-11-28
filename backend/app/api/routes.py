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

# Import request/response schemas
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    PIIExtractRequest,
    PIIExtractResponse,
    UsernameAnalyzeRequest,
    UsernameAnalyzeResponse,
    HealthResponse
)

# Import services
from app.services.pii_extractor import PIIExtractor
from app.services.ner_engine import NEREngine
from app.services.username_analyzer import UsernameAnalyzer


# =============================================================================
# ROUTER INITIALIZATION
# =============================================================================

router = APIRouter()

# Initialize service instances
# These are stateless services, so we can reuse single instances
pii_extractor = PIIExtractor()
ner_engine = NEREngine()
username_analyzer = UsernameAnalyzer()


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
    digital footprint analysis. Accepts username (required) and optionally
    email, phone, and name for enhanced analysis.
    """
)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Perform comprehensive digital footprint analysis.
    
    This endpoint:
    1. Generates platform URLs for the provided username
    2. Creates username variations to check for impersonation
    3. Extracts PII from any provided name/email/phone
    4. Runs NER analysis on the combined input
    5. Calculates a risk score based on exposure level
    
    Args:
        request: AnalyzeRequest containing username (required) and 
                optional email, phone, and name
    
    Returns:
        AnalyzeResponse: Comprehensive analysis results including:
            - Platform URLs
            - Username variations
            - Extracted PII
            - NER entities
            - Risk assessment
            - Recommendations
    
    Raises:
        HTTPException: 400 if username is empty or invalid
        HTTPException: 500 for internal processing errors
    """
    start_time = time.time()
    
    try:
        # ---------------------------------------------------------------------
        # Input Validation
        # ---------------------------------------------------------------------
        if not request.username or not request.username.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is required and cannot be empty"
            )
        
        username = request.username.strip()
        
        # ---------------------------------------------------------------------
        # Username Analysis
        # ---------------------------------------------------------------------
        # Generate platform URLs for the main username
        platform_urls = username_analyzer.generate_platform_urls(username)
        
        # Generate username variations to check for impersonation
        variations = username_analyzer.generate_variations(username)
        
        # Analyze username patterns
        pattern_analysis = username_analyzer.analyze_patterns(username)
        
        # ---------------------------------------------------------------------
        # PII Extraction
        # ---------------------------------------------------------------------
        # Combine all provided information for PII extraction
        combined_text = f"{username}"
        if request.name:
            combined_text += f" {request.name}"
        if request.email:
            combined_text += f" {request.email}"
        if request.phone:
            combined_text += f" {request.phone}"
        
        extracted_pii = pii_extractor.extract_all(combined_text)
        
        # If email was directly provided, ensure it's included
        if request.email:
            if request.email not in extracted_pii.get("emails", []):
                extracted_pii["emails"].append(request.email)
        
        # If phone was directly provided, normalize and include
        if request.phone:
            normalized_phone = pii_extractor.normalize_phone(request.phone)
            if normalized_phone and normalized_phone not in extracted_pii.get("phones", []):
                extracted_pii["phones"].append(normalized_phone)
        
        # ---------------------------------------------------------------------
        # NER Analysis
        # ---------------------------------------------------------------------
        # Run NER on name if provided
        ner_results = {"persons": [], "locations": [], "organizations": []}
        if request.name:
            ner_results = ner_engine.extract_entities(request.name)
        
        # ---------------------------------------------------------------------
        # Risk Assessment
        # ---------------------------------------------------------------------
        risk_score, risk_level = calculate_risk_score(
            username=username,
            email_provided=bool(request.email),
            phone_provided=bool(request.phone),
            pattern_analysis=pattern_analysis,
            pii_count=len(extracted_pii.get("emails", [])) + len(extracted_pii.get("phones", []))
        )
        
        # ---------------------------------------------------------------------
        # Generate Recommendations
        # ---------------------------------------------------------------------
        recommendations = generate_recommendations(
            risk_level=risk_level,
            pattern_analysis=pattern_analysis,
            email_provided=bool(request.email),
            phone_provided=bool(request.phone)
        )
        
        # ---------------------------------------------------------------------
        # Calculate Processing Time
        # ---------------------------------------------------------------------
        processing_time = round((time.time() - start_time) * 1000, 2)  # in ms
        
        # ---------------------------------------------------------------------
        # Build Response
        # ---------------------------------------------------------------------
        return AnalyzeResponse(
            username=username,
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
        print(f"Error in analyze endpoint: {str(e)}")
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
        print(f"Error in extract_pii endpoint: {str(e)}")
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
        print(f"Error in analyze_username endpoint: {str(e)}")
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
    phone_provided: bool
) -> list:
    """
    Generate personalized recommendations based on analysis results.
    
    Args:
        risk_level: Calculated risk level (low/medium/high)
        pattern_analysis: Results from username pattern analysis
        email_provided: Whether email was provided
        phone_provided: Whether phone was provided
    
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
    
    # PII-specific recommendations
    if email_provided:
        recommendations.append(
            "Check if your email has been involved in data breaches at haveibeenpwned.com"
        )
    
    if phone_provided:
        recommendations.append(
            "Be cautious about sharing your phone number publicly"
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
