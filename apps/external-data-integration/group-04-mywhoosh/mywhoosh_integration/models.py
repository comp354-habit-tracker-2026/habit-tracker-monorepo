from django.db import models

# Create your models here.

# Generated with assistance from ChatGPT (OpenAI), adapted for project needs.

class SyncStatus(models.Model):
    STATUS_SUCCESS = "success"
    STATUS_PARTIAL = "partial"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Success"),
        (STATUS_PARTIAL, "Partial"),
        (STATUS_FAILED, "Failed"),
    ]

    user_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    sessions_imported = models.PositiveIntegerField(default=0)
    duplicates_skipped = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user_id", "-timestamp"]),
        ]

    def __str__(self) -> str:
        return (
            f"SyncStatus(user_id={self.user_id}, status={self.status}, "
            f"sessions_imported={self.sessions_imported}, "
            f"duplicates_skipped={self.duplicates_skipped})"
        )
class ImportedSession(models.Model):
    user_id = models.IntegerField()
    provider = models.CharField(max_length=50, default="mywhoosh")
    external_id = models.CharField(max_length=255)

    activity_type = models.CharField(max_length=50, default="cycling")
    session_date = models.DateField()

    distance = models.FloatField(blank=True, null=True)
    calories = models.FloatField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)

    raw_data = models.JSONField(default=dict)
    imported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-imported_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "provider", "external_id"],
                name="unique_imported_session_per_user_provider_external_id",
            )
        ]

    def __str__(self) -> str:
        return (
            f"ImportedSession(user_id={self.user_id}, provider={self.provider}, "
            f"external_id={self.external_id})"
        )
