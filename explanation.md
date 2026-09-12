# VulnerableMart - Monorepo Microservices Architecture (Commit 1 Baseline)

## Architecture Overview

VulnerableMart is structured as a 4-microservice e-commerce platform written in Python using FastAPI. The application follows an asynchronous microservices pattern where `order-service` acts as the orchestrator / public API gateway, communicating with internal services over HTTP using `httpx`.

```
                    +-----------------------+
                    |    Public Gateway     |
                    |     order-service     |
                    |      (Port 8000)      |
                    +-----------+-----------+
                                |
        +-----------------------+-----------------------+
        |                       |                       |
        v                       v                       v
+---------------+       +---------------+       +------------------+
| inventory-svc |       |  payment-svc  |       | notification-svc |
|  (Port 8001)  |       |  (Port 8002)  |       |   (Port 8003)    |
+---------------+       +---------------+       +------------------+
```

---

## Service Specifications

### 1. `order-service` (Port 8000)
- **Role**: Orchestrator & Public API Gateway.
- **Endpoints**:
  - `GET /healthz`: Returns `{"status": "ok"}` for Kubernetes readiness and liveness checks.
  - `POST /orders`: Accepts an order payload (`item_id`, `amount`, `customer_email`).
- **Workflow**:
  1. Calls `GET http://inventory-service:8001/items/{item_id}` via `httpx.AsyncClient` to check item availability and stock.
  2. Calls `POST http://payment-service:8002/charge` via `httpx.AsyncClient` with `amount` and `currency` to process payment.
  3. Calls `POST http://notification-service:8003/notify` via `httpx.AsyncClient` to send an order confirmation email notification.
  4. Aggregates and returns a consolidated receipt.

### 2. `inventory-service` (Port 8001)
- **Role**: Internal stock manager.
- **Endpoints**:
  - `GET /healthz`: Health check endpoint.
  - `GET /items/{item_id}`: Returns mock stock metadata (`item_id`, `in_stock: True`, `price: 49.99`).

### 3. `payment-service` (Port 8002)
- **Role**: Internal payment processor.
- **Endpoints**:
  - `GET /healthz`: Health check endpoint.
  - `POST /charge`: Accepts charge payload (`amount`, `currency`), returns transaction confirmation (`transaction_id: "tx_mock_123"`, `status: "succeeded"`).

### 4. `notification-service` (Port 8003)
- **Role**: Internal notification dispatcher.
- **Endpoints**:
  - `GET /healthz`: Health check endpoint.
  - `POST /notify`: Accepts notification payload (`email`, `message`), returns delivery status (`delivered: True`).

---

## DevSecOps & Containerization Hardening

All microservices follow production container security standards:
1. **Lightweight Base Image**: Uses `python:3.11-slim` to minimize image footprint and vulnerable attack surfaces.
2. **Non-Root Execution**: Creates a dedicated Linux user (`appuser`, UID `10001`) and group (`appgroup`, GID `10001`). Containers do not run as `root`.
3. **Environment Flags**: Sets `PYTHONUNBUFFERED=1` to stream logs directly to standard output and `PYTHONDONTWRITEBYTECODE=1` to prevent unnecessary disk writes.

---

## Kubernetes Infrastructure (`k8s/`)

Each microservice has a matching Kubernetes manifest containing both a `Deployment` and a `Service`:

1. **Service Types**:
   - `order-service`: Exposed via `type: LoadBalancer` (public access on port 8000).
   - `inventory-service`, `payment-service`, `notification-service`: Internal services exposed via `type: ClusterIP` (ports 8001, 8002, 8003).

2. **Resource Management**:
   - `requests`: `cpu: "50m"`, `memory: "64Mi"`
   - `limits`: `cpu: "200m"`, `memory: "128Mi"`
   - Ensures stable running on single-node VM/cluster environments without OOM kills or CPU starvation.

3. **Probes**:
   - `livenessProbe` & `readinessProbe` configured on `/healthz` for each container (`initialDelaySeconds: 5`, `periodSeconds: 5`).
