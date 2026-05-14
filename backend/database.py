import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

logger = logging.getLogger("runbanditsrun.database")

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://runbandits:runbandits@localhost:5432/runbandits"
)

logger.info(f"Connecting to database: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

logger.info("Database connection established")


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        logger.debug("Database session closed")
