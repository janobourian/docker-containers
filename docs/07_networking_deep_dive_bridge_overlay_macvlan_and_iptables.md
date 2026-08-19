# Module 08: Docker Networking Architecture, CNM & Service Discovery

**Track:** Docker Container Systems & Virtualization Architecture
**Category:** Container Networking, Container Network Model (CNM), Bridge, Overlay & DNS
**Standard Identifier:** `DOC-STD-UNIVERSAL-2026`
**Status:** ✅ Completed

---

## 📑 Table of Contents

1. [High-Level Overview & Executive Summary](#1-high-level-overview--executive-summary)

2. [The Container Network Model (CNM) & Libnetwork Architecture](#2-the-container-network-model-cnm--libnetwork-architecture)

3. [Network Driver Typology: Bridge, Host, Overlay, Macvlan & None](#3-network-driver-typology-bridge-host-overlay-macvlan--none)

4. [Embedded DNS Engine (`127.0.0.11`) & Service Discovery](#4-embedded-dns-engine-1270011--service-discovery)

5. [Linux Kernel Networking: veth Pairs, Bridges & Iptables NAT](#5-linux-kernel-networking-veth-pairs-bridges--iptables-nat)

6. [Certification & Exam Essentials (Cheat Sheet)](#6-certification--exam-essentials-cheat-sheet)

7. [Comparative Analysis Matrix: Docker Network Drivers](#7-comparative-analysis-matrix-docker-network-drivers)

8. [Performance & Resource Optimization](#8-performance--resource-optimization)

9. [Step-by-Step Hands-On Production Walkthrough](#9-step-by-step-hands-on-production-walkthrough)

10. [Pure CLI / Command Interface](#10-pure-cli--command-interface)

11. [Advanced Architecture & Edge-Case Failure Modes](#11-advanced-architecture--edge-case-failure-modes)

12. [Detailed Sub-Components & Subsystems](#12-detailed-sub-components--subsystems)

13. [References (The 5+5 Rule)](#13-references-the-55-rule)

14. [Universal FinOps & Resource Cost Governance](#14-universal-finops--resource-cost-governance)

---

## 1. High-Level Overview & Executive Summary

Docker networking provides the communication fabric connecting containers to each other, to the host operating system, and to external networks. Rather than implementing ad-hoc network scripts, Docker implements the **Container Network Model (CNM)** via the **`libnetwork`** engine. The CNM abstracts network connectivity into three fundamental primitives—**Sandboxes** (isolated network namespaces), **Endpoints** (virtual network interfaces), and **Networks** (isolated communication domains).

Docker supports five distinct network drivers: **Bridge** (single-host private network with built-in DNS service discovery), **Host** (attaches directly to the host network stack, eliminating NAT overhead), **Overlay** (multi-host VXLAN tunnel encapsulation for distributed clusters), **Macvlan / Ipvlan** (assigns physical LAN IP/MAC addresses directly to container interfaces), and **None** (completely air-gapped container loopback isolation).

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│               DOCKER BRIDGE NETWORK & VETH PAIR ARCHITECTURE                   │
├────────────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────┐        ┌──────────────────────────────┐       │
│ │ CONTAINER 1 (`172.20.0.2`)   │        │ CONTAINER 2 (`172.20.0.3`)   │       │
│ │ - Network Namespace (Sandbox)│        │ - Network Namespace (Sandbox)│       │
│ │ - Interface: `eth0`          │        │ - Interface: `eth0`          │       │
│ └──────────────┬───────────────┘        └──────────────┬───────────────┘       │
│                │                                       │                       │
│                │ (veth pair tunnel)                    │ (veth pair tunnel)    │
│                ▼                                       ▼                       │
│ ┌────────────────────────────────────────────────────────────────────────────┐ │
│ │ HOST LINUX KERNEL SOFTWARE BRIDGE: `br-custom` (`172.20.0.1/16`)          │ │
│ │ - Layer 2 Ethernet Packet Switching between Containers                     │ │
│ │ - Embedded DNS Resolver: `127.0.0.11:53` (Translates Names to IPs)         │ │
│ └──────────────────────────────┬─────────────────────────────────────────────┘ │
│                                │                                               │
│                                ▼ (iptables MASQUERADE / NAT)                   │
│ ┌────────────────────────────────────────────────────────────────────────────┐ │
│ │ PHYSICAL HOST NETWORK INTERFACE: `eth0` (`192.168.1.100`) ──► [INTERNET]   │ │
│ └────────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 👔 Executive Summary (For Managers & Non-Technical Stakeholders)

* **Business Purpose**: Enables distributed application components (web storefronts, payment gateways, databases) to communicate securely over private virtual networks while defending sensitive data against external internet intruders.
* **How It Works**: Creates isolated software networks inside the host server. Containers locate each other automatically by name (e.g. `payment-api` connects directly to `postgres-db`), while external firewalls strictly block public access to internal database ports.
* **Key Business Value & ROI**: Delivers zero-trust network micro-segmentation, prevents lateral network movement during security incidents, and eliminates the complexity of configuring manual hardware switches and routers.

---

## 2. The Container Network Model (CNM) & Libnetwork Architecture

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                   THE THREE PILLARS OF THE CNM SPECIFICATION                   │
├────────────────────────────────────────────────────────────────────────────────┤
│ 1. SANDBOX: An isolated network stack containing container interfaces,         │
│    routing tables, and DNS configuration. (Implemented as Linux `netns`).      │
├────────────────────────────────────────────────────────────────────────────────┤
│ 2. ENDPOINT: A virtual network interface connecting a Sandbox to a Network.    │
│    (Implemented as one end of a virtual ethernet `veth` pair).                 │
├────────────────────────────────────────────────────────────────────────────────┤
│ 3. NETWORK: A collection of interconnected Endpoints able to communicate       │
│    at Layer 2 or Layer 3. (Implemented as a Linux bridge, VLAN, or VXLAN).    │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Network Driver Typology: Bridge, Host, Overlay, Macvlan & None

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                     DOCKER NETWORK DRIVERS BREAKDOWN                           │
├───────────────────┬───────────────────┬────────────────────────────────────────┤
│ Network Driver    │ Scope             │ Production Significance                │
├───────────────────┼───────────────────┼────────────────────────────────────────┤
│ **Bridge**        │ Single Host       │ Default user-defined network; provides │
│ (Recommended)     │                   │ automatic DNS name resolution & NAT.   │
├───────────────────┼───────────────────┼────────────────────────────────────────┤
│ **Host**          │ Single Host       │ Bypasses network isolation; shares host│
│ (Max Performance) │                   │ IP/ports directly (0% NAT overhead!).  │
├───────────────────┼───────────────────┼────────────────────────────────────────┤
│ **Overlay**       │ Multi-Host        │ VXLAN packet encapsulation (UDP 4789)  │
│ (Distributed)     │ (Cluster)         │ connecting Swarm / multi-node nodes.   │
├───────────────────┼───────────────────┼────────────────────────────────────────┤
│ **Macvlan**       │ Single / Multi    │ Assigns physical MAC & LAN IP directly │
│ (Legacy Telecom)  │                   │ to container (Underlay network mode).  │
├───────────────────┼───────────────────┼────────────────────────────────────────┤
│ **None**          │ Isolated Host     │ Disables all networking except loopback│
│ (Air-Gapped)      │                   │ (`127.0.0.1`) for air-gapped security. │
└───────────────────┴───────────────────┴────────────────────────────────────────┘
```

---

## 4. Embedded DNS Engine (`127.0.0.11`) & Service Discovery

In **User-Defined Bridge Networks**, Docker runs an embedded DNS server at IP **`127.0.0.11:53`** inside every container's network namespace:

1. When an application resolves `http://database:5432`, the container sends a DNS query to `127.0.0.11`.
2. The embedded DNS resolver looks up the internal container catalog, returning the private IP address of the `database` container.
3. If the query is an external domain (e.g. `api.stripe.com`), the embedded DNS forwards the request to the upstream DNS nameservers configured on the host (`/etc/resolv.conf`).
4. ⚠️ **The Default Bridge Trap**: The legacy default `bridge` network (`docker0`) does **NOT** support embedded DNS resolution! Containers on `docker0` can only reach each other via IP address or deprecated `--link` flags. Always create custom user-defined networks!

---

## 5. Linux Kernel Networking: veth Pairs, Bridges & Iptables NAT

### 5.1 Port Forwarding & Destination NAT (DNAT)

When a container publishes a port (`-p 8080:80`):

1. Docker adds an `iptables` rule in the `PREROUTING` chain of the `nat` table:
   `-A DOCKER -p tcp -m tcp --dport 8080 -j DNAT --to-destination 172.20.0.2:80`

2. External packets hitting host port 8080 have their destination IP rewritten to the container's private IP (`172.20.0.2:80`).
3. Outbound packets originating from the container have their source IP rewritten to the host's physical IP using **Source NAT (SNAT / MASQUERADE)**.

---

## 6. Certification & Exam Essentials (Cheat Sheet)

* ⚠️ **Default Bridge vs User-Defined Bridge**:
  * Default `bridge` (`docker0`): No automatic DNS name resolution; requires hardcoded IPs.
  * User-Defined Bridge (`docker network create`): **Built-in automatic DNS resolution**, fine-grained network micro-segmentation, and dynamic connect/disconnect support.
* 🔒 **Internal Network Security (`--internal`)**: Creating a network with `docker network create --internal secure-net` isolates containers completely from the outside world: containers can talk to each other, but **cannot route traffic to or from the internet**.
* ⚙️ **Overlay Network Ports (Firewall Requirements)**: For Docker Swarm Overlay networks across multiple servers, ensure these 3 ports are open in security groups:
  * `TCP port 2377`: Cluster management communication.
  * `TCP/UDP port 7946`: Node discovery and gossip control plane.
  * `UDP port 4789`: VXLAN data plane encapsulation.
* ⚠️ **Port Collisions in Host Network Mode**: When using `--network host`, two containers cannot bind to the same port (e.g. port 80), because they share the exact same host network stack.

---

## 7. Comparative Analysis Matrix: Docker Network Drivers

| Driver | DNS Resolution | Port Forwarding (NAT) | Max Throughput | Multi-Host Support |
| :--- | :--- | :--- | :--- | :--- |
| **User-Defined Bridge** | **Automatic (Built-in)** | Yes (iptables DNAT) | High | No (Single Host) |
| **Default Bridge** | None (IP only) | Yes (iptables DNAT) | High | No (Single Host) |
| **Host** | Host DNS | **No (Direct Socket Bind)** | **Maximum (Zero Overhead)** | No (Single Host) |
| **Overlay** | Automatic (Distributed) | Yes (Ingress Mesh) | Moderate (VXLAN Tax) | **Yes (Multi-Host)** |
| **Macvlan** | Host / LAN DNS | No (Physical LAN IP) | **Ultra-High** | Yes (Underlay LAN) |

---

## 8. Performance & Resource Optimization

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                     NETWORKING PERFORMANCE PLAYBOOK                            │
├────────────────────────────────────────────────────────────────────────────────┤
│ 1. Use `--network host` for latency-critical network applications (e.g. VoIP). │
│ 2. Disable `userland-proxy` in `daemon.json` to route via kernel iptables NAT. │
│ 3. Adjust MTU on Overlay networks (`--opt mtu=1450`) to avoid VXLAN fragmentation│
│ 4. Segment sensitive tiers onto internal bridge networks (`--internal`).       │
│ 5. Connect multi-tier containers to multiple discrete networks for isolation.  │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Step-by-Step Hands-On Production Walkthrough

### Step 1: Create Segmented Production Network Topology

```bash

# 1. Create Public Frontend DMZ Network
docker network create \
    --driver bridge \
    --subnet 172.20.0.0/24 \
    --gateway 172.20.0.1 \
    public-dmz-net

# 2. Create Isolated Internal Backend Database Network (No Internet Access!)
docker network create \
    --driver bridge \
    --subnet 172.21.0.0/24 \
    --gateway 172.21.0.1 \
    --internal \
    private-backend-net
```

---

### Step 2: Deploy Microservices with Network Micro-Segmentation

```bash

# 1. Deploy PostgreSQL Database (Attached ONLY to private-backend-net)
docker run \
    --detach \
    --name core-postgres \
    --network private-backend-net \
    --env "POSTGRES_DB=prod_db" \
    --env "POSTGRES_PASSWORD=SecurePass2026!" \
    postgres:16-alpine

# 2. Deploy API Gateway (Attached to BOTH public-dmz-net AND private-backend-net)
docker run \
    --detach \
    --name api-gateway \
    --network public-dmz-net \
    --env "DB_HOST=core-postgres" \
    node:20-alpine sleep 3600

# Attach API Gateway to private backend network dynamically:
docker network connect private-backend-net api-gateway

# 3. Deploy Frontend Web UI (Attached ONLY to public-dmz-net)
docker run \
    --detach \
    --name frontend-ui \
    --network public-dmz-net \
    --publish 80:80 \
    nginx:alpine
```

---

### Step 3: Verify Zero-Trust Network Micro-Segmentation & DNS

```bash

# 1. Verify API Gateway CAN resolve and reach core-postgres:
docker exec api-gateway ping -c 2 core-postgres

# 2. Verify Frontend UI CANNOT reach core-postgres (Strict Network Isolation!):
docker exec frontend-ui ping -c 2 -W 2 core-postgres || echo "SUCCESS: Frontend blocked from database access!"

# 3. Verify Database CANNOT reach external internet (Enforced by --internal):
docker exec core-postgres ping -c 2 -W 2 8.8.8.8 || echo "SUCCESS: Database air-gapped from internet!"
```

---

## 10. Pure CLI / Command Interface

### 1. Inspect Network Subnet and Connected Container IP Map

Query connected container IPs and MAC addresses:

```bash
docker network inspect public-dmz-net \
    --format 'Subnet: {{range .IPAM.Config}}{{.Subnet}}{{end}} | Containers: {{range $k, $v := .Containers}}{{$v.Name}} ({{$v.IPv4Address}}) {{end}}'
```

### 2. Dynamically Disconnect a Container from a Network

Sever a compromised container from the internal network without stopping it:

```bash
docker network disconnect private-backend-net api-gateway
```

### 3. Remove All Unused Docker Networks

Prune stale networks not attached to active containers:

```bash
docker network prune --force
```

---

## 11. Advanced Architecture & Edge-Case Failure Modes

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                    NETWORKING FAILURE RECOVERY MATRIX                          │
├──────────────────────┬────────────────────────┬────────────────────────────────┤
│ Failure Scenario     │ Underlying Root Cause  │ Production Mitigation Runbook  │
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **DNS Resolution**   │ Containers placed on   │ Create custom user-defined     │
│ **Fails by Name**    │ default `bridge` net.  │ bridge network (`docker net`). │
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **Overlay Network**  │ MTU size exceeds       │ Configure `--opt mtu=1450`     │
│ **Packet Dropping**  │ cloud network MTU.     │ to allow 50B VXLAN header.     │
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **Host Port Binding**│ Port already bound by  │ Re-map published port          │
│ **Error (EADDRINUSE)│ local host daemon.     │ (`-p 8081:80`) or stop daemon. │
├──────────────────────┼────────────────────────┼────────────────────────────────┤
│ **IP Exhaustion in** │ Subnet `/24` exhausted │ Define larger subnet           │
│ **Bridge Network**   │ by 254 containers.     │ (e.g. `--subnet 172.20.0.0/16`).│
└──────────────────────┴────────────────────────┴────────────────────────────────┘
```

---

## 12. Detailed Sub-Components & Subsystems

### 1. Embedded DNS Resolver (`127.0.0.11`)

* **Key Concepts**: Asynchronous DNS server multiplexer managing internal service discovery and external DNS upstream forwarding.
* **CLI / Tool Snippet**:

```bash
docker exec api-gateway cat /etc/resolv.conf
```

### 2. Linux veth Pair Virtual Cable

* **Key Concepts**: Bi-directional virtual ethernet link where packets entering one end in the container namespace emerge on the host bridge.
* **CLI / Tool Snippet**:

```bash
ip link show type veth
```

### 3. iptables NAT Chain Manager

* **Key Concepts**: Dynamically injects `PREROUTING`, `POSTROUTING`, and `DOCKER` rules to manage container traffic routing and isolation filters.
* **CLI / Tool Snippet**:

```bash
iptables -t nat -L DOCKER -n -v 2>/dev/null || true
```

### 4. VXLAN Overlay Encapsulator

* **Key Concepts**: Linux kernel VXLAN driver encapsulating Layer 2 ethernet frames inside Layer 3 UDP datagrams on port 4789 for multi-host routing.
* **CLI / Tool Snippet**:

```bash
ip link show type vxlan
```

---

## 13. References (The 5+5 Rule)

### Official Documentation & OCI Specifications

1. [Docker Official Documentation: Networking Overview](https://docs.docker.com/network/)
2. [Docker Official Documentation: Use Bridge Networks](https://docs.docker.com/network/drivers/bridge/)
3. [Docker Official Documentation: Use Overlay Networks](https://docs.docker.com/network/drivers/overlay/)
4. [Moby Libnetwork Official Architecture and Specification](https://github.com/moby/libnetwork)
5. [IETF RFC 7348: Virtual eXtensible Local Area Network (VXLAN)](https://www.rfc-editor.org/rfc/rfc7348.html)

### Authoritative Engineering Blogs & Architecture Deep Dives

1. [Julia Evans: How Docker Networking and DNS Works](https://jvns.ca/)
2. [Brendan Gregg: Linux Network Performance, iptables and NAT Profiling](https://www.brendangregg.com/)
3. [Liz Rice: Understanding Container Networking from Scratch](https://www.lizrice.com/)
4. [Martin Fowler: Microservices Zero-Trust Network Segmentation](https://martinfowler.com/)
5. [High-Performance Linux Systems: Tuning iptables and VXLAN MTU for Containers](https://www.kernel.org/)

---

## 14. Universal FinOps & Resource Cost Governance

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                      NETWORK FINOPS SAVINGS MATRIX                             │
├──────────────────────────┬──────────────────────────┬──────────────────────────┤
│ Optimization Strategy    │ Technical Mechanism      │ Measurable FinOps ROI    │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **`--internal` Isolation**| Blocks unneeded external │ Eliminates unintended cloud│
│                          │ outbound data egress     │ internet bandwidth fees  │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **Host Network Mode**    │ Eliminates iptables NAT  │ Cuts CPU network routing │
│                          │ translation processing   │ load by 15% on gateways  │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **Overlay MTU Alignment**| Prevents packet          │ Eliminates CPU packet    │
│                          │ fragmentation retries    │ reassembly latency taxes │
├──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ **Embedded DNS Caching** │ Caches local lookups     │ Reduces cloud Private DNS│
│                          │ in memory (`127.0.0.11`) │ per-query API billing    │
└──────────────────────────┴──────────────────────────┴──────────────────────────┘
```

### 1. Cloud Network Egress Cost Elimination via `--internal`

In cloud environments where outbound internet data transfer is billed at \$0.09/GB:

* Misconfigured backend database containers making unwanted external updates or vulnerability downloads consume 500GB of egress data monthly ($~\$45/\text{month per database node}$).
* Declaring the database network as `--internal` completely blocks external routing at the kernel level.
* **FinOps ROI**: Eliminates accidental egress charges and guarantees compliance isolation.

### 2. Host Network Mode Compute Savings on High-Throughput Ingress Gateways

For high-traffic API gateways handling 50,000 HTTP requests per second:

* Running on a standard bridge network forces every packet through iptables `PREROUTING` and connection tracking (`conntrack`), consuming **~25% of total server CPU** purely for NAT translation.
* Deploying the gateway with `--network host` allows NGINX to bind directly to the physical interface, eliminating NAT.
* Gateway CPU utilization drops by **25%**, allowing the instance tier to downsize from an AWS `c6g.4xlarge` (\$490/month) to a `c6g.2xlarge` (\$245/month), saving **\$2,940/year per gateway node**.
