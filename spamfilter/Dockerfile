FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy the spam filter VNF script
COPY spamfilter.py /app/

# Install Prometheus client
RUN pip install --no-cache-dir prometheus_client

# Expose metrics port
EXPOSE 8080

# Run the spam filter VNF
CMD ["python", "-u", "spamfilter.py"]
