import sys
import asyncio
import os

# Apply fix first
# if sys.platform == 'win32':
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#     print("Policy set to WindowsSelectorEventLoopPolicy")

from playwright.async_api import async_playwright

async def run():
    print("Starting raw Playwright test...")
    try:
        async with async_playwright() as p:
            print("Playwright initialized.")
            print("Launching browser...")
            browser = await p.chromium.launch(headless=True)
            print(f"Browser launched: {browser.version}")
            
            page = await browser.new_page()
            print("Page created.")
            
            await page.goto("http://example.com")
            print("Navigated to example.com")
            
            title = await page.title()
            print(f"Page title: {title}")
            
            await browser.close()
            print("Browser closed.")
            print("SUCCESS: Raw Playwright working!")
            return True
    except Exception as e:
        print(f"FAILURE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(run())
    sys.exit(0 if success else 1)
