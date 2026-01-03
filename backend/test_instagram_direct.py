"""
Direct test of Instagram OSINT functionality
Tests deep scan with "cristiano ronaldo" identifier
"""
# CRITICAL: Import asyncio_fix FIRST to resolve Python 3.13 compatibility
# CRITICAL: Import asyncio_fix FIRST to resolve Python 3.13 compatibility
# import asyncio_fix

import asyncio
import json
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.osint.orchestrator import OSINTOrchestrator


async def test_instagram_scan():
    """Test Instagram deep scan with cristiano ronaldo."""
    
    print("=" * 80)
    print("🔍 INSTAGRAM DEEP SCAN TEST")
    print("=" * 80)
    print(f"Identifier: dhanukananayakkara")
    print(f"Platform: Instagram")
    print("-" * 80)
    
    try:
        # Initialize orchestrator
        print("\n📦 Initializing OSINT Orchestrator...")
        orchestrator = OSINTOrchestrator()
        
        # Perform analysis
        print("🚀 Starting deep scan...")
        print("⏳ This may take a while as it uses Playwright to scrape Instagram...")
        print()
        
        result = await orchestrator.analyze(
            identifier="dhanukananayakkara",
            platforms=["instagram"],
            use_search=False
        )
        
        print("\n" + "=" * 80)
        print("✅ SCAN COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
        # Display results
        print(f"\n📊 SUMMARY:")
        print(f"   Input: {result.get('input', 'N/A')}")
        print(f"   Identifier Type: {result.get('identifier_type', 'N/A')}")
        print(f"   Username: {result.get('username', 'N/A')}")
        print(f"   Total Profiles Found: {result.get('total_profiles_found', 0)}")
        print(f"   Total Impersonation Risks: {result.get('total_impersonation_risks', 0)}")
        
        # Display profiles
        profiles = result.get('profiles_found', [])
        print(f"\n📷 INSTAGRAM PROFILES ({len(profiles)}):")
        print("-" * 80)
        
        for i, profile in enumerate(profiles, 1):
            print(f"\n  Profile #{i}:")
            print(f"    Platform: {profile.get('platform', 'N/A')}")
            print(f"    Username: {profile.get('username', 'N/A')}")
            print(f"    Name: {profile.get('name', 'N/A')}")
            print(f"    URL: {profile.get('url', 'N/A')}")
            print(f"    Followers: {profile.get('followers', 'N/A')}")
            print(f"    Following: {profile.get('following', 'N/A')}")
            print(f"    Posts: {profile.get('posts', 'N/A')}")
            print(f"    Verified: {profile.get('verified', False)}")
            
            bio = profile.get('bio', '')
            if bio:
                bio_preview = bio[:100] + "..." if len(bio) > 100 else bio
                print(f"    Bio: {bio_preview}")
            
            # Display PII
            pii_data = profile.get('pii', {})
            total_pii = sum(len(v) if isinstance(v, list) else 0 for v in pii_data.values())
            
            if total_pii > 0:
                print(f"\n    🔍 EXPOSED PII ({total_pii} items):")
                for pii_type, items in pii_data.items():
                    if items and isinstance(items, list):
                        print(f"      {pii_type.upper()}: {items}")
            else:
                print(f"\n    ✅ No PII detected in this profile")
            
            # Display impersonation score
            imp_score = profile.get('impersonation_score', 0)
            print(f"\n    ⚠️  Impersonation Score: {imp_score}/100")
        
        # Display impersonation risks
        imp_risks = result.get('impersonation_risks', [])
        if imp_risks:
            print(f"\n\n⚠️  IMPERSONATION RISKS ({len(imp_risks)}):")
            print("-" * 80)
            for i, risk in enumerate(imp_risks, 1):
                print(f"  {i}. {risk}")
        else:
            print(f"\n\n✅ No impersonation risks detected")
        
        # Display overall risk
        overall_risk = result.get('overall_risk', {})
        print(f"\n\n🎯 OVERALL RISK ASSESSMENT:")
        print("-" * 80)
        print(f"   Risk Level: {overall_risk.get('level', 'N/A').upper()}")
        print(f"   Risk Score: {overall_risk.get('score', 0)}/100")
        print(f"   PII Exposure: {'YES' if overall_risk.get('pii_exposure') else 'NO'}")
        print(f"   Impersonation Detected: {'YES' if overall_risk.get('impersonation_detected') else 'NO'}")
        
        factors = overall_risk.get('factors', [])
        if factors:
            print(f"\n   Risk Factors:")
            for factor in factors:
                print(f"      • {factor}")
        
        recommendations = overall_risk.get('recommendations', [])
        if recommendations:
            print(f"\n   Recommendations:")
            for rec in recommendations:
                print(f"      • {rec}")
        
        # Save full results to file
        output_file = Path(__file__).parent / "test_results_instagram.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n\n💾 Full results saved to: {output_file}")
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
        return result
        
    except Exception as e:
        print(f"\n\n❌ ERROR during scan:")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Message: {e}")
        print(f"\n📋 Full traceback:")
        import traceback
        traceback.print_exc()
        
        # Additional debugging info
        print(f"\n� Debugging Information:")
        print(f"   Python Version: {sys.version}")
        print(f"   Platform: {sys.platform}")
        
        # Check if it's a Playwright-specific error
        if "playwright" in str(e).lower() or "browser" in str(e).lower():
            print(f"\n⚠️  This appears to be a Playwright/Browser error.")
            print(f"   Possible causes:")
            print(f"   1. Python 3.13 is not fully compatible with Playwright")
            print(f"   2. Browser automation may be blocked")
            print(f"   3. Session file may be invalid or expired")
        
        return None


if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_instagram_scan())
    
    # Exit with appropriate code
    sys.exit(0 if result else 1)
