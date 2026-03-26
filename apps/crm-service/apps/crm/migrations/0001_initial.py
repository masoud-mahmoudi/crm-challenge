from __future__ import annotations

import django.core.validators
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Lead",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("company_id", models.UUIDField(db_index=True)),
                ("owner_user_id", models.UUIDField(blank=True, db_index=True, null=True)),
                ("created_by_user_id", models.UUIDField(db_index=True)),
                ("name", models.CharField(max_length=255)),
                ("email", models.EmailField(blank=True, max_length=254, null=True)),
                ("phone", models.CharField(blank=True, max_length=64, null=True)),
                ("source", models.CharField(blank=True, max_length=128, null=True)),
                ("status", models.CharField(choices=[("NEW", "New"), ("QUALIFIED", "Qualified"), ("UNQUALIFIED", "Unqualified"), ("REVIEW_REQUIRED", "Review required")], default="NEW", max_length=32)),
                ("enrichment_status", models.CharField(choices=[("PENDING", "Pending"), ("PROCESSING", "Processing"), ("COMPLETED", "Completed"), ("FAILED", "Failed")], default="PENDING", max_length=32)),
                ("score", models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.AddIndex(
            model_name="lead",
            index=models.Index(fields=["company_id", "status"], name="crm_lead_company_status_idx"),
        ),
        migrations.AddIndex(
            model_name="lead",
            index=models.Index(fields=["owner_user_id"], name="crm_lead_owner_idx"),
        ),
        migrations.AddIndex(
            model_name="lead",
            index=models.Index(fields=["created_by_user_id"], name="crm_lead_creator_idx"),
        ),
    ]