import asyncio
import json
import httpx

base_url = "http://localhost:8001/api/v1"
auth_data = {"email":"admin@example.com","password":"Password123!"}

async def main():
    async with httpx.AsyncClient() as client:
        # Login
        resp = await client.post(f"{base_url}/auth/login", json=auth_data)
        token = resp.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get Plugins with full details
        plugins_resp = await client.get(f"{base_url}/admin/plugins", headers=headers)
        plugins = plugins_resp.json()["data"]
        
        # Get Questions
        questions_resp = await client.get(f"{base_url}/admin/questions", headers=headers)
        questions = questions_resp.json()["data"]

        print(f"Total Plugins: {len(plugins)}")
        print(f"Total Questions: {len(questions)}")

        # Print detailed first plugin to see fields
        if plugins:
            print("Sample Plugin Structure:", json.dumps(plugins[0], indent=2))

        # Collect all plugin references from questions
        used_plugin_identifiers = set()
        for q in questions:
            data = q.get("data", {})
            # Check likely fields
            pid = data.get("plugin_id")
            if pid:
                used_plugin_identifiers.add(pid)
            
            # Check if there are other fields
            # print(f"Question {q['id']} uses: {pid}")

        print("\nIdentifiers used in Questions:", used_plugin_identifiers)

        # detailed matching
        unused_plugins = []
        for p in plugins:
            # We need to check if p['id'] or p['name'] or p['slug'] is in used_plugin_identifiers
            # Let's check all possible identifiers
            
            is_used = False
            # Check ID (UUID)
            if p['id'] in used_plugin_identifiers:
                is_used = True
            
            # Check Name (if exists)
            if 'name' in p and p['name'] in used_plugin_identifiers:
                is_used = True
                
            # Check 'module_name' or similar if exists
            
            if not is_used:
                unused_plugins.append(p)

        print(f"\nFound {len(unused_plugins)} potentially unused plugins.")
        for p in unused_plugins:
            print(f"Unused: ID={p['id']}, Name={p.get('name', 'N/A')}")
            
            # Also printing keys just in case
            # print(p.keys())

if __name__ == "__main__":
    asyncio.run(main())
