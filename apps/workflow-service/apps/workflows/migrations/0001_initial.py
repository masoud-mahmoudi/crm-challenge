from __future__ import annotations

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ProcessedMessage",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("event_id", models.UUIDField(db_index=True, unique=True)),
                ("topic", models.CharField(max_length=128)),
                ("consumer_name", models.CharField(max_length=128)),
                ("processed_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ("-processed_at",)},
        ),
        migrations.CreateModel(
            name="WorkflowRun",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("event_id", models.UUIDField(db_index=True)),
                ("event_type", models.CharField(db_index=True, max_length=128)),
                ("lead_id", models.UUIDField(blank=True, db_index=True, null=True)),
                ("company_id", models.UUIDField(blank=True, db_index=True, null=True)),
                ("status", models.CharField(choices=[("RECEIVED", "Received"), ("PROCESSING", "Processing"), ("COMPLETED", "Completed"), ("FAILED", "Failed"), ("DEAD_LETTERED", "Dead lettered")], default="RECEIVED", max_length=32)),
                ("retry_count", models.PositiveIntegerField(default=0)),
                ("error_message", models.TextField(blank=True, default="")),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ("-started_at",)},
        ),
        migrations.CreateModel(
            name="DeadLetterEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("event_id", models.UUIDField(db_index=True)),
                ("topic", models.CharField(max_length=128)),
                ("event_type", models.CharField(max_length=128)),
                ("payload", models.JSONField()),
                ("error_message", models.TextField()),
                ("failed_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ("-failed_at",)},
        ),
        migrations.AddIndex(
            model_name="processedmessage",
            index=models.Index(fields=["topic", "consumer_name"], name="wf_msg_topic_consumer_idx"),
        ),
        migrations.AddIndex(
            model_name="workflowrun",
            index=models.Index(fields=["status", "event_type"], name="workflow_run_status_event_idx"),
        ),
        migrations.AddIndex(
            model_name="workflowrun",
            index=models.Index(fields=["lead_id"], name="workflow_run_lead_idx"),
        ),
        migrations.AddIndex(
            model_name="workflowrun",
            index=models.Index(fields=["company_id"], name="workflow_run_company_idx"),
        ),
        migrations.AddIndex(
            model_name="deadletterevent",
            index=models.Index(fields=["event_type"], name="workflow_dlq_event_type_idx"),
        ),
    ]
