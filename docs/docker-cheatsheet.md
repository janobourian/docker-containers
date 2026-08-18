# Module: Docker Enterprise Command Line Cheat Sheet
**Category:** Operational Quick Reference & SRE Commands
**Status:** ✅ Completed

---

## 1. High-Level Overview
This reference guide provides a consolidated, production-grade cheat sheet of essential Docker CLI commands, formatted according to enterprise standards with strict multiline backslash (`\`) escaping, 4-space parameter indentation, and zero in-code comments.

### 👔 Executive Summary (For Managers & Non-Technical Stakeholders)
* **Business Purpose**: Serves as the rapid-reference operational playbook for site reliability engineers, enabling rapid issue resolution, system maintenance, and infrastructure audits.
* **How It Works**: Standardizes critical maintenance commands into clear, executable operational runbooks for quick copy-paste execution during production incidents.
* **Key Business Value & Use Cases**: Reduces incident recovery times (MTTR), standardizes operations across global engineering teams, and prevents human errors during critical maintenance windows.

---

## 📌 Comprehensive Quick Reference & Flags (Original Notes)

### Help Navigation
* `docker --help` - Top-level CLI manual.
* `docker <COMMAND> --help` - Command-specific flag documentation.

### Core CLI Commands Annotated
* `docker version` - Display detailed client and server build metadata.
* `docker info` - Show host system resources, storage driver, and security profiles.
* `docker --version` - Quick client release version.
* `docker images` - List all locally downloaded and built container images.
* `docker pull <IMAGE_NAME>:<VERSION>` - Pull a specific image from Docker Hub / ECR.
* `docker run --name <CONTAINER_NAME> --detach --publish <INTERNAL_PORT>:<EXPOSE_PORT> <IMAGE_NAME>:<VERSION>` - Instantiate container.
* `docker ps` - List currently running containers.
* `docker ps --all` - List all containers in any lifecycle state.
* `docker exec -it <CONTAINER_NAME> <COMMAND>` - Execute command in interactive mode.
* `docker stop <CONTAINER_NAME>` - Gracefully terminate container with SIGTERM.
* `docker rm <CONTAINER_NAME>` - Delete stopped container.
* `docker rmi <IMAGE_NAME>:<VERSION>` - Delete container image.
* `docker build -t <IMAGE_NAME>:<VERSION> .` - Build image from Dockerfile.
* `docker start <CONTAINER_NAME>` - Start an existing stopped container.
* `docker restart <CONTAINER_NAME>` - Restart a running or stopped container.
* `docker init` - Automatically initialize Dockerfile, compose.yaml, and .dockerignore assets.
* `docker tag <CURRENT_TAG> <NEW_TAG>` - Assign an alias tag to an image.

### Parameter Flags Quick Reference
* `--name string` - Assign a custom name to the container.
* `[-d | --detach]` - Run container in background and print container ID.
* `[-p | --publish] <HOST_PORT>:<CONTAINER_PORT>` - Publish container port to host interface.
* `ps [-a | --all]` - Show all containers (including stopped/exited).
* `exec [-it | --interactive --tty]` - Allocate a pseudo-TTY connected to container stdin.
* `exec [--user | -u] <USERNAME>` - Execute container command under specified user/UID.
* `start [-ia | -i -a]` - Attach container standard I/O and forward signals.
* `build [-t | --tag]` - Name and optionally a tag in the 'name:tag' format.
* `run --env-file <LIST_ENV_FILES>` - Read in a file of environment variables.
* `run [--rm]` - Automatically remove container and anonymous volumes on exit.
* `run [--restart <POLICY>]` - Restart policy (`no`, `on-failure`, `always`, `unless-stopped`).

### Docker Compose CLI Reference
* `docker compose version` - Display Compose plugin release version.
* `docker compose up` - Build, (re)create, start, and attach to containers.
* `docker compose build <SERVICE>` - Build or rebuild services.
* `docker compose down` - Stop and remove containers, networks, and images.
* `docker compose down -v --remove-orphans` - Remove named volumes and orphan containers.
* `docker compose build --no-cache <SERVICE>` - Rebuild service image from scratch.
* `docker compose ps` - List stack containers and health status.
* `docker compose logs -f` - Stream live logs from all stack services.
* `docker compose logs -f <SERVICE>` - Stream live logs from a specific service.

### Image Inspection Commands
* `docker inspect <IMAGE_NAME>:<VERSION>` - Display low-level JSON representation of image.
* `docker history <IMAGE_NAME>:<VERSION>` - Show the build history and layer sizes.
* `docker manifest inspect <IMAGE_NAME>:<VERSION>` - Inspect multi-arch manifest list.

---

## 2. Essential Docker Operations

### Container Lifecycle Commands
Launch a background container with memory limits and port publishing:
```bash
docker run -d \
    --name production-web \
    --restart=unless-stopped \
    --memory="512m" \
    --cpus="1.0" \
    -p 80:80 \
    nginx:alpine
```

Stop and gracefully terminate a running container with custom timeout:
```bash
docker stop \
    --time=30 \
    production-web
```

Force-kill and remove a container:
```bash
docker rm -f production-web
```

### Image Management Commands
Build an image using multi-stage Dockerfile and BuildKit:
```bash
DOCKER_BUILDKIT=1 docker build \
    --no-cache \
    --tag api-service:v2.1.0 \
    --file Dockerfile .
```

Scan image for critical vulnerabilities:
```bash
docker scout quickview api-service:v2.1.0
```

### System Maintenance & Storage Cleanup
Reclaim all disk space from unused containers, networks, dangling images, and volumes:
```bash
docker system prune \
    --all \
    --volumes \
    --force
```

Display detailed disk breakdown consumed by images, containers, and build cache:
```bash
docker system df -v
```

---

## References

### Official Documentation
* [Docker CLI Reference Index](https://docs.docker.com/engine/reference/commandline/cli/) - Complete command documentation.
* [Docker System Commands](https://docs.docker.com/engine/reference/commandline/system/) - Pruning and telemetry.
* [Docker Inspect Reference](https://docs.docker.com/engine/reference/commandline/inspect/) - Go template formatting.
* [Docker Build Commands](https://docs.docker.com/engine/reference/commandline/build/) - Build flags and caching.
* [Docker Compose CLI](https://docs.docker.com/compose/reference/) - Stack lifecycle commands.

### Authoritative Web Pages, Blogs & Tutorials
* [Docker Desktop & CLI Cheat Sheet](https://www.docker.com/resources/cheat-sheets/) - Official quick reference.
* [A Cloud Guru: Docker Certified Associate (DCA) Exam Cheat Sheet](https://www.pluralsight.com/) - Exam focus areas.
* [Datadog Engineering: Docker Troubleshooting Runbooks](https://www.datadoghq.com/blog/) - Production diagnostics.
* [Snyk Security: Container Security Cheat Sheet](https://snyk.io/) - Hardening quick reference.
* [FinOps Foundation: Docker Cost Management Runbook](https://www.finops.org/) - Storage and compute pruning.

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
