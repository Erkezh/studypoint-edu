import asyncio
import httpx

base_url = "http://localhost:8001/api/v1"
auth_data = {"email":"admin@example.com","password":"Password123!"}

ids_to_delete = [
    "90627428-8ed3-436d-8031-4dcd9e6be8de",
    "4fb3653c-a03f-4688-b4fc-fd93ce95bc10",
    "8eafe739-97a9-4281-8ddf-860b2aeeebd1",
    "4511aff0-ec70-403e-a62e-00137ec258a6",
    "4ec6abb5-8a36-47d2-ba8b-d35f77c335cc",
    "9293cebb-4775-45f5-9ab3-c320d411d185"
]

async def main():
    async with httpx.AsyncClient() as client:
        # Login
        resp = await client.post(f"{base_url}/auth/login", json=auth_data)
        token = resp.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        for pid in ids_to_delete:
            print(f"Deleting plugin {pid}...")
            del_resp = await client.delete(f"{base_url}/admin/plugins/{pid}", headers=headers)
            if del_resp.status_code in [200, 204]:
                print(f"Successfully deleted {pid}")
            else:
                print(f"Failed to delete {pid}: {del_resp.text}")

if __name__ == "__main__":
    asyncio.run(main())
