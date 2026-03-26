from __future__ import annotations

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


class WorkflowServiceError(Exception):
    pass


class DownstreamServiceError(WorkflowServiceError):
    def __init__(self, message: str, *, status_code: int = 502, payload: object | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


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
