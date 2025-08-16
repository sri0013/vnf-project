FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy the content filtering VNF script
COPY content_filtering.py /app/

# Run the content filtering VNF
CMD ["python", "-u", "content_filtering.py"]
