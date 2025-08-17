FROM python:3.11-slim

# Install the aiosmtpd package at build time
RUN pip install aiosmtpd

# Expose SMTP port
EXPOSE 2525

# Start the SMTP debug server on container startup
CMD ["python3", "-m", "aiosmtpd", "-n", "-l", "0.0.0.0:2525"]
