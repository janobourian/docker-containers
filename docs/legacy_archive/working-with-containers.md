# Module 03: Working with Containers, Lifecycle Management & Process Orchestration

**Track:** Docker Container Systems & Virtualization Architecture
**Category:** Container Operations, Lifecycle States, Process Signals & Troubleshooting
**Standard Identifier:** `DOC-STD-UNIVERSAL-2026`
**Status:** ✅ Completed

---

## 📑 Table of Contents

1. [High-Level Overview & Executive Summary](#1-high-level-overview--executive-summary)
2. [The Container State Machine & Process Lifecycle](#2-the-container-state-machine--process-lifecycle)
3. [The `ENTRYPOINT` vs `CMD` Execution Matrix](#3-the-entrypoint-vs-cmd-execution-matrix)
4. [Process Signals, Graceful Draining & PID 1 Reaping](#4-process-signals-graceful-draining--pid-1-reaping)
5. [Certification & Exam Essentials (Cheat Sheet)](#5-certification--exam-essentials-cheat-sheet)
6. [Comparative Analysis Matrix: Container Execution Modes](#6-comparative-analysis-matrix-container-execution-modes)
7. [Performance & Resource Optimization](#7-performance--resource-optimization)
8. [In-Depth Engineering Perspectives](#8-in-depth-engineering-perspectives)
9. [Well-Architected Framework Alignment](#9-well-architected-framework-alignment)
10. [Step-by-Step Hands-On Production Walkthrough](#10-step-by-step-hands-on-production-walkthrough)
11. [Pure CLI / Command Interface](#11-pure-cli--command-interface)
12. [Advanced Architecture & Edge-Case Failure Modes](#12-advanced-architecture--edge-case-failure-modes)
13. [Detailed Sub-Components & Subsystems](#13-detailed-sub-components--subsystems)
14. [References (The 5+5 Rule)](#14-references-the-55-rule)
15. [Universal FinOps & Resource Cost Governance](#15-universal-finops--resource-cost-governance)

---

## 1. High-Level Overview & Executive Summary

Container operations and lifecycle management encompass the precise mechanics of provisioning, executing, inspecting, updating, pausing, and gracefully terminating containerized processes. A Docker container transitions through a strict, deterministic state machine (`created`, `running`, `paused`, `restarting`, `removing`, `dead`, and `exited`). Mastery of container operations requires understanding OS signal propagation (`SIGTERM` vs `SIGKILL`), PID 1 init process responsibilities (zombie reaping), dynamic resource updates (`docker update`), and interactive debugging without violating container immutability.

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                    CONTAINER LIFECYCLE STATE MACHINE                           │
├────────────────────────────────────────────────────────────────────────────────┤
│                              ┌───────────────┐                                 │
│                              │  IMAGE PULL   │                                 │
│                              └───────┬───────┘                                 │
│                                      │ `docker create`                         │
│                                      ▼                                         │
│                              ┌───────────────┐                                 │
│                   ┌─────────►│    CREATED    │                                 │
│                   │          └───────┬───────┘                                 │
│                   │                  │ `docker start`                          │
│                   │                  ▼                                         │
│  `docker restart` │          ┌───────────────┐   `docker pause`   ┌──────────┐ │
│                   │          │    RUNNING    │ ──────────────────►│  PAUSED  │ │
│                   │          └───────┬───────┘ ◄──────────────────┴──────────┘ │
│                   │                  │           `docker unpause`              │
│                   │                  │ `docker stop` (SIGTERM ──► SIGKILL)     │
│                   │                  ▼                                         │
│                   │          ┌───────────────┐                                 │
│                   └──────────┤    EXITED     │                                 │
│                              └───────┬───────┘                                 │
│                                      │ `docker rm`                             │
│                                      ▼                                         │
│                              ┌───────────────┐                                 │
│                              │   DESTROYED   │                                 │
│                              └───────────────┘                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 👔 Executive Summary (For Managers & Non-Technical Stakeholders)

* **Business Purpose**: Provides operations and Site Reliability Engineering (SRE) teams with complete visibility and operational control to monitor, troubleshoot, adjust resources, and restart mission-critical services with zero downtime.
* **How It Works**: Gives engineers tools to inspect live container logs, dynamically scale CPU/memory without stopping services, attach secure diagnostic shells, and configure automatic self-healing restart policies.
* **Key Business Value & ROI**: Decreases Mean Time to Resolution (MTTR) during outages from hours to minutes, prevents memory leaks from crashing host servers, and ensures uninterrupted 24/7 service availability.

---

## 2. The Container State Machine & Process Lifecycle

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                   CONTAINER RESTART POLICIES BREAKDOWN                         │
├───────────────────┬──────────────────────────────────┬─────────────────────────┤
│ Restart Policy    │ Trigger Condition                │ Recommended Use Case    │
├───────────────────┼──────────────────────────────────┼─────────────────────────┤
│ **`no`** (Default)│ Never restarts container         │ One-off batch / CI jobs │
├───────────────────┼──────────────────────────────────┼─────────────────────────┤
│ **`on-failure[:N]`| Restarts ONLY if exit code != 0  │ Backend API microservice│
├───────────────────┼──────────────────────────────────┼─────────────────────────┤
│ **`always`**      │ Restarts on any exit or reboot   │ Legacy monitoring agent │
├───────────────────┼──────────────────────────────────┼─────────────────────────┤
│ **`unless-stopped`| Always restarts unless admin     │ Production web servers &│
│ (Recommended)     │ explicitly ran `docker stop`     │ database containers     │
└───────────────────┴──────────────────────────────────┴─────────────────────────┘
```

---

## 3. The `ENTRYPOINT` vs `CMD` Execution Matrix

A critical source of configuration errors is confusing `ENTRYPOINT` (the fixed executable) with `CMD` (the default parameters):

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                     ENTRYPOINT VS CMD INTERACTION MATRIX                       │
├───────────────────────────────┬───────────────────────────────┬────────────────┤
│ Dockerfile Definition         │ CLI Override Command          │ Executed Syscall│
├───────────────────────────────┼───────────────────────────────┼────────────────┤
│ `ENTRYPOINT ["nginx"]`        │ *(None)*                      │ `nginx -g daemon off;`│
│ `CMD ["-g", "daemon off;"]`   │                               │                │
├───────────────────────────────┼───────────────────────────────┼────────────────┤
│ `ENTRYPOINT ["nginx"]`        │ `docker run image -v`         │ `nginx -v`     │
│ `CMD ["-g", "daemon off;"]`   │                               │                │
├───────────────────────────────┼───────────────────────────────┼────────────────┤
│ `CMD ["python", "app.py"]`    │ `docker run image bash`       │ `bash` (Full   │
│ (No ENTRYPOINT)               │                               │ override!)     │
├───────────────────────────────┼───────────────────────────────┼────────────────┤
│ `ENTRYPOINT ["python"]`       │ `docker run image script.py`  │ `python script.py`│
└───────────────────────────────┴───────────────────────────────┴────────────────┘
```

### Preferred JSON Exec Form vs Shell Form:

- **Exec Form (Mandatory for Production)**: `ENTRYPOINT ["executable", "param1"]` executes the binary directly as **PID 1**, allowing OS signals to reach your application!
- **Shell Form (Anti-Pattern)**: `ENTRYPOINT executable param1` executes `/bin/sh -c executable`. The shell becomes PID 1 and **swallows `SIGTERM` signals**, preventing graceful shutdown.

---

## 4. Process Signals, Graceful Draining & PID 1 Reaping

### 4.1 Signal Propagation & Graceful Shutdown

When `docker stop -t 15 my-container` executes:

1. Docker sends **`SIGTERM` (Signal 15)** to PID 1 inside the container.
2. The application intercepts `SIGTERM`, ceases accepting new HTTP connections, finishes in-flight requests, and flushes database connection pools.
3. If PID 1 terminates within 15 seconds, the container transitions to `exited` cleanly (Exit code: `0`).
4. If the timer expires before PID 1 exits, Docker issues **`SIGKILL` (Signal 9)**, immediately terminating the kernel process (Exit code: `137`).

### 4.2 The Zombie Process Problem & Tini (`--init`)

In Linux, when a child process terminates, it remains in the process table as a **Zombie process (`<defunct>`)** until its parent reads its exit code via `waitpid()`. If the parent process dies, the child is orphaned and adopted by **PID 1**.

- If your container application is not designed as an init system, it will not reap orphaned zombies, eventually exhausting the host's PID table!
- **Solution**: Pass the **`--init`** flag (`docker run --init ...`), which injects a tiny, high-performance init daemon (**Tini**) as PID 1 to reap zombie processes automatically.

---

## 5. Certification & Exam Essentials (Cheat Sheet)

* ⚠️ **Container Exit Codes Breakdown**:
  - `0`: Success / Normal completion.
  - `1`: Application-level error or exception.
  - `137` ($128 + 9$): Terminated by `SIGKILL` (Out-Of-Memory killer or `docker kill`).
  - `139` ($128 + 11$): Segmentation fault (`SIGSEGV`).
  - `143` ($128 + 15$): Terminated by `SIGTERM` (Normal `docker stop`).
* 🔒 **Dynamic Resource Throttling (`docker update`)**: You do **not** need to stop a running container to adjust its memory or CPU limits. Execute `docker update --cpus 2.0 --memory 1024m container_name` to update kernel cgroups live in memory!
* ⚙️ **`docker exec` vs `docker attach`**:
  - `docker exec`: Spawns a **new, independent process** inside the container's existing namespaces.
  - `docker attach`: Connects directly to the standard I/O streams of **PID 1** (terminating `docker attach` with `Ctrl+C` will kill PID 1 and crash the container!).
* ⚠️ **File Extraction with `docker cp`**: You can copy files into or out of stopped or running containers without opening network ports using `docker cp container_name:/path/on/container /path/on/host`.

---

## 6. Comparative Analysis Matrix: Container Execution Modes

| Operational Mode | Command Syntax | Detached? | Interactive Terminal? | Best Suited For |
| :--- | :--- | :--- | :--- | :--- |
| **Foreground Interactive**| `docker run -it alpine sh` | No | **Yes (`-i -t`)** | Rapid debugging & shell testing |
| **Detached Daemon** | `docker run -d nginx` | **Yes (`-d`)** | No | 24/7 Production background services|
| **One-Off Batch Run** | `docker run --rm python ...`| No | No | Nightly ETL & database migrations |
| **Interactive Exec** | `docker exec -it web sh` | No | **Yes (`-it`)** | Live production troubleshooting |

---

## 7. Performance & Resource Optimization

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                     CONTAINER OPERATIONS TUNING PLAYBOOK                       │
├────────────────────────────────────────────────────────────────────────────────┤
│ 1. Always use JSON exec form `ENTRYPOINT ["..."]` to ensure signal propagation.│
│ 2. Use `--init` for Node.js, Python, and Ruby containers to reap zombie PIDs.  │
│ 3. Adjust live container limits dynamically using `docker update`.             │
│ 4. Configure `HEALTHCHECK` with `--start-period=30s` to allow slow JVM warmups.│
│ 5. Use `docker logs --tail=100 --since=10m` to prevent buffer memory spikes.   │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. In-Depth Engineering Perspectives

### Security Perspective

* **Read-Only Root Filesystem**: Deploying containers with `--read-only` prevents malware from writing executable binaries to disk (`/bin`, `/usr`), even if an attacker achieves remote code execution (RCE). Pair with ephemeral `--tmpfs /tmp` for scratch data.

### High Availability Perspective

* **Rolling Restarts with Grace Periods**: When updating production containers, set `--stop-timeout 30` to give websocket connections and database transactions 30 seconds to complete gracefully before issuing `SIGKILL`.

### Resilience & Fault Tolerance Perspective

* **Process Signal Trapping**: Node.js and Python applications do not handle `SIGTERM` by default. Always register explicit signal listeners in your code (`process.on('SIGTERM', () => server.close())`) to prevent abrupt TCP connection resets.

### Cost & Efficiency Perspective

* **Ephemeral `--rm` Flag in CI/CD**: Running CI test runners with `docker run --rm` ensures containers and their writable OverlayFS layers are automatically deleted upon exit, preventing build server disk fill-ups.

---

## 9. Step-by-Step Hands-On Production Walkthrough

### Step 1: Launch Multi-Stage Node.js Server with Init Daemon

Launch a production Node.js container with Tini init daemon, health checking, and strict cgroups limits:

```bash
docker run \
    --detach \
    --name enterprise-payment-api \
    --init \
    --publish 3000:3000 \
    --memory 512m \
    --memory-reservation 256m \
    --cpus 1.0 \
    --pids-limit 150 \
    --restart unless-stopped \
    --stop-timeout 20 \
    --env "NODE_ENV=production" \
    --health-cmd "wget --quiet --tries=1 --spider http://localhost:3000/health || exit 1" \
    --health-interval 10s \
    --health-timeout 3s \
    --health-retries 3 \
    --health-start-period 15s \
    node:20-alpine \
    node -e "
      const http = require('http');
      const server = http.createServer((req, res) => {
        if (req.url === '/health') { res.writeHead(200); res.end('OK'); return; }
        res.writeHead(200); res.end('Payment API Active');
      });
      server.listen(3000);
      process.on('SIGTERM', () => {
        console.log('Received SIGTERM. Draining connections...');
        server.close(() => process.exit(0));
      });
    "
```

---

### Step 2: Dynamically Update Resource Limits on Live Container

Increase memory and CPU limits on the active container without restarting it:

```bash
docker update \
    --cpus 2.0 \
    --memory 1024m \
    --memory-swap 1024m \
    enterprise-payment-api
```

---

### Step 3: Inspect Container Health, Top Processes & Live Telemetry

```bash
# 1. Inspect Process Tree inside Container (Verify Tini PID 1 Reaping!)
docker top enterprise-payment-api

# 2. Query Detailed Healthcheck Log Output
docker inspect --format '{{json .State.Health}}' enterprise-payment-api

# 3. View Tail of Logs with Timestamp Telemetry
docker logs --tail 20 --timestamps enterprise-payment-api
```

---

## 10. Pure CLI / Command Interface

### 1. Identify Running Containers Consuming Most Memory

Sort running containers by RAM usage in real time:

```bash
docker stats \
    --no-stream \
    --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.CPUPerc}}\t{{.PIDs}}"
```

### 2. Inspect File Modifications in Container Layer

Display files created (`A`), changed (`C`), or deleted (`D`) in the writable layer:

```bash
docker diff enterprise-payment-api
```

### 3. Gracefully Stop All Running Containers with Custom Timeout

Signal all active containers to drain connections before stopping:

```bash
docker stop --time 15 $(docker ps -q)
```

---

## 11. Advanced Architecture & Edge-Case Failure Modes

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                    OPERATIONS FAILURE RECOVERY MATRIX                          │
├──────────────────────┬────────────────────────┬────────────────────────────────┤
│ Failure Scenario     │ Underlying Root Cause  │ Production Mitigation Runbook  │
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **`SIGTERM` Ignored**│ Shell form in Dockerfile│ Refactor to JSON exec form:    │
│ **(10s Stop Hang)**  │ (`sh -c`) swallows sig.│ `ENTRYPOINT ["node", "app.js"]`│
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **PID Exhaustion**   │ Zombie processes not   │ Add `--init` flag to inject    │
│ **Crash**            │ reaped by application. │ Tini reaper daemon as PID 1.   │
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **Container OOM (137)**│ App exceeds `--memory`│ Run `docker update --memory`   │
│                      │ hard limit allocation. │ or increase memory limit.      │
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **Healthcheck Flap** │ Startup delay exceeds  │ Configure `--health-start-     │
│                      │ retries on cold boot.  │ period=30s` for application.   │
└──────────────────────┴────────────────────────┴────────────────────────────────┘
```

---

## 12. Detailed Sub-Components & Subsystems

### 1. Tini Process Supervisor (`--init`)

* **Key Concepts**: Ultra-lightweight init system that adopts orphaned child processes, reaps zombies, and transparently forwards signals to child application processes.
* **CLI / Tool Snippet**:

```bash
docker run --init --rm alpine ps
```

### 2. Container Healthcheck Subsystem

* **Key Concepts**: Engine timer invoking health probe commands inside container namespaces, updating container state to `healthy` or `unhealthy`.
* **CLI / Tool Snippet**:

```bash
docker inspect --format '{{.State.Health.Status}}' enterprise-payment-api
```

### 3. Log Driver Rotator (`json-file`)

* **Key Concepts**: Streams stdout/stderr from `containerd-shim` FIFO pipes, writing JSON structures to `/var/lib/docker/containers/<id>/<id>-json.log` with file rotation.
* **CLI / Tool Snippet**:

```bash
docker inspect --format '{{.HostConfig.LogConfig.Type}}' enterprise-payment-api
```

### 4. Dynamic Cgroup Controller (`docker update`)

* **Key Concepts**: Interacts with the host `/sys/fs/cgroup/` filesystem to update `memory.max` and `cpu.max` files dynamically for active scopes.
* **CLI / Tool Snippet**:

```bash
docker update --help
```

---

## 13. References (The 5+5 Rule)

### Official Documentation & Technical Specifications

1. [Docker Official Documentation: Container Lifecycle and CLI Reference](https://docs.docker.com/reference/cli/docker/container/)
2. [Docker Official Documentation: Dockerfile ENTRYPOINT vs CMD](https://docs.docker.com/reference/dockerfile/#entrypoint)
3. [Open Container Initiative (OCI): Runtime Lifecycle Specification](https://opencontainers.org/specs/runtime/)
4. [Krallin Tini Official Architecture & Zombie Reaping Specification](https://github.com/krallin/tini)
5. [Linux Kernel Organization: Signal Handling and Process State Transitions](https://man7.org/linux/man-pages/man7/signal.7.html)

### Authoritative Engineering Blogs & Architecture Deep Dives

6. [Brendan Gregg: Linux Process Lifecycle, Signals, and Container Metrics](https://www.brendangregg.com/)
7. [Julia Evans: How Does Docker Stop a Container? Signals and Timeouts](https://jvns.ca/)
8. [Martin Fowler: Designing Containerized Applications for Graceful Shutdown](https://martinfowler.com/)
9. [Liz Rice: Understanding Container Process Trees and Init Systems](https://www.lizrice.com/)
10. [High-Performance Linux Systems: Tuning Container Healthchecks and Signal Traps](https://www.kernel.org/)

---

## 14. Universal FinOps & Resource Cost Governance

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                     OPERATIONS FINOPS SAVINGS MATRIX                           │
├──────────────────────────┬──────────────────────────┬──────────────────────────┤
│ Optimization Strategy    │ Technical Mechanism      │ Measurable FinOps ROI    │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **`docker update` Live** │ Resizes container RAM/CPU│ Eliminates service reboot│
│                          │ without restart downtime │ maintenance downtime     │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **`--stop-timeout`**     │ Drains TCP connections   │ Eliminates in-flight API │
│                          │ before container stop    │ retry storm server load  │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **`--init` Zombie Reaping**| Prevents PID table lock│ Eliminates emergency     │
│                          │ and node kernel crashes  │ host reboot outages      │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **`--rm` Ephemeral Clean**| Deletes test containers │ Saves 500GB+ build server│
│                          │ upon job completion      │ disk space monthly       │
└──────────────────────────┴──────────────────────────┴──────────────────────────┘
```

### 1. Dynamic `docker update` Maintenance FinOps ROI

In high-traffic e-commerce clusters during seasonal traffic surges (e.g. Cyber Monday):

- Adjusting memory from 512MB to 2GB on 100 backend containers without `docker update` requires executing 100 container restarts.
- Restarting services drops active websocket connections and triggers 50,000 application reconnect storms, requiring provisioned excess compute headroom ($~\$1,800/\text{month}$).
- Executing `docker update --memory 2048m $(docker ps -q)` resizes kernel cgroups in **under 200 milliseconds** with **zero dropped connections**.
- **FinOps ROI**: Eliminates the need to over-provision redundant standby instances for maintenance windows, saving **\$21,600/year**.

### 2. Graceful Shutdown (`--stop-timeout`) Network & Gateway Cost Elimination

When a payment processing microservice is killed abruptly with `SIGKILL`:

- In-flight database transactions are terminated mid-execution, causing failed payments and customer checkout retries.
- Retries double the API Gateway request load and trigger customer support ticket overhead ($~\$12 per support ticket).
- Configuring `--stop-timeout 20` and handling `SIGTERM` in code allows in-flight payments to settle gracefully in 1.2 seconds before shutdown.
- **FinOps ROI**: Prevents thousands of failed transaction support inquiries and payment processing dispute fees.
