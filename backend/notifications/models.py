# Add notification persistence models here (templates, delivery records, preferences).
from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_CHOICES = [
        ('ACHIEVEMENT', 'Achievement'),
        ('INACTIVITY_REMINDER', 'Inactivity Reminder'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
        ('SNOOZED', 'Snoozed'),
        ('ARCHIVED', 'Archived'),
    ]

    CHANNEL_CHOICES = [
        ('EMAIL', 'Email'),
        ('IN_APP', 'In App'),
    ]

    notif_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()
    read = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    archived = models.BooleanField(default=False)

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