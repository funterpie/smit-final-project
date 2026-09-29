.PHONY: install test lint format

install:
	pip install -e ".[dev]" -r requirements-dev.txt

test:
	pytest tests/ -v

lint:
	ruff check .

format:
	black .
