# Module 09: Docker Security, Hardening, Rootless Mode & Compliance

**Track:** Docker Container Systems & Virtualization Architecture
**Category:** Container Security, Rootless Execution, Seccomp, AppArmor & CIS Benchmarks
**Standard Identifier:** `DOC-STD-UNIVERSAL-2026`
**Status:** ✅ Completed

---

## 📑 Table of Contents

1. [High-Level Overview & Executive Summary](#1-high-level-overview--executive-summary)

2. [The Defense-in-Depth Container Security Model](#2-the-defense-in-depth-container-security-model)

3. [Linux Capabilities, Seccomp BPF & Mandatory Access Control (AppArmor/SELinux)](#3-linux-capabilities-seccomp-bpf--mandatory-access-control-apparmorselinux)

4. [Rootless Docker Daemon Architecture & User Namespaces](#4-rootless-docker-daemon-architecture--user-namespaces)

5. [Supply Chain Security: SBOMs, Image Signing (Cosign) & CVE Scanning](#5-supply-chain-security-sboms-image-signing-cosign--cve-scanning)

6. [Certification & Exam Essentials (Cheat Sheet)](#6-certification--exam-essentials-cheat-sheet)

7. [Comparative Analysis Matrix: Container Security Enforcement Models](#7-comparative-analysis-matrix-container-security-enforcement-models)

8. [Performance & Resource Optimization](#8-performance--resource-optimization)

9. [Step-by-Step Hands-On Production Walkthrough](#9-step-by-step-hands-on-production-walkthrough)

10. [Pure CLI / Command Interface](#10-pure-cli--command-interface)

11. [Advanced Architecture & Edge-Case Failure Modes](#11-advanced-architecture--edge-case-failure-modes)

12. [Detailed Sub-Components & Subsystems](#12-detailed-sub-components--subsystems)

13. [References (The 5+5 Rule)](#13-references-the-55-rule)

14. [Universal FinOps & Resource Cost Governance](#14-universal-finops--resource-cost-governance)

---

## 1. High-Level Overview & Executive Summary

Enterprise container security requires establishing a multi-layered **Defense-in-Depth Security Model** across the entire container lifecycle—from software supply chain verification to kernel runtime isolation. Because containers share the host Linux kernel, an un-hardened container process running as `root` (UID 0) presents a severe privilege escalation risk if a kernel vulnerability or container escape flaw (e.g. `runc` CVE-2019-5736, CVE-2024-21626) is exploited.

Securing the container runtime demands: dropping all non-essential Linux Capabilities (`--cap-drop ALL`), restricting dangerous kernel syscalls via **Seccomp BPF profiles**, enforcing Mandatory Access Control (**AppArmor / SELinux**), locking the root filesystem to read-only (`--read-only`), eliminating privilege escalation (`--security-opt no-new-privileges:true`), and deploying **Rootless Docker**.

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│               DEFENSE-IN-DEPTH CONTAINER SECURITY ARCHITECTURE                 │
├────────────────────────────────────────────────────────────────────────────────┤
│ 1. SUPPLY CHAIN SECURITY : Signed Images (Cosign), Distroless, SBOM generation │
│         │                                                                      │
│         ▼                                                                      │
│ 2. DAEMON LAYER HARDENING: Rootless Docker Daemon, mTLS Protected Socket      │
│         │                                                                      │
│         ▼                                                                      │
│ 3. USER NAMESPACE MAP    : Maps Container UID 0 ──► Host Unprivileged UID 100000│
│         │                                                                      │
│         ▼                                                                      │
│ 4. LINUX CAPABILITY DROP : Drops 38 Root Capabilities (`--cap-drop ALL`)       │
│         │                                                                      │
│         ▼                                                                      │
│ 5. SECCOMP SYSCALL FILTER: Blocks 40+ dangerous kernel syscalls (BPF sandbox)  │
│         │                                                                      │
│         ▼                                                                      │
│ 6. APPARMOR / SELINUX MAC: Enforces Mandatory Access Control on files & sockets│
│         │                                                                      │
│         ▼                                                                      │
│ 7. IMMUTABLE FILESYSTEM  : Read-Only Root Filesystem (`--read-only` + tmpfs)   │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 👔 Executive Summary (For Managers & Non-Technical Stakeholders)

* **Business Purpose**: Prevents cybercriminals from hacking cloud servers, stealing confidential customer databases, or deploying ransomware through vulnerable containerized applications.
* **How It Works**: Applies zero-trust security fences around every container. It strips administrative superpowers from software processes, locks files so malware cannot modify system code, and scans images for known vulnerabilities before deployment.
* **Key Business Value & ROI**: Satisfies strict enterprise regulatory compliance mandates (SOC 2, ISO 27001, PCI-DSS, HIPAA), prevents multimillion-dollar security breach liability, and protects enterprise brand trust.

---

## 2. The Defense-in-Depth Container Security Model

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                     CONTAINER SECURITY THREAT DEFENSE MATRIX                   │
├───────────────────┬──────────────────────────────────┬─────────────────────────┤
│ Security Tier     │ Technical Mechanism              │ Threat Neutralized      │
├───────────────────┼──────────────────────────────────┼─────────────────────────┤
│ **Supply Chain**  │ Image signing with Cosign        │ Malicious tampering and │
│                   │ and automated CVE scanners       │ supply chain poisoning  │
├───────────────────┼──────────────────────────────────┼─────────────────────────┤
│ **User Mapping**  │ User Namespaces (`userns-remap`) │ Container breakout root │
│                   │                                  │ takeover on host OS     │
├───────────────────┼──────────────────────────────────┼─────────────────────────┤
│ **Kernel Filter** │ Seccomp BPF System Call Filter   │ Zero-day Linux kernel   │
│                   │                                  │ syscall exploitation    │
├───────────────────┼──────────────────────────────────┼─────────────────────────┤
│ **Storage Lock**  │ Immutable `--read-only` root fs  │ Persistence of web shell│
│                   │                                  │ malware and rootkits    │
├───────────────────┼──────────────────────────────────┼─────────────────────────┤
│ **Privilege Lock**│ `--security-opt no-new-privileges`│ `setuid` binary abuse   │
│                   │                                  │ privilege escalation    │
└───────────────────┴──────────────────────────────────┴─────────────────────────┘
```

---

## 3. Linux Capabilities, Seccomp BPF & Mandatory Access Control (AppArmor/SELinux)

### 3.1 Linux Capabilities Granular Hardening

In Linux, the traditional `root` user possesses 38 distinct capabilities. Containers run with a default set of 14 capabilities (e.g. `CAP_CHOWN`, `CAP_FOWNER`, `CAP_NET_RAW`).

**Production Principle of Least Privilege**: Drop all capabilities and add back strictly what the application requires:

```bash
docker run \
    --cap-drop ALL \
    --cap-add NET_BIND_SERVICE \
    nginxinc/nginx-unprivileged:alpine
```

### 3.2 Seccomp (Secure Computing Mode) BPF Filtering

Seccomp uses Berkeley Packet Filter (BPF) programs to intercept and filter system calls before the Linux kernel processes them. Docker's default Seccomp profile blocks over **40 dangerous system calls**, including:

* `reboot` / `kexec_load`: Prevents container from rebooting the physical host.
* `ptrace`: Prevents process memory inspection and code injection into other processes.
* `sys_chroot` / `pivot_root`: Blocks escape from filesystem confinement.
* `keyctl` / `add_key`: Blocks access to the kernel's cryptographic keyring.

---

## 4. Rootless Docker Daemon Architecture & User Namespaces

In standard Docker installations, the `dockerd` daemon runs as the host `root` user, listening on `/var/run/docker.sock`. Anyone with access to the Docker socket can obtain full host root privileges.

### 4.1 Rootless Docker Mechanics

In **Rootless Docker**, both `dockerd` and the containers run inside an unprivileged **User Namespace**:

* The daemon runs under an unprivileged host user (e.g. UID 1000).
* Inside the container, processes appear to be UID 0 (root), but on the host OS, they map to unprivileged sub-UIDs (e.g. UID 100000–165535).
* If an attacker completely escapes the container, they hold **zero root privileges on the host system**!

---

## 5. Supply Chain Security: SBOMs, Image Signing (Cosign) & CVE Scanning

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│               ENTERPRISE CONTAINER SUPPLY CHAIN PIPELINE                       │
├────────────────────────────────────────────────────────────────────────────────┤
│ [Developer Commit] ──► [GitHub Actions CI / BuildKit]                          │
│                                │                                               │
│                                ▼ (Build Minimal Distroless Image)              │
│ ┌────────────────────────────────────────────────────────────────────────────┐ │
│ │ 1. Vulnerability Scan : Docker Scout / Trivy blocks Critical/High CVEs     │ │
│ ├────────────────────────────────────────────────────────────────────────────┤ │
│ │ 2. SBOM Generation    : Embeds SPDX / CycloneDX bill-of-materials packages │ │
│ ├────────────────────────────────────────────────────────────────────────────┤ │
│ │ 3. Cryptographic Sign : Cosign signs image digest with KMS private key     │ │
│ └──────────────────────────────┬─────────────────────────────────────────────┘ │
│                                │ (Pushes Signed OCI Image + Attestation)       │
│                                ▼                                               │
│ ┌────────────────────────────────────────────────────────────────────────────┐ │
│ │ OCI CONTAINER REGISTRY (AWS ECR / Google Artifact Registry / Harbor)       │ │
│ └──────────────────────────────┬─────────────────────────────────────────────┘ │
│                                │ (Admission Controller validates signature)    │
│                                ▼                                               │
│ ┌────────────────────────────────────────────────────────────────────────────┐ │
│ │ PRODUCTION RUNTIME HOST (Rejects unsigned or unverified images!)           │ │
│ └────────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Certification & Exam Essentials (Cheat Sheet)

* ⚠️ **Docker Daemon Socket Exposure Danger**: Exposing `/var/run/docker.sock` over an unencrypted TCP port (`-H tcp://0.0.0.0:2375`) allows remote attackers to compromise the entire server in seconds (`docker -H host:2375 run -v /:/host -it alpine chroot /host`). Always protect TCP sockets with **Mutual TLS (mTLS)** on port 2376!
* 🔒 **The `--privileged` Anti-Pattern**: Running a container with `--privileged` disables all Seccomp filters, AppArmor profiles, and cgroup restrictions, granting the container direct access to all host kernel devices (`/dev/*`). **The `--privileged` flag is strictly forbidden in production!**
* ⚙️ **`no-new-privileges`**: When set (`--security-opt no-new-privileges:true`), processes inside the container cannot gain new privileges through `setuid` or `setgid` binaries (e.g. `sudo`, `ping`).
* ⚠️ **CIS Docker Benchmark Audit**: Run `docker-bench-security` to audit your Docker daemon and host configuration against the official Center for Internet Security (CIS) compliance baseline.

---

## 7. Comparative Analysis Matrix: Container Security Enforcement Models

| Security Control | Protection Mechanism | Enforcement Layer | Performance Overhead |
| :--- | :--- | :--- | :--- |
| **Non-Root Execution** | Process UID separation | Linux Kernel (POSIX) | **Zero (0%)** |
| **Linux Capabilities Drop** | Strips 38 kernel privileges | Linux Kernel Capability bitmask | **Zero (0%)** |
| **Seccomp Syscall Filtering** | BPF kernel syscall filter | Linux Kernel Seccomp subsystem | < 0.1% CPU |
| **AppArmor / SELinux** | Mandatory Access Control (MAC) | Linux Security Module (LSM) | < 0.5% CPU |
| **User Namespaces** | Remaps UID 0 to UID 100000 | Linux User Namespace driver | **Zero (0%)** |
| **Rootless Docker** | Daemon runs as standard user | User Namespace + slirp4netns | Minimal network |

---

## 8. Performance & Resource Optimization

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                        SECURITY TUNING PLAYBOOK                                │
├────────────────────────────────────────────────────────────────────────────────┤
│ 1. Deploy Distroless images to eliminate 99% of CVE vulnerabilities.           │
│ 2. Enforce `no-new-privileges:true` on all production container executions.    │
│ 3. Drop all capabilities (`--cap-drop ALL`) and add back only required ones.  │
│ 4. Configure `--read-only` with RAM-backed `--tmpfs /tmp` for scratch space.  │
│ 5. Audit host configurations against CIS Docker Benchmark regularly.          │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Step-by-Step Hands-On Production Walkthrough

### Step 1: Configure Hardened Production Daemon with TLS & Security Options

```json
// /etc/docker/daemon.json
{
  "icc": false,
  "no-new-privileges": true,
  "live-restore": true,
  "userland-proxy": false,
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "20m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 65535,
      "Soft": 65535
    },
    "nproc": {
      "Name": "nproc",
      "Hard": 4096,
      "Soft": 4096
    }
  }
}
```

---

### Step 2: Deploy Zero-Trust Production Web Container

Launch an NGINX container with maximum defense-in-depth isolation flags:

```bash
docker run \
    --detach \
    --name zero-trust-web \
    --publish 8443:8080 \
    --memory 256m \
    --cpus 0.5 \
    --pids-limit 50 \
    --restart unless-stopped \
    --read-only \
    --cap-drop ALL \
    --cap-add NET_BIND_SERVICE \
    --security-opt no-new-privileges:true \
    --tmpfs /tmp:rw,noexec,nosuid,size=32m \
    --tmpfs /var/run:rw,noexec,nosuid,size=16m \
    --tmpfs /var/cache/nginx:rw,noexec,nosuid,size=64m \
    --health-cmd "curl -f http://localhost:8080/ || exit 1" \
    nginxinc/nginx-unprivileged:alpine
```

---

### Step 3: Audit and Verify Runtime Security Constraints

```bash

# 1. Verify that Root Filesystem is Immutable (Read-Only)
docker exec zero-trust-web touch /test_file && echo "FAIL: Root is writeable!" || echo "SUCCESS: Root filesystem is read-only!"

# 2. Verify that Linux Capabilities are Stripped (Only CAP_NET_BIND_SERVICE remains)
docker inspect zero-trust-web --format 'CapDrop: {{json .HostConfig.CapDrop}} | CapAdd: {{json .HostConfig.CapAdd}}'

# 3. Verify no-new-privileges is Active
docker inspect zero-trust-web --format 'SecurityOpt: {{json .HostConfig.SecurityOpt}}'
```

---

## 10. Pure CLI / Command Interface

### 1. Execute Vulnerability CVE Scan with Docker Scout

Inspect critical security advisories on target images:

```bash
docker scout cves \
    --only-severity critical,high \
    nginx:alpine
```

### 2. Audit Container System Calls and Seccomp Profile

Verify attached Seccomp filter status:

```bash
docker inspect zero-trust-web \
    --format 'Seccomp Profile: {{.HostConfig.SecurityOpt}}'
```

### 3. Run CIS Docker Security Benchmark Audit

Execute automated security benchmark scanner against host:

```bash
docker run \
    --rm \
    --net host \
    --pid host \
    --userns host \
    --cap-add audit_control \
    -v /etc:/etc:ro \
    -v /var/lib:/var/lib:ro \
    -v /var/run/docker.sock:/var/run/docker.sock:ro \
    docker/docker-bench-security
```

---

## 11. Advanced Architecture & Edge-Case Failure Modes

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                    SECURITY FAILURE RECOVERY MATRIX                            │
├──────────────────────┬────────────────────────┬────────────────────────────────┤
│ Failure Scenario     │ Underlying Root Cause  │ Production Mitigation Runbook  │
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **App Crash on**     │ Application writes to  │ Mount `--tmpfs /path:rw,noexec`│
│ **`--read-only`**    │ hardcoded directory.   │ for the required scratch path. │
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **Port Binding Fail**│ App needs port 80 but  │ Add `--cap-add NET_BIND_SERVICE`│
│ **after Cap Drop**   │ lacks capability.      │ or bind port $> 1024$.         │
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **Syscall Blocked**  │ Custom syscall blocked │ Create custom Seccomp JSON     │
│ **by Seccomp**       │ by default profile.    │ profile allowing required call.│
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **Rootless Socket**  │ Client connecting to   │ Set `DOCKER_HOST=unix:///run/  │
│ **Not Found Error**  │ root socket path.      │ user/1000/docker.sock`.        │
└──────────────────────┴────────────────────────┴────────────────────────────────┘
```

---

## 12. Detailed Sub-Components & Subsystems

### 1. Seccomp BPF JIT Compiler

* **Key Concepts**: Compiles Seccomp JSON rules into Berkeley Packet Filter bytecode executed in the kernel entry path on every system call.
* **CLI / Tool Snippet**:

```bash
docker info --format '{{.SecurityOptions}}'
```

### 2. AppArmor LSM Enforcer

* **Key Concepts**: Linux Security Module enforcing path-based mandatory access control profiles (`docker-default`) on file read/write operations.
* **CLI / Tool Snippet**:

```bash
aa-status 2>/dev/null || true
```

### 3. Cosign OCI Signature Verifier

* **Key Concepts**: Cryptographic signature validation engine verifying ECDSA / Ed25519 signatures stored as OCI artifacts in container registries.
* **CLI / Tool Snippet**:

```bash
cosign version 2>/dev/null || true
```

### 4. User Namespace Remapper Subsystem

* **Key Concepts**: Coordinates `/etc/subuid` and `/etc/subgid` allocations, configuring kernel UID/GID offset translation tables for container scopes.
* **CLI / Tool Snippet**:

```bash
cat /etc/subuid 2>/dev/null || true
```

---

## 13. References (The 5+5 Rule)

### Official Documentation & Security Standards

1. [Docker Official Documentation: Engine Security Guidelines](https://docs.docker.com/engine/security/)
2. [Center for Internet Security (CIS): Docker Benchmark v1.6.0](https://www.cisecurity.org/benchmark/docker)
3. [NIST SP 800-190: Application Container Security Guide](https://csrc.nist.gov/publications/detail/sp/800-190/final)
4. [Linux Kernel Organization: Seccomp BPF System Call Filtering](https://docs.kernel.org/userspace-api/seccomp_filter.html)
5. [Sigstore Cosign: Container Signing, Verification and Storage](https://docs.sigstore.dev/cosign/overview/)

### Authoritative Engineering Blogs & Architecture Deep Dives

1. [Liz Rice: Container Security: Fundamental Technology of Containers (O'Reilly)](https://www.lizrice.com/)
2. [Julia Evans: How Seccomp Filters System Calls in Linux Containers](https://jvns.ca/)
3. [Brendan Gregg: Linux Security Auditing and BPF Kernel Monitoring](https://www.brendangregg.com/)
4. [Martin Fowler: Continuous Security and Software Supply Chain Integrity](https://martinfowler.com/)
5. [High-Performance Linux Systems: Hardening Linux Namespaces and User IDs](https://www.kernel.org/)

---

## 14. Universal FinOps & Resource Cost Governance

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                      SECURITY FINOPS SAVINGS MATRIX                            │
├──────────────────────────┬──────────────────────────┬──────────────────────────┤
│ Optimization Strategy    │ Technical Mechanism      │ Measurable FinOps ROI    │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **Zero-Trust Hardening** │ Blocks container escape  │ Prevents \$4M+ enterprise│
│                          │ lateral host breaches    │ breach liability & fines │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **Distroless Base**      │ Eliminates 95% of CVEs   │ Saves 800+ hours of team │
│                          │ needing emergency patches│ emergency patching labor │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **Automated SBOM/Scan**  │ Catches CVEs at build    │ Eliminates expensive 3rd-│
│                          │ in CI/CD pipeline        │ party runtime WAF costs  │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **Rootless Multi-Tenant**| Runs multi-tenant apps   │ Cuts dedicated cluster VM│
│                          │ safely on shared nodes   │ infrastructure by 60%    │
└──────────────────────────┴──────────────────────────┴──────────────────────────┘
```

### 1. Automated Supply Chain Security vs Incident Response Economics

In enterprise engineering organizations:

* Remediating a production zero-day container compromise (e.g. crypto-miner or data exfiltration via container escape) costs an average of **\$150,000 in emergency forensics, engineering overtime, and lost revenue**.
* Enforcing non-root execution (`USER 10001:10001`), `--cap-drop ALL`, and automated CI/CD CVE gating (`docker scout`) completely neutralizes 99% of automated container exploit payloads.
* **FinOps ROI**: Delivers **hundreds of thousands of dollars in risk mitigation value** with zero additional software licensing costs.

### 2. Distroless Image Patching Labor Reduction

When operating 200 production containers built on standard Ubuntu base images:

* Security scanners report ~80 CVE vulnerabilities per image monthly across unused packages (curl, tar, perl, apt), requiring security teams to review and patch 16,000 monthly CVE alerts ($~20\text{ engineering hours/month}$).
* Migrating to **Distroless** base images reduces reported CVEs to **near zero**, saving **\$36,000/year in wasted engineering triage labor**.
