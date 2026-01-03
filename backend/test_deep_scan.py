"""
Test script for deep scan API
"""
import requests
import json
import time

def test_deep_scan(identifier, platforms=["instagram"]):
    """Test the deep scan API endpoint."""
    url = "http://localhost:8000/api/deep-scan/direct"
    
    payload = {
        "identifier_value": identifier,
        "identifier_type": "name",
        "platforms": platforms
    }
    
    print(f"🔍 Starting deep scan for: {identifier}")
    print(f"📡 URL: {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    print("-" * 60)
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=30)
        end_time = time.time()
        
        print(f"⏱️  Response time: {end_time - start_time:.2f} seconds")
        print(f"🔢 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS - Deep scan results:")
            print("=" * 60)
            
            # Print key results
            print(f"Input: {result.get('input', 'N/A')}")
            print(f"Identifier Type: {result.get('identifier_type', 'N/A')}")
            print(f"Username: {result.get('username', 'N/A')}")
            print(f"Total Profiles Found: {result.get('total_profiles_found', 0)}")
            print(f"Total Impersonation Risks: {result.get('total_impersonation_risks', 0)}")
            
            # Print profiles found
            profiles = result.get('profiles_found', [])
            print(f"\n📊 PROFILES FOUND ({len(profiles)}):")
            for i, profile in enumerate(profiles, 1):
                print(f"\n  Profile {i}:")
                print(f"    Platform: {profile.get('platform', 'N/A')}")
                print(f"    Username: {profile.get('username', 'N/A')}")
                print(f"    Name: {profile.get('name', 'N/A')}")
                print(f"    Bio: {profile.get('bio', 'N/A')[:100]}...")
                
                # Print PII data
                pii_data = profile.get('pii', {})
                total_pii = sum(len(v) if isinstance(v, list) else 0 for v in pii_data.values())
                print(f"    PII Items Found: {total_pii}")
                
                if total_pii > 0:
                    print(f"    PII Details:")
                    for pii_type, items in pii_data.items():
                        if items:
                            print(f"      {pii_type.title()}: {items}")
            
            # Print impersonation risks
            imp_risks = result.get('impersonation_risks', [])
            if imp_risks:
                print(f"\n⚠️  IMPERSONATION RISKS ({len(imp_risks)}):")
                for i, risk in enumerate(imp_risks, 1):
                    print(f"  Risk {i}: {risk}")
            
            # Print overall risk
            overall_risk = result.get('overall_risk', {})
            print(f"\n🎯 OVERALL RISK ASSESSMENT:")
            print(f"    Level: {overall_risk.get('level', 'N/A')}")
            print(f"    Score: {overall_risk.get('score', 0)}/100")
            print(f"    PII Exposure: {overall_risk.get('pii_exposure', False)}")
            print(f"    Impersonation Detected: {overall_risk.get('impersonation_detected', False)}")
            
            factors = overall_risk.get('factors', [])
            if factors:
                print(f"    Risk Factors:")
                for factor in factors:
                    print(f"      - {factor}")
            
            recommendations = overall_risk.get('recommendations', [])
            if recommendations:
                print(f"    Recommendations:")
                for rec in recommendations:
                    print(f"      - {rec}")
            
            # Print warning if any
            warning = result.get('warning')
            if warning:
                print(f"\n⚠️  WARNING: {warning}")
            
        else:
            print(f"\n❌ ERROR - API request failed")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERROR - Network/connection error: {e}")
    except Exception as e:
        print(f"\n❌ ERROR - Unexpected error: {e}")

if __name__ == "__main__":
    # Test with "cristiano ronaldo"
    test_deep_scan("cristiano ronaldo", ["instagram"])