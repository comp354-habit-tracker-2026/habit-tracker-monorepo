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


class FileRecord(models.Model):
    url_link = models.URLField(max_length=500)
    file_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

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


class FileRecord(models.Model):
    url_link = models.URLField(max_length=500)
    file_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.file_name} ({self.created_at.strftime('%Y-%m-%d %H:%M:%S')})"
