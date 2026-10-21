.PHONY: install test lint format demo

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
