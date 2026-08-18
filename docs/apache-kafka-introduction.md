# Module: Running Distributed Apache Kafka with Docker Compose
**Category:** Event Streaming & Distributed Systems in Containers
**Status:** ✅ Completed

---

## 1. High-Level Overview
**Apache Kafka** is an enterprise-grade distributed event streaming platform capable of handling trillions of events per day with ultra-low latency, high throughput, and fault tolerance. Running Apache Kafka in containerized environments enables rapid development and reproducible integration testing for microservice event-driven architectures. Modern Kafka deployments utilize **KRaft (Kafka Raft Metadata mode)**, eliminating the legacy external Apache ZooKeeper dependency by running metadata consensus directly inside Kafka controller nodes.

### 👔 Executive Summary (For Managers & Non-Technical Stakeholders)
* **Business Purpose**: Provides a lightning-fast digital highway for corporate business events, enabling payment systems, mobile apps, and fraud-detection engines to communicate in real time without lag.
* **How It Works**: Operates as a distributed, indestructible ledger. Applications post events (like customer payments or order updates) to topics where subscribing systems process them immediately.
* **Key Business Value & Use Cases**: Powers real-time analytics, decouples monolithic software systems into scalable microservices, and guarantees zero data loss during high-volume peak transaction events.

---

## 2. KRaft vs ZooKeeper Architecture

```
Modern KRaft Mode (ZooKeeper-Free Architecture)
+-------------------------------------------------------------+
|               Kafka Controller Quorum (KRaft)               |
|            (Integrated Metadata Log & Raft Leader)          |
+-------------------------------------------------------------+
                              |
                +-------------+-------------+
                |                           |
                v                           v
+-------------------------------+ +---------------------------+
|        Kafka Broker 1         | |       Kafka Broker 2      |
|    (Topic Partitions: P0, P1) | | (Topic Partitions: P2, P3)|
+-------------------------------+ +---------------------------+
```

---

## 📌 Core Terminology & Standalone Quickstart (Original Notes)

* **Documentation Reference**: [Apache Kafka Documentation](https://kafka.apache.org/documentation/)

### Essential Terminology Glossary
* **Queue**: A traditional point-to-point messaging pattern; in Kafka similar semantics are implemented using topics and consumer groups.
* **Broker**: A Kafka server that stores topic partitions, serves client requests, and coordinates replication and leader election.
* **Event**: A single message (record) containing a key, value, and metadata (timestamp, headers) produced to a topic.
* **Producer**: A client application that writes events to one or more Kafka topics.
* **Consumer**: A client application that reads events from topics; consumers in a group share partition ownership for parallel processing.
* **Topic**: A named feed or category to which events are published; topics are partitioned for scalability and fault tolerance.
* **Partition**: An ordered, immutable sequence of events within a topic that provides parallelism and serves as the unit of storage and replication.

### Standalone Kafka Container Quickstart
Launch an ephemeral single-node Kafka broker and execute built-in CLI scripts:
```bash
docker pull apache/kafka:latest
docker run -d \
    --name kafka-standalone \
    -p 9092:9092 \
    apache/kafka:latest
docker exec -it kafka-standalone bash
```
Locate Kafka administration scripts inside container:
```bash
find / -name "kafka-topics.sh"
```
Create, describe, produce, and consume events directly from inside the container:
```bash
/opt/kafka/bin/kafka-topics.sh --create \
    --topic quickstart-events \
    --bootstrap-server localhost:9092 \
    --partitions 1 \
    --replication-factor 1

/opt/kafka/bin/kafka-topics.sh --describe \
    --topic quickstart-events \
    --bootstrap-server localhost:9092

/opt/kafka/bin/kafka-console-producer.sh \
    --topic quickstart-events \
    --bootstrap-server localhost:9092

/opt/kafka/bin/kafka-console-consumer.sh \
    --topic quickstart-events \
    --from-beginning \
    --bootstrap-server localhost:9092
```

---

## 3. Hands-On Walkthrough: Deploying KRaft Kafka with Docker Compose
### Step 1: Define the `compose.yaml` Manifest for KRaft Kafka
Declare Kafka broker and management UI:
```yaml
services:
  kafka:
    image: apache/kafka:3.7.0
    container_name: kafka-broker
    ports:
      - "9092:9092"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@localhost:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_LOG_DIRS: /tmp/kraft-combined-logs
    volumes:
      - kafka-data:/tmp/kraft-combined-logs

volumes:
  kafka-data:
```

### Step 2: Start the Kafka Cluster
Launch the Kafka stack in detached mode:
```bash
docker compose up -d
```

### Step 3: Create a Kafka Topic and Produce Events
Create an enterprise event topic:
```bash
docker exec -it kafka-broker \
    /opt/kafka/bin/kafka-topics.sh \
    --create \
    --topic orders.payments \
    --bootstrap-server localhost:9092 \
    --partitions 3 \
    --replication-factor 1
```

---

## 4. Pure CLI Commands
### 1. List Kafka Topics
Inspect existing topics on the broker:
```bash
docker exec -it kafka-broker \
    /opt/kafka/bin/kafka-topics.sh \
    --list \
    --bootstrap-server localhost:9092
```

### 2. Consume Messages from Topic
Read real-time messages from the beginning:
```bash
docker exec -it kafka-broker \
    /opt/kafka/bin/kafka-console-consumer.sh \
    --topic orders.payments \
    --from-beginning \
    --bootstrap-server localhost:9092
```

---

## References

### Official Documentation
* [Apache Kafka Official Documentation](https://kafka.apache.org/documentation/) - Core architecture and configuration.
* [Kafka KRaft Mode Documentation](https://cwiki.apache.org/confluence/display/KAFKA/KIP-500%3A+Replace+ZooKeeper+with+a+Self-Managed+Metadata+Quorum) - Metadata quorum specifications.
* [Apache Kafka Docker Official Image](https://hub.docker.com/r/apache/kafka) - Configuration variables reference.
* [Kafka Performance Tuning Guide](https://kafka.apache.org/documentation/#design) - Pagecache and zero-copy disk I/O.
* [Kafka Security & SASL/SSL](https://kafka.apache.org/documentation/#security) - Authentication and encryption in transit.

### Authoritative Web Pages, Blogs & Tutorials
* [Confluent Engineering Blog: The Elimination of ZooKeeper in Kafka](https://www.confluent.io/blog/) - KRaft consensus deep dive.
* [A Cloud Guru: Apache Kafka Deep Dive](https://www.pluralsight.com/) - Partitioning and consumer group rebalancing.
* [Datadog Engineering: Monitoring Kafka Broker Metrics and Consumer Lag](https://www.datadoghq.com/blog/) - Critical alerting thresholds.
* [Snyk Security: Hardening Kafka in Docker Containers](https://snyk.io/) - Securing plaintext listeners.
* [FinOps Foundation: Optimizing Distributed Event Storage Costs](https://www.finops.org/) - Topic retention and tiered storage policies.

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
