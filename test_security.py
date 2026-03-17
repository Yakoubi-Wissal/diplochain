
import requests
import time

BASE_URL = "http://localhost:8000/api/users"

def test_security_flow():
    print("--- Security Verification (JWT & RBAC) ---")
    
    unique_user = f"testuser_{int(time.time())}"
    email = f"{unique_user}@example.com"
    password = "secretpassword"

    # 1. Create User
    print(f"Step 1: Creating user {email}...")
    # service='users', path='/' -> http://user-service:8000/users// -> normalized to /users/
    resp = requests.post(f"{BASE_URL}/", json={
        "username": unique_user,
        "email": email,
        "password": password,
        "status": "ACTIF"
    })
    if resp.status_code != 201:
        print(f"FAIL: Create user failed: {resp.status_code} - {resp.text}")
        return
    print("SUCCESS: User created.")

    # 2. Login
    print("Step 2: Logging in...")
    resp = requests.post(f"{BASE_URL}/auth/login", data={
        "username": email,
        "password": password
    })
    if resp.status_code != 200:
        print(f"FAIL: Login failed: {resp.status_code} - {resp.text}")
        return
    token = resp.json()["access_token"]
    print(f"SUCCESS: Logged in. Token received.")

    # 3. Access /me (Auth check)
    print("Step 3: Accessing /auth/me...")
    # service='users', path='auth/me' -> http://user-service:8000/users/auth/me
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    if resp.status_code != 200:
        print(f"FAIL: /me access failed: {resp.text}")
        return
    user_info = resp.json()
    print(f"SUCCESS: Retrieved profile for {user_info['email']}")

    print("--- Security Flow Verified ---")

if __name__ == "__main__":
    test_security_flow()
