from django.urls import path

from .views import CompanyDetailView, CompanyListView, MembershipListView


urlpatterns = [
    path("companies/", CompanyListView.as_view(), name="company-list"),
    path("companies/<uuid:company_id>/", CompanyDetailView.as_view(), name="company-detail"),
    path("memberships/", MembershipListView.as_view(), name="membership-list"),
]
