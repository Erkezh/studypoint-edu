.PHONY: install install-dev run fmt lint test migrate revision downgrade seed

PYTHON ?= ./venv/bin/python

install:
	$(PYTHON) -m pip install -r requirements.txt

install-dev:
	$(PYTHON) -m pip install -r requirements-dev.txt

run:
	$(PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

migrate:
	$(PYTHON) -m alembic upgrade head

revision:
	$(PYTHON) -m alembic revision --autogenerate -m "$(m)"

downgrade:
	$(PYTHON) -m alembic downgrade -1

seed:
	$(PYTHON) -m app.db.seed

test:
	$(PYTHON) -m pytest -q
