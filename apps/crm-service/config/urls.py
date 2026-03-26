from __future__ import annotations

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(_: object) -> JsonResponse:
    return JsonResponse({"service": "crm-service", "status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", health, name="health"),
    path("api/v1/", include("apps.crm.urls")),
]