#!/bin/bash
# ======================================
# QStream Production Deployment Script
# DigitalOcean VPS: 178.128.55.142
# ======================================

set -e  # Exit on error

echo "🚀 Starting QStream Production Deployment..."
echo "=============================================="

# Check if running as root or with sudo
if [ "$EUID" -eq 0 ]; then 
    echo "✅ Running with sudo privileges"
else
    echo "⚠️  Please run with sudo: sudo bash deploy.sh"
    exit 1
fi

# 1. Update system packages
echo ""
echo "📦 Step 1: Updating system packages..."
apt update && apt upgrade -y

# 2. Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo ""
    echo "🐳 Step 2: Installing Docker..."
    apt install -y docker.io docker-compose
    systemctl enable docker
    systemctl start docker
else
    echo ""
    echo "✅ Docker already installed"
fi

# 3. Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo ""
    echo "🐳 Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    echo ""
    echo "✅ Docker Compose already installed"
fi

# 4. Clone repository (if not exists)
if [ ! -d "/opt/qstream" ]; then
    echo ""
    echo "📥 Step 3: Cloning repository..."
    echo "⚠️  Please enter your Git repository URL:"
    read -p "Git URL: " GIT_URL
    git clone "$GIT_URL" /opt/qstream
    cd /opt/qstream
else
    echo ""
    echo "✅ Repository already exists, pulling latest changes..."
    cd /opt/qstream
    git pull origin main
fi

# 5. Setup environment file
echo ""
echo "⚙️  Step 4: Setting up environment..."
if [ ! -f ".env.production" ]; then
    echo "❌ ERROR: .env.production file not found!"
    echo "Please create .env.production with your configuration"
    exit 1
else
    cp .env.production .env
    echo "✅ Environment file configured"
fi

# 6. Stop existing containers
echo ""
echo "🛑 Step 5: Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || true

# 7. Build and start containers
echo ""
echo "🏗️  Step 6: Building containers..."
docker-compose -f docker-compose.prod.yml --env-file .env.production build --no-cache

echo ""
echo "🚀 Step 7: Starting containers..."
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d

# 8. Wait for services to be healthy
echo ""
echo "⏳ Step 8: Waiting for services to be ready..."
sleep 10

# 9. Check container status
echo ""
echo "📊 Step 9: Checking container status..."
docker-compose -f docker-compose.prod.yml ps

# 10. Show logs
echo ""
echo "📋 Recent logs:"
docker-compose -f docker-compose.prod.yml logs --tail=20

echo ""
echo "=============================================="
echo "✅ Deployment Complete!"
echo "=============================================="
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://178.128.55.142:3000"
echo "   Backend:  http://178.128.55.142:8000"
echo "   API Docs: http://178.128.55.142:8000/docs"
echo ""
echo "📊 Useful commands:"
echo "   View logs:    docker-compose -f docker-compose.prod.yml logs -f"
echo "   Restart:      docker-compose -f docker-compose.prod.yml restart"
echo "   Stop:         docker-compose -f docker-compose.prod.yml down"
echo "   Status:       docker-compose -f docker-compose.prod.yml ps"
echo ""
echo "🔐 Important: Update firewall rules to allow:"
echo "   - Port 3000 (Frontend)"
echo "   - Port 8000 (Backend API)"
echo ""
