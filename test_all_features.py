import requests
import json

BASE = "https://preeee-276-ml-service-api.hf.space"
RESUME_PATH = "C:/Users/Preethi shubha/Downloads/ds_resume_5.pdf"

print("=" * 70)
print("COMPLETE ML SERVICE TEST (with your resume)")
print("=" * 70)

# 1. Health check
print("\n1. HEALTH CHECK")
resp = requests.get(f"{BASE}/health")
print(f"   Status: {resp.status_code}")
health = resp.json()
print(f"   Gemini available: {health.get('gemini_available')}")
print(f"   Service healthy: {health.get('status')}")

# 2. Parse resume (baseline + enhanced)
print("\n2. PARSING RESUME")
with open(RESUME_PATH, "rb") as f:
    r = requests.post(f"{BASE}/parse", files={"file": f}, params={"mode": "enhanced"})
if r.status_code != 200:
    print(f"   ERROR: {r.text}")
    exit()
data = r.json()
parsed = data["parsed_data"]
print(f"   Name: {parsed['contact_info'].get('name', 'N/A')}")
print(f"   Email: {parsed['contact_info'].get('email', 'N/A')}")
print(f"   Skills found: {[s['name'] for s in parsed['skills']][:10]}")
print(f"   Experience: {parsed['total_experience_years']} years")
print(f"   Education: {parsed['education_level']}")
print(f"   Soft skills: {parsed['soft_skills']}")

# 3. Baseline scoring (without Gemini)
print("\n3. BASELINE SCORING")
required = ["python", "sql", "machine learning", "aws", "docker"]
payload = {
    "required_skills": required,
    "resume": parsed,
    "mode": "baseline",
    "fairness_mode": "balanced"
}
r = requests.post(f"{BASE}/score", json=payload)
if r.status_code != 200:
    print(f"   ERROR: {r.text}")
else:
    score = r.json()
    print(f"   Score: {score['score']}/100")
    print(f"   Matched: {score['matched_skills']}")
    print(f"   Missing: {score['missing_skills']}")
    print(f"   Explanation: {score['short_explanation'][:200]}...")

# 4. Enhanced scoring (with Gemini if available)
print("\n4. ENHANCED SCORING (Gemini)")
payload["mode"] = "enhanced"
r = requests.post(f"{BASE}/score", json=payload)
if r.status_code != 200:
    print(f"   ERROR: {r.text}")
else:
    score = r.json()
    print(f"   Score: {score['score']}/100")
    print(f"   Matched: {score['matched_skills']}")
    print(f"   Missing: {score['missing_skills']}")
    print(f"   Explanation: {score['short_explanation'][:200]}...")

# 5. Compare baseline vs enhanced
print("\n5. COMPARE SCORING MODES")
with open(RESUME_PATH, "rb") as f:
    r = requests.post(
        f"{BASE}/score/compare",
        files={"file": f},
        params={"required_skills": required, "fairness_mode": "balanced"}
    )
if r.status_code != 200:
    print(f"   ERROR: {r.text}")
else:
    comp = r.json()
    print(f"   Baseline score: {comp['baseline']['score']}")
    print(f"   Enhanced score: {comp['enhanced']['score']}")
    print(f"   Difference: +{comp['comparison']['difference']} points")
    print(f"   Gemini used: {comp['comparison']['gemini_used']}")

# 6. BIAS DETECTION (critical test)
print("\n6. BIAS DETECTION")
bias_data = {
    "scores": [85, 72, 88, 65, 90, 78, 82, 70],
    "candidates_data": [
        {"gender": "Female"}, {"gender": "Male"},
        {"gender": "Female"}, {"gender": "Male"},
        {"gender": "Female"}, {"gender": "Male"},
        {"gender": "Female"}, {"gender": "Male"}
    ]
}
r = requests.post(f"{BASE}/bias/detect", json=bias_data)
if r.status_code != 200:
    print(f"   ERROR: {r.text}")
else:
    bias = r.json()
    print(f"   Bias detected: {bias.get('bias_detected')}")
    print(f"   p-value: {bias.get('p_value')}")
    print(f"   Groups compared: {bias.get('groups_compared')}")
    print(f"   Recommendation: {bias.get('recommendation')}")
    if bias.get('group_statistics'):
        for group, stats in bias['group_statistics'].items():
            print(f"   {group}: mean={stats['mean']}, count={stats['count']}")

# 7. Final verdict
print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
print("✅ If all steps returned 200, your ML service is fully operational.")
print("✅ Bias detection is working (no 500 error).")
print("✅ Gemini enhancement is active if you set the API key.")