# Dealer Scraper Makefile
# Professional development commands for the dealer scraping application

.PHONY: help install install-dev test lint format type-check security clean run build docker deploy

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install production dependencies
	pip install -r requirements.txt
	playwright install chromium

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8 mypy isort safety bandit
	playwright install chromium

# Development setup
setup: ## Set up development environment
	python scripts/setup.py

# Testing
test: ## Run all tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term

test-fast: ## Run tests without slow tests
	pytest tests/ -v -m "not slow"

# Code quality
lint: ## Run linting checks
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics

format: ## Format code with black and isort
	black .
	isort .

format-check: ## Check code formatting
	black --check --diff .
	isort --check-only --diff .

type-check: ## Run type checking
	mypy . --ignore-missing-imports

# Security
security: ## Run security checks
	safety check
	bandit -r . -f json

# Quality checks (all)
quality: lint format-check type-check security ## Run all quality checks

# Cleaning
clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/

# Running
run: ## Run the web application
	python main.py

run-cli: ## Run CLI with example (override with DEALER and URL)
	python main.py scrape "${DEALER:-Test Dealer}" "${URL:-https://example.com}"

# Building
build: ## Build the application
	python -m build

# Docker
docker-build: ## Build Docker image
	docker build -t dealer-scraper:latest .

docker-run: ## Run Docker container
	docker run -p 8501:8501 dealer-scraper:latest

docker-test: ## Test Docker image
	docker run --rm dealer-scraper:latest python -c "import core, scrapers, utils; print('Docker build successful')"

# Railway deployment
deploy: ## Deploy to Railway (requires Railway CLI)
	railway deploy

# Development workflow
dev-check: format lint type-check test ## Run full development check

# CI simulation
ci: install-dev quality test ## Simulate CI pipeline locally

# Release preparation
release-check: clean install-dev quality test build ## Full release preparation check