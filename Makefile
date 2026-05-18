# AutoPivot Project Makefile
.PHONY: help build up down logs clean test lint format

help:
	@echo "AutoPivot Uganda - Development Commands"
	@echo "========================================"
	@echo "make build              - Build Docker images"
	@echo "make up                 - Start all services"
	@echo "make down               - Stop all services"
	@echo "make logs               - View service logs"
	@echo "make test               - Run tests"
	@echo "make lint               - Run linting"
	@echo "make format             - Format code"
	@echo "make clean              - Remove volumes and cleanup"
	@echo "make db-migrate         - Run database migrations"
	@echo "make db-seed            - Seed database with sample data"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "🚀 Services started"
	@echo "API: http://localhost:8000"
	@echo "Web: http://localhost:3000"
	@echo "Docs: http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

logs-service:
	@read -p "Enter service name: " service; \
	docker-compose logs -f $$service

clean:
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test:
	docker-compose exec listing-service pytest tests/
	docker-compose exec advantage-engine pytest tests/

lint:
	docker-compose exec listing-service flake8 .
	docker-compose exec listing-service mypy .

format:
	docker-compose exec listing-service black .
	docker-compose exec listing-service isort .

db-migrate:
	docker-compose exec postgres psql -U autopivot -d autopivot_db -f /docker-entrypoint-initdb.d/01-init.sql

db-seed:
	@echo "Seeding database with sample data..."
	docker-compose exec postgres psql -U autopivot -d autopivot_db < data/seeds/sample-data.sql

ps:
	docker-compose ps

shell:
	@read -p "Enter service name: " service; \
	docker-compose exec $$service /bin/bash

python-shell:
	@read -p "Enter service name: " service; \
	docker-compose exec $$service python

kill:
	docker-compose kill

restart:
	docker-compose restart

status:
	@echo "Service Status:"
	@docker-compose ps
	@echo "\nAPI Health Check:"
	@curl -s http://localhost:8000/health | python -m json.tool || echo "API not responding"
