from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest
from rest_framework.exceptions import AuthenticationFailed

from auth_lib import AuthError, read_bearer_token


class InternalServiceAuthenticationFailed(AuthenticationFailed):
    default_detail = "A valid internal service token is required."


def has_internal_service_token(request: HttpRequest) -> bool:
    configured_token = getattr(settings, "INTERNAL_SERVICE_TOKEN", "")
    if not configured_token:
        return False
    try:
        token = read_bearer_token(request.headers)
    except AuthError:
        return False
    return token == configured_token


def require_internal_service_token(request: HttpRequest) -> None:
    if not has_internal_service_token(request):
        raise InternalServiceAuthenticationFailed()
