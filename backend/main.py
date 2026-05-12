import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
import backend.models  # ensure all models are registered before create_all
from backend.routers import auth, users, activities, feed, stats, kudos, segments
from backend.services.auth_service import SECRET_KEY

Base.metadata.create_all(bind=engine)

if SECRET_KEY == "change-me-in-production":
    logging.getLogger("uvicorn").warning("Using default JWT secret key — set JWT_SECRET_KEY env var in production!")

app = FastAPI(title="RunBanditsRun")

CORS_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
if CORS_ORIGINS == ["*"]:
    allowed_origins = ["*"]
else:
    allowed_origins = CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(activities.router)
app.include_router(kudos.router)
app.include_router(feed.router)
app.include_router(stats.router)
app.include_router(segments.router)


@app.get("/")
def health():
    return {"status": "ok"}
