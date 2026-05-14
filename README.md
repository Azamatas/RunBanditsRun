# RunBanditsRun

Social fitness tracker. Log runs/rides/walks/hikes, view a feed, give kudos, add friends.

## Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Frontend:** React + Vite + React Query + React Router + Leaflet

## Run

```bash
# Backend (port 8000)
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload

# Frontend (port 5173, proxies /api -> backend)
cd frontend && npm install && npm run dev
```

Open http://localhost:5173

## Test

```bash
# Backend
pytest backend/tests/

# Frontend build check
cd frontend && npm run build
```

## Type Checking

```bash
# Install dev dependencies
pip install -r backend/requirements-dev.txt

# Run mypy
mypy backend
```

## Linting

```bash
# Run ruff
ruff check backend

# Auto-fix issues
ruff check --fix backend
```

## Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

## Project layout

```
backend/          FastAPI app (models, routers, schemas, services)
frontend/         React SPA (api, components, pages, context, constants)
```