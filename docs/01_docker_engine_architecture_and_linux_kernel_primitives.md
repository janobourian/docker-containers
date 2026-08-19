# Module 02: Docker Engine Architecture & Linux Kernel Primitives

**Track:** Docker Container Systems & Virtualization Architecture
**Category:** Container Runtime, Linux Kernel Primitives, Namespaces & Cgroups v2
**Standard Identifier:** `DOC-STD-UNIVERSAL-2026`
**Status:** ✅ Completed

---

## 📑 Table of Contents

1. [High-Level Overview & Executive Summary](#1-high-level-overview--executive-summary)

2. [The Complete Docker Engine Subsystem Topology](#2-the-complete-docker-engine-subsystem-topology)

3. [Linux Kernel Namespaces: The 8 Isolation Dimensions](#3-linux-kernel-namespaces-the-8-isolation-dimensions)

4. [Control Groups (cgroups v2): Unified Resource Governance](#4-control-groups-cgroups-v2-unified-resource-governance)

5. [OverlayFS Storage Driver: Layers, Copy-up & Whiteouts](#5-overlayfs-storage-driver-layers-copy-up--whiteouts)

6. [Certification & Exam Essentials (Cheat Sheet)](#6-certification--exam-essentials-cheat-sheet)

7. [Comparative Analysis Matrix: Container Runtimes](#7-comparative-analysis-matrix-container-runtimes)

8. [Performance & Resource Optimization](#8-performance--resource-optimization)

9. [Step-by-Step Hands-On Production Walkthrough](#9-step-by-step-hands-on-production-walkthrough)

10. [Pure CLI / Command Interface](#10-pure-cli--command-interface)

11. [Advanced Architecture & Edge-Case Failure Modes](#11-advanced-architecture--edge-case-failure-modes)

12. [Detailed Sub-Components & Subsystems](#12-detailed-sub-components--subsystems)

13. [References (The 5+5 Rule)](#13-references-the-55-rule)

14. [Universal FinOps & Resource Cost Governance](#14-universal-finops--resource-cost-governance)

---

## 1. High-Level Overview & Executive Summary

The **Docker Engine** is the core client-server software suite responsible for creating, running, and managing containerized applications. Rather than functioning as a monolithic virtualization hypervisor, the Docker Engine coordinates an ecosystem of specialized components—the Docker CLI, the `dockerd` management daemon, the CNCF-certified **`containerd`** runtime, the decoupled **`containerd-shim`**, and the Open Container Initiative (OCI) reference runtime **`runc`**. Together, these components translate high-level container management APIs into direct Linux kernel syscalls (`clone()`, `unshare()`, `setns()`, `pivot_root()`).

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│               THE COMPLETE DOCKER ENGINE COMPONENT TOPOLOGY                    │
├────────────────────────────────────────────────────────────────────────────────┤
│ [User / Automation / CI/CD] ──► `docker run`                                   │
│         │                                                                      │
│         ▼ (REST API / JSON over UNIX Socket: `/var/run/docker.sock`)           │
│ ┌────────────────────────────────────────────────────────────────────────────┐ │
│ │ DOCKER DAEMON (`dockerd`): Image management, network orchestration, auth   │ │
│ └──────────────────────────────┬─────────────────────────────────────────────┘ │
│                                │ (gRPC over `/run/containerd/containerd.sock`) │
│                                ▼                                               │
│ ┌────────────────────────────────────────────────────────────────────────────┐ │
│ │ CONTAINERD (High-Level Runtime): Snapshot management, content store        │ │
│ └──────────────────────────────┬─────────────────────────────────────────────┘ │
│                                │ (Fork / Exec)                                 │
│                                ▼                                               │
│ ┌────────────────────────────────────────────────────────────────────────────┐ │
│ │ CONTAINERD-SHIM: Parent proxy per container (Decouples container from daemon)│
│ └──────────────────────────────┬─────────────────────────────────────────────┘ │
│                                │ (Executes OCI CLI specification)              │
│                                ▼                                               │
│ ┌────────────────────────────────────────────────────────────────────────────┐ │
│ │ RUNC (Low-Level OCI Runtime): Invokes Linux kernel isolation syscalls      │ │
│ └──────────────────────────────┬─────────────────────────────────────────────┘ │
│                                │                                               │
│                                ▼                                               │
│ ┌────────────────────────────────────────────────────────────────────────────┐ │
│ │ LINUX KERNEL ISOLATION SUBSYSTEMS:                                         │ │
│ │ - 8 Namespaces (PID, NET, MNT, IPC, UTS, USER, CGROUP, TIME)               │ │
│ │ - Control Groups v2 (CPU, Memory, I/O, PIDs throttling)                    │ │
│ │ - Storage OverlayFS (lowerdir, upperdir, merged)                           │ │
│ │ - Security (Seccomp syscall filter, AppArmor/SELinux mandatory access)     │ │
│ └────────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 👔 Executive Summary (For Managers & Non-Technical Stakeholders)

* **Business Purpose**: Provides the foundational engine that powers modern cloud computing, microservices, and AI inference workloads by running isolated applications at near-zero operating system overhead.
* **How It Works**: Operates as a high-speed traffic controller for the Linux operating system. It carves the server's CPU, RAM, and disk storage into hundreds of secure, isolated execution bubbles without requiring multiple virtual machine licenses.
* **Key Business Value & ROI**: Maximizes server compute utilization (saving millions in enterprise hardware costs), eliminates server restart downtime via daemonless live-restores, and enforces strict security fences between multi-tenant workloads.

---

## 2. The Complete Docker Engine Subsystem Topology

### 2.1 The Container Lifecycle Execution Flow

When a user executes `docker run -d --name web nginx`:

1. **Docker CLI**: Translates the CLI flags into an HTTP `POST /containers/create` REST payload and sends it over `/var/run/docker.sock`.
2. **`dockerd`**: Authenticates the request, pulls missing image layers from the registry, configures container networks (e.g. `bridge`), and dispatches a gRPC `CreateContainer` call to `containerd`.
3. **`containerd`**: Mounts the image's OverlayFS root filesystem, creates an OCI `config.json` bundle, and spawns a **`containerd-shim`** process.
4. **`containerd-shim`**: Invokes the **`runc`** binary with the OCI bundle.
5. **`runc`**: Clones new Linux namespaces, creates cgroup directories under `/sys/fs/cgroup/`, sets memory/CPU limits, pivots the root filesystem (`pivot_root()`), applies Seccomp syscall filters, executes the container entrypoint (NGINX), and immediately exits cleanly.
6. **Decoupled Execution**: The container process is now a direct child of `containerd-shim`, allowing `dockerd` to be restarted or upgraded without interrupting the running container.

---

## 3. Linux Kernel Namespaces: The 8 Isolation Dimensions

Namespaces wrap global system resources in an isolated abstraction, ensuring processes inside a container only see their own private environment:

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                   THE 8 LINUX KERNEL NAMESPACE SUBSYSTEMS                      │
├───────────────────┬───────────────────┬────────────────────────────────────────┤
│ Namespace Flag    │ Isolated Resource │ Production Significance                │
├───────────────────┼───────────────────┼────────────────────────────────────────┤
│ **`CLONE_NEWPID`**│ Process IDs (PIDs)│ Container process is PID 1; cannot see │
│                   │                   │ or signal host processes.              │
├───────────────────┼───────────────────┼────────────────────────────────────────┤
│ **`CLONE_NEWNET`**│ Network Stacks    │ Private loopback (`lo`), `eth0`, IP,   │
│                   │                   │ routing tables, and port bindings.     │
├───────────────────┼───────────────────┼────────────────────────────────────────┤
│ **`CLONE_NEWNS`** │ Mount Points (MNT)│ Private filesystem mount table; mounts │
│                   │                   │ inside container do not affect host.   │
├───────────────────┼───────────────────┼────────────────────────────────────────┤
│ **`CLONE_NEWIPC`**│ Inter-Process Comm│ Isolates System V IPC and POSIX message│
│                   │                   │ queues / shared memory segments.       │
├───────────────────┼───────────────────┼────────────────────────────────────────┤
│ **`CLONE_NEWUTS`**│ Hostnames / Domain│ Container sets its own hostname without│
│                   │                   │ altering host server hostname.         │
├───────────────────┼───────────────────┼────────────────────────────────────────┤
│ **`CLONE_NEWUSER`**| User / Group IDs │ Container `root` (UID 0) is mapped to  │
│                   │                   │ an unprivileged user (UID 10001) on host│
├───────────────────┼───────────────────┼────────────────────────────────────────┤
│ **`CLONE_NEWCGROUP`**| Cgroup Root    │ Restricts container from viewing host  │
│                   │                   │ cgroup hierarchy structure.            │
├───────────────────┼───────────────────┼────────────────────────────────────────┤
│ **`CLONE_NEWTIME`**| System Clocks    │ Container can offset monotonic clocks  │
│                   │                   │ without changing host system time.     │
└───────────────────┴───────────────────┴────────────────────────────────────────┘
```

---

## 4. Control Groups (cgroups v2): Unified Resource Governance

While Namespaces govern *what a process can see*, **Control Groups (cgroups)** govern *how much server resources a process can consume*.

### 4.1 cgroups v1 vs cgroups v2 Architecture

* **Legacy cgroups v1**: Multi-hierarchy model where CPU, Memory, and BlkIO lived in separate directory trees (`/sys/fs/cgroup/cpu`, `/sys/fs/cgroup/memory`), making coordinated throttling and memory-buffered writeback attribution mathematically impossible.
* **Modern cgroups v2**: **Unified single hierarchy** rooted at `/sys/fs/cgroup/`. Every container is a sub-directory inheriting rules from parent controllers.

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                      CGROUPS V2 UNIFIED CONTROLLER TREE                        │
├────────────────────────────────────────────────────────────────────────────────┤
│ `/sys/fs/cgroup/` (Root)                                                       │
│ └── `docker.slice/`                                                            │
│     └── `docker-<container_id>.scope/`                                         │
│         ├── `cgroup.procs`         ──► [List of Container Process PIDs]        │
│         ├── `cpu.max`              ──► "50000 100000" (50% of 1 CPU Core)      │
│         ├── `memory.max`           ──► "536870912" (512 MB Hard Limit)         │
│         ├── `memory.high`          ──► "469762048" (448 MB Soft Throttle Thresh)│
│         ├── `memory.oom.group`     ──► "1" (Kills entire container if OOMed)   │
│         ├── `pids.max`             ──► "100" (Fork-bomb limit)                 │
│         └── `io.max`               ──► "8:0 rbps=10485760 wbps=10485760"       │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. OverlayFS Storage Driver: Layers, Copy-up & Whiteouts

Docker uses the **OverlayFS** union filesystem driver to merge immutable read-only image layers with an ephemeral writable container layer into a unified directory tree.

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                     OVERLAYFS DIRECTORY MOUNT STRUCTURE                        │
├────────────────────────────────────────────────────────────────────────────────┤
│ [Unified Virtual Container Mount: `merged/`]  (What container process sees)    │
│        ▲                                                                       │
│        │ (Union Mount)                                                         │
│ ┌──────┴─────────────────────────────────────────────────────────────────────┐ │
│ │ WRITABLE CONTAINER LAYER: `upperdir/`                                      │ │
│ │ - New files created inside container                                       │ │
│ │ - Modified files copied up from lower layers (Copy-Up on Write)            │ │
│ │ - Deletion whiteout markers (`c 0 0` character devices)                    │ │
│ ├────────────────────────────────────────────────────────────────────────────┤ │
│ │ OVERLAYFS WORKING DIRECTORY: `workdir/` (Atomic transaction buffer)        │ │
│ ├────────────────────────────────────────────────────────────────────────────┤ │
│ │ READ-ONLY IMAGE LAYER 2: `lowerdir/layer_2` (App binaries & configs)       │ │
│ ├────────────────────────────────────────────────────────────────────────────┤ │
│ │ READ-ONLY IMAGE LAYER 1: `lowerdir/layer_1` (Base OS packages - Alpine)    │ │
│ └────────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 5.1 Copy-Up on Write & Whiteout Deletion Mechanics

1. **Copy-Up on Write**: When a container mutates an existing file originating from an image layer, OverlayFS physically copies the entire file from `lowerdir` to `upperdir` before executing the write. Modifying a 10GB database file inside an image layer copies the entire 10GB to `upperdir`, causing severe write latency! (Use Volumes for databases).
2. **Whiteout Files**: When a file from `lowerdir` is deleted inside the container, OverlayFS creates a **character device with major:minor number 0:0** in `upperdir`. The merged view masks the file, making it appear deleted.

---

## 6. Certification & Exam Essentials (Cheat Sheet)

* ⚠️ **Live Restore (`"live-restore": true`)**: By default, stopping or updating the Docker daemon terminates all running containers. Adding `"live-restore": true` to `/etc/docker/daemon.json` allows containers to remain running during daemon restarts.
* 🔒 **Docker Socket Privilege Escalation**: Granting a user access to `/var/run/docker.sock` is **equivalent to granting passwordless host root access** (`docker run -v /:/host -it alpine chroot /host`). Never expose the Docker UNIX socket inside unprivileged containers!
* ⚙️ **The OOM Killer (`Exit Code 137`)**: When a container consumes more memory than `memory.max`, the Linux kernel Out-Of-Memory (OOM) killer terminates the process with `SIGKILL` (Signal 9). Exit code is calculated as $128 + 9 = 137$.
* ⚠️ **User Namespace Remapping (`userns-remap`)**: Maps container UID 0 (root) to an unprivileged host UID range (e.g. 100000–165535). If a process escapes the container, it holds zero root privileges on the host system.

---

## 7. Comparative Analysis Matrix: Container Runtimes

| Feature | Docker Engine (dockerd) | containerd | CRI-O | Podman |
| :--- | :--- | :--- | :--- | :--- |
| **Architecture** | Client-Server (Daemon) | Daemon (gRPC) | Daemon (CRI API) | **Daemonless (Fork/Exec)** |
| **Kubernetes CRI** | Deprecated (via dockershim) | **Native CNCF Standard** | **Native Lightweight** | No (Focuses on pods) |
| **Rootless Execution** | Supported (Rootless mode) | Supported | Supported | **Native Default** |
| **Build Capabilities** | Integrated BuildKit | Basic (via plugins) | None (Buildah) | Built-in |
| **Primary Use Case** | Local Dev & Single-Node | Kubernetes Node Runtime | Dedicated K8s Nodes | Rootless Dev & RHEL |

---

## 8. Performance & Resource Optimization

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                      ENGINE KERNEL TUNING PLAYBOOK                             │
├────────────────────────────────────────────────────────────────────────────────┤
│ 1. Switch to cgroups v2 (`systemd.unified_cgroup_hierarchy=1`) on host kernel. │
│ 2. Disable `userland-proxy` in `daemon.json` to route via high-speed iptables. │
│ 3. Mount high-I/O directories (databases, logs) via dedicated Docker Volumes   │
│    to bypass OverlayFS copy-up write penalties.                                │
│ 4. Increase host `max_user_watches` and `fs.file-max` for 500+ container nodes.│
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Step-by-Step Hands-On Production Walkthrough

### Step 1: Configure Hardened Production Docker Daemon

```json
// /etc/docker/daemon.json
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "25m",
    "max-file": "4"
  },
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true,
  "cgroup-parent": "docker.slice",
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 65535,
      "Soft": 65535
    }
  }
}
```

---

### Step 2: Launch Resource-Bounded Secure Container

```bash
docker run \
    --detach \
    --name enterprise-api \
    --publish 9000:9000 \
    --memory 512m \
    --memory-reservation 256m \
    --cpus 1.5 \
    --pids-limit 100 \
    --restart unless-stopped \
    --cap-drop ALL \
    --cap-add NET_BIND_SERVICE \
    --security-opt no-new-privileges:true \
    alpine:latest \
    sleep 3600
```

---

### Step 3: Inspect Kernel Namespaces and Cgroups v2 on Host

```bash

# 1. Obtain Host Process PID of the Running Container
CONTAINER_PID=$(docker inspect --format '{{.State.Pid}}' enterprise-api)
echo "Container Host PID: ${CONTAINER_PID}"

# 2. Inspect Linux Kernel Namespaces Assigned to this PID
ls -la /proc/${CONTAINER_PID}/ns

# 3. Inspect Active Cgroups v2 Controller Allocations
cat /proc/${CONTAINER_PID}/cgroup

# 4. View Exact CPU and Memory Limits Enforced by Cgroup Controller
cat /sys/fs/cgroup/docker.slice/docker-$(docker inspect --format '{{.Id}}' enterprise-api).scope/memory.max
cat /sys/fs/cgroup/docker.slice/docker-$(docker inspect --format '{{.Id}}' enterprise-api).scope/cpu.max
```

---

## 10. Pure CLI / Command Interface

### 1. Inspect Low-Level OCI Container State via Docker Inspect

Extract exact cgroup limits, PID numbers, and IP configurations:

```bash
docker inspect \
    --format 'PID: {{.State.Pid}} | IP: {{.NetworkSettings.IPAddress}} | Mem: {{.HostConfig.Memory}}' \
    enterprise-api
```

### 2. Monitor Container Daemon Resource Utilization

Stream real-time CPU, RAM, Network, and Block I/O statistics:

```bash
docker stats \
    --no-stream \
    --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
```

### 3. Check Docker Daemon Host Storage Driver Status

Verify OverlayFS backing filesystem and cgroup version:

```bash
docker info \
    --format 'Storage Driver: {{.Driver}} | Cgroup Version: {{.CgroupVersion}} | Live Restore: {{.LiveRestoreEnabled}}'
```

---

## 11. Advanced Architecture & Edge-Case Failure Modes

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                    ENGINE FAILURE RECOVERY RUNBOOK MATRIX                      │
├──────────────────────┬────────────────────────┬────────────────────────────────┤
│ Failure Scenario     │ Underlying Root Cause  │ Production Mitigation Runbook  │
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **OverlayFS Inode**  │ Millions of tiny files │ Run `docker system prune` or   │
│ **Exhaustion**       │ exhaust filesystem inodes| format host with `-N` inodes. │
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **cgroups v1 BlkIO** │ Memory-buffered writes │ Upgrade host to cgroups v2     │
│ **Throttling Leak**  │ bypass v1 blkio control| unified hierarchy.            │
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **Fork Bomb Host**   │ Rogue container spawns │ Enforce `--pids-limit 100` on   │
│ **Starvation**       │ 100,000 child procs.   │ all production containers.     │
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **Zombie PID 1**     │ Container process dies │ Launch container with `--init` │
│ **Reaping Leak**     │ without child reaping. │ to inject Tini reaper daemon.  │
└──────────────────────┴────────────────────────┴────────────────────────────────┘
```

---

## 12. Detailed Sub-Components & Subsystems

### 1. containerd Content Store

* **Key Concepts**: Content-addressable blob store tracking immutable OCI layer tarballs by SHA-256 digest in `/var/lib/containerd/io.containerd.content.v1.content/`.
* **CLI / Tool Snippet**:

```bash
ctr --namespace moby content list
```

### 2. runc Syscall Translator

* **Key Concepts**: Unpacks OCI `config.json` specifications, executes Linux kernel `clone()` with namespace bitmasks, and mounts `cgroups`.
* **CLI / Tool Snippet**:

```bash
runc list
```

### 3. Seccomp Syscall Filter Engine

* **Key Concepts**: Berkeley Packet Filter (BPF) sandbox blocking over 40 dangerous Linux syscalls (e.g. `reboot`, `sys_ptrace`, `kexec_load`) from being invoked inside containers.
* **CLI / Tool Snippet**:

```bash
docker info --format '{{.SecurityOptions}}'
```

### 4. containerd-shim Process Supervisor

* **Key Concepts**: Lightweight daemonless proxy process holding POSIX file descriptors and pseudo-terminals (pty) for running containers.
* **CLI / Tool Snippet**:

```bash
pstree -p $(pgrep containerd)
```

---

## 13. References (The 5+5 Rule)

### Official Documentation & OCI Specifications

1. [Docker Official Documentation: Docker Engine Architecture](https://docs.docker.com/engine/)
2. [Open Container Initiative (OCI): Runtime Specification](https://opencontainers.org/specs/runtime/)
3. [containerd Official Architecture & Design Guide](https://containerd.io/docs/)
4. [Linux Kernel Documentation: Control Groups v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)
5. [Linux Kernel Documentation: Namespaces Overview (man 7 namespaces)](https://man7.org/linux/man-pages/man7/namespaces.7.html)

### Authoritative Engineering Blogs & Architecture Deep Dives

1. [Julia Evans: What Happens When You Run a Container? Namespaces and Cgroups](https://jvns.ca/)
2. [Brendan Gregg: Linux Cgroups Performance & Throttling Metrics](https://www.brendangregg.com/)
3. [Liz Rice: Container Security: Fundamental Technology of Containers](https://www.oreilly.com/library/view/container-security/9781492056690/)
4. [Martin Fowler: Microservices and Container Process Isolation](https://martinfowler.com/)
5. [High-Performance Linux Systems: OverlayFS Internals & Inode Management](https://www.kernel.org/doc/html/latest/filesystems/overlayfs.html)

---

## 14. Universal FinOps & Resource Cost Governance

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                      ENGINE FINOPS SAVINGS MATRIX                              │
├──────────────────────────┬──────────────────────────┬──────────────────────────┤
│ Optimization Strategy    │ Technical Mechanism      │ Measurable FinOps ROI    │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **Live Restore**         │ Eliminates maintenance   │ Prevents SLA violation   │
│                          │ container restarts       │ customer penalty fees    │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **cgroups v2 Quotas**    │ Restricts container CPU  │ Prevents runaway queries │
│                          │ & RAM usage precisely    │ from forcing node scale  │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **Direct Volumes**       │ Bypasses OverlayFS       │ Cuts SSD IOPS write tax  │
│                          │ copy-up write penalty    │ fees on cloud storage    │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **Disable Userland Proxy**| Routes via kernel NAT   │ Cuts network latency &   │
│                          │ without userland process │ reduces CPU usage by 15% │
└──────────────────────────┴──────────────────────────┴──────────────────────────┘
```

### 1. OverlayFS Copy-Up Elimination on High-Throughput Databases

Running a high-write database (PostgreSQL, MySQL, Redis) directly on a container's root OverlayFS filesystem causes the engine to copy existing multi-gigabyte data files from `lowerdir` to `upperdir` during writes:

* Generates **$300\times$ write amplification**, saturating cloud SSD provisioned IOPS limits and causing severe database write freezes.
* Attaching a dedicated **Docker Volume** (`-v db_data:/var/lib/postgresql/data`) bypasses OverlayFS, mounting directly to the host filesystem at native NVMe speeds.
* **FinOps ROI**: Eliminates the need to purchase 10,000 Provisioned IOPS on cloud EBS volumes (saving **\$650/month per database node**).

### 2. Disabling `userland-proxy` Compute Savings

By default, Docker spawns a userland proxy process (`docker-proxy`) for every published port to forward traffic between the host and container.

* On a large multi-tenant gateway server running 500 containers with 2,000 published ports, `docker-proxy` allocates **2,000 background processes**, consuming **~4GB of RAM** and significant CPU overhead during network bursts.
* Setting `"userland-proxy": false` in `/etc/docker/daemon.json` routes all traffic directly through native Linux kernel `iptables` / `nftables` connection tracking.
* Memory consumption drops by **4 Gigabytes**, and network throughput latency improves by **18%**.
