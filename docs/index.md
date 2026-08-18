# Docker & Container Engineering Curriculum — Master Index
**Repository:** `vit/docker-containers`
**Domain:** Containerization, Linux Kernel Runtimes & Multi-Container Stacks
**Target Certifications:** DCA (Docker Certified Associate), CKA, SRE Foundations
**Status:** ✅ Complete Production-Grade Reference

---

## 📚 Complete Module Index

| Module | Core Topics & Hands-On Scope | Target Certifications | Document Link |
| :--- | :--- | :--- | :--- |
| **01. Getting Started** | Container fundamentals, Linux namespaces, cgroups, and running first containers | DCA, KCNA | [`getting-started.md`](getting-started.md) |
| **02. Docker Engine** | Engine architecture, dockerd, containerd, runc, and kernel cgroups v2 | DCA, CKA | [`docker-engine.md`](docker-engine.md) |
| **03. Working with Images** | Dockerfile directives, layer caching, and multi-stage builds | DCA, CKAD | [`working-with-images.md`](working-with-images.md) |
| **04. Containerizing Apps** | Twelve-Factor App packaging, non-root users, and health checks | DCA, CKAD | [`containerizing_an_app.md`](containerizing_an_app.md) |
| **05. Container Operations** | Lifecycle states, restart policies, resource constraints, and live exec | DCA, CKA | [`working-with-containers.md`](working-with-containers.md) |
| **06. Multi-Container Stacks** | Docker Compose specification, networks, volumes, and health gating | DCA, CKAD | [`multi-container-apps.md`](multi-container-apps.md) |
| **07. Storage & Volumes** | Named volumes, bind mounts, tmpfs, and database data persistence | DCA, CKA | [`docker-volumes.md`](docker-volumes.md) |
| **08. Docker Networking** | Bridge, Host, Overlay, Macvlan, and embedded DNS resolution | DCA, CKA | [`docker-networking.md`](docker-networking.md) |
| **09. Docker Security** | Capability dropping, read-only root filesystems, seccomp, and CVE scans | DCA, CKS | [`docker-security.md`](docker-security.md) |
| **10. Docker Swarm** | Native clustering, Raft consensus, services, and ingress routing mesh | DCA, SRE | [`docker-swarm.md`](docker-swarm.md) |
| **11. Docker & WebAssembly** | Wasm/WASI runtimes, containerd shims, and sub-millisecond execution | SRE, Cloud-Native | [`docker-and-wasm.md`](docker-and-wasm.md) |
| **12. Command Cheat Sheet** | Escaped CLI reference commands for SRE production operations | DCA, SRE | [`docker-cheatsheet.md`](docker-cheatsheet.md) |
| **13. Apache Kafka in Docker** | Distributed event streaming with KRaft mode in Docker Compose | DevOps, SRE | [`apache-kafka-introduction.md`](apache-kafka-introduction.md) |
| **14. Platform Documentation** | Central architectural overview and curriculum navigation | All Tracks | [`docker-docs.md`](docker-docs.md) |

---

## 📌 Foundations, Ecosystem & Pre-requisite Notes (Original Notes)

### Why Containers? (Evolution from Virtual Machines)
* **The Story with VMware & Hypervisors**: Virtual machines abstract hardware, but running an entire guest OS inside each VM introduces significant overhead:
  * Every OS consumes CPU, RAM, and disk storage that could otherwise run applications.
  * Every VM operating system requires its own patch management, kernel updates, and antivirus agents.
  * Every VM requires continuous uptime monitoring and performance tuning.
  * Virtual machines are slow to provision (minutes vs milliseconds) and difficult to transport across clouds.
* **Cross-Platform Execution**: Linux containers run natively on Windows and macOS using lightweight virtualization (WSL2 on Windows, Apple Hypervisor Framework / Lima / QEMU on macOS).
* **Next-Gen WebAssembly (Wasm)**: Compile code once to universal Wasm bytecode and execute inside sandboxed runtimes with zero guest OS overhead.
* **Specialized Hardware Acceleration in AI/ML**:
  * **GPU** (Graphics Processing Unit) - High-throughput matrix multiplication.
  * **TPU** (Tensor Processing Unit) - Google ASIC hardware for neural network training.
  * **NPU** (Neural Processing Unit) - Low-power edge inference acceleration.
* **Etymology**: Docker is named after *Dock Worker* (stevedores who load and unload shipping containers at sea ports).

### The Container Ecosystem & Standards
* **Two Major Platform Components**:
  1. **Docker CLI Client**: The command-line tool.
  2. **Docker Engine Server**: The background daemon and container runtime.
* **Open Container Initiative (OCI)**:
  * `image-spec`: Format of container images and layer tarballs.
  * `runtime-spec`: Runtime specification implemented by `runc`.
  * `distribution-spec`: Standard protocol for pushing/pulling from container registries.
* **Cloud Native Computing Foundation (CNCF)** Project Phases:
  * **Sandbox** -> **Incubating** -> **Graduated** (e.g. Kubernetes, containerd, Envoy).
* **The Moby Project**: The open-source upstream framework that powers Docker Engine.

### Fast Help & Global Cleanup Commands
```bash
docker version
docker info
docker --version
docker --help
docker rm $(docker ps --all --quiet) -f
docker rmi $(docker images --all --quiet) -f
```

---

## 🛠️ Documentation Standards Applied Across All Guides
1. **👔 Executive Summary**: Non-technical explanation of business purpose, mechanics, and value for managers and teammates.
2. **Technical Deep Dives**: Comprehensive architecture explanations, consensus mechanics, and kernel-level primitives.
3. **Hands-On Step-by-Step Walkthroughs**: Reproducible labs for building, scaling, securing, and debugging workloads.
4. **Clean, Escaped CLI Snippets**: Formatted with trailing ` \` line escapes, 4-space indentation, and zero in-code comments.
5. **Trustworthy Curated Sources**: Exactly 5 official documentation links + 5 authoritative engineering blogs per module.
6. **FinOps & Resource Governance**: 500+ word guidelines on multi-tenant cost allocation, bin-packing, and autoscaling.
