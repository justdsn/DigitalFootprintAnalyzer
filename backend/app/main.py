# =============================================================================
# MAIN APPLICATION ENTRY POINT
# =============================================================================
# FastAPI application initialization and configuration.
# This file sets up the main application instance with CORS, routes, and
# lifecycle events for the Sri Lanka Digital Footprint Analyzer.
# =============================================================================

"""
Main FastAPI Application

This module initializes the FastAPI application with:
- CORS middleware configuration for frontend communication
- API route registration
- Startup/shutdown lifecycle events
- NLP model preloading for optimal performance
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import API routes
from app.api.routes import router as api_router

# Import configuration
from app.core.config import settings

# Import NER engine for preloading
from app.services.ner_engine import preload_nlp_model


# =============================================================================
# APPLICATION LIFECYCLE MANAGEMENT
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle events.
    
    Startup:
    - Preload the spaCy NLP model to avoid cold start delays
    
    Shutdown:
    - Clean up any resources if needed
    
    Args:
        app: FastAPI application instance
    """
    # Startup: Preload NLP model for faster first requests
    logger.info("🚀 Starting Digital Footprint Analyzer...")
    preload_nlp_model()
    logger.info("✅ NLP model loaded successfully")
    
    yield  # Application is running
    
    # Shutdown: Cleanup (if needed)
    logger.info("👋 Shutting down Digital Footprint Analyzer...")


# =============================================================================
# APPLICATION INITIALIZATION
# =============================================================================

# Create FastAPI application instance with metadata
app = FastAPI(
    title="Digital Footprint Analyzer API",
    description="""
    ## Sri Lanka OSINT Digital Footprint Analyzer
    
    A web application designed to help Sri Lankan citizens analyze their digital 
    footprint across social media platforms.
    
    ### Features:
    - **PII Extraction**: Identify personally identifiable information in text
    - **Username Analysis**: Generate platform URLs and variations for usernames
    - **NER Engine**: Extract named entities with Sri Lankan context
    - **Platform URL Generation**: Create links for Facebook, Instagram, X, LinkedIn, etc.
    
    ### Supported Identifiers:
    - Username (required)
    - Email address (optional)
    - Phone number - Sri Lankan formats supported (optional)
    - Full name (optional)
    """,
    version="1.0.0",
    contact={
        "name": "Digital Footprint Analyzer Team",
    },
    license_info={
        "name": "MIT License",
    },
    lifespan=lifespan
)


# =============================================================================
# CORS MIDDLEWARE CONFIGURATION
# =============================================================================
# Configure Cross-Origin Resource Sharing to allow frontend communication.
# In production, restrict origins to your specific frontend domain.
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    # Allow requests from frontend development server and production
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    # Allow all standard HTTP methods
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    # Allow common headers
    allow_headers=["*"],
)


# =============================================================================
# ROUTE REGISTRATION
# =============================================================================

# Include API routes with /api prefix
app.include_router(api_router, prefix="/api", tags=["Analysis"])

# Include OSINT routes
from app.api.routes.osint import router as osint_router
app.include_router(osint_router, prefix="/api/osint", tags=["OSINT"])


# =============================================================================
# ROOT ENDPOINT
# =============================================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint providing API information.
    
    Returns:
        dict: Basic API information and links
    """
    return {
        "message": "Welcome to Digital Footprint Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================
# For development: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
