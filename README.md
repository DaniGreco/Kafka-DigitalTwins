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

## Getting Started

### Prerequisites
To set up the test environment, you'll need the following:
- [Docker](https://www.docker.com/)

### Quickstart guide (WORK IN PROGRESS)
Run the **docker-compose.yaml** file inside the main directory:
```console
docker-compose up --build
```
It may take some time to start up all correctly (even some minutes). If after a few minutes the `consumer` and `producer` containers do not start, do it manually via docker.

---

## Project To-Do
- **Schema for data handling**: Define a structured schema for the messages to be handled more efficiently.
- **docker-compose.yml**: Create a `docker-compose.yml` file containing at least one Kafka broker and multiple containers for publishers and consumers.
