#!/bin/bash
start_time=$(date +%s%N)
curl -s http://127.0.0.1:8001/api/v1/grades > /dev/null
end_time=$(date +%s%N)
elapsed=$((end_time - start_time))
echo "127.0.0.1 time: $elapsed ns"

start_time=$(date +%s%N)
curl -s http://localhost:8001/api/v1/grades > /dev/null
end_time=$(date +%s%N)
elapsed=$((end_time - start_time))
echo "localhost time: $elapsed ns"
