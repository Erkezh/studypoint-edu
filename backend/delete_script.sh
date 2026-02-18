#!/bin/bash
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login -H 'Content-Type: application/json' -d '{"email":"admin@example.com","password":"Password123!"}' | jq -r '.data.access_token')
echo "Token: $TOKEN"

IDS=(
"90627428-8ed3-436d-8031-4dcd9e6be8de"
"4fb3653c-a03f-4688-b4fc-fd93ce95bc10"
"8eafe739-97a9-4281-8ddf-860b2aeeebd1"
"4511aff0-ec70-403e-a62e-00137ec258a6"
"4ec6abb5-8a36-47d2-ba8b-d35f77c335cc"
"9293cebb-4775-45f5-9ab3-c320d411d185"
)

for id in "${IDS[@]}"; do
    echo "Deleting $id..."
    curl -X DELETE "http://localhost:8001/api/v1/admin/plugins/$id" -H "Authorization: Bearer $TOKEN"
    echo ""
done
