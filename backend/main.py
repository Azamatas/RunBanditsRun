import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from psycopg2.errors import NumericValueOutOfRange
from sqlalchemy.exc import DataError

from backend.logging_config import setup_logging
from backend.middleware.logging_middleware import LoggingMiddleware
from backend.routers import activities, auth, feed, kudos, segments, stats, users
from backend.services.auth_service import SECRET_KEY

load_dotenv()

setup_logging()

logger = logging.getLogger("runbanditsrun")

if SECRET_KEY == "change-me-in-production":
    logger.warning("Using default JWT secret key — set JWT_SECRET_KEY env var in production!")

app = FastAPI(title="RunBanditsRun")

app.add_middleware(LoggingMiddleware)


@app.exception_handler(DataError)
async def dataerror_handler(request: Request, exc: DataError) -> JSONResponse:
    if isinstance(exc.orig, NumericValueOutOfRange):
        logger.warning(f"Numeric value out of range: {exc}")
        return JSONResponse(status_code=422, content={"detail": "Integer value out of range"})
    logger.error(f"Database error: {exc}")
    raise exc


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
def health() -> dict[str, str]:
    logger.debug("Health check requested")
    return {"status": "ok"}


logger.info("RunBanditsRun backend started")
