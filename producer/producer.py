import logging
import os
from kafka import KafkaProducer
import zmq

# Configuration Logging
log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "app.log"),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configurazione Kafka
producer = KafkaProducer(bootstrap_servers='broker:9092')
topic = 'my-topic'

# Configurazione ZeroMQ
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://host.docker.internal:5555")  # Connessione a ZeroMQ in locale
socket.setsockopt_string(zmq.SUBSCRIBE, "")  # Sottoscrizione a tutti i messaggi

print("Bridge ZeroMQ -> Kafka avviato...")

while True:
    message = socket.recv_string()
    producer.send(topic, message.encode('utf-8'))
    logging.info(message)
    #print(f"RECEIVED ZtoF: {message}")
