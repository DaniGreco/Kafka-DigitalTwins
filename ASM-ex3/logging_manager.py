"""
    Author:      Nico Pellegrinelli
    Created:     21/03/2025
"""
import logging
from datetime import datetime
import os

def setup_logging(log_level, log_folder, execution_id):
    os.makedirs(log_folder, exist_ok=True)
    log_file = f"{log_folder}/log_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{execution_id}.log"
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logging.info("Logging has been configured.")

def get_logger(name):
    return logging.getLogger(name)