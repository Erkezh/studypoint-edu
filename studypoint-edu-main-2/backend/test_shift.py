import asyncio
import httpx

API_URL = "http://localhost:8001/api/v1/admin"
TOKEN = "token" # Assuming we might bypass auth or we'll get an error

async def test_grade_shift():
    async with httpx.AsyncClient() as client:
        # Get grades
        r = await client.get(f"{API_URL}/grades")
        print("Initial grades:", r.json())
        
        # We need a proper token or bypass to test this programmatically, otherwise we'll test manually.

if __name__ == "__main__":
    asyncio.run(test_grade_shift())
