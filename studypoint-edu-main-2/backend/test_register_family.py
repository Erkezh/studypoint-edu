import urllib.request
import json
import random

# dynamic email
email = f"family_test_{random.randint(1000,9999)}@example.com"
data = {
    "parent_email": email,
    "parent_password": "Password123!",
    "parent_name": "Test Parent",
    "children": [
        {"name": "Child 1", "grade_level": 5},
        {"name": "Child 2", "grade_level": 7}
    ]
}

req1 = urllib.request.Request("http://localhost:8001/api/v1/auth/register/family", data=json.dumps(data).encode(), headers={'Content-Type': 'application/json'})
try:
    res1 = urllib.request.urlopen(req1)
    data1 = json.loads(res1.read().decode())
    token = data1["data"]["access_token"]
    print("Registered and got token:", len(token))

    req2 = urllib.request.Request("http://localhost:8001/api/v1/auth/me/family", headers={'Authorization': 'Bearer ' + token})
    res2 = urllib.request.urlopen(req2)
    print("Family members:", json.loads(res2.read().decode()))
except urllib.error.HTTPError as e:
    print("Error:", e.code, e.reason)
    print(e.read().decode())
