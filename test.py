import sys

if sys.version_info >= (3, 12, 0):
    import six
    sys.modules['kafka.vendor.six.moves'] = six.moves

import random
import time
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='localhost:9092')

t1 = "test-topic"
t2 = "test-topic-2"

t = t1      # Choose topic
while True:
    k = f"{random.randint(10, 99)}".encode()
    v = f"{random.randint(10, 99)}".encode()
    producer.send(
        topic=t,
        key=k,
        value=v
    )
    print("topic: " + t + " | key: " + k.decode() + " | value: " + v.decode())
    time.sleep(1)