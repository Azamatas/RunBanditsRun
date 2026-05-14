# Backend

FastAPI REST API with SQLAlchemy ORM and PostgreSQL.

## Architecture

```
backend/
  main.py            App factory, CORS, router registration
  database.py        SQLAlchemy engine, session, Base
  models/            SQLAlchemy ORM models
    user.py            User model
    activity.py        Activity model
    friendship.py      Friend request model
    kudos.py           Kudos model
    segment.py         Segment + SegmentEffort models
  schemas/           Pydantic request/response schemas
    auth.py             TokenOut, LoginRequest, etc.
    user.py             UserOut, UserUpdate, etc.
    activity.py         ActivityOut, ActivityCreate, etc.
    segment.py          SegmentOut, SegmentCreate, etc.
    stats.py            StatsOut
  routers/           FastAPI route handlers
    auth.py             POST /auth/login, /auth/register, /auth/refresh
    users.py            /users/me, /users/{id}, friend requests, search
    activities.py       /activities/ CRUD
    feed.py             /feed/ with owner_username + user_has_kudos
    kudos.py            /activities/{id}/kudos, delete returns JSON
    segments.py         /segments CRUD + efforts
    stats.py            /stats/me
    deps.py             get_current_user dependency
  services/          Business logic layer
    auth_service.py     JWT creation/validation, password hashing
    activity_service.py Activity CRUD helpers
    feed_service.py     Feed assembly with enrichment
    stats_service.py    Stats aggregation
  tests/             Pytest test suite
```

## Key patterns

- **Auth:** JWT access + refresh tokens. `deps.get_current_user` extracts user from `Authorization: Bearer <token>`.
- **Services:** Business logic lives in `services/`, not in routers. Routers handle HTTP and call services.
- **Schemas:** Pydantic models validate input and shape output. `ActivityOut` includes `owner_username` and `user_has_kudos`.
- **Database:** PostgreSQL via SQLAlchemy. Schema is managed by `init_db.sql` (run via `docker compose` or manually). Tests use the same database with transaction rollback isolation.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql://runbandits:runbandits@localhost:5432/runbandits` | PostgreSQL connection string (used by both app and tests) |
| `JWT_SECRET_KEY` | `change-me-in-production` | Secret for signing JWTs |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS origins (comma-separated, or `*`) |

## Getting started

```bash
# Start PostgreSQL
docker compose up -d

# The init_db.sql script runs automatically and creates the schema.

# Install dependencies
pip install -r backend/requirements.txt

# Run tests
pytest backend/tests/ -v

# Start the server
uvicorn backend.main:app --reload
```