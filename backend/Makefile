.PHONY: install install-dev run fmt lint test migrate revision downgrade seed

install:
\tpip install -r requirements.txt

install-dev:
\tpip install -r requirements-dev.txt

run:
\tuvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

migrate:
\talembic upgrade head

revision:
\talembic revision --autogenerate -m "$(m)"

downgrade:
\talembic downgrade -1

seed:
\tpython -m app.db.seed

test:
\tpytest -q

