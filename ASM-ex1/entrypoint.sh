#!/bin/sh

echo "Starting Client Proxy in background..."
python client_proxy.py &> /proc/1/fd/1 &

sleep 3

echo "Starting main client (main.py)..."
python main.py

echo "Client terminated. The container will stop."