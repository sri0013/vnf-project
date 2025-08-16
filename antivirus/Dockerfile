FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy the antivirus VNF script
COPY antivirus.py /app/

# Run the antivirus VNF
CMD ["python", "-u", "antivirus.py"]
