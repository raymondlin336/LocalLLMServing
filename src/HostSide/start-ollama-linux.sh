#!/bin/bash

PORT=11434

# Check if port is in use
if ss -ltn | grep -q ":$PORT "; then
    ip=$(ss -ltn | awk -v p=":$PORT" '$4 ~ p {print $4}' | head -n1 | cut -d':' -f1)
    echo "Ollama is already launched on $ip:$PORT"
else
    export OLLAMA_HOST=0.0.0.0:$PORT
    echo "Starting Ollama on $OLLAMA_HOST..."
    ollama serve
fi
