.PHONY: lint format typecheck check-all

lint:
	poetry run ruff check . --fix

format:
	poetry run ruff format .

typecheck:
	poetry run mypy .

check-all: lint format typecheck