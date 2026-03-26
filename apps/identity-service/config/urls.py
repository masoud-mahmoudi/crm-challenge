from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(_: object) -> JsonResponse:
    return JsonResponse({"service": "identity-service", "status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
    path("api/v1/auth/", include("apps.authn.urls")),
    path("api/v1/users/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.organizations.urls")),
    path(".well-known/jwks.json", include("apps.authn.urls_compat")),
]
