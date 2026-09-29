import time
import requests

BASE = "http://127.0.0.1:8000"
username = f"smoketest_{int(time.time())}"
password = "SmoketestPass123"

print("Using username:", username)

# Register
r = requests.post(f"{BASE}/auth/register", json={"username": username, "password": password})
print("Register status:", r.status_code)
try:
    print(r.json())
except Exception:
    print(r.text)

# Login
r = requests.post(f"{BASE}/auth/login", json={"username": username, "password": password})
print("Login status:", r.status_code)
try:
    data = r.json()
    print(data)
    token = data.get("access_token")
except Exception:
    print(r.text)
    raise SystemExit(1)

if not token:
    print("No token returned; aborting")
    raise SystemExit(1)

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
# Tabular predict
payload = {"features": {"age": 45, "glucose": 130, "bmi": 28.5}}
pr = requests.post(f"{BASE}/predict/tabular", json=payload, headers=headers)
print("Predict status:", pr.status_code)
try:
    print(pr.json())
except Exception:
    print(pr.text)

print("Smoke test completed")
