from rest_framework import serializers

from .models import User


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "is_active", "is_staff", "created_at")


class CurrentUserSerializer(UserSummarySerializer):
    memberships = serializers.SerializerMethodField()

    class Meta(UserSummarySerializer.Meta):
        fields = UserSummarySerializer.Meta.fields + ("memberships",)

    def get_memberships(self, obj: User):
        from apps.organizations.serializers import MembershipSerializer

        memberships = obj.memberships.select_related("company", "company__parent").filter(
            is_active=True,
            company__is_active=True,
        )
        return MembershipSerializer(memberships, many=True).data
