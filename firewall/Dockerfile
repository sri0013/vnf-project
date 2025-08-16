FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy the firewall VNF script
COPY firewall.py /app/

# Run the firewall VNF
CMD ["python", "-u", "firewall.py"]
