from __future__ import annotations

import logging
from time import perf_counter
from uuid import uuid4

from fastapi import Request, Response
from fastapi.responses import RedirectResponse

from app.core.config import settings

logger = logging.getLogger("app.request")
HEALTHCHECK_PATHS = {"/health", "/health/"}


async def request_context_middleware(request: Request, call_next):
    request.state.request_id = request.headers.get("X-Request-ID", str(uuid4()))
    started_at = perf_counter()
    if settings.force_https and request.url.scheme == "http" and request.url.path not in HEALTHCHECK_PATHS:
        secure_url = request.url.replace(scheme="https")
        return RedirectResponse(url=str(secure_url), status_code=307)
    try:
        response: Response = await call_next(request)
    except Exception:
        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        if settings.enable_request_logging:
            logger.exception(
                "request_failed method=%s path=%s request_id=%s duration_ms=%s",
                request.method,
                request.url.path,
                request.state.request_id,
                duration_ms,
            )
        raise

    duration_ms = round((perf_counter() - started_at) * 1000, 2)
    response.headers["X-Request-ID"] = request.state.request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    if settings.enable_request_logging:
        logger.info(
            "request_completed method=%s path=%s status=%s request_id=%s duration_ms=%s",
            request.method,
            request.url.path,
            response.status_code,
            request.state.request_id,
            duration_ms,
        )
    return response
