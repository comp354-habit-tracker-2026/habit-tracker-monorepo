# Add notification persistence models here (templates, delivery records, preferences).


from activities import models
from config import settings


class NotificationType(models.TextChoices):
    GOAL_ACHIEVED = "GOAL_ACHIEVED", "Goal Achieved"
    GOAL_AT_RISK = "GOAL_AT_RISK", "Goal At Risk"
    GOAL_MISSED = "GOAL_MISSED", "Goal Missed"
    INACTIVITY_REMINDER = 'INACTIVITY_REMINDER', 'Inactivity Reminder'


class NotificationStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    SENT = 'SENT', 'Sent'
    FAILED = 'FAILED', 'Failed'
    SNOOZED = 'SNOOZED', 'Snoozed'
    ARCHIVED = 'ARCHIVED', 'Archived'


class NotificationChannel(models.TextChoices):
    EMAIL = 'EMAIL', 'Email'
    IN_APP = 'IN_APP', 'In App'


class Notification(models.Model):
    notif_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=20, choices=NotificationType.choices)
    message = models.TextField()
    read = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=NotificationStatus.choices, default=NotificationStatus.PENDING)
    channel = models.CharField(max_length=20, choices=NotificationChannel.choices)
    payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    archived = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    goal = models.ForeignKey(
        "goals.Goal",
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Notification {self.notif_id} for {self.user} - {self.type}"


class UserNotificationPreference(models.Model):
    pref_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')
    email_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    achievement_notifs = models.BooleanField(default=True)
    inactivity_reminders = models.BooleanField(default=True)
    inactivity_threshold_days = models.IntegerField(default=7)

    def __str__(self):
        return f"Notification Preferences for {self.user}"
