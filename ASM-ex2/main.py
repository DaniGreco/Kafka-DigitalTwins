import uuid
import json
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import logging_manager
from configuration_manager import ConfigurationManager

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

    # Kafka Consumer Setup
    kafka_params = config_manager.get_kafka_params()
    consumer = None
    if kafka_params:
        try:
            consumer = KafkaConsumer(
                *kafka_params['topics'],
                bootstrap_servers=kafka_params['bootstrap_servers'],
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                auto_offset_reset='earliest',
                group_id='asm-consumers'
            )
            logger.info("Kafka consumer initialized successfully.")
        except KafkaError as e:
            logger.error(f"Failed to initialize Kafka consumer: {e}")

    if consumer:
        try:
            for message in consumer:
                logger.info(f"Received message from topic {message.topic}: {message.value}")
                print(f"[ASM-2 CONSUMER] Received: {message.value.get('action')} from topic {message.topic}")
        except KeyboardInterrupt:
            logger.info("Shutting down Kafka consumer.")
        finally:
            consumer.close()
            logger.info("Kafka consumer closed.")