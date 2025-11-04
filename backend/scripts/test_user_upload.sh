#!/bin/bash

GATEWAY="http://localhost:8080"
REGISTRY="http://localhost:8001"

echo "🧪 Testing User Function Upload..."
echo ""

# Test function code
FUNCTION_CODE='
import json
import os

def handler(event):
    """Simple test function"""
    name = event.get("name", "World")
    return {
        "message": f"Hello, {name}!",
        "execution_id": os.getenv("EXECUTION_ID")
    }

if __name__ == "__main__":
    input_data = json.loads(os.getenv("INPUT_DATA", "{}"))
    result = handler(input_data)
    print(json.dumps(result))
'

# Upload function
echo "1️⃣ Uploading function..."
UPLOAD_RESPONSE=$(curl -s -X POST $REGISTRY/functions \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"test_user\",
    \"name\": \"hello_world\",
    \"description\": \"Test hello world function\",
    \"runtime\": \"python3.11\",
    \"code\": $(echo "$FUNCTION_CODE" | jq -Rs .),
    \"dependencies\": \"\"
  }")

echo "$UPLOAD_RESPONSE" | python3 -m json.tool

FUNCTION_ID=$(echo "$UPLOAD_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('function_id', ''))")

if [ -z "$FUNCTION_ID" ]; then
    echo "❌ Failed to upload function"
    exit 1
fi

echo "✅ Function uploaded: $FUNCTION_ID"
echo ""

# Wait for build
echo "2️⃣ Waiting for build to complete..."
for i in {1..60}; do
    STATUS=$(curl -s $REGISTRY/functions/$FUNCTION_ID | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))")
    echo "  Build status: $STATUS"
    
    if [ "$STATUS" == "ready" ]; then
        echo "✅ Build completed!"
        break
    elif [ "$STATUS" == "failed" ]; then
        echo "❌ Build failed"
        curl -s $REGISTRY/functions/$FUNCTION_ID | python3 -m json.tool
        exit 1
    fi
    
    sleep 5
done

echo ""

# Execute function
echo "3️⃣ Executing function..."
EXEC_RESPONSE=$(curl -s -X POST $GATEWAY/api/execute \
  -H "Content-Type: application/json" \
  -d "{
    \"function_name\": \"user_function_$FUNCTION_ID\",
    \"payload\": {\"name\": \"SOPM User\"}
  }")

echo "$EXEC_RESPONSE" | python3 -m json.tool

JOB_ID=$(echo "$EXEC_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('job_id', 0))")

if [ "$JOB_ID" == "0" ]; then
    echo "❌ Failed to execute function"
    exit 1
fi

echo ""

# Get result
echo "4️⃣ Getting result..."
sleep 5

curl -s $GATEWAY/api/status/$JOB_ID | python3 -m json.tool

echo ""
echo "✅ User function upload test complete!"
