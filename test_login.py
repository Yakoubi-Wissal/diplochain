import urllib.request
import urllib.parse
import json
import sys

# Try port 8000 for api-gateway
url = "http://localhost:8000/api/users/auth/login"
data = urllib.parse.urlencode({
    'username': 'admin@diplochain.tn',
    'password': 'Admin@1234'
}).encode('utf-8')

req = urllib.request.Request(url, data=data)
try:
    with urllib.request.urlopen(req) as response:
        result = response.read().decode('utf-8')
        print(f"Success: {response.getcode()}")
        print(result)
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code}")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
