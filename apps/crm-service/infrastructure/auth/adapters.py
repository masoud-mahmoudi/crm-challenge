from __future__ import annotations

from typing import Any, Mapping

from django.conf import settings
from django.http import HttpRequest

from auth_lib import AuthError, build_auth_context
from rest_framework.exceptions import AuthenticationFailed

from .context import RequestAuthContext


def build_auth_context_from_headers(headers: Mapping[str, Any]) -> RequestAuthContext:
    try:
        return build_auth_context(
            headers,
            jwks_url=settings.JWT_JWKS_URL,
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )
    except AuthError as exc:
        raise AuthenticationFailed(exc.message) from exc


def build_auth_context_from_request(request: HttpRequest) -> RequestAuthContext:
    return build_auth_context_from_headers(request.headers)