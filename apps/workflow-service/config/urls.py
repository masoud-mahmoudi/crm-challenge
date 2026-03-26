from __future__ import annotations

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(_: object) -> JsonResponse:
    return JsonResponse({"service": "workflow-service", "status": "ok"})


urlpatterns = [
    path("health", health, name="health"),
    path("api/v1/workflows/", include("apps.workflows.urls")),
    path("api/v1/", include("apps.workflows.compat_urls")),
    path("admin/", admin.site.urls),
]
