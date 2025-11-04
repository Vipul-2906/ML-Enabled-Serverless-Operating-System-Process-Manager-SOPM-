#!/bin/bash

set -e

echo "🔒 Installing gVisor on Minikube..."

# SSH into Minikube node
minikube ssh << 'EOF'
# Download gVisor
curl -fsSL https://storage.googleapis.com/gvisor/releases/release/latest/x86_64/runsc -o /tmp/runsc
curl -fsSL https://storage.googleapis.com/gvisor/releases/release/latest/x86_64/runsc.sha512 -o /tmp/runsc.sha512

# Verify checksum
cd /tmp
sha512sum -c runsc.sha512

# Install runsc
sudo mv /tmp/runsc /usr/local/bin/
sudo chmod +x /usr/local/bin/runsc

# Configure containerd
sudo mkdir -p /etc/containerd
cat <<CONFIG | sudo tee /etc/containerd/config.toml
version = 2
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runsc]
  runtime_type = "io.containerd.runsc.v1"
CONFIG

# Restart containerd
sudo systemctl restart containerd

echo "✅ gVisor installed successfully"
EOF

# Create RuntimeClass in Kubernetes
kubectl apply -f - <<YAML
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc
YAML

echo "✅ gVisor RuntimeClass created"
echo "🎉 gVisor setup complete!"
