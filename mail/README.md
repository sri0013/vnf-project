# Mail Server VNF

This is a mail server VNF (Virtual Network Function) that provides an SMTP debug server for testing email flows through the Service Function Chain.

## Features

- **SMTP Debug Server**: Uses `aiosmtpd` to provide a simple SMTP server for testing
- **Port 2525**: Runs on port 2525 to avoid requiring root privileges
- **Python 3.11**: Based on Python 3.11 slim image for compatibility
- **Pre-installed**: SMTP server is baked into the container image

## Usage

### Building the Image

```bash
cd mail
docker build -t my-mail-vnf .
```

### Running the Container

```bash
docker run -d --name vnf-mail --network bridge my-mail-vnf
```

### Testing SMTP Connection

From Mininet CLI:
```bash
mininet> h1 telnet 10.0.0.100 2525
```

### Viewing Logs

```bash
docker logs vnf-mail
```

## Integration with SFC

The mail server is integrated into the Service Function Chain as the final destination for email traffic:

```
Client → Firewall → Antivirus → Spam Filter → Encryption → Content Filter → Mail Server
```

## SMTP Commands

Once connected via telnet, you can test SMTP commands:

```
HELO client.example.com
MAIL FROM: sender@example.com
RCPT TO: recipient@example.com
DATA
Subject: Test Email
This is a test email body.
.
QUIT
```

The `aiosmtpd` server will log all SMTP interactions for debugging purposes.
