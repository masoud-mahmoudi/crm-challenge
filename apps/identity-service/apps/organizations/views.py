from django.http import Http404
from rest_framework import generics, permissions

from .models import Company
from .selectors import get_company_with_children, list_accessible_companies_for_user, list_memberships_for_user
from .serializers import CompanyDetailSerializer, CompanySummarySerializer, MembershipSerializer


class CompanyListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CompanySummarySerializer

    def get_queryset(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        return list_accessible_companies_for_user(self.request.user)


class CompanyDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CompanyDetailSerializer
    lookup_url_kwarg = "company_id"

    def get_object(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        company = get_company_with_children(self.kwargs["company_id"])
        if not company:
            raise Http404
        if not list_accessible_companies_for_user(self.request.user).filter(id=company.id).exists():
            raise Http404
        return company


class MembershipListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MembershipSerializer

    def get_queryset(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        return list_memberships_for_user(self.request.user)
