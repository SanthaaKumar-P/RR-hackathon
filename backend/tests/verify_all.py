import urllib.request
import json

api_urls = [
    "http://localhost:8000/health",
    "http://localhost:8000/api/v1/overview",
    "http://localhost:8000/api/v1/batters?format=T20",
    "http://localhost:8000/api/v1/bowlers?format=T20",
    "http://localhost:8000/api/v1/pressure?format=T20",
    "http://localhost:8000/api/v1/matches?format=T20",
    "http://localhost:8000/api/v1/scenarios?format=T20&discipline=batter",
    "http://localhost:8000/api/v1/audit",
    "http://localhost:8080/",
    "http://localhost:8080/batters",
    "http://localhost:8080/bowlers",
    "http://localhost:8080/pressure",
    "http://localhost:8080/matches",
    "http://localhost:8080/comparison",
    "http://localhost:8080/methodology",
    "http://localhost:8080/scenarios",
    "http://localhost:8080/audit",
]

print("=== VERIFYING ALL SERVICES & ENDPOINTS ===")
all_passed = True
for url in api_urls:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SupeRR-Verifier/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            code = resp.getcode()
            print(f"[OK {code}] {url}")
    except Exception as e:
        print(f"[FAIL] {url} -> {e}")
        all_passed = False

if all_passed:
    print("\nSUCCESS: All 17 endpoints and routes responded with 200 OK!")
else:
    print("\nWARNING: Some endpoints failed.")
