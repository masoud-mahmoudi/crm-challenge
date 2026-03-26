from __future__ import annotations

import json

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.middleware.csrf import get_token
from strawberry.django.views import GraphQLView

from apps.graphql_api.context import build_graphql_context
from apps.graphql_api.schema import schema


class GatewayGraphQLView(GraphQLView):
    graphql_ide = "graphiql" if settings.DEBUG else None

    @staticmethod
    def _get_request_query(request: HttpRequest) -> tuple[str, str | None]:
        if request.method.upper() == "GET":
            return request.GET.get("query", ""), request.GET.get("operationName")

        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except (UnicodeDecodeError, json.JSONDecodeError):
            return "", None

        if not isinstance(payload, dict):
            return "", None

        query = payload.get("query")
        operation_name = payload.get("operationName")
        return (str(query) if isinstance(query, str) else "", str(operation_name) if isinstance(operation_name, str) else None)

    @classmethod
    def _is_public_introspection_request(cls, request: HttpRequest) -> bool:
        query, operation_name = cls._get_request_query(request)
        normalized_query = query.replace(" ", "")
        return operation_name == "IntrospectionQuery" or "__schema" in normalized_query or "__type" in normalized_query

    def get_context(self, request: HttpRequest, response: JsonResponse):
        return build_graphql_context(request)

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if request.method.upper() in {'GET', 'HEAD', 'OPTIONS'}:
            get_token(request)

        query, _ = self._get_request_query(request)
        is_graphiql_shell = request.method.upper() == "GET" and not query
        is_public_introspection = self._is_public_introspection_request(request)
        if not is_graphiql_shell and not is_public_introspection and getattr(request, "auth_context", None) is None:
            return JsonResponse(
                {
                    "error": {
                        "code": "authentication_required",
                        "message": "Authentication credentials were not provided.",
                    }
                },
                status=401,
            )
        return super().dispatch(request, *args, **kwargs)


graphql_view = GatewayGraphQLView.as_view(schema=schema)