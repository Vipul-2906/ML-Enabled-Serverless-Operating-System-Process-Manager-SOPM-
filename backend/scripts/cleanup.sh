#!/bin/bash

echo "🧹 Cleaning up SOPM deployment..."

kubectl delete namespace sopm

echo "✅ Cleanup complete!"
