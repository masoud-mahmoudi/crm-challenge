from __future__ import annotations

from django.urls import path

from .views import WorkflowRunDetailView, WorkflowRunListView


urlpatterns = [
    path("workflow-runs/", WorkflowRunListView.as_view(), name="compat-workflow-run-list"),
    path("workflow-runs/<uuid:run_id>/", WorkflowRunDetailView.as_view(), name="compat-workflow-run-detail"),
]
