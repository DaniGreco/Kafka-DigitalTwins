from kafka import KafkaConsumer

consumer = KafkaConsumer('my-topic', bootstrap_servers='kafka:9092')

for message in consumer:
    print("Messaggio ricevuto:", message.value)
