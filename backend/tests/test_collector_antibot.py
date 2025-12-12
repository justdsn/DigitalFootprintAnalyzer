# =============================================================================
# COLLECTOR ANTI-BOT/STEALTH TESTS
# =============================================================================
# Unit tests for Playwright collector anti-bot and stealth logic (mocked).
# =============================================================================

"""
Collector Anti-Bot/Stealth Tests

Test suite for:
- User-agent rotation
- Proxy support
- Stealth script injection
- Randomized delays

These tests use mocking to avoid launching real browsers.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.osint.collectors.base_collector import BaseCollector

class DummyCollector(BaseCollector):
    def __init__(self, session_manager=None, user_agent=None, proxy=None):
        super().__init__(session_manager=session_manager, user_agent=user_agent, proxy=proxy)
    def get_platform_name(self):
        return "instagram"
    async def collect(self, url):
        return {"success": True}

@pytest.mark.asyncio
async def test_user_agent_rotation():
    # Test that user-agent is set from the list if not provided
    c1 = DummyCollector()
    c2 = DummyCollector(user_agent="custom-agent")
    assert c1.user_agent in DummyCollector.USER_AGENTS
    assert c2.user_agent == "custom-agent"

@pytest.mark.asyncio
async def test_proxy_support():
    c = DummyCollector(proxy="http://proxy:8080")
    assert c.proxy == "http://proxy:8080"

@pytest.mark.asyncio
async def test_stealth_script_injection():
    c = DummyCollector()
    class AsyncMockPage:
        def __init__(self):
            self.calls = []
        async def add_init_script(self, script):
            self.calls.append(script)
    mock_page = AsyncMockPage()
    await c._apply_stealth(mock_page)
    # Should call add_init_script several times
    assert len(mock_page.calls) >= 4

@pytest.mark.asyncio
async def test_randomized_delay(monkeypatch):
    c = DummyCollector()
    class AsyncMockPage:
        async def goto(self, url, wait_until=None):
            return None
        async def wait_for_selector(self, selector, timeout=None):
            return None
    c.page = AsyncMockPage()
    delays = []
    async def fake_sleep(secs):
        delays.append(secs)
    monkeypatch.setattr("asyncio.sleep", fake_sleep)
    await c.navigate_to_url("http://test", min_delay=1.0, max_delay=2.0)
    assert any(1.0 <= d <= 2.0 for d in delays)
