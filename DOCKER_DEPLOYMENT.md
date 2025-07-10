# 🐳 Docker Deployment Guide

This guide explains how to deploy MessageCraft using Docker, with both single-container and multi-container options.

## 📋 Prerequisites

- Docker 20.10+ installed
- Docker Compose 2.0+ installed
- Environment variables configured
- At least 4GB RAM available

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/architect-moaaz/nuralis-messagecraft.git
cd messagecraft
```

### 2. Set Environment Variables
```bash
# Copy environment template
cp .env.example .env

# Edit with your values
nano .env
```

Required variables:
```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Database
DATABASE_URL=postgresql://postgres:password@host:5432/postgres

# AI Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 3. Build and Run
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Check health
curl http://localhost/health
```

## 🏗️ Architecture Options

### Option 1: Single Container (Default)
**Best for: Development, small deployments, testing**

```yaml
messagecraft:
  build: .
  ports:
    - "80:80"       # Frontend
    - "8000:8000"   # Backend API
```

**Advantages:**
- Simple deployment
- Lower resource usage
- Easy to manage
- Single build process

**Architecture:**
```
┌─────────────────────────────────┐
│      MessageCraft Container     │
├─────────────────────────────────┤
│  Nginx (Port 80)               │
│    ├── React Frontend          │
│    └── Proxy → Backend         │
├─────────────────────────────────┤
│  FastAPI (Port 8000)           │
│    └── AI Agent System         │
├─────────────────────────────────┤
│  Supervisor Process Manager     │
└─────────────────────────────────┘
```

### Option 2: Separate Containers
**Best for: Production, scalability, microservices**

Uncomment the separate services in `docker-compose.yml`:
```yaml
backend:
  build: ./backend
  ports:
    - "8000:8000"

frontend:
  build: ./frontend
  ports:
    - "80:80"
  depends_on:
    - backend
```

**Advantages:**
- Independent scaling
- Better resource isolation
- Easier debugging
- Follows microservices pattern

## 🔧 Configuration Details

### Dockerfile Structure
```dockerfile
# Multi-stage build for efficiency
FROM python:3.12-slim AS backend-builder
# Build backend dependencies

FROM node:18-alpine AS frontend-builder  
# Build frontend assets

