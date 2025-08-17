FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy the firewall VNF script
COPY firewall.py /app/

# Install Prometheus client
RUN pip install --no-cache-dir prometheus_client

# Expose metrics port
EXPOSE 8080

# Run the firewall VNF
CMD ["python", "-u", "firewall.py"]
