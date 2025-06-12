"""
    Author:      Nico Pellegrinelli, Patrizia Scandurra
    Created:     21/03/2025
"""
import os
import requests
import subprocess

import logging_manager

class RestClient:
    def __init__(self, ip, base_port):
        """
        Initialize the rest client class and determine the local domain.
        """
        self.logger = logging_manager.get_logger(__name__)
        self.base_port = base_port
        self.api_base_url = self._resolve_api_endpoint(ip)


    def _resolve_api_endpoint(self, ip):
        """
        Determine the local domain dynamically, especially for WSL environments, or use the input ip parameter if it is not None.
        """
        if ip is not None:
            return f"http://{ip}:{self.base_port}/"
        if "WSL_INTEROP" in os.environ:
            try:
                result = subprocess.run(
                    ["ip", "route"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                '''
                Example of 'ip route' command on WSL:
                    default via 172.25.16.1 dev eth0 proto kernel
                    172.25.16.0/20 dev eth0 proto kernel scope link src 172.25.31.78
                '''
                for line in result.stdout.splitlines():
                    if "default" in line:
                        return f"http://{line.split()[2]}:{self.base_port}/"
            except subprocess.SubprocessError as e:
                self.logger.error(f"Failed to determine WSL IP: {e}")
        return f"http://localhost:{self.base_port}/"

    def _send_request(self, method, endpoint, **kwargs):
        """
        A helper method for sending HTTP requests with error handling.
        """
        url = self.api_base_url + endpoint
        try:
            response = requests.request(method, url, timeout=10, **kwargs)
            response.raise_for_status()
            return response
        except requests.Timeout as e:
            self.logger.error(f"HTTP Request timed out: {e}")
            raise
        except requests.RequestException as e:
            self.logger.error(f"HTTP Request failed: {e}")
            raise