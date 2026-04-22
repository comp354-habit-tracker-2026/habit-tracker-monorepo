
from django.conf import settings
from django.db import models


class DataConsent(models.Model):
    PROVIDER_CHOICES = [
        ('strava', 'Strava'),
        ('mapmyrun', 'MapMyRun'),
        ('weski', 'We Ski'),
        ('mywhoosh', 'MyWhoosh'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='data_consents',
    )
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    consent_granted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'data_integration_data_consent'
        unique_together = [['user', 'provider']]

    def __str__(self):
        status = 'granted' if self.consent_granted else 'revoked'
        return f"{self.user.username} - {self.provider} consent={status}"


class DataConsentHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='data_consent_history',
    )
    provider = models.CharField(max_length=20, choices=DataConsent.PROVIDER_CHOICES)
    consent_granted = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'data_integration_data_consent_history'
        ordering = ['-created_at']

    def __str__(self):
        status = 'granted' if self.consent_granted else 'revoked'
        return f"{self.user.username} - {self.provider} privacy={status}"


class PrivacyStatus(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='privacy_statuses',
    )
    provider_id = models.CharField(max_length=64)
    scope = models.CharField(max_length=128)
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'privacy_status'
        unique_together = [['user', 'provider_id', 'scope']]


class PrivacyAuditLog(models.Model):
    class Decision(models.TextChoices):
        ALLOW = 'ALLOW', 'Allow'
        DENY = 'DENY', 'Deny'
        INFO = 'INFO', 'Info'

    class Action(models.TextChoices):
        VERIFY = 'VERIFY', 'Verify'
        UPDATE = 'UPDATE', 'Update'
        HISTORY = 'HISTORY', 'History'

    caller_service = models.CharField(max_length=128)
    requested_user_id = models.IntegerField()
    provider_id = models.CharField(max_length=64)
    scope = models.CharField(max_length=128)
    decision = models.CharField(max_length=8, choices=Decision.choices)
    reason = models.CharField(max_length=128)
    action = models.CharField(max_length=16, choices=Action.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'privacy_audit_log'
        ordering = ['-created_at']

class FileRecord(models.Model):
    url_link = models.URLField(max_length=500)
    file_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.file_name} ({self.created_at.strftime('%Y-%m-%d %H:%M:%S')})"

