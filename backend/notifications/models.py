from django.conf import settings
from django.db import models


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        GOAL_ACHIEVED = "GOAL_ACHIEVED", "Goal Achieved"
        GOAL_AT_RISK = "GOAL_AT_RISK", "Goal At Risk"
        GOAL_MISSED = "GOAL_MISSED", "Goal Missed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    goal = models.ForeignKey(
        "goals.Goal",
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
        blank=True,
    )
    notification_type = models.CharField(max_length=32, choices=NotificationType.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

        indexes = [
            # Notifications
            models.Index(fields=['user', 'created_at'], name='idx_notification_user_created'),
            # Unread notifications
            models.Index(fields=['user', 'is_read'], name='idx_notification_user_is_read'),
            # Filter by notification type
            models.Index(fields=['notification_type'], name='idx_notification_type'),
            # Notifications by goal
            models.Index(fields=['goal', 'created_at'], name='idx_notification_goal_created'),
        ]
