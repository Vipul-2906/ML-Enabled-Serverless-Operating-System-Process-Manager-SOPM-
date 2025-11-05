# 🖥️ SOPM — Serverless Operating System Process Manager

**Zero Cold Start • 100 Pre-loaded Functions • User Upload Support • Kubernetes Native**

SOPM is a **serverless execution platform** that acts like an **operating system process manager** — capable of executing hundreds of functions instantly with near-zero cold starts, full user upload support, and dynamic sandboxing using **gVisor**.

---

## 🚀 Features

- ⚡ **Zero Cold Start:** Pre-loaded functions execute in under **50ms**
- 🧩 **100 Built-in Functions:** Covering math, text, data, and utility operations
- ☁️ **Serverless Execution:** Functions run as ephemeral Kubernetes jobs
- 🧱 **User Uploads:** Upload and execute your own custom functions dynamically
- 🔐 **Sandboxed Runtime:** Secure execution with **gVisor**
- 📈 **Auto-Scaling:** Kubernetes HPA enables dynamic scaling under load
- 🔄 **Two-Phase Architecture:** Pre-loaded (Phase 1) and User Upload (Phase 2) pipelines

---

## 🏗️ Architecture Overview

```
Phase 1: Pre-loaded Functions
User → Gateway → Scheduler → Worker (100 preloaded functions) → Result

Phase 2: User Uploads
User → Gateway → Function Registry → Image Builder
     → Container Registry → Scheduler → Dynamic K8s Job (gVisor) → Result
```

---

## 📦 Project Structure

```
sopm/
├── services/
│   ├── gateway/              # Main entrypoint and API gateway
│   ├── scheduler/            # Job distribution and orchestration
│   ├── worker/               # Executes preloaded functions
│   ├── function-registry/    # Handles user-uploaded functions
│   └── image-builder/        # Builds Docker images dynamically
│
├── infra/
│   └── k8s/                  # Kubernetes manifests for all services
│
├── scripts/                  # Deployment and testing scripts
│
├── keys/                     # (Local only) Service keys and secrets
└── README.md
```

---

## ⚙️ Quick Start

### Prerequisites

```bash
# Start Minikube
minikube start 

# Verify setup
kubectl version
```

### Phase 1 — Deploy Pre-loaded Functions

```bash
cd scripts
./deploy.sh
```

### Phase 2 — Enable User Uploads

```bash
./setup_gvisor.sh
./deploy_phase2.sh
./apply_phase2_schema.sh
```

### Testing the System

```bash
# Terminal 1: Port forward
kubectl port-forward -n sopm service/gateway-service 8080:80

# Terminal 2: Run tests
./test.sh
./test_user_upload.sh
./benchmark.sh
```

---

## 📡 API Endpoints

### Pre-loaded Functions
| Method | Endpoint | Description |
|--------|-----------|-------------|
| GET | `/api/functions` | List all 100 functions |
| POST | `/api/execute` | Execute a function |
| GET | `/api/status/:id` | Check job status |
| GET | `/api/stats` | View system statistics |

### User Functions
| Method | Endpoint | Description |
|--------|-----------|-------------|
| POST | `/api/user-functions` | Upload new user function |
| GET | `/api/user-functions?user_id=xxx` | List user functions |
| POST | `/api/user-functions/:id/execute` | Execute uploaded function |
| GET | `/api/status/<job-id>` | Check Result |

---

## 📈 Performance Metrics

| Metric | Average |
|--------|----------|
| Cold Start (Pre-loaded) | 0ms |
| Cold Start (User Upload) | 100–200ms |
| Throughput | 1000+ executions/sec (cluster) |

---

## 🤝 Contributors

- **Vipul Kumar** — Project Lead & Developer  

---

## 📜 License

This project is licensed under the **MIT License** — feel free to use and modify it for research or learning purposes.

