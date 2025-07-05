"""
    Author:      Patrizia Scandurra
    Created:     21/03/2025
"""

import os
import sys
import uuid
import time
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Aggiunge la directory padre al sys.path
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging_manager
from configuration_manager import ConfigurationManager
from model_uploader import ModelUploader
from enforcer import EnforcerExample

def run(enforcer:EnforcerExample, model_uploader:ModelUploader, producer: KafkaProducer, topics: list[str]):
    """
    Run a series of tests for the Target System, with or without an ASM model used as enforcement policy specification

    Parameters:

        enforcer (Enforcer or None):  enforcement module (if any) to validate and correct actions.
        model_uploader(ModelUploader or None): module for uploading the ASM model and its libraries.
        producer (KafkaProducer): Kafka producer to send messages.
        topics (list[str]): Kafka topics to send messages to.
   
    Returns:
        None
    """
        
    execute_enforcer = enforcer != None
    
    if execute_enforcer:
        start_time = time.perf_counter()
        model_uploader.upload_runtime_model()
        upload_delay = (time.perf_counter() - start_time) * 1000

    #test_runs = 1 #Number of test episodes to run. Default is 1.
    #for i in range(test_runs):
    logger.info("--Starting new test run--")
    test_run_start = time.perf_counter()
    
    n_step = 0
    if execute_enforcer:
            total_sanitisation_delay = 0
            max_sanitisation_delay = 0
            enforcer_interventions = 0 # Number of step in which the enforcer changed the input action to a different action
            start_time = time.perf_counter()
            enforcer.begin_enforcement()
            start_delay = (time.perf_counter() - start_time) * 1000
        
    done = False
    while not done:
        logger.info("--Executing new step--")
        # Automated execution: run for a fixed number of steps
        # Define a list of predefined actions
        actions = ["FASTER", "LANE_RIGHT", "SLOWER", "LANE_LEFT", "IDLE"]
        out_action = actions[n_step % len(actions)]
        right_lane_free = "true" if n_step % 2 == 0 else "false"

        print(f"[ASM-1] Step {n_step}: Action: {out_action}, Right Lane Free: {right_lane_free}")
        
        # If the enforcer is running, try to sanitise the system's output with the ASM enforcement model
        if execute_enforcer:
            start_time = time.perf_counter()
            n_step+=1
            #prepare the input for the ASM model (a dict: the name of the function is the key, the value is the function's value)
            input_dict = {}
            input_dict["inputAction"] = out_action 
            input_dict["rightLaneFree"] = right_lane_free
            #invoke the output sanitization step
            enforced_action = enforcer.sanitise_output(input_dict)
            #some stats 
            sanitisation_delay = (time.perf_counter() - start_time) * 1000
            max_sanitisation_delay = max(max_sanitisation_delay, sanitisation_delay)
            total_sanitisation_delay += sanitisation_delay
            # Change the action if the enforcer returns a new different one
            if enforced_action != None: 
                out_action = enforced_action
                enforcer_interventions += 1
            else:
                logger.info(f"Action: {out_action}")
        # Run the step on the environment using the effector interface
        # No target system exists in this version, so we do nothing.  
        
        # Send the action to Kafka
        try:
            for topic in topics:
                future = producer.send(topic, {'action': out_action, 'sender': 'ASM-ex1'})
                record_metadata = future.get(timeout=10)
                logger.info(f"Sent message to Kafka topic {topic}: {out_action} at offset {record_metadata.offset}")
                print(f"[ASM-1 PRODUCER] Sent: {out_action} to topic {topic}")
        except KafkaError as e:
            logger.error(f"Failed to send message to Kafka: {e}")

        # Automated execution: run indefinitely
        done = False
        time.sleep(1) # Add a small delay to simulate real-time processing
            
    # Stop the execution of the runtime model
    if execute_enforcer:
            start_time = time.perf_counter()
            enforcer.end_enforcement()
            stop_delay = (time.perf_counter() - start_time) * 1000
            logger.info("Enforcer delays:")
            logger.info(f"* Start delay: {start_delay:.2f}ms")
            logger.info(f"* Total sanitisation delay: {total_sanitisation_delay:.2f}ms (max {max_sanitisation_delay:.2f}ms)")
            logger.info(f"* Stop delay: {stop_delay:.2f}ms")
            logger.info(f"Number of enforcer interventions: {enforcer_interventions} (out of {n_step})")

    test_execution_time = (time.perf_counter() - test_run_start) * 1000
    #logger.info(f"Test run {i} completed in {test_execution_time:.2f}ms:")
    logger.info(f"Test run completed in {test_execution_time:.2f}ms:")
    logger.info(f"* Model simulation steps: {n_step}")
    logger.info("")


    # Delete the runtime models
    if execute_enforcer:
        start_time = time.perf_counter()
        model_uploader.delete_runtime_model()
        delete_delay = (time.perf_counter() - start_time) * 1000
        logger.info(f"Upload model delay: {upload_delay:.2f}ms")
        logger.info(f"Delete model delay: {delete_delay:.2f}ms")



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

    # Kafka Producer Setup
    kafka_params = config_manager.get_kafka_params()
    producer = None
    if kafka_params:
        try:
            producer = KafkaProducer(
                bootstrap_servers=kafka_params['bootstrap_servers'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logger.info("Kafka producer initialized successfully.")
        except KafkaError as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")

    # Run the ASM model
    ip, port, asm_path, asm_file_name = config_manager.get_server_params()
    enforcer = EnforcerExample(ip, port, asm_file_name)
    model_uploader = ModelUploader(ip, port, asm_path, asm_file_name)
    try:            
        run(enforcer, model_uploader, producer, kafka_params.get('topics'))
    except Exception as e:
        # Try to run the tests again without the ASM model if at a certain point the server is down  
        logger.error(f"Failed to connect to the server - Executing the test runs WITHOUT the model")            
        run(None, None, None, [])
    finally:
        if producer:
            producer.close()
            logger.info("Kafka producer closed.")


