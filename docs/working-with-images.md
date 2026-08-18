# Module: Working with Docker Images & Multi-Stage Builds
**Category:** Container Image Lifecycle & Optimization
**Status:** ✅ Completed

---

## 1. High-Level Overview
A **Docker Image** is a read-only, immutable, layered blueprint used to instantiate running containers. Images are constructed using a declarative **Dockerfile** containing sequential build instructions (`FROM`, `COPY`, `RUN`, `ENV`, `EXPOSE`, `CMD`, `ENTRYPOINT`). Each instruction creates an immutable read-only image layer managed by a union filesystem driver (**overlay2**). 

Production container engineering demands the use of **Multi-Stage Builds** to separate the compilation/build environment from the final runtime environment, stripping unnecessary compilers, debug symbols, and package managers to produce minimal, secure, and cost-effective container images.

### 👔 Executive Summary (For Managers & Non-Technical Stakeholders)
* **Business Purpose**: Creates secure, ultra-compact, production-ready software packages that deploy rapidly across cloud servers while preventing security vulnerabilities.
* **How It Works**: Uses an assembly-line recipe (Dockerfile) to build the application. By discarding heavy compilers and source code after building, it keeps only the bare minimum files needed to run the software.
* **Key Business Value & Use Cases**: Reduces container image download times by up to 90%, slashes cloud bandwidth and storage bills, and drastically shrinks the cybersecurity attack surface by eliminating unnecessary operating system tools.

---

## 2. Dockerfile Directives & Multi-Stage Architecture

```
Stage 1: Build & Compilation (Heavy: Golang / Node / Rust Compiler - ~1.2GB)
+-------------------------------------------------------------+
| FROM golang:1.22-alpine AS builder                          |
| COPY . .                                                    |
| RUN go build -o /app/server .                               |
+-------------------------------------------------------------+
                              |
                              | (Extract ONLY the compiled binary)
                              v
Stage 2: Production Runtime (Ultra-Minimal: Distroless / Scratch - ~15MB)
+-------------------------------------------------------------+
| FROM gcr.io/distroless/static-debian12                      |
| COPY --from=builder /app/server /server                     |
| ENTRYPOINT ["/server"]                                      |
+-------------------------------------------------------------+
```

---

## 📌 Image Fundamentals, Tagging & Multi-Arch (Original Notes)

* **Lightweight Base**: The most lightweight Linux distribution image is Alpine Linux (~5MB).
* **Image Registries Lifecycle**: `Build -> Share -> Run`.
* **Image Naming and Tagging Schema**: `Registry/User-Org/Repository:Image-tag` (e.g., `docker.io/janobourian/bank-app:latest`).
* **Layer Immutability**: Images are collections of loosely connected read-only layers where each layer comprises one or more files.
* **Content vs Distribution Hashes**:
  * **Content Hash**: SHA256 digest calculated over the uncompressed layer contents.
  * **Distribution Hash**: Digest of the compressed layer archive transferred over the wire.
* **Multi-Architecture Images & Manifests**:
  * **Manifest Lists**: A single tag pointing to an array of architecture-specific manifests (AMD64, ARM64, RISC-V).
  * **Buildx**: Client plugin for building multi-platform images using QEMU emulation or Docker Build Cloud.

### Essential Image Investigation Commands
* Pull and run interactive language shells:
```bash
docker pull python:latest \
    && docker run -it --name macarena -d python:latest \
    && docker start -ai macarena
docker pull elixir:latest \
    && docker run -it --name iex_shell -d elixir:latest \
    && docker start -ai iex_shell
docker pull gcc \
    && docker run -it --name samba gcc:latest bash
```
* Inspect metadata, layers, and manifests:
```bash
docker inspect node:latest
docker history node:latest
docker manifest inspect nginx:latest
docker images --digests alpine:latest
docker buildx imagetools inspect amazonlinux:latest
docker scout quickview nginx:latest
```
* Batch remove all local images:
```bash
docker rmi $(docker images -q) -f
```

---

## 3. Hands-On Walkthrough: Creating an Optimized Multi-Stage Go Image
### Step 1: Write an Optimized Multi-Stage Dockerfile
Define a multi-stage build stripping build tools:
```dockerfile
FROM golang:1.22-alpine AS builder
WORKDIR /src
COPY main.go .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /bin/app main.go

FROM scratch
COPY --from=builder /bin/app /bin/app
USER 10001:10001
ENTRYPOINT ["/bin/app"]
```

### Step 2: Build the Container Image
Build the image with an explicit tag:
```bash
docker build \
    -t my-app:v1.0.0 \
    -f Dockerfile .
```

### Step 3: Inspect Image Layer Sizes
Audit the size of each image layer:
```bash
docker history my-app:v1.0.0
```

---

## 4. Pure CLI Commands
### 1. List Local Container Images Sorted by Size
Inspect local image repository:
```bash
docker images \
    --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

### 2. Prune Unused and Dangling Images
Reclaim disk space by purging untagged build layers:
```bash
docker image prune -f
```

---

## 5. Detailed Sub-Components

### Docker BuildKit Engine

Next-generation parallel build subsystem for Docker.

* **Key Concepts**:
  Features concurrent dependency graph execution, build secret mounting without baking into layers (`--mount=type=secret`), and high-performance build caching.

* **CLI Snippet**:
  Enable BuildKit and build image with inline cache:
  ```bash
  DOCKER_BUILDKIT=1 docker build \
      --build-arg BUILDKIT_INLINE_CACHE=1 \
      -t optimized-app:latest .
  ```

---

## References

### Official Documentation
* [Dockerfile Best Practices Guide](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/) - Production image authoring guidelines.
* [Multi-Stage Builds Documentation](https://docs.docker.com/build/building/multi-stage/) - Separating build and runtime environments.
* [Docker BuildKit User Guide](https://docs.docker.com/build/buildkit/) - Advanced build caching and secret mounting.
* [Docker Registry API Specification](https://docs.docker.com/registry/spec/api/) - Image manifest distribution standards.
* [Distroless Container Images](https://github.com/GoogleContainerTools/distroless) - Language-focused minimal base images.

### Authoritative Web Pages, Blogs & Tutorials
* [Google Cloud Architecture Blog: Best Practices for Building Containers](https://cloud.google.com/blog/products/containers-kubernetes/) - Production caching and layer ordering.
* [A Cloud Guru: Docker Certified Associate (DCA) Image Mastery](https://www.pluralsight.com/) - Mastering CMD vs ENTRYPOINT.
* [Snyk Security: Top 10 Docker Security Best Practices](https://snyk.io/blog/) - Vulnerability scanning in container layers.
* [Datadog Engineering: Shrinking Production Container Images](https://www.datadoghq.com/blog/) - Eliminating image bloat.
* [FinOps Foundation: Container Image Storage and Egress Optimization](https://www.finops.org/) - Cutting container registry cloud costs.

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
