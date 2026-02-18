import asyncio
import httpx
import json

base_url = "http://127.0.0.1:8001/api/v1"
auth_data = {"email":"admin@example.com","password":"Password123!"}

async def main():
    try:
        async with httpx.AsyncClient() as client:
            # Login
            print("Logging in...")
            resp = await client.post(f"{base_url}/auth/login", json=auth_data)
            if resp.status_code != 200:
                print(f"Login failed: {resp.status_code} {resp.text}")
                return
            token = resp.json()["data"]["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # Get Topics
            print("Fetching topics...")
            topics_resp = await client.get(f"{base_url}/admin/topics", headers=headers)
            print(f"Topics Response Status: {topics_resp.status_code}")
            
            if topics_resp.status_code == 200:
                data = topics_resp.json()
                print(f"Topics Data Type: {type(data.get('data'))}")
                if isinstance(data.get('data'), list):
                    print(f"Topics Count: {len(data['data'])}")
                else:
                    print("Topics data is NOT a list:", data)
            else:
                print(f"Error fetching topics: {topics_resp.text}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(main())
