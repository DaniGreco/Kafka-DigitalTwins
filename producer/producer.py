from kafka import KafkaProducer
import time

producer = KafkaProducer(bootstrap_servers='broker:9092')
topic = 'my-topic'
i = 0

print("time to sleep")
time.sleep(5)

while True:
    i += 1
    message = "Messaggio di prova " + str(i)
    producer.send(topic, message.encode('utf-8'))
    print("Messaggio inviato: " + message)
    time.sleep(1)