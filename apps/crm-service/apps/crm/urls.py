from __future__ import annotations

from django.urls import path

from .views import InternalLeadDetailView, InternalLeadWorkflowUpdateView, LeadAssignView, LeadDetailView, LeadListCreateView


urlpatterns = [
    path("leads/", LeadListCreateView.as_view(), name="lead-list-create"),
    path("leads/<uuid:lead_id>/", LeadDetailView.as_view(), name="lead-detail"),
    path("leads/<uuid:lead_id>/assign/", LeadAssignView.as_view(), name="lead-assign"),
    path("internal/leads/<uuid:lead_id>/", InternalLeadDetailView.as_view(), name="internal-lead-detail"),
    path("internal/leads/<uuid:lead_id>/workflow-update/", InternalLeadWorkflowUpdateView.as_view(), name="internal-lead-workflow-update"),
]