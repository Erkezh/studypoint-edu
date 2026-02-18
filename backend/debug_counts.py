import asyncio
import json
import httpx

base_url = "http://localhost:8001/api/v1"
auth_data = {"email":"admin@example.com","password":"Password123!"}

async def main():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{base_url}/auth/login", json=auth_data)
            if resp.status_code != 200:
                print(f"Login failed: {resp.text}")
                return

            token = resp.json()["data"]["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            plugins_resp = await client.get(f"{base_url}/admin/plugins", headers=headers)
            questions_resp = await client.get(f"{base_url}/admin/questions", headers=headers)

            plugins = plugins_resp.json()["data"]
            questions = questions_resp.json()["data"]

            print(f"Plugins count: {len(plugins)}")
            print(f"Questions count: {len(questions)}")

            # Check logic
            plugin_ids = set()
            for p in plugins:
                plugin_ids.add(p["id"])

            print("\nPlugin IDs:")
            for pid in sorted(list(plugin_ids)):
                print(f"- {pid}")

            print("\nQuestions:")
            # Inspect first question structure to see if we can link it back
            if questions:
                # We need to see if questions have a 'plugin_id' or similar in 'data'
                print(json.dumps(questions[0], indent=2))
                
                # Check how many questions are linked to plugins
                linked_count = 0
                seen_plugins = set()
                
                for q in questions:
                    # Check if question data has plugin references
                    # Usually in data['plugin_id'] or metadata
                    q_data = q.get('data', {})
                    p_id = q_data.get('plugin_id')
                    if p_id:
                        linked_count += 1
                        seen_plugins.add(p_id)
                
                print(f"\nQuestions linked to plugins: {linked_count}")
                print(f"Plugins used in questions: {len(seen_plugins)}")
                
                unused_plugins = plugin_ids - seen_plugins
                print(f"Unused Plugins: {unused_plugins}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
