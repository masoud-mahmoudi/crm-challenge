from __future__ import annotations

from dataclasses import dataclass

from django.http import HttpRequest

from infrastructure.auth.context import RequestAuthContext
from infrastructure.services import ServiceContainer, build_service_container


@dataclass(frozen=True)
class GraphQLContext:
    request: HttpRequest
    auth_context: RequestAuthContext | None
    services: ServiceContainer


def build_graphql_context(request: HttpRequest) -> GraphQLContext:
    return GraphQLContext(
        request=request,
        auth_context=getattr(request, "auth_context", None),
        services=build_service_container(),
    )