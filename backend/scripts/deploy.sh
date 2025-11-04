#!/bin/bash

set -e

echo "🚀 Deploying SOPM with 100 Functions..."

# Navigate to project root
cd /mnt/d/sopm

# Use Minikube's Docker environment
echo "🐳 Configuring Docker to use Minikube..."
eval $(minikube docker-env)

# Build worker image with 100 functions
echo "📦 Building Worker image (100 functions)..."
cd services/worker
docker build -t sopm-worker:latest .
if [ $? -ne 0 ]; then
    echo "❌ Worker build failed!"
    exit 1
fi
cd ../..

# Build gateway image
echo "📦 Building Gateway image..."
cd services/gateway
docker build -t sopm-gateway:latest .
if [ $? -ne 0 ]; then
    echo "❌ Gateway build failed!"
    exit 1
fi
cd ../..

# Restart worker pods
echo "♻️  Restarting Worker pods..."
kubectl delete pods -l app=worker -n sopm

# Restart gateway pods
echo "♻️  Restarting Gateway pods..."
kubectl delete pods -l app=gateway -n sopm

# Wait for pods to restart
echo "⏳ Waiting for pods to restart (30 seconds)..."
sleep 30

# Check pod status
echo "📊 Checking pod status..."
kubectl get pods -n sopm

# Verify worker has 100 functions
echo ""
echo "🔍 Verifying function count in worker..."
kubectl logs deployment/worker -n sopm | grep "Registered"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📡 To access the gateway:"
echo "   Terminal 1: kubectl port-forward -n sopm service/gateway-service 8080:80"
echo "   Terminal 2: curl http://localhost:8080/api/functions"