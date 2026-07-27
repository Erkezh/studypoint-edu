import requests

def test():
    # Attempt login
    res = requests.post("http://localhost:8001/api/v1/auth/login", json={"email": "erkezh123@gmail.com", "password": "Password123!"})
    if res.status_code != 200:
        print("Login failed", res.text)
        return
    token = res.json()["data"]["access_token"]
    user = res.json()["data"]["user"]
    print("Logged in as:", user)
    
    # Hit family endpoint
    res2 = requests.get("http://localhost:8001/api/v1/auth/me/family", headers={"Authorization": f"Bearer {token}"})
    print("Family members response:", res2.status_code)
    print(res2.json())

test()
