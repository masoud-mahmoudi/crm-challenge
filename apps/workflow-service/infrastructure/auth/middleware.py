from __future__ import annotations

from django.http import HttpRequest, HttpResponse, JsonResponse

from .adapters import build_auth_context_from_request


class OptionalJWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        setattr(request, "auth_context", None)
        if request.headers.get("Authorization"):
            try:
                setattr(request, "auth_context", build_auth_context_from_request(request))
            except Exception as exc:
                return JsonResponse({"error": {"code": "unauthorized", "message": str(exc)}}, status=401)
        return self.get_response(request)
