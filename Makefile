.PHONY: lint format typecheck check-all

format:
	poetry run ruff format .

lint:
	poetry run ruff check . --fix

ruff: format lint

typecheck:
	poetry run mypy .

check-all: format lint typecheck