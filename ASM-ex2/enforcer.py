"""
    Author:      Nico Pellegrinelli, Patrizia Scandurra
    Created:     21/03/2025
"""
import time
import logging_manager
from rest_client import RestClient

class EnforcerExample(RestClient):    
    def __init__(self, ip, base_port, asm_name):
        """
        Initialize the Enforcer class.
        """
        super().__init__(ip, base_port)
        self.logger = logging_manager.get_logger(__name__)
        self.asm_name = asm_name
        self.exec_id = None
    
    def begin_enforcement(self):
        """
        Start a new execution of the ASM.
        """
        try:
            response = self._send_request("POST", "start", params={"name": self.asm_name})
            self.exec_id = response.json()["id"]
            self.logger.info(f"Execution started with ID: {self.exec_id}")
        except Exception as e:
            self.logger.error(f"Failed to start execution: {e}")
            raise

    def end_enforcement(self):
        """
        Stop the execution of the ASM.
        """
        try:
            self._send_request("DELETE", "stop-model", params={"id": str(self.exec_id)})
            self.logger.info(f"Execution stopped for ID: {self.exec_id}")
        except Exception as e:
            self.logger.error(f"Failed to stop execution: {e}")
            raise


    #Your output sanitization logic goes here. This is application-specific and depends on the
    #I/O interfaces (and also on Probe/Effector interfaces in case of gray-box enforcement).
    def sanitise_output(self, input_dict):
        """
        Perform a step on the ASM and repair (if necessar) the system action (i.e. output sanitisation).
        """
        endpoint = "step"
        json_data = {}
        json_data["id"] = self.exec_id
        json_data["monitoredVariables"] = input_dict    
        system_out_action =  input_dict["inputAction"]  
        try:
            start_time = time.perf_counter()
            response = self._send_request("PUT", endpoint, json=json_data)
            delay = (time.perf_counter() - start_time) * 1000
            self.logger.info(f"ASM step performed for ID {self.exec_id} with delay {delay:.2f} ms")
            if not response.json()["runOutput"]["outvalues"]: # outAction not set (should never happen)
                self.logger.error("The Enforcer returned no outAction but should always return something")
                self.logger.info(f"System Output: {system_out_action}")
                return None
            enforced_action = response.json()["runOutput"]["outvalues"]["outAction"]
            if enforced_action == input_dict["inputAction"]:
                self.logger.info("Enforcer not applied - keeping input action")
                self.logger.info(f"System Output: {system_out_action}")
                return None
            else:
                self.logger.info("Enforcer applied - changing action")
            self.logger.info(f"System Output: {system_out_action}")
            self.logger.info(f"After Safety Enforcement: {enforced_action}")
            return enforced_action
        except Exception as e:
            self.logger.error("ASM step execution failed: %s", e)
            raise    
        