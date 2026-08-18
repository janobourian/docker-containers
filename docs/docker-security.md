# Module: Docker Security, Hardening & Compliance
**Category:** Container Security, Rootless Mode & Vulnerability Scanning
**Status:** ✅ Completed

---

## 1. High-Level Overview
Securing Docker environments requires defense-in-depth across the entire container supply chain and runtime lifecycle: **Image Security** (scanning base images for CVEs and enforcing immutable digest pinning), **Build Security** (multi-stage builds, non-root user execution, and secret redaction), **Runtime Security** (dropping unnecessary Linux capabilities, enforcing `no-new-privileges`, seccomp profile system call filtering, and AppArmor/SELinux mandatory access control), and **Host Daemon Security** (enabling Rootless Docker and daemon socket TLS authentication).

### 👔 Executive Summary (For Managers & Non-Technical Stakeholders)
* **Business Purpose**: Protects company data, customer privacy, and cloud servers against cyberattacks, ransomware, and unauthorized access.
* **How It Works**: Enforces strict security guardrails. It scans software for vulnerabilities before deployment, strips administrative (root) superpowers from running applications, and locks down server access.
* **Key Business Value & Use Cases**: Satisfies strict enterprise compliance standards (SOC 2, ISO 27001, PCI-DSS, HIPAA), prevents catastrophic security breaches, and protects company reputation.

---

## 📌 Security Foundations & Swarm Integration (Original Notes)

* **Swarm Security Synergy**: Docker security primitives (mutual TLS node identity, encrypted overlay networks, and Docker Secrets) work natively and seamlessly with Docker Swarm mode to provide end-to-end zero-trust clustering.

---

## 2. Core Security Controls & Linux Hardening

1. **Non-Root Container Execution (`USER`)**:
   - Running as UID 0 inside a container gives attackers root-level privileges if a container breakout vulnerability occurs. Always enforce non-root execution (`USER 10001:10001`).

2. **Linux Capabilities Dropping (`--cap-drop=ALL`)**:
   - By default, Docker grants containers a subset of Linux capabilities (e.g. `CAP_NET_BIND_SERVICE`, `CAP_CHOWN`). Production containers should drop all capabilities and selectively add back only what is strictly required:
     ```bash
     --cap-drop=ALL --cap-add=NET_BIND_SERVICE
     ```

3. **Read-Only Root Filesystems (`--read-only`)**:
   - Mounts the container root filesystem as read-only, preventing malicious scripts or malware from writing persistent binaries to `/bin` or `/usr`.

4. **Seccomp & AppArmor Profiles**:
   - **Seccomp (Secure Computing Mode)**: Restricts the system calls a container process can invoke in the Linux kernel (blocking risky syscalls like `ptrace`, `sys_chroot`, `keyctl`).
   - **AppArmor / SELinux**: Enforces mandatory access controls on files, capabilities, and network sockets.

---

## 3. Hands-On Walkthrough: Running a Hardened, Zero-Trust Container
### Step 1: Run a Hardened Container with Dropped Capabilities and Read-Only Filesystem
Launch an Nginx container with maximum security flags:
```bash
docker run -d \
    --name secure-web \
    --security-opt=no-new-privileges:true \
    --cap-drop=ALL \
    --cap-add=NET_BIND_SERVICE \
    --read-only \
    --tmpfs /var/cache/nginx:rw,noexec,nosuid \
    --tmpfs /var/run:rw,noexec,nosuid \
    -p 8082:80 \
    nginx:alpine
```

### Step 2: Audit Security Constraints
Verify that capability escalation is blocked:
```bash
docker exec secure-web sh -c "ping 8.8.8.8"
```

### Step 3: Cleanup
Stop and remove container:
```bash
docker rm -f secure-web
```

---

## 4. Pure CLI Commands
### 1. Scan Container Image for Vulnerabilities
Scan image for known CVEs using Docker Scout:
```bash
docker scout cves \
    nginx:alpine
```

### 2. Inspect Container Security Options
Audit attached seccomp and AppArmor profiles:
```bash
docker inspect secure-web \
    --format '{{json .HostConfig.SecurityOpt}} {{json .HostConfig.CapDrop}}'
```

---

## References

### Official Documentation
* [Docker Security Documentation](https://docs.docker.com/engine/security/) - Hardening guidelines and security architecture.
* [Docker Rootless Mode Guide](https://docs.docker.com/engine/security/rootless/) - Running daemon as non-root user.
* [Seccomp Security Profiles in Docker](https://docs.docker.com/engine/security/seccomp/) - System call filtering reference.
* [AppArmor Profiles in Docker](https://docs.docker.com/engine/security/apparmor/) - Mandatory access control policies.
* [CIS Docker Benchmark Guide](https://www.cisecurity.org/benchmark/docker) - Industry standard configuration baseline.

### Authoritative Web Pages, Blogs & Tutorials
* [Snyk Security: 10 Docker Security Best Practices](https://snyk.io/blog/) - Comprehensive container hardening guide.
* [Datadog Security Labs: Analyzing Container Breakout Techniques](https://securitylabs.datadoghq.com/) - Kernel capability exploits.
* [A Cloud Guru: Docker Certified Associate (DCA) Security](https://www.pluralsight.com/) - Least privilege container execution.
* [Aqua Security Blog: Hardening Docker Daemons in Production](https://blog.aquasec.com/) - Daemon socket protection.
* [FinOps Foundation: Security Compliance and Resource Governance](https://www.finops.org/) - Balancing security overhead with efficiency.

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
