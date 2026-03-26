from rest_framework.permissions import BasePermission

from apps.organizations.models import Company, Membership


class CanViewUserMemberships(BasePermission):
    def has_permission(self, request, view) -> bool:
        target_user_id = str(view.kwargs.get("user_id"))
        if str(request.user.id) == target_user_id or request.user.is_staff:
            return True

        return Membership.objects.filter(
            user=request.user,
            role=Membership.Role.PARENT_ADMIN,
            is_active=True,
            company__is_active=True,
            company__company_type=Company.CompanyType.PARENT,
        ).exists()
