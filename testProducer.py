import sys
if sys.version_info >= (3, 12, 0):
    import six
    sys.modules['kafka.vendor.six.moves'] = six.moves

import random
import time
from kafka import KafkaProducer

# Kafka producer that sends data to server at localhost:9092 (broker container)
producer = KafkaProducer(bootstrap_servers='localhost:9092')

# 2 topics created
t1 = "test-topic"
t2 = "test-topic-2"

# select topic to publish on
t = t2
while True:
    k = f"{random.randint(10, 99)}".encode()
    v = f"{random.randint(10, 99)}".encode()

    producer.send(
        topic=t,
        key=k,
        value=v
    )

    print(f"topic: {t} | "
          f"key: {k.decode()} | "
          f"value: {v.decode()}")

    time.sleep(1)