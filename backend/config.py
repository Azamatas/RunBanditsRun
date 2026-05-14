import logging
import os

logger = logging.getLogger("runbanditsrun.config")


class Config:
    # Database
    DATABASE_URL = os.environ.get(
        "DATABASE_URL", "postgresql://runbandits:runbandits@localhost:5432/runbandits"
    )

    # JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-me-in-production")
    JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # CORS
    ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

    # Common activity detection job settings
    COMMON_ACTIVITY_DETECTION_ENABLED = os.environ.get("COMMON_ACTIVITY_DETECTION_ENABLED", "true").lower() == "true"
    COMMON_ACTIVITY_DETECTION_INTERVAL_SECONDS = int(os.environ.get("COMMON_ACTIVITY_DETECTION_INTERVAL_SECONDS", "10"))
    COMMON_ACTIVITY_DETECTION_CLUSTER_THRESHOLD = float(os.environ.get("COMMON_ACTIVITY_DETECTION_CLUSTER_THRESHOLD", "50.0"))
    COMMON_ACTIVITY_DETECTION_MIN_ACTIVITIES = int(os.environ.get("COMMON_ACTIVITY_DETECTION_MIN_ACTIVITIES", "3"))
    COMMON_ACTIVITY_DETECTION_MIN_LENGTH = float(os.environ.get("COMMON_ACTIVITY_DETECTION_MIN_LENGTH", "100.0"))


config = Config()

logger.info("Configuration loaded")
logger.debug(f"DATABASE_URL: {config.DATABASE_URL}")
logger.debug(f"COMMON_ACTIVITY_DETECTION_ENABLED: {config.COMMON_ACTIVITY_DETECTION_ENABLED}")
logger.debug(f"COMMON_ACTIVITY_DETECTION_INTERVAL_SECONDS: {config.COMMON_ACTIVITY_DETECTION_INTERVAL_SECONDS}")
