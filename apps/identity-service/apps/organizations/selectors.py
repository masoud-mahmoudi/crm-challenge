from django.db.models import Prefetch, Q

from .models import Company, Membership


def list_memberships_for_user(user):
    return Membership.objects.filter(user=user, is_active=True, company__is_active=True).select_related(
        "company", "company__parent"
    )


def get_company_with_children(company_id):
    return (
        Company.objects.filter(id=company_id)
        .select_related("parent")
        .prefetch_related(
            "children",
            Prefetch(
                "memberships",
                queryset=Membership.objects.select_related("user", "company").filter(is_active=True),
            ),
        )
        .first()
    )


def list_accessible_companies_for_user(user):
    membership_company_ids = list(
        list_memberships_for_user(user).values_list("company_id", flat=True)
    )
    parent_company_ids = list(
        list_memberships_for_user(user)
        .filter(company__company_type=Company.CompanyType.PARENT)
        .values_list("company_id", flat=True)
    )
    return (
        Company.objects.filter(
            Q(id__in=membership_company_ids) | Q(parent_id__in=parent_company_ids),
            is_active=True,
        )
        .select_related("parent")
        .distinct()
        .order_by("name")
    )
