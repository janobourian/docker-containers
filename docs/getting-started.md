# Module: Getting Started with Docker & Containerization
**Category:** Container Runtime & Fundamentals
**Status:** ✅ Completed

---

## 1. High-Level Overview
Docker is an open-source containerization platform that packages applications and their entire runtime environment—including libraries, system binaries, configuration files, and dependencies—into standardized lightweight executable units called **containers**. Unlike traditional virtual machines that virtualize physical hardware via a hypervisor and execute complete guest operating systems, Docker containers share the host Linux kernel while utilizing kernel namespaces and control groups (cgroups) to guarantee process isolation, deterministic resource allocation, and zero environment drift across development, staging, and production environments.

### 👔 Executive Summary (For Managers & Non-Technical Stakeholders)
* **Business Purpose**: Solves the classic "it works on my machine" problem by packaging software and its dependencies into a single digital shipping container that runs identically everywhere.
* **How It Works**: Packages application code and required system tools into a portable, lightweight container that shares the host server's operating system engine, launching in milliseconds rather than minutes.
* **Key Business Value & Use Cases**: Cuts server infrastructure costs through higher workload density, speeds up software release cycles from months to minutes, and ensures 100% reliable software deployments across on-premises servers and any cloud provider.

---

## 📌 Core Fundamentals & Perspectives (Original Notes)

* **Get and work with Docker**:
  * Docker Desktop
  * Multipass
  * Server installs on Linux

### The Ops perspective
* Images are objects that contain everything an app needs to run.
* You can start a new Bash process inside the container.

### The Dev perspective
* Containers are all about applications.
* Example Application Dockerfile:

```dockerfile
FROM alpine
LABEL maintainer="your-email@example.com"
RUN apk add --update nodejs npm curl
COPY . /src
WORKDIR /src
RUN npm install
EXPOSE 8080
ENTRYPOINT ["node", "./app.js"]
```

### Essential Quick Reference Commands
* `docker --version` - Show client version
* `docker version` - Show detailed client and server version
* `docker info` - Display system-wide Docker configuration
* `docker --help` - CLI command help
* `docker images` - List local images
* `docker pull nginx:latest` - Download image
* `docker run --name test -d -p 8080:80 nginx:latest` - Run container
* `docker ps` - List running containers
* `docker ps -a` - List all containers
* `docker exec -it test bash` - Open interactive bash shell
* `docker stop test` - Stop container
* `docker rm test` - Remove container
* `docker build -t test:latest .` - Build image from Dockerfile
* `docker run -d --name web1 --publish 8080:8080 test:latest` - Run custom build
* `docker rm web1 -f` - Force remove container
* `docker rmi test:latest` - Remove image

### Common Flags Reference
* `--name` - The Docker container name
* `-d / --detach` - Run container in background and print container ID
* `-p / --publish` - Publish a container's port(s) to the host
* `-a / --all` - Show all containers (default shows just running)

---

## 2. Core Architecture & Container Mechanics
Docker operates on a client-server architecture:
- **Docker CLI (`docker`)**: The user-facing command-line interface that communicates with the daemon via REST API over UNIX domain sockets (`/var/run/docker.sock`) or TLS network sockets.
- **Docker Daemon (`dockerd`)**: The background service managing images, containers, networks, and storage volumes.
- **Containerd & runc**: The low-level CNCF-certified container runtime and OCI-compliant runtime that interfaces directly with Linux kernel namespaces (PID, NET, MNT, IPC, UTS, USER) and cgroups v2.
- **Docker Registry**: The central distribution service (Docker Hub, AWS ECR, GitHub Container Registry) for storing and pulling container images.

---

## 3. Common Production Use Cases
* **Microservices Application Hosting**: Running independent, loosely coupled services with isolated networking and lifecycle management.
* **Continuous Integration & Continuous Delivery (CI/CD)**: Ephemeral build runners and testing environments that spin up in seconds and destroy cleanly after test execution.
* **Legacy Application Modernization**: Encapsulating legacy runtimes (Python 2, Java 8, older C runtimes) on modern Linux hosts without dependency conflicts.

---

## 4. Certification & Exam Essentials (Cheat Sheet)
* ⚠️ **Key Constraints**: Containers share the host OS kernel; a Linux container cannot natively execute Windows kernel system calls without hypervisor virtualization.
* 🔒 **Security & Governance**: Running containers as `root` inside the container poses privilege escalation risks; always use non-root users (`USER appuser`).
* ⚙️ **Operational Gotchas**: Ephemeral storage lifecycle means all data written to the container layer is destroyed upon container deletion unless persistent volumes are attached.

---

## 5. Hands-On Walkthrough: Running Your First Isolated Container
### Step 1: Verify Docker Installation
Query the Docker daemon version and runtime capabilities:
```bash
docker version
```

