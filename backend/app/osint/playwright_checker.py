# =============================================================================
# PLAYWRIGHT CHECKER
# =============================================================================
# Verifies Playwright installation and browser availability on startup.
# =============================================================================

import logging
import sys
import subprocess
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def check_playwright_installation() -> Dict[str, Any]:
    """
    Check if Playwright is properly installed with browsers.
    
    Returns:
        Dict with status and error details if any
    """
    result = {
        "installed": False,
        "browsers_installed": False,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "errors": [],
        "warnings": []
    }
    
    # Check Python version
    if sys.version_info >= (3, 13):
        result["warnings"].append(
            f"⚠️  Python {result['python_version']} detected. "
            "Playwright may have compatibility issues with Python 3.13+. "
            "Recommended: Python 3.11.x or 3.12.x"
        )
    
    # Check if Playwright is installed
    try:
        from playwright.async_api import async_playwright
        result["installed"] = True
        logger.info("✅ Playwright package is installed")
    except ImportError as e:
        result["errors"].append(f"❌ Playwright not installed: {e}")
        logger.error(f"Playwright import failed: {e}")
        return result
    
    # Check if browsers are installed
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            try:
                # Try to get browser executable path
                browser = await p.chromium.launch(headless=True)
                await browser.close()
                result["browsers_installed"] = True
                logger.info("✅ Playwright browsers are installed and working")
            except Exception as e:
                result["errors"].append(
                    f"❌ Playwright browsers not installed or not working: {e}"
                )
                result["errors"].append(
                    "Run: playwright install chromium"
                )
                logger.error(f"Browser launch failed: {e}")
                
    except Exception as e:
        result["errors"].append(f"❌ Failed to check browser installation: {e}")
        logger.error(f"Browser check failed: {e}")
    
    return result


def install_playwright_browsers():
    """
    Attempt to install Playwright browsers automatically.
    """
    try:
        logger.info("📥 Installing Playwright browsers...")
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("✅ Playwright browsers installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install Playwright browsers: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error installing browsers: {e}")
        return False
