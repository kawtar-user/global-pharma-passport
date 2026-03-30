from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("app.errors")


def build_error_response(
    *,
    request_id: str,
    code: str,
    message: str,
    status_code: int,
    details: list[dict[str, str]] | None = None,
) -> JSONResponse:
    payload: dict[str, object] = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }
    if details:
        payload["error"] = {**payload["error"], "details": details}
    return JSONResponse(status_code=status_code, content=payload)


def _extract_http_message(detail: object) -> str:
    if isinstance(detail, str):
        return detail
    if isinstance(detail, dict):
        message = detail.get("message")
        if isinstance(message, str) and message.strip():
            return message
    if isinstance(detail, list) and detail:
        return "The request could not be completed. Please review the submitted information."
    return "The request could not be completed."


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    logger.warning(
        "http_exception method=%s path=%s status=%s request_id=%s detail=%r",
        request.method,
        request.url.path,
        exc.status_code,
        request_id,
        exc.detail,
    )
    return build_error_response(
        request_id=request_id,
        code="http_error",
        message=_extract_http_message(exc.detail),
        status_code=exc.status_code,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    details = [
        {
            "field": ".".join(str(item) for item in error.get("loc", [])[1:]),
            "message": error.get("msg", "Invalid value"),
        }
        for error in exc.errors()
    ]
    logger.info(
        "validation_error method=%s path=%s request_id=%s details=%s",
        request.method,
        request.url.path,
        request_id,
        details,
    )
    return build_error_response(
        request_id=request_id,
        code="validation_error",
        message="Some information is missing or invalid. Please review the form and try again.",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details=details,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    logger.exception(
        "unhandled_exception method=%s path=%s request_id=%s",
        request.method,
        request.url.path,
        request_id,
        exc_info=exc,
    )
    return build_error_response(
        request_id=request_id,
        code="internal_server_error",
        message="An unexpected error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