### Step 2: Run an Nginx Web Server Container
Launch an isolated container in detached mode mapping host port 8080 to container port 80:
```bash
docker run -d \
    --name web-server \
    -p 8080:80 \
    nginx:alpine
```

### Step 3: Test Web Server Responsiveness
Verify web server output via curl:
```bash
curl http://localhost:8080
```

### Step 4: Clean Up Running Container
Stop and remove the container:
```bash
docker stop web-server \
    && docker rm web-server
```

---

## 6. Pure CLI Commands
### 1. Inspect System-Wide Docker Resource Usage
Display container counts, storage driver, and cgroup version:
```bash
docker system info
```

### 2. Stream Live Container Resource Metrics
Monitor CPU, memory percentage, and network I/O across all running containers:
```bash
docker stats \
    --no-stream
```

---

## 7. Detailed Sub-Components

### Docker Daemon (dockerd)

The primary daemon managing container lifecycles and API endpoints.

* **Key Concepts**:
  Listens for Docker Engine API requests and coordinates with containerd to launch OCI containers.

* **CLI Snippet**:
  Inspect daemon logs on systemd-managed Linux host:
  ```bash
  sudo journalctl -u docker \
      -n 50 \
      --no-pager
  ```

---

## References

### Official Documentation
* [Docker Overview Documentation](https://docs.docker.com/get-started/overview/) - Architectural fundamentals and core runtime guide.
* [Docker Engine Reference](https://docs.docker.com/engine/reference/commandline/cli/) - Complete CLI command manual.
* [Docker Security Best Practices](https://docs.docker.com/engine/security/) - Hardening container isolation and user namespaces.
* [OCI (Open Container Initiative) Specifications](https://opencontainers.org/) - Industry standard container image and runtime specs.
* [Docker CLI Installation Guide](https://docs.docker.com/engine/install/) - Platform-specific installation packages.

### Authoritative Web Pages, Blogs & Tutorials
* [Brendan Gregg: Linux Container Performance and Cgroups](https://www.brendangregg.com/) - Kernel-level profiling of containerized processes.
* [Julia Evans: What Happens When You Run a Docker Container?](https://jvns.ca/) - Illustrated guide to namespaces and chroot.
* [A Cloud Guru: Docker Certified Associate (DCA) Preparation Guide](https://www.pluralsight.com/) - Essential enterprise container concepts.
* [Datadog Engineering: The State of Container Adoption and Monitoring](https://www.datadoghq.com/blog/) - Telemetry benchmarks for containerized fleets.
* [FinOps Foundation: Introduction to Container Economics](https://www.finops.org/) - Sizing compute requests and bin-packing efficiency.

---

## FinOps & Resource Cost Governance in Container Environments

*Financial Operations (FinOps) in Docker and containerized environments focuses on minimizing container resource waste, optimizing image transfer bandwidth, maximizing host server bin-packing, and eliminating orphaned storage volumes.*

### 1. Cost Visibility & Container Resource Allocation
- **Container Sizing Baselines** – Measure real-world CPU and memory usage using `docker stats` and cgroup metrics. Avoid running containers without resource constraints (`--memory` and `--cpus`), which lead to noisy-neighbor resource starvation and premature host scaling.
- **Labeling for Cost Allocation** – Apply standardized Docker labels (`com.company.environment=prod`, `com.company.owner=sre-team`, `com.company.costcenter=104`) to all containers and images to enable automated container showback and chargeback.

### 2. Image Layer Optimization & Bandwidth Reduction
- **Multi-Stage Builds** – Utilize multi-stage Docker builds to eliminate build-time dependencies, compilers, and source files from final production container images, reducing image sizes by up to 80-95% (e.g. from 1.2GB to 45MB).
- **Minimal Base Images** – Use minimal base images like Alpine Linux or distroless images (`gcr.io/distroless`) to reduce cloud container registry storage costs and network egress transfer fees during deployment pipelines.

### 3. Storage Volume & Image Pruning Automation
- **Orphaned Volume Purging** – Dangling Docker volumes (`docker volume ls -f dangling=true`) continue to consume expensive cloud block storage. Automate periodic execution of `docker system prune --volumes -f` via cron jobs to reclaim lost storage.
- **Container Registry Retention Policies** – Configure automatic lifecycle rules on container registries (AWS ECR, Docker Hub, Harbor) to delete untagged and older image tags after 14-30 days.

### 4. Continuous Optimization Lifecycle
- **Host Bin-Packing** – Increase container density per host machine by setting strict memory boundaries (`--memory-reservation`), allowing higher server consolidation and slashing cloud virtual machine counts by 40-60%.
- **Development Fleet Cleanup** – Automate the shutdown of local and staging Docker Compose stacks outside business hours to eliminate idle compute spend.
