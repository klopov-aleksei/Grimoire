.DEFAULT_GOAL := help
.PHONY: help install lint format format-check test test-integration check up down

help: ## Show this help
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-18s %s\n", $$1, $$2}'

install: ## Install dependencies and git hooks
	uv sync
	uv run pre-commit install --hook-type pre-commit --hook-type commit-msg

lint: ## Run ruff lint
	uv run ruff check .

format: ## Format code with ruff
	uv run ruff check --select I --fix .
	uv run ruff format .

format-check: ## Check formatting without changing files
	uv run ruff format --check .

test: ## Run unit tests (no integration)
	uv run pytest

test-integration: ## Run integration tests (needs `make up`)
	uv run pytest -m integration --no-cov

check: lint format-check test ## Lint, format check and tests with coverage gate

up: ## Start docker compose services
	docker compose up -d

down: ## Stop docker compose services
	docker compose down
