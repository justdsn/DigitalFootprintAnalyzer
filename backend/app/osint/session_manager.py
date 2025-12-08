# =============================================================================
# SESSION MANAGER
# =============================================================================
# Manages persistent Playwright browser sessions for OSINT platforms.
# Handles session storage, validation, and auto-detection of expired sessions.
# =============================================================================

"""
Session Manager

This module manages persistent login sessions for OSINT data collection.
Sessions are stored as JSON files (Playwright storageState) to maintain
authentication across multiple collection runs.

Features:
- One OSINT account per platform (Instagram, Facebook, LinkedIn, X)
- Secure session storage in JSON format
- Auto-detection of expired sessions
- Graceful handling of login-wall errors

Example Usage:
    session_mgr = SessionManager()
    state = session_mgr.load_session("instagram")
    if not state:
        # Session doesn't exist or expired
        pass
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# SESSION MANAGER CLASS
# =============================================================================

class SessionManager:
    """
    Manages persistent Playwright browser sessions for OSINT platforms.
    
    Attributes:
        session_dir: Directory where session files are stored
        supported_platforms: List of platforms with session support
    """
    
    SUPPORTED_PLATFORMS = ["instagram", "facebook", "linkedin", "twitter"]
    SESSION_VALIDITY_DAYS = 30  # Sessions expire after 30 days
    
    def __init__(self, session_dir: Optional[str] = None):
        """
        Initialize the Session Manager.
        
        Args:
            session_dir: Custom session directory path (optional)
        """
        if session_dir:
            self.session_dir = Path(session_dir)
        else:
            # Use config setting or default
            base_dir = Path(__file__).parent
            self.session_dir = base_dir / settings.OSINT_SESSION_DIR.split('/')[-1]
        
        # Ensure session directory exists
        self.session_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Session directory: {self.session_dir}")
    
    def get_session_path(self, platform: str) -> Path:
        """
        Get the path to a platform's session file.
        
        Args:
            platform: Platform name (instagram, facebook, linkedin, twitter)
        
        Returns:
            Path to session JSON file
        """
        platform = platform.lower()
        if platform not in self.SUPPORTED_PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return self.session_dir / f"{platform}_session.json"
    
    def load_session(self, platform: str) -> Optional[Dict[str, Any]]:
        """
        Load a stored session for a platform.
        
        Args:
            platform: Platform name
        
        Returns:
            Playwright storageState dict if session exists and is valid,
            None otherwise
        """
        session_path = self.get_session_path(platform)
        
        if not session_path.exists():
            logger.warning(f"No session file found for {platform}")
            return None
        
        try:
            with open(session_path, 'r') as f:
                session_data = json.load(f)
            
            # Check if session has metadata
            if "metadata" in session_data:
                created_at = datetime.fromisoformat(session_data["metadata"]["created_at"])
                age = datetime.now() - created_at
                
                if age > timedelta(days=self.SESSION_VALIDITY_DAYS):
                    logger.warning(f"Session for {platform} expired (age: {age.days} days)")
                    return None
                
                logger.info(f"Loaded valid session for {platform} (age: {age.days} days)")
            
            # Return the storageState portion
            return session_data.get("storageState") or session_data
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error loading session for {platform}: {e}")
            return None
    
    def save_session(self, platform: str, storage_state: Dict[str, Any]) -> bool:
        """
        Save a session for a platform.
        
        Args:
            platform: Platform name
            storage_state: Playwright storageState dict
        
        Returns:
            True if saved successfully, False otherwise
        """
        session_path = self.get_session_path(platform)
        
        try:
            # Wrap storage state with metadata
            session_data = {
                "metadata": {
                    "platform": platform,
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0"
                },
                "storageState": storage_state
            }
            
            with open(session_path, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            logger.info(f"Session saved for {platform}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving session for {platform}: {e}")
            return False
    
    def delete_session(self, platform: str) -> bool:
        """
        Delete a stored session for a platform.
        
        Args:
            platform: Platform name
        
        Returns:
            True if deleted successfully, False otherwise
        """
        session_path = self.get_session_path(platform)
        
        try:
            if session_path.exists():
                session_path.unlink()
                logger.info(f"Session deleted for {platform}")
                return True
            else:
                logger.warning(f"No session file to delete for {platform}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting session for {platform}: {e}")
            return False
    
    def validate_session(self, platform: str) -> Dict[str, Any]:
        """
        Validate a session without loading it fully.
        
        Args:
            platform: Platform name
        
        Returns:
            Dict with validation results
        """
        session_path = self.get_session_path(platform)
        
        result = {
            "platform": platform,
            "exists": False,
            "valid": False,
            "age_days": None,
            "expires_in_days": None,
            "error": None
        }
        
        if not session_path.exists():
            result["error"] = "Session file not found"
            return result
        
        result["exists"] = True
        
        try:
            with open(session_path, 'r') as f:
                session_data = json.load(f)
            
            if "metadata" in session_data:
                created_at = datetime.fromisoformat(session_data["metadata"]["created_at"])
                age = datetime.now() - created_at
                result["age_days"] = age.days
                result["expires_in_days"] = self.SESSION_VALIDITY_DAYS - age.days
                
                if age > timedelta(days=self.SESSION_VALIDITY_DAYS):
                    result["error"] = f"Session expired ({age.days} days old)"
                else:
                    result["valid"] = True
            else:
                result["error"] = "Session missing metadata"
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def get_all_sessions_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all platform sessions.
        
        Returns:
            Dict mapping platform names to their validation results
        """
        return {
            platform: self.validate_session(platform)
            for platform in self.SUPPORTED_PLATFORMS
        }
    
    def session_exists(self, platform: str) -> bool:
        """
        Check if a session file exists for a platform.
        
        Args:
            platform: Platform name
        
        Returns:
            True if session file exists
        """
        return self.get_session_path(platform).exists()
