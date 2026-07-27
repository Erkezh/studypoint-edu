import asyncio
import json
import httpx

base_url = "http://localhost:8001/api/v1"
auth_data = {"email":"admin@example.com","password":"Password123!"}

async def main():
    try:
        async with httpx.AsyncClient() as client:
            # Login
            resp = await client.post(f"{base_url}/auth/login", json=auth_data)
            token = resp.json()["data"]["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # Fetch
            plugins = (await client.get(f"{base_url}/admin/plugins", headers=headers)).json()["data"]
            questions = (await client.get(f"{base_url}/admin/questions", headers=headers)).json()["data"]

            # Map Plugin ID to Name
            plugin_map = {p["id"]: p.get("name", "Unknown") for p in plugins}

            # Usage counts
            plugin_usage = {pid: 0 for pid in plugin_map.keys()}
            
            for q in questions:
                # Check data for plugin_id
                # Structure of Q data varies but for plugins it usually has plugin_id
                q_data = q.get("data", {})
                pid = q_data.get("plugin_id")
                
                # Some questions might NOT be plugins (though output said 12 linked)
                if pid and pid in plugin_usage:
                    plugin_usage[pid] += 1
                elif pid:
                    print(f"Warning: Question {q['id']} uses unknown plugin {pid}")

            unused = []
            duplicates = []
            
            for pid, count in plugin_usage.items():
                if count == 0:
                    unused.append(plugin_map[pid])
                elif count > 1:
                    duplicates.append((plugin_map[pid], count))

            print("Unused Plugins:", ", ".join(unused))
            if duplicates:
                print("Plugins used multiple times:", ", ".join([f"{name} ({count}x)" for name, count in duplicates]))
            
            print(f"Total Plugins: {len(plugins)}")
            print(f"Total Questions: {len(questions)}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
