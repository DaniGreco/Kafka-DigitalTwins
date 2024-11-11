#!/bin/bash
# Attende qualche secondo per garantire che Kafka sia pronto
sleep 10
# Crea il topic "my-topic" con 1 partizione e fattore di replica 1
kafka-topics --create --topic my-topic --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1
