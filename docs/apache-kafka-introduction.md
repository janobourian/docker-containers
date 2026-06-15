# Apache Kafka

This is the documentation to work with Apache Kafka but using docker containers :D ![This is the docs](https://kafka.apache.org/42/)

## Terminology

* Queue: A traditional point-to-point messaging pattern; in Kafka similar semantics are implemented using topics and consumer groups.
* Broker: A Kafka server that stores topic partitions, serves client requests, and coordinates replication and leader election.
* Event: A single message (record) containing a key, value, and metadata (timestamp, headers) produced to a topic.
* Producer: A client that writes events to one or more Kafka topics.
* Consumer: A client that reads events from topics; consumers in a group share partition ownership for parallel processing.
* Topic: A named feed or category to which events are published; topics are partitioned for scalability and fault tolerance.
* Partition: An ordered, immutable sequence of events within a topic that provides parallelism and a unit of storage and replication.

## Quickstart

Create the docker container:

```bash
docker pull apache/kafka:4.2.0
docker run -p 9092:9092 apache/kafka:4.2.0
docker exec -it confident_mendeleev bash
```

Searcht the `kafka-*.sh`:

```bash
find / -name "kafka-topics.sh"
find / -name "kafka-*.sh"
```

Create the topic and inspect it:

```bash
/opt/kafka/bin/kafka-topics.sh
/opt/kafka/bin/kafka-topics.sh --create --topic quickstart-events --bootstrap-server localhost:9092
/opt/kafka/bin/kafka-topics.sh --describe --topic quickstart-events --bootstrap-server localhost:9092
/opt/kafka/bin/kafka-console-producer.sh --topic quickstart-events --bootstrap-server localhost:9092
/opt/kafka/bin/kafka-console-consumer.sh --topic quickstart-events --from-beginning --bootstrap-server localhost:9092
```