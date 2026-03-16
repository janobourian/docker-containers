# Use the official Ollama image as a base
FROM ollama/ollama:latest

# Set an environment variable for the desired coding model
# You can replace deepseek-coder with other models like codellama, llama3.1, etc.
ENV OLLAMA_MODEL="deepseek-coder-v2:16b"

# Copy a script into the container to handle model pulling and serving
COPY ./start_ollama.sh /usr/local/bin/start_ollama.sh

# Make the script executable
RUN chmod +x /usr/local/bin/start_ollama.sh

# Expose the default Ollama port
EXPOSE 11434

# Set the entrypoint to run the startup script
ENTRYPOINT ["/usr/local/bin/start_ollama.sh"]
