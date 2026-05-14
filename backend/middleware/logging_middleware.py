"""Request/Response logging middleware for FastAPI."""

import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.logging_config import request_id_var

logger = logging.getLogger("runbanditsrun.middleware")

SENSITIVE_HEADERS = {
    "authorization",
    "cookie",
    "x-api-key",
    "x-access-token",
    "x-refresh-token",
}


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        log_request_body: bool = False,
        log_response_body: bool = False,
        max_body_size: int = 10000,
    ):
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = str(uuid.uuid4())[:8]
        request_id_var.set(request_id)
        start_time = time.perf_counter()

        await self._log_request(request, request_id)

        try:
            response = await call_next(request)
        except Exception as e:
            self._log_exception(request, request_id, e, start_time)
            raise
        finally:
            request_id_var.set(None)

        await self._log_response(response, request, request_id, start_time)
        return response

    async def _log_request(self, request: Request, request_id: str) -> None:
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        headers = self._filter_headers(request.headers)
        client = request.client.host if request.client else "unknown"

        log_data = {
            "request_id": request_id,
            "method": method,
            "path": path,
            "query_params": query_params,
            "headers": headers,
            "client": client,
        }

        logger.info("Request received", extra=log_data)

    async def _log_response(
        self, response: Response, request: Request, request_id: str, start_time: float
    ) -> None:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        headers = self._filter_headers(response.headers)

        log_data = {
            "request_id": request_id,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "headers": headers,
        }

        logger.info("Response sent", extra=log_data)

    def _log_exception(
        self, request: Request, request_id: str, exception: Exception, start_time: float
    ) -> None:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "duration_ms": duration_ms,
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
        }

        logger.error("Request failed", extra=log_data, exc_info=True)

    def _filter_headers(self, headers) -> dict:
        filtered = {}
        for key, value in headers.items():
            if key.lower() not in SENSITIVE_HEADERS:
                filtered[key] = value
            else:
                filtered[key] = "[REDACTED]"
        return filtered


def create_logging_middleware(
    log_request_body: bool = False,
    log_response_body: bool = False,
    max_body_size: int = 10000,
) -> LoggingMiddleware:
    return LoggingMiddleware(
        app=None,
        log_request_body=log_request_body,
        log_response_body=log_response_body,
        max_body_size=max_body_size,
    )
