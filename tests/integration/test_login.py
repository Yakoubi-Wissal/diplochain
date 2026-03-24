import requests
url = "http://localhost:8000/api/users/auth/login"
data = {
    "username": "superadmin@diplochain.com",
    "password": "superadmin123"
}
try:
    # OAuth2 login usually expects form-data
    resp = requests.post(url, data=data) 
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
