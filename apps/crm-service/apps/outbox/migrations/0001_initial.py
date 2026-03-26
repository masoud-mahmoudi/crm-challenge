from __future__ import annotations

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="OutboxEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("event_type", models.CharField(db_index=True, max_length=128)),
                ("aggregate_type", models.CharField(max_length=64)),
                ("aggregate_id", models.UUIDField(db_index=True)),
                ("payload", models.JSONField()),
                ("headers", models.JSONField(blank=True, default=dict)),
                ("status", models.CharField(choices=[("PENDING", "Pending"), ("PUBLISHED", "Published"), ("FAILED", "Failed")], default="PENDING", max_length=16)),
                ("retry_count", models.PositiveIntegerField(default=0)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ("created_at",)},
        ),
    ]