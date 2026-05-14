"""Comprehensive logging configuration for RunBanditsRun backend."""

import json
import logging
import os
import sys
import time
from collections.abc import Callable
from contextvars import ContextVar
from datetime import datetime
from types import TracebackType
from typing import Any, TypeVar

from typing_extensions import override

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

F = TypeVar("F", bound=Callable[..., Any])


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get() or "-"
        return True


class StructuredFormatter(logging.Formatter):
    STANDARD_RECORD_ATTRS: frozenset[str] = frozenset(
        {
            "name",
            "msg",
            "args",
            "created",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "exc_info",
            "exc_text",
            "thread",
            "threadName",
            "message",
            "request_id",
            "asctime",
        }
    )

    def __init__(self, include_timestamp: bool = True, include_level: bool = True) -> None:
        super().__init__()
        self.include_timestamp = include_timestamp
        self.include_level = include_level

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "logger": record.name,
            "message": record.getMessage(),
        }

        if self.include_timestamp:
            log_data["timestamp"] = self.formatTime(record)

        if self.include_level:
            log_data["level"] = record.levelname
            log_data["level_num"] = record.levelno

        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        log_data["source"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }

        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
            }

        extra_fields: dict[str, Any] = {}
        for key, value in record.__dict__.items():
            if key not in (
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "exc_info",
                "exc_text",
                "thread",
                "threadName",
                "message",
                "request_id",
                "asctime",
            ):
                extra_fields[key] = value

        if extra_fields:
            log_data["extra"] = extra_fields

        return json.dumps(log_data, default=str)


class ColorFormatter(logging.Formatter):
    GRAY = "\033[90m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    LEVEL_COLORS: dict[int, str] = {
        logging.DEBUG: GRAY,
        logging.INFO: BLUE,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: BOLD + RED,
    }

    def format(self, record: logging.LogRecord) -> str:
        level_color = self.LEVEL_COLORS.get(record.levelno, self.RESET)
        level_name = f"{level_color}{record.levelname}{self.RESET}"
        timestamp = self.formatTime(record)
        message = record.getMessage()
        request_id = getattr(record, "request_id", "-")
        source = f"{record.pathname}:{record.lineno}"

        return f"{timestamp} | {level_name} | {request_id} | {source} | {message}"

    @override
    def formatException(
        self,
        ei: tuple[type[BaseException], BaseException, TracebackType | None]
        | tuple[None, None, None],
    ) -> str:
        return f"{self.RED}{super().formatException(ei)}{self.RESET}"


def setup_logging(
    log_level: str = "INFO",
    json_format: bool = False,
) -> None:
    level = getattr(logging, os.environ.get("LOG_LEVEL", log_level).upper(), logging.INFO)
    use_json = json_format or os.environ.get("LOG_FORMAT", "text").lower() == "json"

    log_dir = os.environ.get("LOGS_DIR", "logs")
    timestamp = datetime.now().strftime("%Y-%m-%d")
    log_file = f"{log_dir}/app_{timestamp}.log"

    os.makedirs(log_dir, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    if use_json:
        formatter: logging.Formatter = StructuredFormatter()
    else:
        formatter = ColorFormatter()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RequestIdFilter())
    root_logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(StructuredFormatter())
    file_handler.addFilter(RequestIdFilter())
    root_logger.addHandler(file_handler)

    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(level)
    logging.getLogger("uvicorn.error").setLevel(level)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("passlib").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger = logging.getLogger("runbanditsrun")
    logger.info(
        "Logging configured",
        extra={
            "log_level": logging.getLevelName(level),
            "log_file": log_file,
            "json_format": use_json,
        },
    )


def timed(logger_name: str | None = None):
    def decorator(func: F) -> F:
        name = logger_name or func.__module__
        logger = logging.getLogger(name)

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - start_time
                logger.debug(
                    f"{func.__name__} executed",
                    extra={"duration_ms": round(elapsed * 1000, 2), "function": func.__name__},
                )

        return wrapper  # type: ignore[return-value]

    return decorator


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


setup_logging()
