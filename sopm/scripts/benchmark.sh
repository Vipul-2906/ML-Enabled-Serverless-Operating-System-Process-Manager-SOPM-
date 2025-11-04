#!/bin/bash

GATEWAY_URL="http://$(minikube ip):30000"

echo "⚡ SOPM Performance Benchmark"
echo "=============================="
echo ""

# Function to measure execution time
measure_execution() {
    local function_name=$1
    local payload=$2
    local iterations=$3
    
    echo "Testing: $function_name ($iterations iterations)"
    
    local total_time=0
    local success_count=0
    
    for i in $(seq 1 $iterations); do
        start=$(date +%s%3N)
        
        response=$(curl -s -X POST "$GATEWAY_URL/api/execute" \
          -H "Content-Type: application/json" \
          -d "{\"function_name\": \"$function_name\", \"payload\": $payload}")
        
        job_id=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('job_id', 0))" 2>/dev/null)
        
        if [ "$job_id" != "0" ]; then
            # Poll for completion
            while true; do
                status=$(curl -s "$GATEWAY_URL/api/status/$job_id" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null)
                
                if [ "$status" == "completed" ] || [ "$status" == "failed" ]; then
                    break
                fi
                sleep 0.1
            done
            
            end=$(date +%s%3N)
            elapsed=$((end - start))
            total_time=$((total_time + elapsed))
            success_count=$((success_count + 1))
        fi
    done
    
    if [ $success_count -gt 0 ]; then
        avg_time=$((total_time / success_count))
        echo "  ✓ Average time: ${avg_time}ms (${success_count}/${iterations} successful)"
    else
        echo "  ✗ All requests failed"
    fi
    echo ""
}

# Run benchmarks
echo "🏃 Running benchmarks..."
echo ""

measure_execution "sentiment_analysis" '{"text": "SOPM is awesome"}' 10
measure_execution "hash_generator" '{"text": "benchmark test"}' 10
measure_execution "calculator" '{"operation": "add", "a": 10, "b": 20}' 10
measure_execution "word_counter" '{"text": "test test test", "top_n": 5}' 10

echo "✅ Benchmark complete!"