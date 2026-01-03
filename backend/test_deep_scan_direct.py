"""
Test script for Deep Scan Direct endpoint
Tests the /api/deep-scan/direct endpoint using OSINT with stored sessions
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8000"
ENDPOINT = f"{API_BASE_URL}/api/deep-scan/direct"

# Test data
test_data = {
    "identifier_type": "name",  # Can be: name, username, email
    "identifier_value": "cristiano ronaldo",  # Test identifier
    "platforms": ["instagram", "facebook", "linkedin", "x"]  # Platforms to search
}

def test_deep_scan_direct():
    """Test the deep scan direct endpoint"""
    print("=" * 80)
    print("TESTING DEEP SCAN DIRECT ENDPOINT")
    print("=" * 80)
    print(f"\nEndpoint: {ENDPOINT}")
    print(f"\nTest Data:")
    print(json.dumps(test_data, indent=2))
    print("\n" + "=" * 80)
    
    try:
        print("\n📡 Sending request to backend...")
        start_time = time.time()
        
        response = requests.post(
            ENDPOINT,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minutes timeout for deep scan
        )
        
        duration = time.time() - start_time
        
        print(f"\n✅ Response received in {duration:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            results = response.json()
            print("\n" + "=" * 80)
            print("RESULTS:")
            print("=" * 80)
            print(json.dumps(results, indent=2))
            
            # Summary
            print("\n" + "=" * 80)
            print("SUMMARY:")
            print("=" * 80)
            print(f"✅ Success: {results.get('success', False)}")
            print(f"🆔 Scan ID: {results.get('scan_id', 'N/A')}")
            print(f"📊 Platforms Analyzed: {results.get('platforms_analyzed', 0)}")
            print(f"👤 Total Profiles Found: {results.get('total_profiles_found', 0)}")
            print(f"🔒 Total PII Exposed: {results.get('total_pii_exposed', 0)}")
            print(f"⚠️  Risk Score: {results.get('risk_score', 0)}")
            print(f"📈 Risk Level: {results.get('risk_level', 'N/A')}")
            
            # Platform details
            if results.get('platform_summary'):
                print("\n📱 Platform Details:")
                for platform, details in results.get('platform_summary', {}).items():
                    print(f"  - {platform.capitalize()}:")
                    print(f"      Profiles: {details.get('profiles_count', 0)}")
                    print(f"      PII Exposed: {details.get('pii_count', 0)}")
            
            # Exposed PII
            if results.get('exposed_pii'):
                print("\n🔓 Exposed PII:")
                for pii in results.get('exposed_pii', []):
                    print(f"  - {pii.get('type', 'N/A')}: {pii.get('value', 'N/A')}")
                    print(f"      Found on: {', '.join(pii.get('platforms', []))}")
            
            # Recommendations
            if results.get('recommendations'):
                print("\n💡 Recommendations:")
                for i, rec in enumerate(results.get('recommendations', []), 1):
                    print(f"  {i}. {rec}")
            
            print("\n" + "=" * 80)
            
        else:
            print(f"\n❌ Error: Status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out after 120 seconds")
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection error - is the server running on http://localhost:8000?")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    test_deep_scan_direct()
