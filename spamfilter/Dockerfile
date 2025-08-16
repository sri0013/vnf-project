FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy the spam filter VNF script
COPY spamfilter.py /app/

# Run the spam filter VNF
CMD ["python", "-u", "spamfilter.py"]
