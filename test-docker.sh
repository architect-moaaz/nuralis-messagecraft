#!/bin/bash
# Quick Docker test script for MessageCraft

set -e

echo "🐳 Testing MessageCraft Docker Setup"
echo "======================================"

# Check if required files exist
echo "📁 Checking required files..."
required_files=(
    "backend/requirements.txt"
    "frontend/package.json"
    "frontend/nginx.conf"
    "docker/supervisord.conf"
    "Dockerfile.simple"
    "docker-compose.yml"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

echo ""
echo "🔧 Building Docker image..."
docker build -f Dockerfile.simple -t messagecraft-test . || {
    echo "❌ Docker build failed"
    exit 1
}

echo ""
echo "✅ Docker build successful!"
echo ""
echo "🚀 To run the container:"
echo "   docker run -p 80:80 -p 8000:8000 messagecraft-test"
echo ""
echo "🐳 Or use docker-compose:"
echo "   docker-compose up -d"
echo ""
echo "📍 Access points:"
echo "   Frontend: http://localhost"
echo "   Backend:  http://localhost:8000"
echo "   Health:   http://localhost/health"