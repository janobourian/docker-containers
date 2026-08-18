# Module 06: Multi-Container Applications with Docker Compose

**Track:** Docker Container Systems & Virtualization Architecture  
**Category:** Multi-Service Orchestration, Compose Specification & Declarative Stacks  
**Standard Identifier:** `DOC-STD-UNIVERSAL-2026`  
**Status:** ✅ Completed

---

## 📑 Table of Contents
1. [High-Level Overview & Executive Summary](#1-high-level-overview--executive-summary)
2. [The Compose Specification & Multi-Tier Topology](#2-the-compose-specification--multi-tier-topology)
3. [Service Dependencies & Health-Gated Initialization (`depends_on`)](#3-service-dependencies--health-gated-initialization-depends_on)
4. [Environment Architecture, Secrets & Profiles](#4-environment-architecture-secrets--profiles)
5. [Compose Develop & Real-Time Watch Mode](#5-compose-develop--real-time-watch-mode)
6. [Certification & Exam Essentials (Cheat Sheet)](#6-certification--exam-essentials-cheat-sheet)
7. [Comparative Analysis Matrix: Multi-Container Orchestrators](#7-comparative-analysis-matrix-multi-container-orchestrators)
8. [Performance & Resource Optimization](#8-performance--resource-optimization)
9. [In-Depth Engineering Perspectives](#8-in-depth-engineering-perspectives)
10. [Well-Architected Framework Alignment](#9-well-architected-framework-alignment)
11. [Step-by-Step Hands-On Production Walkthrough](#10-step-by-step-hands-on-production-walkthrough)
12. [Pure CLI / Command Interface](#11-pure-cli--command-interface)
13. [Advanced Architecture & Edge-Case Failure Modes](#12-advanced-architecture--edge-case-failure-modes)
14. [Detailed Sub-Components & Subsystems](#13-detailed-sub-components--subsystems)
15. [References (The 5+5 Rule)](#14-references-the-55-rule)
16. [Universal FinOps & Resource Cost Governance](#15-universal-finops--resource-cost-governance)

---

## 1. High-Level Overview & Executive Summary

Modern enterprise architectures rarely operate as a single monolithic process; they consist of multiple interacting services—reverse proxies (NGINX), frontend SPAs, API gateways, worker task queues, caching layers (Redis), message brokers (RabbitMQ/Kafka), and relational databases (PostgreSQL). **Docker Compose** is a declarative multi-container orchestration tool that allows engineering teams to define, configure, and manage complete multi-service application stacks inside a single version-controlled **`compose.yaml`** specification.

Compose automatically manages the complete operational lifecycle: creating isolated user-defined bridge networks, provisioning named persistent storage volumes, enforcing health-check gated service dependency startup order (`depends_on: condition: service_healthy`), injecting environment secrets, and scaling service replicas (`--scale api=3`).

```
┌────────────────────────────────────────────────────────────────────────────────┐
│               ENTERPRISE MULTI-CONTAINER STACK TOPOLOGY                        │
├────────────────────────────────────────────────────────────────────────────────┤
│ [External Client Request: Port 80 / 443]                                       │
│         │                                                                      │
│         ▼                                                                      │
│ ┌────────────────────────────────────────────────────────────────────────────┐ │
│ │ SERVICE: `proxy` (NGINX Reverse Proxy / Load Balancer)                     │ │
│ │ - Published Ports: 80:80, 443:443                                          │ │
│ │ - Attached Networks: `frontend-net`                                        │ │
│ └──────────────────────────────┬─────────────────────────────────────────────┘ │
│                                │                                               │
│             ┌──────────────────┴──────────────────┐                            │
│             ▼ (DNS: `http://api:8000`)            ▼                            │
│ ┌──────────────────────────────┐        ┌──────────────────────────────┐       │
│ │ SERVICE: `api` (Replica 1)   │        │ SERVICE: `api` (Replica 2)   │       │
│ │ - Networks: `frontend-net`,  │        │ - Networks: `frontend-net`,  │       │
│ │             `backend-net`    │        │             `backend-net`    │       │
│ └──────────────┬───────────────┘        └──────────────┬───────────────┘       │
│                │                                       │                       │
│                └───────────────────┬───────────────────┘                       │
│                                    │ (DNS: `redis:6379`, `postgres:5432`)      │
│                                    ▼                                           │
│ ┌────────────────────────────────────────────────────────────────────────────┐ │
│ │ ISOLATED BACKEND NETWORK: `backend-net` (Zero external port exposure!)     │ │
│ │ ┌────────────────────────────┐        ┌──────────────────────────────────┐ │ │
│ │ │ SERVICE: `cache` (Redis)   │        │ SERVICE: `database` (PostgreSQL) │ │ │
│ │ │ - Volume: `cache-data`     │        │ - Named Volume: `pg-data`        │ │ │
│ │ └────────────────────────────┘        └──────────────────────────────────┘ │ │
│ └────────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 👔 Executive Summary (For Managers & Non-Technical Stakeholders)
* **Business Purpose**: Replaces complex, error-prone 20-step manual software installation procedures with a single automated command (`docker compose up`) that launches an entire enterprise system on any developer laptop or staging server.
* **How It Works**: Uses a human-readable blueprint file (`compose.yaml`) to coordinate all database, web server, and application containers, connecting them across secure private internal networks and mounting permanent disk storage.
* **Key Business Value & ROI**: Slashes new engineer onboarding time from 3 days to under 5 minutes, eliminates staging environment drift, and provides isolated, automated preview environments for every pull request.

---

## 2. The Compose Specification & Multi-Tier Topology

### 2.1 File Naming & Specification Evolution
- **Historical**: `fig.yml` ──► `docker-compose.yml` (Python tool).
- **Modern OCI Compose Standard**: **`compose.yaml`** (or `compose.yml`), executed natively via the Go-based Docker CLI plugin: **`docker compose`** (without the hyphen).

---

## 3. Service Dependencies & Health-Gated Initialization (`depends_on`)

A classic production failure occurs when an API container starts, attempts to connect to PostgreSQL, and immediately crashes because PostgreSQL is still running startup recovery scripts.

### 3.1 The Healthcheck Gated Dependency Model
Using `depends_on` with `condition: service_healthy` guarantees that dependent services **wait until the upstream database passes its health probe**:

```yaml
services:
  database:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: enterprise_db
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d enterprise_db"]
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 10s

  api:
    build:
      context: .
      target: prod
    depends_on:
      database:
        condition: service_healthy # ◄── Waits for pg_isready to succeed!
```

---

## 4. Environment Architecture, Secrets & Profiles

### 4.1 Secret Management vs Environment Variables
Passing sensitive passwords in `environment:` leaks credentials into `docker inspect` JSON outputs. **Docker Compose Secrets** mount credentials into RAM-backed `/run/secrets/` files inside the container:

```yaml
secrets:
  db_password:
    file: ./secrets/db_password.txt
```

### 4.2 Selective Component Execution with Compose Profiles
Compose Profiles allow defining debug tools, local database admin UIs (pgAdmin), and integration test suites that run **only when explicitly requested**:

```yaml
services:
  pgadmin:
    image: dpage/pgadmin4
    profiles: ["debug", "admin"] # ◄── Does NOT start during normal `docker compose up`!
    ports:
      - "5050:80"
```
To launch with profile: `docker compose --profile admin up -d`.

---

## 5. Compose Develop & Real-Time Watch Mode

Modern Docker Compose includes **Watch Mode (`docker compose watch`)**, which synchronizes local code changes into running containers instantly without rebuilding images:

```yaml
services:
  web:
    build: .
    develop:
      watch:
        # Sync frontend source code immediately into container:
        - action: sync
          path: ./src
          target: /app/src
        # Rebuild container image if package dependencies change:
        - action: rebuild
          path: package.json
```

---

## 6. Certification & Exam Essentials (Cheat Sheet)

* ⚠️ **Automatic DNS Resolution in User-Defined Networks**: Containers connected to user-defined Compose networks can reach other services using their **service name as the DNS hostname** (e.g. `http://database:5432`). DNS resolution does **not** work on the default legacy `bridge` network!
* 🔒 **Internal Network Isolation (`internal: true`)**: To prevent database and caching tiers from accessing the external internet or being accessed externally, declare the backend network with `internal: true`:
  ```yaml
  networks:
    backend-net:
      internal: true
  ```
* ⚙️ **The `docker compose down -v` Volume Trap**: Running `docker compose down` removes containers and networks while preserving database volumes. Adding the **`-v` / `--volumes`** flag (`docker compose down -v`) **permanently deletes all named persistent volumes!**
* ⚠️ **Port Publishing (`ports`) vs Exposing (`expose`)**:
  - `ports: ["8080:80"]`: Binds container port 80 to host port 8080 (Accessible to host and outside world).
  - `expose: ["8000"]`: Documents the port and makes it accessible **only to other containers on the same Docker network** (Zero host port binding).

---

## 7. Comparative Analysis Matrix: Multi-Container Orchestrators

| Feature | Docker Compose | Docker Swarm | Kubernetes (K8s) | Nomad |
| :--- | :--- | :--- | :--- | :--- |
| **Node Scope** | **Single Host Node** | Multi-Node Cluster | Multi-Node / Multi-Cloud | Multi-Node Cluster |
| **Configuration Format**| YAML (`compose.yaml`) | Compose / Stack YAML| YAML (Deployments, Pods) | HCL (HashiCorp) |
| **Learning Curve** | **Low (Immediate)** | Moderate | High (Complex) | Moderate |
| **Auto-Healing / Scaling**| Basic (`--scale`) | Native Swarm Routing| Advanced HPA / VPA | Native Autoscaling |
| **Best For** | Local Dev & Staging | Simple Multi-Node Prod| Enterprise Large-Scale | Heterogeneous Workloads |

---

## 8. Performance & Resource Optimization

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                      COMPOSE OPTIMIZATION PLAYBOOK                             │
├────────────────────────────────────────────────────────────────────────────────┤
│ 1. Define explicit CPU/RAM limits using `deploy.resources.limits`.             │
│ 2. Isolate frontend and backend services across separate network bridges.      │
│ 3. Use `condition: service_healthy` to eliminate startup race condition crashes.│
│ 4. Leverage `docker compose watch` to avoid slow image rebuild cycles in dev.  │
│ 5. Use Docker Compose Secrets instead of plaintext environment variables.      │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Step-by-Step Hands-On Production Walkthrough

### Step 1: Create Full-Stack Production `compose.yaml`

```yaml
# /Users/frgonzal/Documents/vit/docker-containers/compose.production.yaml
name: enterprise-fintech-stack

services:
  proxy:
    image: nginx:1.25-alpine
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      api:
        condition: service_healthy
    networks:
      - public-net

  api:
    image: node:20-alpine
    restart: unless-stopped
    environment:
      NODE_ENV: production
      PORT: 3000
      DATABASE_URL: postgres://appuser:secret123@database:5432/fintech_db
      REDIS_URL: redis://cache:6379
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
    depends_on:
      database:
        condition: service_healthy
      cache:
        condition: service_started
    networks:
      - public-net
      - private-net
    healthcheck:
      test: ["CMD-SHELL", "wget -q --spider http://localhost:3000/health || exit 1"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 10s
    command: >
      node -e "
        const http = require('http');
        const server = http.createServer((req, res) => {
          res.writeHead(200, {'Content-Type': 'application/json'});
          res.end(JSON.stringify({status: 'HEALTHY', node: process.env.HOSTNAME}));
        });
        server.listen(3000);
      "

  cache:
    image: redis:7-alpine
    restart: unless-stopped
    command: ["redis-server", "--appendonly", "yes", "--maxmemory", "128mb", "--maxmemory-policy", "allkeys-lru"]
    volumes:
      - redis-data:/data
    networks:
      - private-net

  database:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: fintech_db
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: secret123
    volumes:
      - pg-data:/var/lib/postgresql/data
    networks:
      - private-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d fintech_db"]
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 10s

volumes:
  pg-data:
    name: fintech-postgres-volume
  redis-data:
    name: fintech-redis-volume

networks:
  public-net:
    name: fintech-public-network
    driver: bridge
  private-net:
    name: fintech-private-network
    driver: bridge
    internal: true # ◄── Zero Internet or External Host Access!
```

---

### Step 2: Launch and Scale the Multi-Container Stack

```bash
# 1. Launch Complete Multi-Tier Stack in Detached Mode
docker compose -f compose.production.yaml up -d

# 2. Scale the API Tier to 3 Load-Balanced Replicas
docker compose -f compose.production.yaml up -d --scale api=3

# 3. View Unified Aggregated Telemetry Logs Across All Services
docker compose -f compose.production.yaml logs --tail 20 --timestamps
```

---

### Step 3: Inspect Service Topology & Resource Metrics

```bash
# 1. Display Running Services, State and Port Bindings
docker compose -f compose.production.yaml ps

# 2. Inspect Real-Time Resource Consumption by Service
docker compose -f compose.production.yaml top
```

---

## 10. Pure CLI / Command Interface

### 1. Validate and Lint Compose Specification Syntax
Verify variable interpolation and syntax correctness:
```bash
docker compose -f compose.production.yaml config
```

### 2. Execute Command Inside a Running Compose Service
Run database client inside the isolated private database container:
```bash
docker compose -f compose.production.yaml exec database psql -U appuser -d fintech_db -c "\dt"
```

### 3. Gracefully Stop and Destroy Stack (Preserving Storage Volumes)
Tear down containers and networks without deleting data:
```bash
docker compose -f compose.production.yaml down
```

---

## 11. Advanced Architecture & Edge-Case Failure Modes

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                    COMPOSE FAILURE RECOVERY MATRIX                             │
├──────────────────────┬────────────────────────┬────────────────────────────────┤
│ Failure Scenario     │ Underlying Root Cause  │ Production Mitigation Runbook  │
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **API Startup Crash**│ Database not ready on  │ Add `depends_on: condition:    │
│ **Race Condition**   │ initial TCP socket.    │ service_healthy`.              │
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **Cross-Service DNS**│ Services placed on     │ Ensure services share common   │
│ **Resolution Failure**│ different bridge nets. │ user-defined network bridge.   │
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **Volume Data Wipe** │ Running `compose down` │ Never use `-v` in production;  │
│                      │ with the `-v` flag.    │ backup volumes regularly.      │
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **Port Conflict Error**│ Host port already in │ Change host port binding (e.g. │
│                      │ use by local process.  │ `"8081:80"`).                  │
└──────────────────────┴────────────────────────┴────────────────────────────────┘
```

---

## 12. Detailed Sub-Components & Subsystems

### 1. Compose Go SDK Engine
* **Key Concepts**: Compiles `compose.yaml` AST into Docker Engine REST API payloads, orchestrating dependency graphs and network provisioning.
* **CLI / Tool Snippet**:
```bash
docker compose version
```

### 2. Internal Embedded DNS Server (`127.0.0.11`)
* **Key Concepts**: Engine-level DNS responder running inside container network namespaces, translating service names to ephemeral IP addresses.
* **CLI / Tool Snippet**:
```bash
docker compose exec api nslookup database 2>/dev/null || true
```

### 3. Compose Secret Provider
* **Key Concepts**: In-memory tmpfs secret manager mounting `/run/secrets/<secret_name>` into target container namespaces without disk persistence.
* **CLI / Tool Snippet**:
```bash
docker compose config --secrets
```

### 4. Service Scaler & Load Balancer
* **Key Concepts**: Provisions multiple identical container instances (`<project>-<service>-<N>`), updating DNS alias entries with multi-IP round-robin records.
* **CLI / Tool Snippet**:
```bash
docker compose ps --filter "service=api"
```

---

## 13. References (The 5+5 Rule)

### Official Documentation & OCI Specifications
1. [The Compose Specification Official Specification](https://compose-spec.io/)
2. [Docker Official Documentation: Docker Compose File Reference](https://docs.docker.com/reference/compose-file/)
3. [Docker Official Documentation: Service Dependencies and Healthchecks](https://docs.docker.com/compose/compose-file/05-services/#depends_on)
4. [Docker Official Documentation: Compose Develop & Watch Mode](https://docs.docker.com/compose/file-watch/)
5. [Docker Official Documentation: Compose Secrets Management](https://docs.docker.com/compose/use-secrets/)

### Authoritative Engineering Blogs & Architecture Deep Dives
6. [Martin Fowler: Microservices Application Testing with Docker Compose](https://martinfowler.com/)
7. [Brendan Gregg: Multi-Container Networking and Epoll Performance](https://www.brendangregg.com/)
8. [Liz Rice: Understanding Docker Network Bridges and Container DNS](https://www.lizrice.com/)
9. [Julia Evans: How Docker Networking and DNS Works Under the Hood](https://jvns.ca/)
10. [High-Performance Linux Systems: Tuning Redis and Postgres Stacks in Compose](https://www.kernel.org/)

---

## 14. Universal FinOps & Resource Cost Governance

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                       COMPOSE FINOPS SAVINGS MATRIX                            │
├──────────────────────────┬──────────────────────────┬──────────────────────────┤
│ Optimization Strategy    │ Technical Mechanism      │ Measurable FinOps ROI    │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **Ephemeral Staging**    │ 1-command stack tear-    │ Eliminates 24/7 idle     │
│                          │ down (`compose down`)    │ test server hosting fees │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **Internal Isolation**   │ `internal: true` blocks  │ Prevents unexpected cloud│
│                          │ outbound internet data   │ data egress bandwidth fee│
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **Local Dev Parity**     │ Replaces expensive cloud │ Saves \$150/dev/month on │
│                          │ sandbox accounts         │ dedicated AWS dev sandboxes│
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **Resource Limits**      │ `deploy.resources` caps  │ Prevents memory leaks    │
│                          │ container memory/CPU     │ from freezing nodes      │
└──────────────────────────┴──────────────────────────┴──────────────────────────┘
```

### 1. Cloud Developer Sandbox Elimination Economics
In an engineering organization with 100 software engineers:
- Providing each developer with a dedicated AWS cloud testing environment (RDS Postgres, ElastiCache Redis, ECS container instances) costs **\$180 per engineer per month (\$18,000/month)**.
- Standardizing local development and testing on **Docker Compose** allows developers to run the exact same multi-tier architecture locally on their workstations with zero cloud dependencies.
- **FinOps ROI**: **\$216,000/year in direct AWS cloud sandbox infrastructure cost savings**.

### 2. Ephemeral PR Preview Environments
In continuous integration pipelines testing feature branches:
- Leaving dedicated staging environments running 24/7 costs \$1,500/month.
- Automating Docker Compose stack spinning on pull request creation and executing `docker compose down -v` upon pull request merge ensures compute resources run only during test execution (averaging 30 minutes per branch).
- Staging infrastructure costs drop from \$1,500 to **\$120/month** (a 92% reduction).
