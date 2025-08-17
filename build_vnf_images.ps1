# Build VNF Images Script
# This script builds all VNF Docker images for the Service Function Chain

Write-Host "🔧 Building VNF Docker Images..." -ForegroundColor Green

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Array of VNF directories and their image names
$vnfs = @(
    @{dir="firewall"; image="my-firewall-vnf"},
    @{dir="antivirus"; image="my-antivirus-vnf"},
    @{dir="spamfilter"; image="my-spamfilter-vnf"},
    @{dir="encryption_gateway"; image="my-encryption-vnf"},
    @{dir="content_filtering"; image="my-contentfilter-vnf"},
    @{dir="mail"; image="my-mail-vnf"}
)

# Build each VNF image
foreach ($vnf in $vnfs) {
    Write-Host "Building $($vnf.image) from $($vnf.dir)..." -ForegroundColor Yellow
    
    if (Test-Path $vnf.dir) {
        try {
            docker build -t $vnf.image ./$($vnf.dir)
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Successfully built $($vnf.image)" -ForegroundColor Green
            } else {
                Write-Host "❌ Failed to build $($vnf.image)" -ForegroundColor Red
            }
        } catch {
            Write-Host "❌ Error building $($vnf.image): $_" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️  Directory $($vnf.dir) not found, skipping..." -ForegroundColor Yellow
    }
}

Write-Host "`n📋 Built Images:" -ForegroundColor Green
docker images | Select-String "my-.*-vnf"

Write-Host "`n🚀 Ready to run SFC topology!" -ForegroundColor Green
Write-Host "Run: sudo python3 scripts/sfc_topology.py" -ForegroundColor Cyan
Write-Host "`n📧 Mail server VNF is ready for SMTP testing on port 2525!" -ForegroundColor Green
