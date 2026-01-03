# =============================================================================
# OSINT API ROUTES
# =============================================================================
# FastAPI endpoints for OSINT data collection and analysis.
# =============================================================================

"""
OSINT API Routes

Endpoints:
- POST /api/osint/analyze - Main analysis endpoint
- GET /api/osint/status/{task_id} - Check analysis status (future async support)
- POST /api/osint/sessions/validate - Validate platform sessions
- GET /api/osint/sessions/status - Get session health status
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import logging

from app.osint.orchestrator import OSINTOrchestrator
from app.osint.session_manager import SessionManager
from app.osint.schemas import (
    OSINTAnalyzeRequest,
    OSINTAnalyzeResponse,
    SessionValidateRequest,
    SessionStatus,
    SessionsStatusResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
orchestrator = OSINTOrchestrator()
session_manager = SessionManager()


# =============================================================================
# MAIN ANALYSIS ENDPOINT
# =============================================================================

@router.post(
    "/analyze",
    response_model=OSINTAnalyzeResponse,
    summary="OSINT Profile Analysis",
    description="""
    Perform comprehensive OSINT analysis using Playwright-based data collection.
    
    This endpoint:
    1. Detects the identifier type (username, email, name, phone)
    2. Generates profile URLs for supported platforms
    3. Collects data using headless browser automation
    4. Parses profile information from HTML
    5. Integrates with existing analysis services (NER, PII, correlation)
    6. Calculates impersonation risk scores
    7. Returns structured JSON output
    
    Supported platforms: Instagram, Facebook, LinkedIn, X (Twitter)
    """
)
async def osint_analyze(request: OSINTAnalyzeRequest) -> OSINTAnalyzeResponse:
    """
    Perform OSINT analysis.
    
    Args:
        request: Analysis request with identifier and options
    
    Returns:
        Complete analysis results
    
    Raises:
        HTTPException: 400 if identifier is invalid
        HTTPException: 500 for internal errors
    """
    try:
        if not request.identifier or not request.identifier.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Identifier is required and cannot be empty"
            )
        
        clean_identifier = request.identifier.lower().strip()
        logger.info(f"🔍 Processing identifier: '{clean_identifier}' (Original: '{request.identifier}')")

        # Perform analysis
        result = await orchestrator.analyze(
            identifier=request.identifier.strip(),
            platforms=request.platforms,
            use_search=request.use_search
        )
        
        logger.info(f"✅ OSINT analysis completed successfully")
        
        # Convert to response model
        return OSINTAnalyzeResponse(**result)
        
    except RuntimeError as e:
        # Critical errors (browser init failures)
        logger.error(f"❌ CRITICAL ERROR in OSINT analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Browser initialization failed",
                "message": str(e),
                "solution": (
                    "Playwright browser automation failed. "
                    "This may be due to: "
                    "1. Missing browser installation - Run: playwright install chromium "
                    "2. Python 3.13 compatibility issues - Use Python 3.11.x or 3.12.x "
                    "3. System dependencies missing - Check Playwright documentation"
                )
            }
        )
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"❌ Error in OSINT analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during OSINT analysis: {str(e)}"
        )


# =============================================================================
# SESSION MANAGEMENT ENDPOINTS
# =============================================================================

@router.post(
    "/sessions/validate",
    response_model=SessionStatus,
    summary="Validate Platform Session",
    description="Validate a specific platform's session without loading it."
)
async def validate_session(request: SessionValidateRequest) -> SessionStatus:
    """
    Validate a platform session.
    
    Args:
        request: Validation request with platform name
    
    Returns:
        Session status information
    
    Raises:
        HTTPException: 400 if platform is invalid
    """
    try:
        platform = request.platform.lower()
        
        if platform not in session_manager.SUPPORTED_PLATFORMS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platform: {platform}. "
                       f"Supported: {', '.join(session_manager.SUPPORTED_PLATFORMS)}"
            )
        
        validation_result = session_manager.validate_session(platform)
        return SessionStatus(**validation_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during session validation: {str(e)}"
        )


@router.get(
    "/sessions/status",
    response_model=SessionsStatusResponse,
    summary="Get All Sessions Status",
    description="Get health status of all platform sessions."
)
async def get_sessions_status() -> SessionsStatusResponse:
    """
    Get status of all platform sessions.
    
    Returns:
        Status information for all platforms
    """
    try:
        all_status = session_manager.get_all_sessions_status()
        
        # Convert to SessionStatus models
        sessions = {
            platform: SessionStatus(**status_data)
            for platform, status_data in all_status.items()
        }
        
        # Calculate summary counts
        healthy_count = sum(1 for s in sessions.values() if s.valid)
        expired_count = sum(
            1 for s in sessions.values()
            if s.exists and not s.valid
        )
        missing_count = sum(1 for s in sessions.values() if not s.exists)
        
        return SessionsStatusResponse(
            sessions=sessions,
            healthy_count=healthy_count,
            expired_count=expired_count,
            missing_count=missing_count
        )
        
    except Exception as e:
        logger.error(f"Error getting sessions status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred getting sessions status: {str(e)}"
        )


# =============================================================================
# STATUS CHECK ENDPOINT (Placeholder for async support)
# =============================================================================

@router.get(
    "/status/{task_id}",
    summary="Check Analysis Status",
    description="""
    Check the status of an asynchronous analysis task.
    
    Note: This is a placeholder for future async task support.
    Currently, all analyses are synchronous.
    """
)
async def check_status(task_id: str) -> Dict[str, Any]:
    """
    Check analysis task status.
    
    Args:
        task_id: Task identifier
    
    Returns:
        Task status information
    """
    return {
        "task_id": task_id,
        "status": "not_implemented",
        "message": "Async task support not yet implemented. All analyses are currently synchronous."
    }
