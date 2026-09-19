# VulnerableMart - DevSecOps Portfolio Platform

![DevSecOps Pipeline](https://img.shields.io/badge/DevSecOps-Defense--in--Depth-blueviolet?style=for-the-badge&logo=shield)
![Python](https://img.shields.io/badge/Python-3.11--slim-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi)
![Kubernetes](https://img.shields.io/badge/Kubernetes-K3s-326CE5?style=for-the-badge&logo=kubernetes)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker)

**VulnerableMart** is an enterprise-grade DevSecOps portfolio project demonstrating a modern, production-hardened microservices platform backed by an automated **Defense-in-Depth CI/CD Security Pipeline**.

---

## 🏗 Architecture Overview

VulnerableMart is structured as a 4-microservice monorepo platform written in Python (FastAPI). The architecture decouples application responsibilities, enforces non-root execution, and relies on an internal network topology.

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

### Microservices Breakdown

| Service Name | Port | Access Level | Description |
|---|---|---|---|
| **`order-service`** | `8000` | Public (`LoadBalancer`) | API Gateway & Orchestrator. Coordinates requests asynchronously via `httpx`. |
| **`inventory-service`** | `8001` | Internal (`ClusterIP`) | Manages product stock verification and item metadata. |
| **`payment-service`** | `8002` | Internal (`ClusterIP`) | Processes simulated payment charges and transaction receipts. |
| **`notification-service`** | `8003` | Internal (`ClusterIP`) | Dispatches customer email and message confirmations. |

---

## 🛡 DevSecOps Pipeline (4-Stage Defense-in-Depth)

The CI/CD pipeline ([`.github/workflows/devsecops-pipeline.yaml`](.github/workflows/devsecops-pipeline.yaml)) executes automated security gates on every push and pull request to the `main` branch.

```
+-----------------------------------------------------------------------------------+
| STAGE 1: Code & Secret Security                                                   |
|  * TruffleHog (Secret Scanning)                                                   |
|  * SonarQube (SAST Code Quality Analysis)                                         |
|  * Snyk (SCA Dependency Vulnerability Scanning)                                   |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
| STAGE 2: Container Security & Supply Chain                                        |
|  * Matrix Docker Image Builds (4 services)                                        |
|  * Trivy (Container OS & Library Vulnerability Scan)                              |
|  * GCP Artifact Registry Push (us-central1-docker.pkg.dev)                        |
|  * Cosign (Keyless Image Signing with GitHub OIDC)                                |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
| STAGE 3: Policy Validation & K8s Deployment                                       |
|  * Kyverno CLI (Kubernetes Manifest Security Policy Enforcement)                  |
|  * K3s Cluster Deployment (kubectl apply -f k8s/)                                 |
|  * Rollout Verification (kubectl rollout status)                                  |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
| STAGE 4: Dynamic Testing (DAST) & Security Orchestration                          |
|  * OWASP ZAP (API DAST Scan against live OpenAPI endpoints)                       |
|  * DefectDojo (Automated Scan Result Ingestion API)                               |
+-----------------------------------------------------------------------------------+
```

### Security Tooling Stack

1. **Secret Scanning (TruffleHog)**: Scans Git history for high-entropy hardcoded secrets, API tokens, and credentials.
2. **Static Application Security Testing (SonarQube)**: Performs SAST code analysis to detect security flaws (e.g., CWE-89 SQL Injection) and code smells.
3. **Software Composition Analysis (Snyk)**: Scans `requirements.txt` dependencies for known CVEs.
4. **Container Security (Trivy)**: Scans built Docker images for critical OS/package vulnerabilities, breaking builds on `CRITICAL` severity findings.
5. **Supply Chain Security (Cosign)**: Attests and signs pushed container images using GitHub OIDC keyless signing.
6. **Policy Engine (Kyverno)**: Validates Kubernetes manifests against custom security policies ([`.github/policies/`](.github/policies/)) before deployment.
7. **Dynamic Application Security Testing (OWASP ZAP)**: Executes active API DAST scans against live deployed endpoints (`/openapi.json`).
8. **Vulnerability Management (DefectDojo)**: Automatically ingests scanner reports via REST API to centralize security dashboards and defect tracking.

---

## 🚀 Local Development & Setup

### Prerequisites
* [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
* [Python 3.11+](https://www.python.org/)

### 1. Run Microservices & Security Stack Locally
Launch the microservices along with DefectDojo and SonarQube instances using Docker Compose:

```bash
docker-compose up -d --build
```

#### Access Endpoints Locally:
* **Order Service (Gateway)**: `http://localhost:8000/docs`
* **Inventory Service**: `http://localhost:8001/docs`
* **Payment Service**: `http://localhost:8002/docs`
* **Notification Service**: `http://localhost:8003/docs`
* **DefectDojo Dashboard**: `http://localhost:8080`
* **SonarQube Dashboard**: `http://localhost:9000`

---

## ☸️ Kubernetes Deployment

Deployment manifests are located in the [`k8s/`](k8s/) directory:

```bash
# Apply all manifests to the k3s cluster
kubectl apply -f k8s/

# Verify rollout status
kubectl rollout status deployment/order-service --timeout=90s
kubectl rollout status deployment/inventory-service --timeout=90s
kubectl rollout status deployment/payment-service --timeout=90s
kubectl rollout status deployment/notification-service --timeout=90s
```

All deployment manifests enforce:
* `livenessProbe` & `readinessProbe` pointing to `/healthz`
* Conservative CPU limits (`200m`) and Memory limits (`128Mi`)
* Non-root user execution standards

---

## 📊 Summary of Pipeline Security Controls

| Security Control | Tool | Stage | Action / Enforcement |
|---|---|---|---|
| **Secret Detection** | TruffleHog | Stage 1 | Scans commit history; flags leaked credentials |
| **SAST** | SonarQube | Stage 1 | Analyzes Python code for security bugs and vulnerabilities |
| **SCA** | Snyk | Stage 1 | Identifies vulnerable third-party dependencies |
| **Container Scan** | Trivy | Stage 2 | Fails build (`exit-code 1`) on `CRITICAL` OS vulnerabilities |
| **Signing** | Cosign | Stage 2 | Signs container images with keyless GitHub OIDC attestation |
| **Policy Engine** | Kyverno | Stage 3 | Validates K8s manifests against security policies |
| **DAST** | OWASP ZAP | Stage 4 | Performs live API security tests against active endpoints |
| **Vulnerability Aggregation** | DefectDojo | Stage 1-4 | Ingests report artifacts into a unified vulnerability dashboard |
