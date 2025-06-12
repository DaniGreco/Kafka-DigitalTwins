"""
    Author:      Nico Pellegrinelli, Patrizia Scandurra
    Created:     21/03/2025
"""
import json
import logging_manager

class ConfigurationManager:
    def __init__(self, config_file):
        self.logger = logging_manager.get_logger(__name__)
        with open(config_file) as json_file:
            self.json_data = json.load(json_file)

    
    def get_runtime_model(self):
        return self.json_data["asmeta_server"]["runtime_model"]
    
    def get_server_params(self):
        enf_param = self.json_data["asmeta_server"]
        return enf_param.get("ip", None), enf_param["base_port"], enf_param["spec_path"], enf_param["runtime_model"]

    def get_logging_params(self):
        log_param = self.json_data["logging"]
        return log_param["level"], log_param["target_folder"]
    
    
    def log_configuration(self):
        self.logger.info("Configuration: ")
        self.logger.info(f"* Runtime ASM model: {self.json_data['asmeta_server']['runtime_model']}")

    