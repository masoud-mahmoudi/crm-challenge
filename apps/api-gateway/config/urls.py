from __future__ import annotations

from django.urls import include, path

from config.schema import graphql_view


urlpatterns = [
    path("api/", include("apps.rest_api.urls")),
    path("graphql", graphql_view, name="graphql"),
]