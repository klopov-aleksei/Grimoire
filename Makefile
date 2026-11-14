.DEFAULT_GOAL := help
.PHONY: help install lint format test test-integration check up down

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

test: ## Run unit tests (no integration)
	uv run pytest

test-integration: ## Run integration tests (needs `make up`)
	uv run pytest -m integration --no-cov

check: ## Lint, format check and tests with coverage gate
	uv run ruff check .
	uv run ruff format --check .
	uv run pytest

up: ## Start docker compose services
	docker compose up -d

down: ## Stop docker compose services
	docker compose down
