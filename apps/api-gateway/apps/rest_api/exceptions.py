from __future__ import annotations

from typing import Any

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from infrastructure.exceptions import GatewayError


def _format_error(message: str, *, code: str, details: Any | None = None) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    return {"error": error}


def api_exception_handler(exc, context):
    if isinstance(exc, GatewayError):
        return Response(
            _format_error(str(exc), code=exc.code, details=exc.details),
            status=exc.status_code,
        )

    response = drf_exception_handler(exc, context)
    if response is None:
        return Response(
            _format_error("Unexpected server error", code="server_error"),
            status=500,
        )

    details = response.data
    message = "Request failed"
    if isinstance(details, dict):
        detail_value = details.get("detail")
        if isinstance(detail_value, str):
            message = detail_value
    elif isinstance(details, list) and details and isinstance(details[0], str):
        message = details[0]

    response.data = _format_error(message, code="request_error", details=details)
    return response