from __future__ import annotations

from typing import Any

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def api_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        return Response({"error": {"code": "server_error", "message": "Unexpected server error"}}, status=500)

    detail = response.data
    message = "Request failed"
    if isinstance(detail, dict) and isinstance(detail.get("detail"), str):
        message = detail["detail"]
    response.data = {"error": {"code": "request_error", "message": message, "details": detail}}
    return response