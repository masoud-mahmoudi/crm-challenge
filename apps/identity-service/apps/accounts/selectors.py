from django.db.models import Prefetch

from apps.organizations.models import Membership

from .models import User


def get_user_by_id(user_id):
    return (
        User.objects.filter(id=user_id)
        .prefetch_related(
            Prefetch(
                "memberships",
                queryset=Membership.objects.select_related("company", "company__parent").filter(
                    is_active=True,
                    company__is_active=True,
                ),
            )
        )
        .first()
    )
