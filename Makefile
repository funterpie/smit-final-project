.PHONY: install test lint format demo demo-seed

install:
	pip install -e . -r requirements.txt
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v

lint:
	ruff check .

format:
	black .

demo:
	./demo/run_demo.sh

demo-seed:
	AUDIT_DB_PATH=demo/demo.db $(PYTHON) -m scripts.seed_demo

PYTHON ?= .venv/bin/python
