"""
Asyncio Event Loop Policy Fix for Python 3.13 on Windows
This module must be imported before any other asyncio-related modules.
"""
import sys
import asyncio

# Fix for Playwright on Windows - Set event loop policy before any other imports
# Windows defaults to ProactorEventLoop (in 3.8+), which breaks Playwright
# We must force WindowsSelectorEventLoopPolicy for all Windows versions
# if sys.platform == 'win32':
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#     print("✅ Set WindowsSelectorEventLoopPolicy for Playwright compatibility")