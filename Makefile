.PHONY: install test-db test-unit test-integration test-e2e test test-down
install:
	uv sync --frozen
test-db:
	docker compose -f docker-compose.test.yml up -d --wait
test-unit:
	uv run pytest -m unit
test-integration: test-db
	uv run pytest -m integration
test-e2e: test-db
	uv run pytest -m e2e
test: test-db
	uv run pytest --cov --cov-report=term-missing --cov-report=xml:reports/coverage.xml --cov-report=html:reports/htmlcov --junitxml=reports/tests.xml
test-down:
	docker compose -f docker-compose.test.yml down -v
