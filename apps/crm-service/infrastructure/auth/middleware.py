from __future__ import annotations

from django.http import HttpRequest, HttpResponse, JsonResponse
from rest_framework.exceptions import AuthenticationFailed

from .adapters import build_auth_context_from_request
from .service_tokens import has_internal_service_token


class OptionalJWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        setattr(request, "auth_context", None)
        setattr(request, "internal_service_authenticated", False)
        if request.headers.get("Authorization"):
            if has_internal_service_token(request):
                setattr(request, "internal_service_authenticated", True)
                return self.get_response(request)
            try:
                setattr(request, "auth_context", build_auth_context_from_request(request))
            except AuthenticationFailed as exc:
                return JsonResponse({"error": {"code": "unauthorized", "message": str(exc)}}, status=401)
        return self.get_response(request)