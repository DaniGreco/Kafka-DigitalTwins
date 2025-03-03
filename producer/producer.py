import zmq
from kafka import KafkaProducer
import time

# Configurazione Kafka
producer = KafkaProducer(bootstrap_servers='broker:9092')
topic = 'my-topic'

# Configurazione ZeroMQ
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")  # Connessione a ZeroMQ in locale
socket.setsockopt_string(zmq.SUBSCRIBE, "")  # Sottoscrizione a tutti i messaggi

print("Attesa per stabilizzazione...")
time.sleep(5)
print("Bridge ZeroMQ -> Kafka avviato...")

while True:
    message = socket.recv_string()
    producer.send(topic, message.encode('utf-8'))
    print(f"Messaggio ricevuto da ZeroMQ e inviato a Kafka: {message}")
