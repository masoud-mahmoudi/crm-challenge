from __future__ import annotations

from django.urls import path

from .views import DeadLetterListView, ReplayWorkflowEventView, WorkflowRunDetailView, WorkflowRunListView


urlpatterns = [
    path("runs/", WorkflowRunListView.as_view(), name="workflow-run-list"),
    path("runs/<uuid:run_id>/", WorkflowRunDetailView.as_view(), name="workflow-run-detail"),
    path("dead-letters/", DeadLetterListView.as_view(), name="dead-letter-list"),
    path("replay/<uuid:event_id>/", ReplayWorkflowEventView.as_view(), name="workflow-replay"),
]
