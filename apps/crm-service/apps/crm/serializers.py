from __future__ import annotations

from rest_framework import serializers

from .models import Lead


class LeadListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = (
            "id",
            "name",
            "email",
            "phone",
            "status",
            "enrichment_status",
            "score",
            "company_id",
            "owner_user_id",
            "source",
            "created_at",
            "updated_at",
        )


class LeadDetailSerializer(LeadListSerializer):
    created_by_user_id = serializers.UUIDField(read_only=True)

    class Meta(LeadListSerializer.Meta):
        fields = LeadListSerializer.Meta.fields + ("created_by_user_id",)


class CreateLeadSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    owner_user_id = serializers.UUIDField(required=False, allow_null=True)
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    phone = serializers.CharField(max_length=64, required=False, allow_null=True, allow_blank=True)
    source = serializers.CharField(max_length=128, required=False, allow_null=True, allow_blank=True)


class UpdateLeadSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    phone = serializers.CharField(max_length=64, required=False, allow_null=True, allow_blank=True)
    source = serializers.CharField(max_length=128, required=False, allow_null=True, allow_blank=True)
    status = serializers.ChoiceField(choices=Lead.Status.choices, required=False)


class AssignLeadSerializer(serializers.Serializer):
    owner_user_id = serializers.UUIDField()


class InternalLeadWorkflowUpdateSerializer(serializers.Serializer):
    enrichment_status = serializers.ChoiceField(choices=Lead.EnrichmentStatus.choices, required=False)
    score = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    status = serializers.ChoiceField(choices=Lead.Status.choices, required=False)