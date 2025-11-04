#!/bin/bash

GATEWAY_URL="http://$(minikube ip):30000"
CONCURRENT_REQUESTS=50

echo "💪 SOPM Stress Test"
echo "==================="
echo "Concurrent requests: $CONCURRENT_REQUESTS"
echo ""

# Create temporary directory for results
TEMP_DIR=$(mktemp -d)

echo "🚀 Sending $CONCURRENT_REQUESTS concurrent requests..."

# Send concurrent requests
for i in $(seq 1 $CONCURRENT_REQUESTS); do
    {
        start=$(date +%s%3N)
        curl -s -X POST "$GATEWAY_URL/api/execute" \
          -H "Content-Type: application/json" \
          -d '{"function_name": "calculator", "payload": {"operation": "multiply", "a": 7, "b": 6}}' \
          > "$TEMP_DIR/response_$i.json"
        end=$(date +%s%3N)
        echo $((end - start)) > "$TEMP_DIR/time_$i.txt"
    } &
done

# Wait for all requests to complete
wait

echo "✅ All requests sent. Processing results..."
echo ""

# Count successful responses
success_count=0
for file in "$TEMP_DIR"/response_*.json; do
    if grep -q "job_id" "$file"; then
        success_count=$((success_count + 1))
    fi
done

# Calculate average response time
total_time=0
count=0
for file in "$TEMP_DIR"/time_*.txt; do
    time=$(cat "$file")
    total_time=$((total_time + time))
    count=$((count + 1))
done

if [ $count -gt 0 ]; then
    avg_time=$((total_time / count))
fi

echo "📊 Results:"
echo "  Total requests: $CONCURRENT_REQUESTS"
echo "  Successful: $success_count"
echo "  Failed: $((CONCURRENT_REQUESTS - success_count))"
echo "  Average response time: ${avg_time}ms"

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "✅ Stress test complete!"
