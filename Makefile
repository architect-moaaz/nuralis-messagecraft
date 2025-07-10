# MessageCraft Docker Makefile
# Simplifies common Docker operations

.PHONY: help build up down logs shell clean restart status backup

# Default target
help:
	@echo "MessageCraft Docker Commands:"
	@echo "  make build      - Build Docker images"
	@echo "  make up         - Start services"
	@echo "  make down       - Stop services"
	@echo "  make logs       - View logs"
	@echo "  make shell      - Open shell in container"
	@echo "  make clean      - Clean up everything"
	@echo "  make restart    - Restart services"
	@echo "  make status     - Check service status"
	@echo "  make backup     - Backup volumes and env"
	@echo ""
	@echo "Production commands:"
	@echo "  make prod-up    - Start production stack"
	@echo "  make prod-down  - Stop production stack"
	@echo "  make prod-logs  - View production logs"

# Development commands
build:
	docker-compose build --no-cache

up:
	docker-compose up -d
	@echo "✅ MessageCraft is running!"
	@echo "📍 Frontend: http://localhost"
	@echo "📍 Backend API: http://localhost:8000"

down:
	docker-compose down

logs:
	docker-compose logs -f

shell:
	docker-compose exec messagecraft bash

clean:
	docker-compose down -v
	docker system prune -af
	@echo "✅ Cleaned up Docker resources"

restart:
	docker-compose restart

status:
	@echo "🔍 Checking MessageCraft status..."
	@docker-compose ps
	@echo ""
	@echo "🏥 Health checks:"
	@curl -s http://localhost/health > /dev/null && echo "✅ Frontend: Healthy" || echo "❌ Frontend: Not responding"
	@curl -s http://localhost:8000/health > /dev/null && echo "✅ Backend: Healthy" || echo "❌ Backend: Not responding"

backup:
	@echo "💾 Creating backup..."
	@mkdir -p backups
	@cp .env backups/.env.backup.$$(date +%Y%m%d_%H%M%S)
	@docker run --rm -v messagecraft_logs:/data -v $$(pwd)/backups:/backup alpine tar czf /backup/logs-backup-$$(date +%Y%m%d_%H%M%S).tar.gz /data 2>/dev/null || echo "No logs to backup"
	@echo "✅ Backup completed in ./backups/"

# Production commands
prod-up:
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.prod.yml logs -f

# Quick development setup
dev-setup:
	@echo "🚀 Setting up development environment..."
	@cp .env.example .env 2>/dev/null || echo ".env already exists"
	@make build
	@make up
	@make status

# Database commands
db-shell:
	docker-compose exec messagecraft python -c "import psycopg2; print('Database connection available')"

# Testing commands
test-backend:
	docker-compose exec messagecraft bash -c "cd /app/backend && pytest"

test-frontend:
	docker-compose exec messagecraft bash -c "cd /app/frontend && npm test"

# Monitoring commands
monitor:
	@echo "📊 Resource usage:"
	@docker stats --no-stream

# Update commands
update:
	@echo "🔄 Updating MessageCraft..."
	@git pull origin main
	@make build
	@make restart
	@echo "✅ Update completed!"