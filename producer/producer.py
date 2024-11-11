from kafka import KafkaProducer
import time

producer = KafkaProducer(bootstrap_servers='kafka:9092')
topic = 'my-topic'

while True:
    producer.send(topic, b'Messaggio di prova')
    print("Messaggio inviato")
    time.sleep(1)
