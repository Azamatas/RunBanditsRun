# RunBanditsRun

Social fitness tracker. Log runs/rides/swims, view a feed, give kudos, follow athletes, create segments.

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

## Project layout

```
backend/          FastAPI app (models, routers, schemas, services)
frontend/         React SPA (api, components, pages, context, constants)
```