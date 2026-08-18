# Module: Docker Storage, Volumes & Bind Mounts
**Category:** Persistent Storage & Data Management
**Status:** ✅ Completed

---

## 1. High-Level Overview
By default, all files created inside a Docker container are stored in a temporary, writable container layer using a union filesystem (such as **overlay2**). When the container is deleted, this writable layer is permanently destroyed, and write performance is subject to copy-on-write (CoW) overhead. For stateful enterprise applications—such as relational databases, search indices, and shared file repositories—Docker provides three primary storage mechanisms: **Named Volumes** (fully managed by Docker in `/var/lib/docker/volumes`), **Bind Mounts** (mounting arbitrary host filesystem paths into the container), and **tmpfs Mounts** (in-memory temporary storage that never touches disk).

### 👔 Executive Summary (For Managers & Non-Technical Stakeholders)
* **Business Purpose**: Guarantees that valuable corporate data, database records, and transaction logs are stored safely on permanent server disks and never lost when containers restart or update.
* **How It Works**: Separates the application software from its permanent data storage. When a database container is upgraded to a newer version, the permanent data disk is reattached to the new container instantly.
* **Key Business Value & Use Cases**: Prevents catastrophic business data loss, enables automated database backups and snapshots, and delivers high-speed disk performance for enterprise database systems.

---

## 2. Storage Types Comparison

| Storage Type | Managed By | Host Location | Performance / Use Case |
| :--- | :--- | :--- | :--- |
| **Named Volumes** | Docker Engine | `/var/lib/docker/volumes/<vol_name>/_data` | Production databases, high I/O performance, backup/restore support |
| **Bind Mounts** | Host OS / User | Arbitrary path (e.g. `/home/user/code`) | Development source code hot-reloading, host config file injection |
| **tmpfs Mounts** | Linux Kernel RAM | Host system memory (never written to disk) | High-security ephemeral tokens, sensitive in-memory caching |

---

## 📌 Volume Architecture & Host Locations (Original Notes)

* **First-Class Objects**: Volumes are first-class, independent objects in Docker with their own distinct lifecycles.
* **Default Host Storage Path**:
  * **Linux Hosts**: `/var/lib/docker/volumes/<vol_name>/_data/`
  * **macOS Docker Desktop**: Inside the Docker VM disk image (`~/Library/Containers/com.docker.docker/Data/Docker.qcow2` or `Docker.raw`).
* **Volume Reuse**: Docker attaches existing named volumes if they exist or creates a new volume on demand.

### Essential Volume & Bind Mount Operations
* Launch an Alpine container with a named volume using `--mount`:
```bash
docker volume create bizvol
docker run -it \
    --name voltainer \
    --mount source=bizvol,target=/vol \
    alpine
```
* Launch Debian container with a host directory bind mount:
```bash
docker run -it \
    --name voltainer \
    --mount type=bind,source=/Users/frgonzal/Fluxfox/voltainer,target=/home \
    debian:stable-slim \
    && docker start -ai voltainer
```
* Deploy NocoDB container with persistent host bind mount:
```bash
docker run -d \
    --name nocodb \
    -p 8080:8080 \
    --mount type=bind,source=/Users/frgonzal/Fluxfox/nocodb,target=/usr/app/data \
    nocodb/nocodb:latest
```

### Volume Management Commands
```bash
docker volume create myvol
docker volume ls
docker volume inspect myvol
docker volume prune
docker volume rm myvol
```

---

## 3. Hands-On Walkthrough: Persistent PostgreSQL Storage
### Step 1: Create a Dedicated Named Volume
Create an isolated volume with standard local driver:
```bash
docker volume create postgres-data
```

### Step 2: Mount Volume into Database Container
Launch PostgreSQL container mounting the named volume:
```bash
docker run -d \
    --name stateful-db \
    -e POSTGRES_PASSWORD=SecurePass123! \
    -v postgres-data:/var/lib/postgresql/data \
    postgres:16-alpine
```

### Step 3: Verify Data Persistence Across Container Deletion
Remove container and attach the same volume to a new container instance:
```bash
docker rm -f stateful-db \
    && docker run -d \
        --name stateful-db-v2 \
        -e POSTGRES_PASSWORD=SecurePass123! \
        -v postgres-data:/var/lib/postgresql/data \
        postgres:16-alpine
```

---

## 4. Pure CLI Commands
### 1. List and Filter Dangling Storage Volumes
Identify unused storage volumes taking up disk space:
```bash
docker volume ls \
    --filter dangling=true
```

### 2. Inspect Volume Mount Points and Metadata
Query the exact host path backing the volume:
```bash
docker volume inspect postgres-data \
    --format '{{.Mountpoint}}'
```

---

## References

### Official Documentation
* [Docker Storage Overview](https://docs.docker.com/storage/) - Volumes, bind mounts, and tmpfs.
* [Docker Volumes Guide](https://docs.docker.com/storage/volumes/) - Creating, managing, and backing up volumes.
* [Docker Bind Mounts Reference](https://docs.docker.com/storage/bind-mounts/) - Host path mapping and permissions.
* [Docker tmpfs Mounts](https://docs.docker.com/storage/tmpfs/) - In-memory ephemeral storage.
* [Docker Storage Drivers (overlay2)](https://docs.docker.com/storage/storagedriver/) - Copy-on-write layer mechanics.

### Authoritative Web Pages, Blogs & Tutorials
* [Brendan Gregg: Linux File System I/O Performance in Containers](https://www.brendangregg.com/) - Overlay2 vs native block volume benchmarks.
* [A Cloud Guru: Docker Certified Associate (DCA) Storage Guide](https://www.pluralsight.com/) - Volume lifecycle and backup patterns.
* [Datadog Engineering: Monitoring Docker Disk Utilization and Volume I/O](https://www.datadoghq.com/blog/) - Disk alerting strategies.
* [Snyk Security: Securing Docker Bind Mounts Against Host Takeover](https://snyk.io/) - Restricting read-only host mounts.
* [FinOps Foundation: Purging Orphaned Cloud Storage Volumes](https://www.finops.org/) - Reclaiming unused disk space.

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
