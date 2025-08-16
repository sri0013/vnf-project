FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy the encryption gateway VNF script
COPY encryption_gateway.py /app/

# Run the encryption gateway VNF
CMD ["python", "-u", "encryption_gateway.py"]
