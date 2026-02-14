# IXL-like Learning Platform Backend (FastAPI)

Production-ready backend APIs for skills-based practice, progress tracking, and analytics.

## Stack
- FastAPI (Pydantic v2), Python 3.11+
- PostgreSQL + SQLAlchemy 2.0 async (asyncpg)
- Alembic migrations
- Redis (cache, rate limits, session/idempotency)
- JWT auth (access+refresh), Argon2 password hashing
- pytest + httpx (async)

## Quickstart
1) Create env file:
```bash
cp .env.example .env
```

2) Start services:
```bash
docker compose up --build
```
`docker-compose.yml` forces container-safe connection URLs (`postgres`, `redis`) for the API service,
so Docker startup will not fail from `localhost` Redis/Postgres values in `.env`.
It also runs `alembic upgrade head` automatically before starting Uvicorn.

3) Run migrations + seed:
```bash
docker compose exec api python -m app.db.seed
```

OpenAPI: `http://localhost:8001/docs`

## Run without Docker (local Postgres + Redis)
Set `.env` to local services (e.g. `DATABASE_URL=...@localhost:5432/ixl`, `REDIS_URL=redis://localhost:6379/0`), then:
```bash
./venv/bin/python -m alembic upgrade head
./venv/bin/python -m app.db.seed
./venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

If your shell resolves global binaries (for example `/Library/Frameworks/Python.framework/.../uvicorn`),
run backend commands via `python -m ...` (or `./venv/bin/python -m ...`) to guarantee packages from `backend/venv`.

### Common local DB error
If you see `asyncpg.exceptions.InvalidAuthorizationSpecificationError: role "<name>" does not exist`,
your `DATABASE_URL` username does not exist in your local Postgres instance.
Fix `backend/.env` `DATABASE_URL` to a valid local role (for Docker setup use `postgres:postgres`),
or create that role in Postgres.

## IXL-like practice mapping (MVP)
- SmartScore zones: `LEARNING` (0–69), `REFINING` (70–89), `CHALLENGE` (90–100)
- Challenge Zone: correct `+1..+2`, incorrect `-3..-8`, mastery `100` requires long streak
- Active time: `active_time_seconds` with inactivity cap via `/practice/sessions/{id}/heartbeat`
- Resume: starting a skill returns unfinished session (24h expiry via `PRACTICE_SESSION_EXPIRY_HOURS`)
- Questions Log: `/analytics/skills/{skill_id}/questions-log`
- Score Grid: assignments have `target_smartscore` and update on every submit; teacher grid at `/teacher/classrooms/{cid}/assignments/{aid}/score-grid`
- PDFs: `/reports/practice-sessions/{session_id}.pdf`, `/reports/assignments/{assignment_id}.pdf`, certificates at `/awards/certificates/{type}.pdf`

## Example flow (curl)
Register:
```bash
curl -sS -X POST http://localhost:8001/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"student@example.com","password":"Password123!","full_name":"Student","role":"STUDENT","grade_level":5}' | jq
```

Login:
```bash
TOKENS=$(curl -sS -X POST http://localhost:8001/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"student@example.com","password":"Password123!"}')
ACCESS=$(echo "$TOKENS" | jq -r '.data.access_token')
```

Start practice session:
```bash
curl -sS -X POST http://localhost:8001/api/v1/practice/sessions \
  -H "Authorization: Bearer $ACCESS" \
  -H 'Content-Type: application/json' \
  -d '{"skill_id":1}' | jq
```

Submit answer:
```bash
curl -sS -X POST http://localhost:8001/api/v1/practice/sessions/<session_id>/submit \
  -H "Authorization: Bearer $ACCESS" \
  -H 'Content-Type: application/json' \
  -d '{"question_id":1,"submitted_answer":{"choice":"A"},"time_spent_sec":12}' | jq
```

## Dev commands
- `make run`
- `make migrate`
- `make seed`
- `make test`

## Seeded demo accounts
- Admin: `admin@example.com` / `Password123!`
- Teacher: `teacher@example.com` / `Password123!`
- Student: `student@example.com` / `Password123!`

## Run tests (Docker)
```bash
docker compose exec api pytest -q
```
