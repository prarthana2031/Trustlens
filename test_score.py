import requests

BASE = "https://preeee-276-ml-service-api.hf.space"

print("=" * 60)
print("TESTING ML RESUME SERVICE WITH GEMINI")
print("=" * 60)

# 1. Check health (should show gemini_available: true)
print("\n1. HEALTH CHECK:")
response = requests.get(f"{BASE}/health")
print(f"   Status: {response.status_code}")
data = response.json()
print(f"   Gemini Available: {data.get('gemini_available')}")
print(f"   Document AI Available: {data.get('document_ai_available')}")

# 2. Compare Baseline vs Enhanced scoring
print("\n2. COMPARING BASELINE VS ENHANCED SCORING:")
print("   (Upload a resume file to see the difference)")

resume_path = input("\n   Enter resume file path: ").strip().strip('"')

try:
    with open(resume_path, "rb") as f:
        response = requests.post(
            f"{BASE}/score/compare",
            files={"file": f},
            params={"required_skills": ["python", "sql", "java", "aws", "docker"]}
        )
    
    print(f"\n   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n   📊 BASELINE SCORE:")
        print(f"      Score: {result['baseline']['score']}/100")
        print(f"      Skills Found: {result['baseline']['skills_found']}")
        print(f"      Matched: {result['baseline']['matched_skills']}")
        print(f"      Missing: {result['baseline']['missing_skills']}")
        
        print("\n   ✨ ENHANCED SCORE (with Gemini):")
        print(f"      Score: {result['enhanced']['score']}/100")
        print(f"      Skills Found: {result['enhanced']['skills_found']}")
        print(f"      Matched: {result['enhanced']['matched_skills']}")
        print(f"      Missing: {result['enhanced']['missing_skills']}")
        
        print("\n   📈 COMPARISON:")
        print(f"      Score Difference: +{result['comparison']['score_difference']} points")
        print(f"      Better Mode: {result['comparison']['better_mode']}")
        print(f"      Gemini Used: {result['comparison']['gemini_used']}")
        
        if result['comparison']['gemini_used']:
            print("\n   ✅ GEMINI IS WORKING! Enhanced mode active.")
        else:
            print("\n   ⚠️ Gemini not available. Check if API key is set correctly.")
    else:
        print(f"   Error: {response.text}")
        
except FileNotFoundError:
    print(f"   File not found: {resume_path}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)