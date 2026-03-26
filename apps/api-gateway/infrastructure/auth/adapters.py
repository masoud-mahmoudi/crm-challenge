from __future__ import annotations

from typing import Any, Mapping

from django.conf import settings
from django.http import HttpRequest

from auth_lib import AuthError, build_auth_context

from infrastructure.exceptions import UnauthorizedError

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
        raise UnauthorizedError(exc.message) from exc


def build_auth_context_from_request(request: HttpRequest) -> RequestAuthContext:
    return build_auth_context_from_headers(request.headers)


def get_request_bearer_token(request: HttpRequest) -> str | None:
    auth_context = getattr(request, "auth_context", None)
    if auth_context is not None:
        return auth_context.token

    authorization = request.headers.get("Authorization", "")
    if authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip()

    return None