# =============================================================================
# Sports Prophet - Project Makefile
# =============================================================================

.PHONY: help install install-dev test lint format clean run-backend run-frontend docker-up docker-down

# Default target
help:
	@echo "Sports Prophet - Available Commands"
	@echo "===================================="
	@echo ""
	@echo "Setup:"
	@echo "  make install       Install production dependencies"
	@echo "  make install-dev   Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run-backend   Start the FastAPI backend server"
	@echo "  make run-frontend  Start the React frontend server"
	@echo "  make test          Run all tests"
	@echo "  make lint          Run linting checks"
	@echo "  make format        Format code with black and ruff"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up     Start all Docker services"
	@echo "  make docker-down   Stop all Docker services"
	@echo "  make docker-build  Build Docker images"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         Remove build artifacts and caches"

# =============================================================================
# Setup
# =============================================================================

install:
	pip install -r backend/requirements.txt

install-dev:
	pip install -e ".[dev]"
	cd frontend && npm install

# =============================================================================
# Development
# =============================================================================

run-backend:
	cd backend && uvicorn app:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm start

test:
	pytest tests/ -v --tb=short

test-cov:
	pytest tests/ -v --cov=backend --cov=utils --cov-report=html --cov-report=term

lint:
	ruff check backend/ utils/ tests/
	mypy backend/ utils/ --ignore-missing-imports

format:
	black backend/ utils/ tests/
	ruff check --fix backend/ utils/ tests/

# =============================================================================
# Docker
# =============================================================================

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# =============================================================================
# Cleanup
# =============================================================================

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf build/ dist/ 2>/dev/null || true
