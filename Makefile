.PHONY: help dev down logs backend-install backend-lint backend-test backend-migrate web-install web-lint web-build

help: ## List available targets
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "%-18s %s\n", $$1, $$2}'

dev: ## Bring up web+api+db locally
	docker compose up --build

down: ## Stop and remove local containers
	docker compose down

logs: ## Tail logs from all services
	docker compose logs -f

backend-install: ## Install backend dependencies with uv
	cd backend && uv sync

backend-lint: ## Lint + typecheck the backend
	cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy .

backend-test: ## Run backend unit/integration tests
	cd backend && uv run pytest

backend-migrate: ## Apply pending Alembic migrations
	cd backend && uv run alembic upgrade head

web-install: ## Install web dependencies with pnpm
	cd web && pnpm install

web-lint: ## Lint + typecheck the web app
	cd web && pnpm run lint && pnpm exec tsc --noEmit

web-build: ## Production build of the web app
	cd web && pnpm run build
