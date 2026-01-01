# =============================================================================
# TEST: PLAYWRIGHT ERROR HANDLING
# =============================================================================
# Minimal test to verify error handling improvements without full dependencies
# =============================================================================

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock


class TestPlaywrightErrorHandling:
    """Test improved error handling for Playwright initialization failures."""
    
    def test_base_collector_raises_runtime_error_on_browser_init_failure(self):
        """Test that BaseCollector raises RuntimeError with helpful message."""
        # This test verifies the error handling structure without actually
        # trying to initialize Playwright (which requires browsers installed)
        
        # Read the base_collector.py file
        with open('app/osint/collectors/base_collector.py', 'r') as f:
            content = f.read()
        
        # Verify key error handling improvements are present
        assert 'raise RuntimeError(' in content, \
            "Should raise RuntimeError on browser init failure"
        
        assert 'Failed to initialize Playwright browser' in content, \
            "Error message should provide context"
        
        assert 'Python 3.13 compatibility' in content, \
            "Error message should mention Python 3.13 compatibility"
        
        assert 'playwright install chromium' in content, \
            "Error message should suggest solution"
    
    def test_orchestrator_tracks_browser_failures(self):
        """Test that orchestrator tracks browser initialization failures."""
        with open('app/osint/orchestrator.py', 'r') as f:
            content = f.read()
        
        # Verify fail-fast logic
        assert 'browser_init_failures' in content, \
            "Should track browser initialization failures"
        
        assert 'if browser_init_failures == len(platform_names)' in content, \
            "Should check if ALL platforms failed"
        
        assert 'All platform data collection failed' in content, \
            "Should provide clear error message when all platforms fail"
    
    def test_api_catches_runtime_error(self):
        """Test that API routes catch RuntimeError separately."""
        with open('app/api/routes/osint.py', 'r') as f:
            content = f.read()
        
        # Verify RuntimeError handling
        assert 'except RuntimeError as e:' in content, \
            "Should catch RuntimeError separately from other exceptions"
        
        assert '"error": "Browser initialization failed"' in content, \
            "Should return structured error response"
        
        assert '"solution"' in content, \
            "Should provide solutions in error response"
    
    def test_playwright_checker_module_exists(self):
        """Test that playwright_checker module was created."""
        import os
        assert os.path.exists('app/osint/playwright_checker.py'), \
            "playwright_checker.py should exist"
        
        with open('app/osint/playwright_checker.py', 'r') as f:
            content = f.read()
        
        # Verify key functions exist
        assert 'async def check_playwright_installation' in content, \
            "Should have check_playwright_installation function"
        
        assert 'def install_playwright_browsers' in content, \
            "Should have install_playwright_browsers function"
        
        assert 'Python 3.13' in content, \
            "Should check for Python 3.13 compatibility"
    
    def test_main_app_has_startup_check(self):
        """Test that main.py has Playwright startup check."""
        with open('app/main.py', 'r') as f:
            content = f.read()
        
        # Verify startup check was added
        assert 'from app.osint.playwright_checker import' in content, \
            "Should import playwright_checker"
        
        assert 'check_playwright_installation' in content, \
            "Should call check_playwright_installation"
        
        assert 'playwright_status' in content, \
            "Should store and check playwright status"
    
    def test_documentation_exists(self):
        """Test that documentation files were created."""
        import os
        
        # Check OSINT_SETUP.md
        assert os.path.exists('OSINT_SETUP.md'), \
            "OSINT_SETUP.md should exist"
        
        with open('OSINT_SETUP.md', 'r') as f:
            content = f.read()
        
        assert 'Python 3.11.x or 3.12.x' in content, \
            "Should recommend Python 3.11 or 3.12"
        
        assert 'playwright install chromium' in content, \
            "Should include installation instructions"
        
        assert 'Troubleshooting' in content, \
            "Should include troubleshooting section"
        
        # Check runtime.txt
        assert os.path.exists('runtime.txt'), \
            "runtime.txt should exist"
        
        with open('runtime.txt', 'r') as f:
            content = f.read().strip()
        
        assert content.startswith('python-3.12'), \
            "runtime.txt should specify Python 3.12"
        
        # Check .python-version
        assert os.path.exists('.python-version'), \
            ".python-version should exist"
        
        with open('.python-version', 'r') as f:
            content = f.read().strip()
        
        assert content.startswith('3.12'), \
            ".python-version should specify Python 3.12"
    
    def test_requirements_updated(self):
        """Test that requirements.txt was updated."""
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        # Check Playwright version
        assert 'playwright>=1.42.0' in content, \
            "Should pin Playwright to 1.42.0+"
        
        # Check for Python 3.13 warning
        assert 'Python 3.13' in content or 'CRITICAL' in content, \
            "Should include warning about Python 3.13"
        
        # Check for installation instructions
        assert 'playwright install chromium' in content, \
            "Should include browser installation instructions"


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '--tb=short'])
