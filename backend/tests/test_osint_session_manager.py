# =============================================================================
# SESSION MANAGER TESTS
# =============================================================================
# Unit tests for OSINT session management functionality.
# =============================================================================

"""
Session Manager Tests

Test suite for SessionManager:
- Session creation and storage
- Session validation
- Session expiration
- Session deletion

Run with: pytest tests/test_osint_session_manager.py -v
"""

import pytest
import sys
import os
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.osint.session_manager import SessionManager


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def temp_session_dir():
    """Create a temporary directory for session storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def session_manager(temp_session_dir):
    """Create a SessionManager instance with temp directory."""
    return SessionManager(session_dir=temp_session_dir)


@pytest.fixture
def mock_storage_state():
    """Create mock Playwright storage state."""
    return {
        "cookies": [
            {
                "name": "sessionid",
                "value": "mock_session_value",
                "domain": ".instagram.com",
                "path": "/",
                "expires": -1,
                "httpOnly": True,
                "secure": True,
                "sameSite": "None"
            }
        ],
        "origins": []
    }


# =============================================================================
# SESSION OPERATIONS TESTS
# =============================================================================

class TestSessionOperations:
    """Tests for basic session operations."""
    
    def test_save_and_load_session(self, session_manager, mock_storage_state):
        """Test saving and loading a session."""
        platform = "instagram"
        
        # Save session
        result = session_manager.save_session(platform, mock_storage_state)
        assert result is True
        
        # Load session
        loaded_state = session_manager.load_session(platform)
        assert loaded_state is not None
        assert "cookies" in loaded_state
        assert len(loaded_state["cookies"]) > 0
    
    def test_load_nonexistent_session(self, session_manager):
        """Test loading a session that doesn't exist."""
        result = session_manager.load_session("instagram")
        assert result is None
    
    def test_delete_session(self, session_manager, mock_storage_state):
        """Test deleting a session."""
        platform = "facebook"
        
        # Save and then delete
        session_manager.save_session(platform, mock_storage_state)
        result = session_manager.delete_session(platform)
        assert result is True
        
        # Verify it's gone
        loaded = session_manager.load_session(platform)
        assert loaded is None
    
    def test_session_exists(self, session_manager, mock_storage_state):
        """Test checking if session exists."""
        platform = "linkedin"
        
        assert session_manager.session_exists(platform) is False
        
        session_manager.save_session(platform, mock_storage_state)
        assert session_manager.session_exists(platform) is True


# =============================================================================
# SESSION VALIDATION TESTS
# =============================================================================

class TestSessionValidation:
    """Tests for session validation."""
    
    def test_validate_valid_session(self, session_manager, mock_storage_state):
        """Test validating a valid session."""
        platform = "twitter"
        
        session_manager.save_session(platform, mock_storage_state)
        result = session_manager.validate_session(platform)
        
        assert result["exists"] is True
        assert result["valid"] is True
        assert result["age_days"] == 0
    
    def test_validate_nonexistent_session(self, session_manager):
        """Test validating a non-existent session."""
        result = session_manager.validate_session("instagram")
        
        assert result["exists"] is False
        assert result["valid"] is False
        assert result["error"] is not None
    
    def test_validate_expired_session(self, session_manager, mock_storage_state):
        """Test validating an expired session."""
        platform = "facebook"
        
        # Create session with old timestamp
        session_data = {
            "metadata": {
                "platform": platform,
                "created_at": (datetime.now() - timedelta(days=31)).isoformat(),
                "version": "1.0"
            },
            "storageState": mock_storage_state
        }
        
        # Manually save the modified session
        session_path = session_manager.get_session_path(platform)
        with open(session_path, 'w') as f:
            json.dump(session_data, f)
        
        # Validate - should be expired
        result = session_manager.validate_session(platform)
        assert result["exists"] is True
        assert result["valid"] is False
        assert "expired" in result["error"].lower()


# =============================================================================
# MULTI-SESSION TESTS
# =============================================================================

class TestMultiSessionOperations:
    """Tests for operations on multiple sessions."""
    
    def test_get_all_sessions_status(self, session_manager, mock_storage_state):
        """Test getting status of all sessions."""
        # Save sessions for some platforms
        session_manager.save_session("instagram", mock_storage_state)
        session_manager.save_session("facebook", mock_storage_state)
        
        result = session_manager.get_all_sessions_status()
        
        assert isinstance(result, dict)
        assert len(result) == len(session_manager.SUPPORTED_PLATFORMS)
        assert "instagram" in result
        assert result["instagram"]["valid"] is True
        assert "linkedin" in result
        assert result["linkedin"]["exists"] is False


# =============================================================================
# PLATFORM SUPPORT TESTS
# =============================================================================

class TestPlatformSupport:
    """Tests for platform support validation."""
    
    def test_unsupported_platform_raises_error(self, session_manager):
        """Test that unsupported platform raises error."""
        with pytest.raises(ValueError, match="Unsupported platform"):
            session_manager.get_session_path("unsupported_platform")
    
    def test_supported_platforms_list(self, session_manager):
        """Test that all expected platforms are supported."""
        expected_platforms = ["instagram", "facebook", "linkedin", "twitter"]
        assert session_manager.SUPPORTED_PLATFORMS == expected_platforms
