

test:
	poetry run pytest --envfile=.env -vv --capture=tee-sys

snap-update:
	poetry run pytest --envfile=.env --snapshot-update

whole_test:
	python3 -m examples.basics
	poetry run pytest --envfile=.env -vv --capture=tee-sys
	poetry run pytest --envfile=.env --snapshot-update
	poetry run pytest --envfile=.env -vv --capture=tee-sys


.PHONY: lint format typecheck check-all

format:
	poetry run ruff format .

lint:
	poetry run ruff check . --fix

ruff: lint format

typecheck:
	poetry run mypy .

check-all: lint format typecheck