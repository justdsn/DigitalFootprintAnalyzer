# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================
# Centralized configuration management using Pydantic Settings.
# Loads configuration from environment variables with sensible defaults.
# =============================================================================

"""
Application Configuration

This module manages all application configuration using Pydantic Settings.
Configuration can be overridden via environment variables or .env file.

Environment Variables:
- APP_NAME: Application name
- DEBUG: Enable debug mode (default: False)
- CORS_ORIGINS: Comma-separated list of allowed origins
- SPACY_MODEL: spaCy model to use for NER

Example .env file:
    APP_NAME=Digital Footprint Analyzer
    DEBUG=True
    CORS_ORIGINS=http://localhost:3000,http://localhost:8080
    SPACY_MODEL=en_core_web_sm
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


# =============================================================================
# SETTINGS CLASS
# =============================================================================

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Uses Pydantic BaseSettings for automatic environment variable loading
    and type validation.
    
    Attributes:
        APP_NAME: Display name of the application
        DEBUG: Enable/disable debug mode for development
        CORS_ORIGINS: List of allowed CORS origins for frontend
        SPACY_MODEL: spaCy model name for NER processing
        API_V1_PREFIX: API version prefix for routes
    """
    
    # -------------------------------------------------------------------------
    # Application Settings
    # -------------------------------------------------------------------------
    APP_NAME: str = "Digital Footprint Analyzer"
    DEBUG: bool = False
    
    # -------------------------------------------------------------------------
    # CORS Configuration
    # -------------------------------------------------------------------------
    # Default origins for development - add production domains in .env
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",      # React development server
        "http://localhost:8080",      # Alternative frontend port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]
    
    # -------------------------------------------------------------------------
    # NLP Configuration
    # -------------------------------------------------------------------------
    # spaCy model to use for Named Entity Recognition
    # Options: en_core_web_sm (small), en_core_web_md (medium), en_core_web_lg (large)
    SPACY_MODEL: str = "en_core_web_sm"
    
    # -------------------------------------------------------------------------
    # API Configuration
    # -------------------------------------------------------------------------
    API_V1_PREFIX: str = "/api"
    
    # -------------------------------------------------------------------------
    # Sri Lankan Context Configuration
    # -------------------------------------------------------------------------
    # Major cities in Sri Lanka for NER recognition
    SRI_LANKAN_CITIES: List[str] = [
        "Colombo",
        "Kandy",
        "Galle",
        "Jaffna",
        "Negombo",
        "Matara",
        "Trincomalee",
        "Anuradhapura",
        "Batticaloa",
        "Ratnapura",
        "Kurunegala",
        "Badulla",
        "Moratuwa",
        "Dehiwala",
        "Mount Lavinia",
        "Nuwara Eliya"
    ]
    
    # Common Sri Lankan family names for NER recognition
    SRI_LANKAN_NAMES: List[str] = [
        "Perera",
        "Silva",
        "Fernando",
        "Bandara",
        "Jayawardena",
        "Wickramasinghe",
        "Dissanayake",
        "Rajapaksa",
        "Senanayake",
        "Gunasekara",
        "Rathnayake",
        "Karunaratne",
        "Wijesinghe",
        "Herath",
        "Kumara"
    ]
    
    # Major Sri Lankan organizations for NER recognition
    SRI_LANKAN_ORGANIZATIONS: List[str] = [
        "Dialog",
        "Mobitel",
        "SLT",
        "BOC",
        "NSB",
        "Commercial Bank",
        "Sampath Bank",
        "HNB",
        "Ceylon Bank",
        "People's Bank",
        "Cargills",
        "John Keells",
        "MAS Holdings",
        "Hayleys",
        "SriLankan Airlines"
    ]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# =============================================================================
# SETTINGS INSTANCE
# =============================================================================
# Create a singleton settings instance for use throughout the application

settings = Settings()


# =============================================================================
# CONFIGURATION HELPERS
# =============================================================================

def get_cors_origins() -> List[str]:
    """
    Get CORS origins, parsing from environment if needed.
    
    If CORS_ORIGINS env var is set as comma-separated string,
    this function parses it into a list.
    
    Returns:
        List[str]: List of allowed CORS origins
    """
    cors_env = os.getenv("CORS_ORIGINS", "")
    if cors_env:
        return [origin.strip() for origin in cors_env.split(",")]
    return settings.CORS_ORIGINS


def is_debug_mode() -> bool:
    """
    Check if application is running in debug mode.
    
    Returns:
        bool: True if debug mode is enabled
    """
    return settings.DEBUG or os.getenv("DEBUG", "").lower() == "true"