FROM python:3.12-slim
# Combine both services with Nginx & Supervisor
```

### Key Configuration Files

#### `docker/nginx.conf`
- Serves React frontend on port 80
- Proxies `/api/*` requests to backend
- Enables gzip compression
- Adds security headers
- Handles SPA routing

#### `docker/supervisord.conf`
- Manages both services in single container
- Auto-restart on failure
- Centralized logging
- Process monitoring

#### `docker/startup.sh`
- Checks environment variables
- Waits for services to be ready
- Provides startup feedback
- Health check validation

## 📦 Building Images

### Build for Production
```bash
# Build with no cache for clean image
docker build --no-cache -t messagecraft:latest .

# Build with specific platform
docker build --platform linux/amd64 -t messagecraft:latest .

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t messagecraft:latest .
```

### Build Arguments
```bash
# Build with custom Python version
docker build --build-arg PYTHON_VERSION=3.11 -t messagecraft:latest .

# Build with npm registry
docker build --build-arg NPM_REGISTRY=https://registry.npmjs.org -t messagecraft:latest .
```

## 🚢 Deployment Commands

### Basic Operations
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f messagecraft

# Execute commands in container
docker-compose exec messagecraft bash
```

### Health Monitoring
```bash
# Check container health
docker-compose ps

# Check application health
curl http://localhost/health
curl http://localhost:8000/health

# View resource usage
docker stats messagecraft
```

### Debugging
```bash
# View supervisor status
docker-compose exec messagecraft supervisorctl status

# View nginx logs
docker-compose exec messagecraft tail -f /var/log/nginx/access.log

# View backend logs
docker-compose exec messagecraft tail -f /var/log/supervisor/backend.out.log

# Interactive shell
docker-compose exec messagecraft bash
```

## 🔐 Security Considerations

### 1. Run as Non-Root User
The Dockerfile creates and uses an `app` user:
```dockerfile
RUN useradd --create-home --shell /bin/bash app
USER app
```

### 2. Environment Variables
Never commit `.env` files. Use Docker secrets in production:
```bash
# Create secret
echo "your_api_key" | docker secret create anthropic_key -

# Use in compose
secrets:
  - anthropic_key
```

### 3. Network Isolation
Use custom networks for service communication:
```yaml
networks:
  messagecraft-network:
    driver: bridge
    internal: true  # For backend services
```

### 4. Resource Limits
Set resource constraints:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
    reservations:
      cpus: '1'
      memory: 2G
```

## 📊 Performance Optimization

### 1. Build Optimization
- Multi-stage builds reduce image size
- Layer caching for faster rebuilds
- Only copy necessary files

### 2. Runtime Optimization
```yaml
# Nginx performance tuning
worker_processes auto;
worker_connections 1024;

# Python optimization
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
```

### 3. Volume Mounting
```yaml
volumes:
  # Persist logs
  - ./logs:/app/logs
  
  # Development hot-reload
  - ./backend:/app/backend:ro
  - ./frontend/src:/app/frontend/src:ro
```

## 🔄 Updates and Maintenance

### Update Process
```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose build --no-cache

# Update running containers
docker-compose up -d

# Remove old images
docker image prune -f
```

### Backup Strategy
```bash
# Backup volumes
docker run --rm -v messagecraft_logs:/data -v $(pwd):/backup alpine tar czf /backup/logs-backup.tar.gz /data

# Backup environment
cp .env .env.backup.$(date +%Y%m%d)
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port
lsof -i :80
lsof -i :8000

# Change ports in docker-compose.yml
ports:
  - "8080:80"
  - "8001:8000"
```

#### 2. Container Won't Start
```bash
# Check logs
docker-compose logs messagecraft

# Check build errors
docker-compose build --no-cache

# Verify environment variables
docker-compose config
```

#### 3. API Connection Issues
```bash
# Check nginx config
docker-compose exec messagecraft nginx -t

# Test backend directly
docker-compose exec messagecraft curl http://localhost:8000/health

# Check supervisor
docker-compose exec messagecraft supervisorctl status
```

#### 4. Memory Issues
```bash
# Increase Docker memory limit
# Docker Desktop > Preferences > Resources

# Or use swap
docker-compose up -d --scale messagecraft=1 --memory=4g
```

## 🌐 Production Deployment

### 1. Use Production Image
```dockerfile
# Production Dockerfile
FROM python:3.12-slim as production
ENV ENVIRONMENT=production
```

### 2. Enable HTTPS
Use reverse proxy like Traefik or Nginx:
```yaml
traefik:
  image: traefik:v2.10
  command:
    - "--providers.docker=true"
    - "--entrypoints.websecure.address=:443"
    - "--certificatesresolvers.le.acme.tlschallenge=true"
```

### 3. Monitoring Stack
```yaml
prometheus:
  image: prom/prometheus
  
grafana:
  image: grafana/grafana
  
cadvisor:
  image: gcr.io/cadvisor/cadvisor
```

## 📝 Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SUPABASE_URL` | Supabase project URL | Yes | - |
| `SUPABASE_KEY` | Supabase anonymous key | Yes | - |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service key | Yes | - |
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | Yes | - |
| `ENVIRONMENT` | Environment (development/production) | No | production |
| `LOG_LEVEL` | Logging level | No | INFO |

## 🎯 Quick Commands Reference

```bash
# Development
docker-compose up                    # Start with logs
docker-compose up -d                 # Start detached
docker-compose logs -f               # View logs
docker-compose down                  # Stop and remove

# Production
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs

# Maintenance
docker system prune -a               # Clean everything
docker-compose pull                  # Update images
docker-compose build --pull          # Rebuild with latest
```

---

## 🚀 Ready to Deploy?

1. **Set your environment variables** in `.env`
2. **Run** `docker-compose up -d`
3. **Access** MessageCraft at `http://localhost`
4. **Monitor** with `docker-compose logs -f`

Need help? Check the logs or open an issue on GitHub! 🐳