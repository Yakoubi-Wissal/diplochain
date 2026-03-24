#!/usr/bin/env python3
"""
Creates admin user via API and tests login.
Run this in WSL: python3 /home/wissal/diplochain/create_admin.py
"""
import urllib.request
import urllib.parse
import json

BASE = "http://localhost:8000"

def post_json(url, data):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as r:
            return r.getcode(), json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
    except Exception as ex:
        return 0, str(ex)

def post_form(url, data):
    body = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(url, data=body)
    try:
        with urllib.request.urlopen(req) as r:
            return r.getcode(), json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
    except Exception as ex:
        return 0, str(ex)

print("=== Step 1: Create admin user ===")
code, resp = post_json(f"{BASE}/api/users/", {
    "email": "admin@diplochain.tn",
    "username": "admin",
    "password": "Admin@1234",
    "status": "ACTIVE",
    "revoked": False,
    "expired": False
})
print(f"Status: {code}, Response: {json.dumps(resp, indent=2)}")

print("\n=== Step 2: Test login ===")
code2, resp2 = post_form(f"{BASE}/api/users/auth/login", {
    "username": "admin@diplochain.tn",
    "password": "Admin@1234"
})
print(f"Status: {code2}, Response: {json.dumps(resp2, indent=2)}")

if code2 == 200 and "access_token" in resp2:
    print("\n✅ LOGIN SUCCESSFUL! Token received.")
    print(f"   Token (first 50 chars): {resp2['access_token'][:50]}...")
else:
    print("\n❌ Login failed. Checking user-service directly on port 8001...")
    # Try direct user-service
    code3, resp3 = post_form("http://localhost:8001/auth/login", {
        "username": "admin@diplochain.tn",
        "password": "Admin@1234"
    })
    print(f"Direct Status: {code3}, Response: {json.dumps(resp3, indent=2)}")
