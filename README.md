# Kafka and data streams for Digital Twins

## Overview
This project sets up a simple Kafka environment using Docker containers to simulate a publisher-consumer interaction. A Kafka broker serves as the backbone for a publisher that generates and sends random key-value pairs to specified topics, and a consumer that reads and prints these messages.

## Project Structure

- **Kafka Broker**: Runs in a Docker container.
- **Publisher**: Generates random integer key-value pairs every second and publishes them to one of these two topics:
  - `test-topic` (1 partition)
  - `test-topic-2` (1 partition)
- **Consumer**: Reads and prints every message published on a selected topic.

Each service (broker, publisher, consumer) ideally runs in its own container managed by a `docker-compose.yml` file, with specific access privileges for each topic.

---

### ![immagine](https://github.com/user-attachments/assets/e8c07b85-251e-44f5-bf53-23fe95e3bb1f) Python Packages Used
| Package       | Version |
|---------------|---------|
| kafka-python  | 2.0.2   |
| six           | 1.16.0  |

---

## Getting Started

### Prerequisites
To set up the test environment, you'll need the following:
- [Kafka Docker Image](https://hub.docker.com/r/apache/kafka): A Docker image of the Apache Kafka broker.
- [Python Code](https://needablackcoffee.medium.com/learn-apache-kafka-with-these-python-examples-454b5275109e): Refer to this quickstart guide.

---

## Project To-Do
- **Schema for data handling**: Define a structured schema for the messages to be handled more efficiently.
- **docker-compose.yml**: Create a `docker-compose.yml` file containing at least one Kafka broker and multiple containers for publishers and consumers.
