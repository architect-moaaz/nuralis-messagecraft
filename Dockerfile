# MessageCraft Multi-Service Dockerfile
# This Dockerfile builds both frontend and backend services in a single container
# For production, consider using separate containers for each service

FROM python:3.12-slim AS backend-builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend requirements and install
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Frontend builder stage
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ .

# Build frontend
RUN npm run build

# Runtime stage - combines both services
FROM python:3.12-slim

# Install runtime dependencies including Node.js for process management
RUN apt-get update && apt-get install -y \
    curl \
    nginx \
    supervisor \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy backend from builder
COPY --from=backend-builder /app/backend /app/backend
COPY --from=backend-builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy frontend build from builder
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Copy nginx configuration
COPY frontend/nginx.conf /etc/nginx/sites-available/default

# Copy supervisor configuration
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy startup script
COPY docker/startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

# Create necessary directories
RUN mkdir -p /var/log/supervisor /var/log/nginx /app/logs

# Set permissions
RUN chown -R app:app /app && \
    chmod +x /app/startup.sh

# Create supervisor and nginx directories
RUN mkdir -p /var/run/supervisor && \
    chown -R app:app /var/log/supervisor

# Expose ports
EXPOSE 80 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health && curl -f http://localhost:8000/health || exit 1

# Start services using supervisor (runs as root for nginx)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]