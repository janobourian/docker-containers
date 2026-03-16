#!/bin/bash

# Start Ollama server in the background
ollama serve &

# Wait for the Ollama server to start
sleep 5

# Pull the desired model using the environment variable
echo "Pulling $OLLAMA_MODEL model..."
ollama pull $OLLAMA_MODEL

# Keep the container running in the foreground
wait -n
