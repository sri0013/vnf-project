# VNF Service Function Chain (SFC) Project

## Overview
This project implements a complete Service Function Chain (SFC) for email security using Virtual Network Functions (VNFs). The SFC processes email traffic through a chain of security functions: Firewall → Antivirus → Spam Filter → Encryption Gateway → Content Filtering.

## Architecture
```
Email Flow: Host → [VNF Chain] → Mail Server → [VNF Chain] → Destination
VNF Chain: Firewall → Antivirus → Spam Filter → Encryption → Content Filter → Mail Server
```

## Diagram workflow (CLI + Git)
- Generate/update the PlantUML diagram source from the template:
  - Linux/macOS:
    ```bash
    ./gen.sh "DRL-Based SFC Provisioning with Forecasting & Monitoring"
    ```
  - Windows (PowerShell):
    ```powershell
    ./gen.ps1 -Title "DRL-Based SFC Provisioning with Forecasting & Monitoring"
    ```
- If PlantUML is installed, the scripts auto-render an image; otherwise, render manually:
  ```bash
  plantuml diagram.puml
  ```
- Commit and push:
  ```bash
  git add diagram.puml
  git commit -m "feat: update architecture diagram"
  git push
  ```

## Project Structure
```
vnf-project/
├── firewall/              # Firewall VNF - IP/Port filtering
├── antivirus/             # Antivirus VNF - Virus scanning
├── spamfilter/            # Spam Filter VNF - Spam detection
├── encryption_gateway/    # Encryption VNF - Email encryption/decryption
├── content_filtering/     # Content Filter VNF - Policy enforcement
├── mail/                  # Mail Server VNF - SMTP debug server
├── scripts/               # Mininet topology and orchestration
└── README.md
```

## VNF Functions

### 1. Firewall VNF
- **Purpose**: Network-level security filtering
- **Functions**: 
  - Blocks malicious IP addresses
  - Controls port access (SMTP, HTTP, HTTPS)
  - Logs all traffic decisions
- **Processing**: Real-time packet inspection

### 2. Antivirus VNF
- **Purpose**: Content-based virus detection
- **Functions**:
  - Scans email content for virus signatures
  - Uses MD5 hash matching for known threats
  - Quarantines infected content
- **Processing**: Deep packet inspection

### 3. Spam Filter VNF
- **Purpose**: Email spam detection and filtering
- **Functions**:
  - Keyword-based spam detection
  - Domain reputation checking
  - Content length analysis
  - Spam scoring system
- **Processing**: Email header and content analysis

### 4. Encryption Gateway VNF
- **Purpose**: Email encryption and decryption
- **Functions**:
  - Encrypts outgoing emails
  - Decrypts incoming emails
  - Manages encryption keys
  - Ensures data confidentiality
- **Processing**: Content transformation

### 5. Content Filtering VNF
- **Purpose**: Data loss prevention and policy enforcement
- **Functions**:
  - Detects sensitive data patterns (credit cards, SSNs)
  - Enforces content policies
  - Prevents data leakage
  - Compliance monitoring
- **Processing**: Pattern matching and policy validation

### 6. Mail Server VNF
- **Purpose**: SMTP debug server for email testing
- **Functions**:
  - Provides SMTP server on port 2525
  - Accepts and logs email connections
  - Uses aiosmtpd for debugging
  - No root privileges required
- **Processing**: Email reception and logging

## Deployment Instructions

### Quick run of Prometheus and Grafana (VM/WSL2 + Windows access)
- Open a Linux VM or WSL2 shell and run:
  
  cd ~/vnf-project/orchestration
  
  docker compose up -d
  
  If using Docker Compose v1:
  
  docker-compose up -d

- Access dashboards:
  - From VM/WSL2: Prometheus http://localhost:9090, Grafana http://localhost:3000 (admin/admin)
  - From Windows host:
    - WSL2: http://localhost:9090 and http://localhost:3000
    - Full VM: find the VM IP (ip addr shows 192.168.x.x) then use http://192.168.x.x:9090 and http://192.168.x.x:3000
    - If needed, enable Bridged networking or port forwarding in the VM settings.

See orchestration/README.md for details and troubleshooting.

### Prerequisites
- Docker installed
- Python 3.8+
- Mininet (for network simulation)
- Git

### Step 1: Build Docker Images (Windows)
```bash
# Build all VNF images
cd firewall && docker build -t my-firewall-vnf .
cd ../antivirus && docker build -t my-antivirus-vnf .
cd ../spamfilter && docker build -t my-spamfilter-vnf .
cd ../encryption_gateway && docker build -t my-encryption-vnf .
cd ../content_filtering && docker build -t my-contentfilter-vnf .
cd ../mail && docker build -t my-mail-vnf .
```

