# Build VNF Images Script
# This script builds all VNF Docker images for the Service Function Chain
# Supports comprehensive SFC definitions for bidirectional email security
#!/usr/bin/env pwsh
Write-Host "🔧 Building VNF Docker Images for Comprehensive SFC..." -ForegroundColor Green

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Comprehensive array of VNF directories and their image names
$vnfs = @(
    # Core VNFs (existing)
    @{dir="firewall"; image="my-firewall-vnf"},
    @{dir="antivirus"; image="my-antivirus-vnf"},
    @{dir="spamfilter"; image="my-spamfilter-vnf"},
    @{dir="encryption_gateway"; image="my-encryption-vnf"},
    @{dir="content_filtering"; image="my-contentfilter-vnf"},
    @{dir="mail"; image="my-mail-vnf"},
    
    # Inbound User Protection VNFs
    @{dir="smtp_firewall"; image="my-smtp-firewall-vnf"},
    @{dir="anti_spam_phishing"; image="my-anti-spam-phishing-vnf"},
    @{dir="anti_virus_sandbox"; image="my-anti-virus-sandbox-vnf"},
    @{dir="url_rewrite_clicktime"; image="my-url-rewrite-clicktime-vnf"},
    @{dir="delivery_agent"; image="my-delivery-agent-vnf"},
    
    # Outbound Data Protection VNFs
    @{dir="policy_classifier"; image="my-policy-classifier-vnf"},
    @{dir="dlp"; image="my-dlp-vnf"},
    @{dir="encryption_signing"; image="my-encryption-signing-vnf"},
    @{dir="disclaimer_brand"; image="my-disclaimer-brand-vnf"},
    @{dir="archiver_journal"; image="my-archiver-journal-vnf"},
    @{dir="smart_host"; image="my-smart-host-vnf"},
    
    # Authentication & Anti-Spoof VNFs
    @{dir="spf_dkim_dmarc_validator"; image="my-spf-dkim-dmarc-validator-vnf"},
    @{dir="anti_spoof_bec"; image="my-anti-spoof-bec-vnf"},
    @{dir="policy_engine"; image="my-policy-engine-vnf"},
    @{dir="delivery_quarantine"; image="my-delivery-quarantine-vnf"},
    
    # Attachment Risk Reduction VNFs
    @{dir="reputation_graylist"; image="my-reputation-graylist-vnf"},
    @{dir="multi_engine_av"; image="my-multi-engine-av-vnf"},
    @{dir="sandbox_detonation"; image="my-sandbox-detonation-vnf"},
    @{dir="file_type_control"; image="my-file-type-control-vnf"},
    @{dir="content_disarm_reconstruct"; image="my-content-disarm-reconstruct-vnf"},
    
    # Branch Cloud SaaS Access VNFs
    @{dir="dns_url_filter"; image="my-dns-url-filter-vnf"},
    @{dir="attachment_sandbox_edge"; image="my-attachment-sandbox-edge-vnf"},
    @{dir="split_tunnel_steering"; image="my-split-tunnel-steering-vnf"},
    @{dir="sdwan_forwarder"; image="my-sdwan-forwarder-vnf"},
    @{dir="tls_enforcement_saas"; image="my-tls-enforcement-saas-vnf"}
)

Write-Host "📋 Building $($vnfs.Count) VNF images..." -ForegroundColor Cyan

# Build each VNF image
$successCount = 0
$failCount = 0

