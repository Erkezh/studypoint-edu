import asyncio
from app.utils.redis import get_redis
import json

async def main():
    r = get_redis()
    keys = await r.keys("student:presence:*")
    print(f"Active student presence keys: {keys}")
    for k in keys:
        val = await r.get(k)
        print(f"Key {k} -> {val}")

if __name__ == "__main__":
    asyncio.run(main())
