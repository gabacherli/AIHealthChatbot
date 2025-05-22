# AI Health Chatbot - Docker Management

.PHONY: help build up down logs restart clean dev prod test setup status logs-backend logs-frontend shell-backend shell-frontend

# Default target
help:
	@echo "AI Health Chatbot - Docker Management"
	@echo ""
	@echo "Available commands:"
	@echo "  build     - Build all Docker images"
	@echo "  up        - Start all services in production mode"
	@echo "  down      - Stop all services"
	@echo "  logs      - View logs from all services"
	@echo "  restart   - Restart all services"
	@echo "  clean     - Remove all containers, images, and volumes"
	@echo "  dev       - Start services in development mode"
	@echo "  prod      - Start services in production mode (alias for up)"
	@echo "  test      - Run tests in containers"
	@echo "  health    - Check service health"
	@echo "  setup     - Initial setup (copy .env.example to .env)"
	@echo "  status    - Check service status"
	@echo "  logs-backend   - View backend logs only"
	@echo "  logs-frontend  - View frontend logs only"
	@echo "  shell-backend  - Access backend container shell"
	@echo "  shell-frontend - Access frontend container shell"
	@echo ""

# Build all images
build:
	docker-compose build

# Start services in production mode
up: setup
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Restart services
restart:
	docker-compose restart

# Clean up everything
clean:
	docker-compose down -v --rmi all --remove-orphans
	docker system prune -f

# Development mode
dev: setup
	docker-compose -f docker-compose.dev.yml up

# Run tests
test:
	docker-compose exec backend python -m pytest
	docker-compose exec frontend npm test -- --coverage --watchAll=false

# Check health
health:
	@echo "Checking backend health..."
	@curl -f http://localhost:5000/api/health || echo "Backend unhealthy"
	@echo ""
	@echo "Checking frontend health..."
	@curl -f http://localhost/ || echo "Frontend unhealthy"

# Quick setup for new users
setup:
	@echo "Setting up AI Health Chatbot..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file. Please edit it with your OpenAI API key."; \
	else \
		echo ".env file already exists."; \
	fi
	@echo "Run 'make up' to start the application."

# Production mode (alias for up)
prod: setup
	docker-compose up -d

# Check service status
status:
	docker-compose ps

# View backend logs only
logs-backend:
	docker-compose logs -f backend

# View frontend logs only
logs-frontend:
	docker-compose logs -f frontend

# Access backend container shell
shell-backend:
	docker-compose exec backend bash

# Access frontend container shell
shell-frontend:
	docker-compose exec frontend sh
