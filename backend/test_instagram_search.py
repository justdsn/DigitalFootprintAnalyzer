import sys
import asyncio
import logging
from pathlib import Path

# Fix for Playwright on Windows (Default Proactor is fine now due to BaseCollector fix)
# But we verify imports
from app.osint.collectors import InstagramCollector

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_search():
    print("=" * 80)
    print("🔍 INSTAGRAM SEARCH TEST")
    print("=" * 80)
    
    identifier = "dhanuka nanayakkara"
    print(f"Target: {identifier}")
    
    collector = InstagramCollector()
    
    try:
        print("\n📦 Initializing Browser...")
        await collector.initialize_browser()
        
        print(f"\n🚀 Searching for '{identifier}'...")
        # Use the NEW search_and_collect method
        result = await collector.search_and_collect(identifier)
        
        print("\n" + "=" * 80)
        if result.get("success"):
            print(f"✅ SEARCH SUCCESSFUL")
            print(f"   Found Profile URL: {result.get('url')}")
            print(f"   Input Identifier: {identifier}")
        else:
            print(f"❌ SEARCH FAILED")
            print(f"   Error: {result.get('error')}")
            
        print("=" * 80)
        return result.get("success")
        
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        if collector.page:
            try:
                await collector.page.screenshot(path="debug_search_fail.png")
                print("📸 Error specific screenshot saved to debug_search_fail.png")
            except:
                pass
        return False
        
    finally:
        print("\n🧹 Closing browser...")
        await collector.close_browser()

if __name__ == "__main__":
    # Add project root to path
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        success = asyncio.run(test_search())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠ Interrupted by user")
