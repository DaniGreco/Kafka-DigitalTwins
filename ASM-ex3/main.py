import os
import sys
import uuid
import time
import json
import threading
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError

# Aggiunge la directory padre al sys.path
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging_manager
from configuration_manager import ConfigurationManager
from model_uploader import ModelUploader
from enforcer import EnforcerExample

def run_simulation(enforcer:EnforcerExample, model_uploader:ModelUploader, producer: KafkaProducer, producer_topic: str, input_action: str):
    """
    Run a single simulation step and produce the result to Kafka.
    """
    execute_enforcer = enforcer != None
    
    if execute_enforcer:
        # In a real scenario, you might not want to upload the model every time.
        # This is simplified for the example.
        model_uploader.upload_runtime_model()
        enforcer.begin_enforcement()

    logger.info(f"--Executing simulation with input: {input_action}--")
    
    out_action = input_action
    if execute_enforcer:
        input_dict = {"inputAction": out_action, "rightLaneFree": "true"} # Assuming rightLaneFree is true for simplicity
        enforced_action = enforcer.sanitise_output(input_dict)
        if enforced_action is not None:
            out_action = enforced_action

    # Send the action to Kafka
    try:
        future = producer.send(producer_topic, {'action': out_action, 'sender': 'ASM-ex3'})
        record_metadata = future.get(timeout=10)
        logger.info(f"Sent message to Kafka topic {producer_topic}: {out_action} at offset {record_metadata.offset}")
        print(f"[ASM-3 PRODUCER] Sent: {out_action} to topic {producer_topic}")
    except KafkaError as e:
        logger.error(f"Failed to send message to Kafka: {e}")

    if execute_enforcer:
        enforcer.end_enforcement()
        model_uploader.delete_runtime_model()

def consumer_thread(consumer: KafkaConsumer, enforcer: EnforcerExample, model_uploader: ModelUploader, producer: KafkaProducer, producer_topic: str):
    """
    Thread for consuming messages and triggering simulations.
    """
    try:
        for message in consumer:
            logger.info(f"Received message from topic {message.topic}: {message.value}")
            print(f"[ASM-3 CONSUMER] Received: {message.value.get('action')} from topic {message.topic}")
            action = message.value.get('action')
            if action:
                                run_simulation(enforcer, model_uploader, producer, producer_topic, action)
    except KeyboardInterrupt:
        logger.info("Shutting down Kafka consumer thread.")
    finally:
        consumer.close()

if __name__ == '__main__':
    CONFIG_FILE = "config.json"

    # Setup from a configuration file
    config_manager = ConfigurationManager(CONFIG_FILE)

    # Setup Logging
    execution_id = uuid.uuid4()
    level, log_folder = config_manager.get_logging_params()
    logging_manager.setup_logging(level, log_folder, execution_id)
    logger = logging_manager.get_logger(__name__)

    logger.info(f"Loaded config.json - Starting execution with id {execution_id}")
    config_manager.log_configuration()

    # Kafka Setup
    kafka_params = config_manager.get_kafka_params()
    producer = None
    consumer = None

    if kafka_params:
        try:
            producer = KafkaProducer(
                bootstrap_servers=kafka_params['bootstrap_servers'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logger.info("Kafka producer initialized successfully.")

            consumer = KafkaConsumer(
                kafka_params['consumer_topic'],
                bootstrap_servers=kafka_params['bootstrap_servers'],
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                auto_offset_reset='earliest',
                group_id='asm3-consumer-group'
            )
            logger.info("Kafka consumer initialized successfully.")

        except KafkaError as e:
            logger.error(f"Failed to initialize Kafka clients: {e}")

    # ASM Setup
    ip, port, asm_path, asm_file_name = config_manager.get_server_params()
    enforcer = EnforcerExample(ip, port, asm_file_name)
    model_uploader = ModelUploader(ip, port, asm_path, asm_file_name)

    if consumer and producer:
        # Start consumer thread
        c_thread = threading.Thread(target=consumer_thread, args=(consumer, enforcer, model_uploader, producer, kafka_params['producer_topic']))
        c_thread.start()
        logger.info("Consumer thread started.")

        try:
            # Keep the main thread alive
            c_thread.join()
        except KeyboardInterrupt:
            logger.info("Main thread interrupted. Shutting down.")
        finally:
            if producer:
                producer.close()
                logger.info("Kafka producer closed.")