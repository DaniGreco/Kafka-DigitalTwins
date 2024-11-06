import sys
if sys.version_info >= (3, 12, 0):
    import six
    sys.modules['kafka.vendor.six.moves'] = six.moves

import time
from kafka import KafkaConsumer

# 2 topics created
t1 = "test-topic"
t2 = "test-topic-2"

# Select topic to read from
t = t2

# Kafka producer that sends data to server at localhost:9092 (broker container)
consumer = KafkaConsumer(t,
                         auto_offset_reset='earliest',
                         group_id=t+'-group1',
                         bootstrap_servers=['localhost:9092'])

for message in consumer:
    print(f"topic: {message.topic} | "
          f"partition: {message.partition} | "
          f"offset: {message.offset} | "
          f"key: {message.key.decode()} | "
          f"value: {message.value.decode()}")