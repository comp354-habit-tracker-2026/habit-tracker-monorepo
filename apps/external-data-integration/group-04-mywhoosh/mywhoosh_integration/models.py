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
