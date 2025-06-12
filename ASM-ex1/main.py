"""
    Author:      Patrizia Scandurra
    Created:     21/03/2025
"""

import os
import sys
import uuid
import time
# Aggiunge la directory padre al sys.path
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging_manager
from configuration_manager import ConfigurationManager
from model_uploader import ModelUploader
from enforcer import EnforcerExample

def run(enforcer:EnforcerExample, model_uploader:ModelUploader):
    """
    Run a series of tests for the Target System, with or without an ASM model used as enforcement policy specification

    Parameters:

        enforcer (Enforcer or None):  enforcement module (if any) to validate and correct actions.
        model_uploader(ModelUploader or None): module for uploading the ASM model and its libraries.
   
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
        # Observe the environment and the target system: your logics goes here (it's application-specific)
        # ... 
        # No target system exists in this version, so for testing purposes, target system's inputs/outputs and probes are simulated via user inputs
        out_action = input('Target system action (FASTER, SLOWER, IDLE, LANE_LEFT, LANE_RIGHT): ') #example of out action of the target system to sanitize
        right_lane_free = input('Is right lane free (true, false)?: ') #example of probe event
        
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
        done = input('Do you want to stop execution (enter T to stop, any other character to continue)?: ') == 'T'  #for running a certain number of tests
            
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

    # Run the ASM model
    ip, port, asm_path, asm_file_name = config_manager.get_server_params()
    enforcer = EnforcerExample(ip, port, asm_file_name)
    model_uploader = ModelUploader(ip, port, asm_path, asm_file_name)
    try:            
        run(enforcer,model_uploader)
    except Exception as e:
        # Try to run the tests again without the ASM model if at a certain point the server is down  
        logger.error("Failed to connect to the server - Executing the test runs WITHOUT the model")            
        run(None, None)
    #else:
    #    run(None, None)


