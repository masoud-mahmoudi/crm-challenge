from __future__ import annotations

import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Lead(models.Model):
    class Status(models.TextChoices):
        NEW = "NEW", "New"
        QUALIFIED = "QUALIFIED", "Qualified"
        UNQUALIFIED = "UNQUALIFIED", "Unqualified"
        REVIEW_REQUIRED = "REVIEW_REQUIRED", "Review required"

    class EnrichmentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_id = models.UUIDField(db_index=True)
    owner_user_id = models.UUIDField(null=True, blank=True, db_index=True)
    created_by_user_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=64, blank=True, null=True)
    source = models.CharField(max_length=128, blank=True, null=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.NEW)
    enrichment_status = models.CharField(
        max_length=32,
        choices=EnrichmentStatus.choices,
        default=EnrichmentStatus.PENDING,
    )
    score = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("company_id", "status"), name="crm_lead_company_status_idx"),
            models.Index(fields=("owner_user_id",), name="crm_lead_owner_idx"),
            models.Index(fields=("created_by_user_id",), name="crm_lead_creator_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.company_id})"

    def clean(self) -> None:
        super().clean()
        if not self.company_id:
            raise ValidationError({"company_id": "company_id is required"})