# Or use the build script:
./build_vnf_images.ps1

### Step 2: Push to Docker Hub (Windows)
```bash
# Tag images for Docker Hub
docker tag my-firewall-vnf yourusername/vnf-firewall:latest
docker tag my-antivirus-vnf yourusername/vnf-antivirus:latest
docker tag my-spamfilter-vnf yourusername/vnf-spamfilter:latest
docker tag my-encryption-vnf yourusername/vnf-encryption:latest
docker tag my-contentfilter-vnf yourusername/vnf-contentfilter:latest

# Push to Docker Hub
docker push yourusername/vnf-firewall:latest
docker push yourusername/vnf-antivirus:latest
docker push yourusername/vnf-spamfilter:latest
docker push yourusername/vnf-encryption:latest
docker push yourusername/vnf-mail:latest
docker push yourusername/vnf-contentfilter:latest
```

### Step 3: Deploy on Linux/Ubuntu VM
```bash
# Pull images from Docker Hub
docker pull yourusername/vnf-firewall:latest
docker pull yourusername/vnf-antivirus:latest
docker pull yourusername/vnf-spamfilter:latest
docker pull yourusername/vnf-encryption:latest
docker pull yourusername/vnf-contentfilter:latest

# Tag for local use
docker tag yourusername/vnf-firewall:latest my-firewall-vnf
docker tag yourusername/vnf-antivirus:latest my-antivirus-vnf
docker tag yourusername/vnf-spamfilter:latest my-spamfilter-vnf
docker tag yourusername/vnf-encryption:latest my-encryption-vnf
docker tag yourusername/vnf-contentfilter:latest my-contentfilter-vnf
```

### Step 4: Run SFC Network
```bash
# Make script executable
chmod +x scripts/sfc_topology.py

# Run the SFC network
sudo python3 scripts/sfc_topology.py
```

## Monitoring and Testing

### View VNF Logs
```bash
# Monitor individual VNF logs
docker logs vnf-firewall
docker logs vnf-antivirus
docker logs vnf-spamfilter
docker logs vnf-encryption
docker logs vnf-contentfilter
```

### Test Network Connectivity
```bash
# From Mininet CLI
h1 ping 10.0.0.100  # Test connectivity to mail server
h1 telnet 10.0.0.100 2525  # Test SMTP connection (port 2525)
```

### Test Mail Server Locally (Windows)
```powershell
# Test if mail server is accessible
Test-NetConnection -ComputerName localhost -Port 2525

# Run mail server container for local testing
docker run -d --name vnf-mail-test -p 2525:2525 my-mail-vnf
```

### Simulate Email Flow
The VNFs automatically simulate email processing:
- Firewall: Tests IP/port filtering
- Antivirus: Scans for virus signatures
- Spam Filter: Detects spam patterns
- Encryption: Encrypts/decrypts content
- Content Filter: Enforces policies

## Network Topology
- **Hosts**: h1(10.0.0.1), h2(10.0.0.2), h3(10.0.0.3), h4(10.0.0.4)
- **Mail Server**: mail(10.0.0.100)
- **Switches**: s1 (entry), s2 (exit)
- **Bandwidth**: 10Mbps for hosts, 100Mbps for SFC path

## Security Features
- **Network Security**: Firewall protection
- **Content Security**: Antivirus scanning
- **Spam Protection**: Intelligent filtering
- **Data Protection**: Encryption/decryption
- **Compliance**: Content policy enforcement

## Troubleshooting
1. **VNF not starting**: Check Docker logs and image availability
2. **Network connectivity issues**: Verify Mininet topology
3. **Permission errors**: Ensure sudo access for Mininet
4. **Container conflicts**: Stop and remove existing containers
5. **Docker not running**: Start Docker Desktop and wait for initialization
6. **SMTP connection issues**: Verify port 2525 is accessible and container is running
7. **Orchestrator PermissionError on /var/run/docker.sock**: The compose file mounts the Docker socket and now runs the orchestrator as root (user: root). Make sure Docker Desktop is using the Linux backend (WSL2) so the Unix socket is available inside Linux containers.

## Development
- Each VNF is containerized for easy deployment
- VNFs communicate through Docker networking
- Logs provide real-time monitoring
- Modular design allows easy VNF addition/removal

## License
This project is for educational and research purposes.
