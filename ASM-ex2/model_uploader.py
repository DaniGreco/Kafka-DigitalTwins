"""
    Author:      Nico Pellegrinelli, Patrizia Scandurra
    Created:     21/03/2025
"""
import os
import logging_manager
from rest_client import RestClient

class ModelUploader(RestClient):
    def __init__(self, ip, base_port, asm_base_path, asm_name):
        """
        Initialize the ModelUploader class.
        """
        super().__init__(ip, base_port)
        self.logger = logging_manager.get_logger(__name__)
        self.asm_name = asm_name
        self.stdl_name = "StandardLibrary.asm"
        #self.ltl_name = "LTLLibrary.asm"
        libraries_base_path = os.path.join(asm_base_path, "..", "libraries")
        self.asm_path = os.path.join(asm_base_path, self.asm_name)
        self.stdl_path = os.path.join(libraries_base_path, self.stdl_name)
        #self.ltl_path = os.path.join(libraries_base_path, self.ltl_name)
        self.logger.info(f"Model engine initialized with domain: {self.api_base_url}")
        self.logger.info(f"Runtime model: {self.asm_name}")
        self.logger.info("")

    def _upload_file(self, endpoint, file_path):
        """
        Helper method to upload a file to a specific endpoint.
        """
        with open(file_path, "rb") as file:
            files = {"file": file}
            self._send_request("POST", endpoint, files=files)
        self.logger.info(f"Uploaded file: {file_path}")

    def upload_runtime_model(self):
        """
        Upload the model and standard library if not already present.
        """
        try:
            self._upload_file("upload-model", self.asm_path)
            response = self._send_request("GET", "model-list")
            libraries = response.json().get("libraries")
            if self.stdl_name not in libraries:
                self._upload_file("upload-library", self.stdl_path)
           # if self.ltl_name not in libraries:
           #     self._upload_file("upload-library", self.ltl_path)
        except Exception as e:
            self.logger.error(f"Failed to upload model or library: {e}")
            raise

    def delete_runtime_model(self):
        """
        Delete the model from the server and the libraries.
        """
        try:
            self._send_request("DELETE", "delete-model", params={"name": self.asm_name})
            self.logger.info(f"Model deleted: {self.asm_name}")    
            response = self._send_request("GET", "model-list")       
            libraries = response.json().get("libraries")
            if self.stdl_name in libraries:
                self._send_request("DELETE", "delete-library", params={"name": self.stdl_name})
          #  if self.ltl_name in libraries:
          #      self._send_request("DELETE", "delete-library", params={"name": self.ltl_name})
        except Exception as e:
            self.logger.error(f"Failed to delete model: {e}")
            raise