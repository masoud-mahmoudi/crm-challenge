from rest_framework import serializers

from apps.accounts.serializers import UserSummarySerializer

from .models import Company, Membership


class CompanySummarySerializer(serializers.ModelSerializer):
    parent_id = serializers.UUIDField(source="parent.id", read_only=True)

    class Meta:
        model = Company
        fields = ("id", "name", "company_type", "parent_id", "is_active", "created_at", "updated_at")


class MembershipSerializer(serializers.ModelSerializer):
    company = CompanySummarySerializer(read_only=True)

    class Meta:
        model = Membership
        fields = ("id", "role", "is_active", "created_at", "updated_at", "company")


class CompanyMembershipSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = Membership
        fields = ("id", "role", "is_active", "created_at", "updated_at", "user")


class CompanyDetailSerializer(CompanySummarySerializer):
    children = CompanySummarySerializer(many=True, read_only=True)
    memberships = CompanyMembershipSerializer(many=True, read_only=True)

    class Meta(CompanySummarySerializer.Meta):
        fields = CompanySummarySerializer.Meta.fields + ("children", "memberships")
