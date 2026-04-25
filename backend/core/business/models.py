from django.db import models

class OutboxEvent(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PUBLISHED = "PUBLISHED", "Published"
        FAILED = "FAILED", "Failed"

    event_id = models.AutoField(primary_key=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    attempts = models.PositiveIntegerField(default=0)
    last_error = models.TextField(null=True, blank=True)

    idempotency_key = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        db_index=True,
        unique=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "outbox_events"
        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]