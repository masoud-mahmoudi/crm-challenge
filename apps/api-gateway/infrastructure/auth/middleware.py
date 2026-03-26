from __future__ import annotations

from django.http import HttpRequest, HttpResponse, JsonResponse

from infrastructure.exceptions import UnauthorizedError

from .adapters import build_auth_context_from_request


class OptionalJWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        setattr(request, "auth_context", None)

        if request.headers.get("Authorization"):
            try:
                setattr(request, "auth_context", build_auth_context_from_request(request))
            except UnauthorizedError as exc:
                return JsonResponse(
                    {"error": {"code": exc.code, "message": str(exc)}},
                    status=exc.status_code,
                )

        return self.get_response(request)