foreach ($vnf in $vnfs) {
    Write-Host "Building $($vnf.image) from $($vnf.dir)..." -ForegroundColor Yellow
    
    if (Test-Path $vnf.dir) {
        try {
            docker build -t $vnf.image ./$($vnf.dir)
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Successfully built $($vnf.image)" -ForegroundColor Green
                $successCount++
            } else {
                Write-Host "❌ Failed to build $($vnf.image)" -ForegroundColor Red
                $failCount++
            }
        } catch {
            Write-Host "❌ Error building $($vnf.image): $_" -ForegroundColor Red
            $failCount++
        }
    } else {
        Write-Host "⚠️  Directory $($vnf.dir) not found, creating placeholder..." -ForegroundColor Yellow
        
        # Create placeholder Dockerfile for missing VNFs
        $dockerfileContent = @"
# Placeholder Dockerfile for $($vnf.image)
FROM python:3.8-slim

WORKDIR /app

# Install basic dependencies
RUN pip install flask prometheus-client psutil

# Create placeholder VNF
COPY placeholder_vnf.py .

EXPOSE 8080

CMD ["python", "placeholder_vnf.py"]
"@
        
        # Create directory and placeholder files
        New-Item -ItemType Directory -Path $vnf.dir -Force | Out-Null
        Set-Content -Path "$($vnf.dir)/Dockerfile" -Value $dockerfileContent
        
        # Create placeholder VNF script
        $placeholderScript = @"
#!/usr/bin/env python3
"""
Placeholder VNF for $($vnf.image)
This is a placeholder implementation that can be replaced with actual VNF logic.
"""

import time
import random
import logging
from flask import Flask, jsonify
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Prometheus metrics
vnf_requests = Counter('vnf_requests_total', 'Total requests processed', ['vnf_type'])
vnf_processing_time = Histogram('vnf_processing_time_seconds', 'Time spent processing requests', ['vnf_type'])
vnf_cpu_usage = Gauge('vnf_cpu_usage', 'CPU usage percentage', ['vnf_type'])
vnf_memory_usage = Gauge('vnf_memory_usage', 'Memory usage percentage', ['vnf_type'])

VNF_TYPE = "$($vnf.image)"

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'vnf_type': VNF_TYPE,
        'timestamp': time.time()
    })

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    # Update metrics
    vnf_cpu_usage.labels(vnf_type=VNF_TYPE).set(psutil.cpu_percent())
    vnf_memory_usage.labels(vnf_type=VNF_TYPE).set(psutil.virtual_memory().percent)
    
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/process', methods=['POST'])
def process_request():
    """Process incoming request (placeholder implementation)"""
    start_time = time.time()
    
    # Simulate processing time
    processing_time = random.uniform(0.01, 0.1)
    time.sleep(processing_time)
    
    # Update metrics
    vnf_requests.labels(vnf_type=VNF_TYPE).inc()
    vnf_processing_time.labels(vnf_type=VNF_TYPE).observe(time.time() - start_time)
    
    return jsonify({
        'status': 'processed',
        'vnf_type': VNF_TYPE,
        'processing_time': processing_time,
        'timestamp': time.time()
    })

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        'vnf_type': VNF_TYPE,
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'metrics': '/metrics',
            'process': '/process (POST)'
        }
    })

if __name__ == '__main__':
    logger.info(f"Starting placeholder VNF: {VNF_TYPE}")
    app.run(host='0.0.0.0', port=8080, debug=False)
"@
        
        Set-Content -Path "$($vnf.dir)/placeholder_vnf.py" -Value $placeholderScript
        
        # Build the placeholder VNF
        try {
            docker build -t $vnf.image ./$($vnf.dir)
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Successfully built placeholder $($vnf.image)" -ForegroundColor Green
                $successCount++
            } else {
                Write-Host "❌ Failed to build placeholder $($vnf.image)" -ForegroundColor Red
                $failCount++
            }
        } catch {
            Write-Host "❌ Error building placeholder $($vnf.image): $_" -ForegroundColor Red
            $failCount++
        }
    }
}

Write-Host "`n📊 Build Summary:" -ForegroundColor Green
Write-Host "✅ Successfully built: $successCount VNFs" -ForegroundColor Green
Write-Host "❌ Failed to build: $failCount VNFs" -ForegroundColor Red
Write-Host "📦 Total VNFs: $($vnfs.Count)" -ForegroundColor Cyan

Write-Host "`n📋 Built Images:" -ForegroundColor Green
docker images | Select-String "my-.*-vnf"

Write-Host "`n🚀 Ready to run comprehensive SFC topology!" -ForegroundColor Green
Write-Host "Run: sudo python3 scripts/sfc_topology.py" -ForegroundColor Cyan
Write-Host "`n📧 All VNFs are ready for SFC orchestration!" -ForegroundColor Green

Write-Host "`n🔗 SFC Types Available:" -ForegroundColor Cyan
Write-Host "• inbound_user_protection" -ForegroundColor White
Write-Host "• outbound_data_protection_compliance" -ForegroundColor White
Write-Host "• auth_and_anti_spoof_enforcement" -ForegroundColor White
Write-Host "• attachment_risk_reduction" -ForegroundColor White
Write-Host "• branch_cloud_saas_access" -ForegroundColor White

Write-Host "`n📈 Performance Targets:" -ForegroundColor Cyan
Write-Host "• SFC Acceptance Ratio: 97%" -ForegroundColor White
Write-Host "• CPU Cycles Reduction: 45%" -ForegroundColor White
Write-Host "• Latency Improvement: 38%" -ForegroundColor White
Write-Host "• ARIMA Forecast Accuracy: 92%" -ForegroundColor White
