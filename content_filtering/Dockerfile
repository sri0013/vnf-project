FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy the content filtering VNF script
COPY content_filtering.py /app/

# Install Prometheus client
RUN pip install --no-cache-dir prometheus_client

# Expose metrics port
EXPOSE 8080

# Run the content filtering VNF
CMD ["python", "-u", "content_filtering.py"]
