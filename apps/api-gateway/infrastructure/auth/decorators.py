from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar, cast

from django.http import HttpRequest
from graphql import GraphQLError
from rest_framework.permissions import BasePermission

from infrastructure.exceptions import UnauthorizedError

from .context import RequestAuthContext


class HasAuthContext(BasePermission):
    message = "Authentication credentials were not provided."

    def has_permission(self, request, view):  # pyright: ignore[reportIncompatibleMethodOverride]
        return getattr(request, "auth_context", None) is not None


def require_request_auth(request: HttpRequest) -> RequestAuthContext:
    auth_context = cast(RequestAuthContext | None, getattr(request, "auth_context", None))
    if auth_context is None:
        raise UnauthorizedError("Authentication credentials were not provided.")
    return auth_context


F = TypeVar("F", bound=Callable[..., Any])


def require_auth_context(view_func: F) -> F:
    @wraps(view_func)
    def wrapped(*args: Any, **kwargs: Any):
        request = next((arg for arg in args if isinstance(arg, HttpRequest)), None)
        if request is None:
            raise UnauthorizedError("Authentication credentials were not provided.")
        require_request_auth(request)
        return view_func(*args, **kwargs)

    return cast(F, wrapped)


def require_graphql_auth(info) -> RequestAuthContext:
    auth_context = getattr(info.context, "auth_context", None)
    if auth_context is None:
        raise GraphQLError(
            "Authentication credentials were not provided.",
            extensions={"code": "UNAUTHENTICATED"},
        )
    return cast(RequestAuthContext, auth_context)