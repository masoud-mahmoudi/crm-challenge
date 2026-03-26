from rest_framework.permissions import BasePermission

from .models import Company, Membership
from .selectors import list_accessible_companies_for_user


class CanAccessCompany(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return list_accessible_companies_for_user(request.user).filter(id=obj.id).exists()


class CanViewMembershipsForUser(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.user.is_staff:
            return True
        return Membership.objects.filter(
            user=request.user,
            role=Membership.Role.PARENT_ADMIN,
            is_active=True,
            company__is_active=True,
            company__company_type=Company.CompanyType.PARENT,
        ).exists()
