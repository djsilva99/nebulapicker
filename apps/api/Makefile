include .env.dev
PYTHON_VERSION := $(shell cat .python-version)

.SILENT:


.PHONY: install
install: ## Install dependencies
	@poetry env use python
	@poetry install --no-root

.PHONY: test
test: ## Run tests
	@poetry run coverage run -m pytest && poetry run coverage report -m

.PHONY: lint
lint: ## Check lint
	@echo "Running ruff"
	@poetry run ruff check src/ tests/

.PHONY: apply-lint
apply-lint: ## Apply lint
	@echo "Apply ruff"
	@poetry run ruff check --fix src/ tests/

.PHONY: local-deployment
local-deployment: ## Deploy app locally
	@echo "Local deployment"
	@poetry run uvicorn src.main:app --env-file .env.dev --port=8080 --reload

.PHONY: apply-migrations
apply-migrations: ## Apply migrations
	@alembic upgrade head

.PHONY: downgrade-migrations
downgrade-migrations: ## Downgrade migrations
	@alembic downgrade -1

.PHONY: docker-compose-dev
docker-compose-dev: ## Docker compose the dev mode
	@poetry env use python
	@poetry install --no-root
	@docker-compose up -d
	@echo "Local deployment"
	@poetry run uvicorn src.main:app --env-file .env.dev --port=8080 --reload

.PHONY: docker-compose-full
docker-compose-full: ## Docker compose the full application
	@docker-compose -f docker-compose-full.yaml up -d

.PHONY: docker-compose-full
docker-compose-full-down: ## Docker compose down the full application
	@docker-compose -f docker-compose-full.yaml down

.PHONY: docker-compose-full
docker-compose-dev-down: ## Docker compose down the dev mode
	@docker-compose -f docker-compose-full.yaml down

.PHONY: docker-build
docker-build: ## Docker build
	@docker build --build-arg PYTHON_VERSION=$(cat .python-version) -t nebulapicker-api .
