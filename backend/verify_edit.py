
import json
import urllib.request
import urllib.error
import sys

BASE_URL = "http://localhost:8000/api/v1"
AUTH_data = {"username": "admin@example.com", "password": "Password123!"}

def request(url, method="GET", data=None, headers={}):
    try:
        if data:
            data = urllib.parse.urlencode(data).encode('utf-8') if 'application/x-www-form-urlencoded' in headers.get('Content-Type', '') else json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, method=method)
        for k, v in headers.items():
            req.add_header(k, v)
        
        with urllib.request.urlopen(req) as response:
            resp_body = response.read().decode('utf-8')
            return json.loads(resp_body)
    except urllib.error.HTTPError as e:
        print(f"Request failed: {method} {url} {e.code}")
        print(e.read().decode('utf-8'))
        raise

try:
    print("Starting verification (urllib)...")
    
    # 1. Login (x-www-form-urlencoded)
    login_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = request(f"{BASE_URL}/auth/access-token", method="POST", data=AUTH_data, headers=login_headers)
    token = resp["access_token"]
    print(f"Login success.")

    auth_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 2. Update Skill
    update_data = {"title": "Updated Title via Python Script"}
    print(f"Updating skill 1 title to: {update_data['title']}")
    resp = request(f"{BASE_URL}/skills/1", method="PATCH", data=update_data, headers=auth_headers)
    new_title = resp['data']['title']
    print(f"Update returned title: {new_title}")
    
    if new_title != update_data['title']:
        print("Update mismatch!")
        sys.exit(1)

    # 3. Verify Get
    print("Verifying via GET...")
    resp = request(f"{BASE_URL}/skills/1", method="GET", headers=auth_headers)
    actual_title = resp['data']['title']
    print(f"GET returned title: {actual_title}")
    
    if actual_title != update_data['title']:
        print("GET mismatch!")
        sys.exit(1)
    
    # 4. Revert
    revert_data = {"title": "Multiply whole numbers"}
    print(f"Reverting title to: {revert_data['title']}")
    resp = request(f"{BASE_URL}/skills/1", method="PATCH", data=revert_data, headers=auth_headers)
    print(f"Revert success. Title: {resp['data']['title']}")
    
    print("VERIFICATION PASSED")

except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
