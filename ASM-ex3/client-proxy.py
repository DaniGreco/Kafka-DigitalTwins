import flask
from flask import request, jsonify
from kafka import KafkaProducer, KafkaConsumer
import json
import uuid

# --- Configurazione Kafka ---
KAFKA_BROKER = "broker:9092"
REQUEST_TOPIC = "asm1_requests"
RESPONSE_TOPIC = "asm1_responses"

# Inizializza Kafka Producer e Consumer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

consumer = KafkaConsumer(
    RESPONSE_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset='earliest',  # Inizia a leggere dall'ultimo messaggio
    group_id=f"client-proxy-group-{uuid.uuid4()}",  # Group ID unico per ricevere tutte le risposte
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

app = flask.Flask(__name__)


# Route "catch-all" per intercettare tutte le richieste
@app.route('/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def forward_request(endpoint):
    correlation_id = str(uuid.uuid4())
    print(f"Ricevuta richiesta per endpoint '{endpoint}' con ID: {correlation_id}")

    # 1. Costruisci il messaggio da inviare a Kafka
    kafka_message = {
        "correlation_id": correlation_id,
        "endpoint": endpoint,
        "method": request.method,
        "params": request.args.to_dict(),
        "json_data": request.get_json(silent=True),
        "headers": dict(request.headers)
    }

    # 2. Invia il messaggio al topic delle richieste
    producer.send(REQUEST_TOPIC, kafka_message)
    producer.flush()
    print(f"Messaggio inviato a Kafka con ID: {correlation_id}")

    # 3. Attendi la risposta sul topic delle risposte
    print(f"In attesa di risposta per ID: {correlation_id}")
    for message in consumer:
        if message.value.get("correlation_id") == correlation_id:
            print(f"Risposta ricevuta per ID: {correlation_id}")
            response_data = message.value.get("response")

            # 4. Inoltra la risposta al client originale
            # Nota: Flask converte automaticamente il dizionario in una Response JSON
            return jsonify(response_data), message.value.get("status_code", 200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)