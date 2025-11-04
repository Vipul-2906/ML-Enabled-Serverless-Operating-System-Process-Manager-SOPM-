#!/bin/bash

set -e

echo "🚀 Deploying SOPM Phase 2 (User Upload Features)..."

cd "$(dirname "$0")/.."

# Use Minikube's Docker
eval $(minikube docker-env)

# Build new images
echo "📦 Building Function Registry..."
cd services/function-registry
docker build -t sopm-function-registry:latest .
cd ../..

echo "📦 Building Image Builder..."
cd services/image-builder
docker build -t sopm-image-builder:latest .
cd ../..

# Apply new infrastructure
echo "☸️  Applying Kubernetes manifests..."

# Create sandbox namespace
kubectl apply -f infra/k8s/sandbox-namespace.yaml

# Deploy MinIO
kubectl apply -f services/minio/k8s/

# Deploy Container Registry
kubectl apply -f infra/k8s/registry/

# Apply RBAC
kubectl apply -f infra/k8s/rbac/

# Apply network policies
kubectl apply -f infra/k8s/network-policies/

# Apply gVisor RuntimeClass
kubectl apply -f infra/k8s/gvisor/runtime-class.yaml

# Deploy Function Registry
kubectl apply -f services/function-registry/k8s/

# Deploy Image Builder
kubectl apply -f services/image-builder/k8s/

# Update database schema
echo "📊 Updating database schema..."
kubectl exec -it deployment/postgres -n sopm -- psql -U postgres -d sopm -f /docker-entrypoint-initdb.d/0002_user_functions.sql

echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=minio -n sopm --timeout=120s
kubectl wait --for=condition=ready pod -l app=registry -n sopm --timeout=120s
kubectl wait --for=condition=ready pod -l app=function-registry -n sopm --timeout=120s
kubectl wait --for=condition=ready pod -l app=image-builder -n sopm --timeout=120s

echo "✅ Phase 2 deployment complete!"
echo ""
echo "📊 Cluster Status:"
kubectl get pods -n sopm
echo ""
echo "🔗 New Services:"
echo "  Function Registry: http://$(minikube ip):30001"
echo "  MinIO Console: http://$(minikube ip):30002"
