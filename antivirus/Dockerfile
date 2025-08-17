FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy the antivirus VNF script
COPY antivirus.py /app/

# Install Prometheus client
RUN pip install --no-cache-dir prometheus_client

# Expose metrics port
EXPOSE 8080

# Run the antivirus VNF
CMD ["python", "-u", "antivirus.py"]
