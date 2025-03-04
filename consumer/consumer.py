from kafka import KafkaConsumer

consumer = KafkaConsumer('my-topic', bootstrap_servers='broker:9092')

for message in consumer:
    print("Messaggio ricevuto: " + message.value.decode('utf-8'))


