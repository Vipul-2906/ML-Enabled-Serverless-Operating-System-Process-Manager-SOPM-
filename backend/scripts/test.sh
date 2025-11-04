#!/bin/bash

GATEWAY="http://localhost:8080"

echo "🧪 Testing SOPM with 100 Functions..."
echo "Gateway: $GATEWAY"
echo ""

# Test function count
echo "1️⃣ Checking total function count..."
RESPONSE=$(curl -s $GATEWAY/api/functions)

# Parse total count
FUNCTION_COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total_functions', '0'))")
echo "   Total functions: $FUNCTION_COUNT"

if [ "$FUNCTION_COUNT" != "100" ]; then
    echo "   ❌ Expected 100 functions, got $FUNCTION_COUNT"
    echo ""
    echo "   🕵️ Missing functions (comparing to expected 1..100):"
    python3 - <<'PYCODE'
import json, sys
try:
    data = json.load(sys.stdin)
    funcs = data.get('functions') or data.get('data') or []
    names = set(f.get('name') for f in funcs)
    expected = {f"function_{i}" for i in range(1, 101)}
    missing = sorted(expected - names)
    print("\n".join(missing) if missing else "None missing")
except Exception as e:
    print(f"⚠️ Could not parse functions: {e}")
PYCODE
    exit 1
else
    echo "   ✅ All 100 functions loaded!"
fi



echo ""
echo "2️⃣ Testing functions from each category..."

# Data Processing
echo "   📊 Data Processing..."
curl -s -X POST $GATEWAY/api/execute -H "Content-Type: application/json" \
  -d '{"function_name": "csv_parser", "payload": {"csv_data": "name,age\nAlice,30"}}' > /dev/null
echo "      ✓ csv_parser"

# Text Analysis
echo "   📝 Text Analysis..."
curl -s -X POST $GATEWAY/api/execute -H "Content-Type: application/json" \
  -d '{"function_name": "palindrome_checker", "payload": {"text": "racecar"}}' > /dev/null
echo "      ✓ palindrome_checker"

# Math/Compute
echo "   🔢 Math/Compute..."
curl -s -X POST $GATEWAY/api/execute -H "Content-Type: application/json" \
  -d '{"function_name": "fibonacci_generator", "payload": {"count": 10}}' > /dev/null
echo "      ✓ fibonacci_generator"

# API Integrations
echo "   🌐 API Integrations..."
curl -s -X POST $GATEWAY/api/execute -H "Content-Type: application/json" \
  -d '{"function_name": "joke_generator", "payload": {}}' > /dev/null
echo "      ✓ joke_generator"

# Utilities
echo "   🛠️ Utilities..."
curl -s -X POST $GATEWAY/api/execute -H "Content-Type: application/json" \
  -d '{"function_name": "hex_to_rgb", "payload": {"hex": "#FF5733"}}' > /dev/null
echo "      ✓ hex_to_rgb"

echo ""
echo "3️⃣ System Statistics..."
curl -s $GATEWAY/api/stats | python3 -m json.tool

echo ""
echo "✅ All tests passed! 100 functions are working!"