import urllib.request
import urllib.parse
import json

req1 = urllib.request.Request("http://localhost:8001/api/v1/auth/login", data=b'{"email": "erkezh123@gmail.com", "password": "Password123!"}', headers={'Content-Type': 'application/json'})
try:
    res1 = urllib.request.urlopen(req1)
    data1 = json.loads(res1.read().decode())
    token = data1["data"]["access_token"]
    print("Token length:", len(token))

    req2 = urllib.request.Request("http://localhost:8001/api/v1/auth/me/family", headers={'Authorization': 'Bearer ' + token})
    res2 = urllib.request.urlopen(req2)
    print("Family members:", json.loads(res2.read().decode()))
except urllib.error.HTTPError as e:
    print("Error:", e.code, e.reason)
    print(e.read().decode())
