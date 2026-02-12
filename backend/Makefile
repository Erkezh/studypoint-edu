.PHONY: install install-dev run fmt lint test migrate revision downgrade seed

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

migrate:
	alembic upgrade head

revision:
	alembic revision --autogenerate -m "$(m)"

downgrade:
	alembic downgrade -1

seed:
	python -m app.db.seed

test:
	pytest -q
