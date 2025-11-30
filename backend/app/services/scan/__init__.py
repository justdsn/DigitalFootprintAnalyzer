# =============================================================================
# SCAN SERVICES MODULE
# =============================================================================
# Services for profile discovery and scanning.
# =============================================================================

"""
Scan Services Module

This module provides scan services for profile discovery:
- LightScanService: Google Dorking-based profile discovery

Example Usage:
    from app.services.scan import LightScanService
    
    # Light scan using Google Dorking
    service = LightScanService()
    result = await service.scan(
        identifier_type="name",
        identifier_value="John Perera",
        location="Sri Lanka"
    )
"""

from .light_scan import LightScanService, get_light_scan_service

__all__ = [
    "LightScanService",
    "get_light_scan_service",
]
