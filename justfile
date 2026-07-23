[default]
scrape:
    PYTHONPATH=. .venv/bin/python main.py

lint:
    .venv/bin/python -m ruff check .

fix:
    .venv/bin/python -m ruff check --fix .

test:
    .venv/bin/python -m pytest -v --cov .

coverage:
    .venv/bin/python -m pytest --cov --cov-report=term-missing --cov-fail-under=80

lock:
    poetry lock

install:
    poetry install

sync:
    poetry sync
