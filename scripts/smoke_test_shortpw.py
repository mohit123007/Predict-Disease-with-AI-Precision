import time
import requests

BASE = "http://127.0.0.1:8000"
username = f"smoketest_short_{int(time.time())}"
password = "a"

print("Using username:", username)

r = requests.post(f"{BASE}/auth/register", json={"username": username, "password": password})
print("Register status:", r.status_code)
print(r.text)

r = requests.post(f"{BASE}/auth/login", json={"username": username, "password": password})
print("Login status:", r.status_code)
print(r.text)
