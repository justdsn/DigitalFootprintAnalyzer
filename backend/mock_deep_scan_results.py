"""
Mock Deep Scan Results for Testing

This simulates what the deep scan should return for "cristiano ronaldo" 
when the Playwright browser is working correctly.
"""

def get_mock_deep_scan_results():
    """
    Mock results showing what should be found for 'cristiano ronaldo' search
    """
    return {
        "input": "cristiano ronaldo",
        "identifier_type": "name",
        "username": "cristiano.ronaldo",
        "timestamp": "2026-01-01T22:15:00.000Z",
        "profiles_found": [
            {
                "platform": "instagram",
                "username": "cristiano",
                "name": "Cristiano Ronaldo",
                "bio": "Manchester United, Portugal, Al Nassr, Nike Athlete",
                "url": "https://www.instagram.com/cristiano",
                "collection_success": True,
                "pii": {
                    "emails": [],
                    "phones": [],
                    "urls": ["https://www.nike.com"],
                    "mentions": ["@nike", "@manchesterunited", "@alnassrfc"]
                },
                "ner_entities": {
                    "PERSON": ["Cristiano Ronaldo"],
                    "ORG": ["Manchester United", "Portugal", "Al Nassr", "Nike"],
                    "GPE": ["Portugal"]
                },
                "analysis": {
                    "username_similarity": 85,
                    "bio_similarity": 95,
                    "pii_exposure_score": 15,  # URLs and mentions
                    "timeline_risk": "medium",
                    "has_exposed_email": False,
                    "has_exposed_phone": False,
                    "total_pii_items": 4
                }
            },
            {
                "platform": "instagram",
                "username": "cristiano_ronaldo_official",
                "name": "CR7 Official",
                "bio": "Official Cristiano Ronaldo fan page. Contact: cr7fan@gmail.com",
                "url": "https://www.instagram.com/cristiano_ronaldo_official",
                "collection_success": True,
                "pii": {
                    "emails": ["cr7fan@gmail.com"],
                    "phones": [],
                    "urls": [],
                    "mentions": ["@cristiano"]
                },
                "ner_entities": {
                    "PERSON": ["Cristiano Ronaldo"],
                    "ORG": ["CR7"]
                },
                "analysis": {
                    "username_similarity": 90,
                    "bio_similarity": 80,
                    "pii_exposure_score": 25,  # Email exposure
                    "timeline_risk": "medium",
                    "has_exposed_email": True,
                    "has_exposed_phone": False,
                    "total_pii_items": 2
                }
            }
        ],
        "impersonation_risks": [
            {
                "type": "potential_impersonation",
                "platform": "instagram", 
                "username": "cristiano_ronaldo_official",
                "risk_level": "medium",
                "reason": "Similar name and references to official account but different username pattern",
                "confidence": 0.75
            }
        ],
        "correlation": {
            "correlated": True,
            "overlaps": ["name_similarity", "sports_references"],
            "contradictions": [],
            "impersonation_score": 0.75,
            "impersonation_level": "medium",
            "flags": ["username_variation", "fan_account_indicators"]
        },
        "overall_risk": {
            "level": "medium",
            "score": 45,
            "factors": [
                "Found 6 PII items across profiles",
                "Detected 1 potential impersonation accounts"
            ],
            "recommendations": [
                "Review and remove exposed personal information from public profiles",
                "Monitor for unauthorized use of your identity"
            ],
            "pii_exposure": True,
            "impersonation_detected": True
        },
        "total_profiles_found": 2,
        "total_impersonation_risks": 1,
        "processing_time_ms": 4500.0
    }

def display_results(results):
    """Display the mock results in a formatted way"""
    print("=" * 80)
    print("🧪 MOCK DEEP SCAN RESULTS FOR 'CRISTIANO RONALDO'")
    print("=" * 80)
    print()
    
    # Input info
    print(f"🔍 Input: {results['input']}")
    print(f"📝 Type: {results['identifier_type']}")
    print(f"👤 Username: {results['username']}")
    print(f"⏱️  Processing Time: {results['processing_time_ms']:.1f}ms")
    print()
    
    # Profiles found
    print(f"👥 PROFILES FOUND: {results['total_profiles_found']}")
    print("-" * 50)
    
    for i, profile in enumerate(results['profiles_found'], 1):
        print(f"\n🎯 Profile {i}: {profile['username']}")
        print(f"   Platform: {profile['platform'].title()}")
        print(f"   Name: {profile['name']}")
        print(f"   Bio: {profile['bio']}")
        print(f"   URL: {profile['url']}")
        
        # PII Analysis
        analysis = profile['analysis']
        print(f"\n   📊 ANALYSIS:")
        print(f"      Username Similarity: {analysis['username_similarity']}%")
        print(f"      Bio Similarity: {analysis['bio_similarity']}%")
        print(f"      PII Exposure Score: {analysis['pii_exposure_score']}/100")
        print(f"      Total PII Items: {analysis['total_pii_items']}")
        print(f"      Has Exposed Email: {analysis['has_exposed_email']}")
        print(f"      Has Exposed Phone: {analysis['has_exposed_phone']}")
        
        # PII Details
        pii = profile['pii']
        if any(pii.values()):
            print(f"\n   🔍 PII FOUND:")
            for pii_type, items in pii.items():
                if items:
                    print(f"      {pii_type.title()}: {items}")
    
    # Impersonation risks
    print(f"\n⚠️  IMPERSONATION RISKS: {results['total_impersonation_risks']}")
    print("-" * 50)
    
    for i, risk in enumerate(results['impersonation_risks'], 1):
        print(f"\n🚨 Risk {i}:")
        print(f"   Type: {risk['type']}")
        print(f"   Platform: {risk['platform'].title()}")
        print(f"   Username: {risk['username']}")
        print(f"   Risk Level: {risk['risk_level'].upper()}")
        print(f"   Reason: {risk['reason']}")
        print(f"   Confidence: {risk['confidence']:.1%}")
    
    # Overall risk
    overall = results['overall_risk']
    print(f"\n🎯 OVERALL RISK ASSESSMENT")
    print("-" * 50)
    print(f"Level: {overall['level'].upper()}")
    print(f"Score: {overall['score']}/100")
    print(f"PII Exposure: {overall['pii_exposure']}")
    print(f"Impersonation Detected: {overall['impersonation_detected']}")
    
    print(f"\n📋 Risk Factors:")
    for factor in overall['factors']:
        print(f"   • {factor}")
    
    print(f"\n💡 Recommendations:")
    for rec in overall['recommendations']:
        print(f"   • {rec}")
    
    print("\n" + "=" * 80)
    print("✅ This is what the deep scan SHOULD return when working correctly!")
    print("🔧 The actual issue: Playwright browser fails to initialize on Python 3.13")
    print("📝 Fix needed: Proper asyncio event loop policy configuration")
    print("=" * 80)

if __name__ == "__main__":
    results = get_mock_deep_scan_results()
    display_results(results)