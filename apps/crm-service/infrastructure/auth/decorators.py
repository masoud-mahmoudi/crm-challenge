from __future__ import annotations

from typing import cast

from django.http import HttpRequest
from rest_framework.exceptions import APIException

from .context import RequestAuthContext


class UnauthorizedException(APIException):
    status_code = 401
    default_detail = "Authentication credentials were not provided."
    default_code = "unauthorized"


def require_request_auth(request: HttpRequest) -> RequestAuthContext:
    auth_context = cast(RequestAuthContext | None, getattr(request, "auth_context", None))
    if auth_context is None:
        raise UnauthorizedException()
    return auth_context