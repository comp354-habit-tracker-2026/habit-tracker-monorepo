from django.db import models
from django.conf import settings


class ConnectedAccount(models.Model):
    """A user's linked external fitness account (e.g. their Strava profile).

    One row per provider per user. Activities are tied to this account
    so we always know which provider an activity came from.
    """

    PROVIDER_CHOICES = [
        ('strava', 'Strava'),
        ('mapmyrun', 'MapMyRun'),
        ('weski', 'We Ski'),
        ('mywhoosh', 'MyWhoosh'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='connected_accounts',
    )
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    external_user_id = models.CharField(max_length=255)
    access_token = models.CharField(max_length=500, null=True, blank=True)
    refresh_token = models.CharField(max_length=500, null=True, blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    connected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'connected_accounts'
        constraints = [
            models.UniqueConstraint(fields=['user', 'provider'], name='unique_user_provider'),
            models.UniqueConstraint(fields=['provider', 'external_user_id'], name='unique_provider_external_user'),
        ]

        indexes = [
            # Filter by User
            models.Index(fields=['user'], name='idx_connected_account_user'),
            # Filter by Provider
            models.Index(fields=['provider'], name='idx_connected_account_provider'),
        ]

    def __str__(self):
        return f"{self.user} via {self.provider}"


class Activity(models.Model):
    """A single fitness activity (run, ride, ski session, etc.) from a connected account.

    Activities always come from an external provider, there is no manual entry.
    Note: account is nullable only during this migration phase; it will be made
    required once existing rows are cleaned up.
    """

    account = models.ForeignKey(
        ConnectedAccount,
        on_delete=models.CASCADE,
        related_name='activities',
        null=True,
        blank=True,
    )
    activity_type = models.CharField(max_length=100)
    duration = models.IntegerField(help_text="Duration in minutes")
    date = models.DateField()
    external_id = models.CharField(max_length=255, blank=True, null=True)
    raw_data = models.JSONField(blank=True, null=True)
    distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    calories = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Activities"
        db_table = 'activities'
        constraints = [
            # Same activity can't be imported twice from the same account.
            # Empty strings are also excluded so only real external IDs are checked.
            models.UniqueConstraint(
                fields=['account', 'external_id'],
                name='unique_account_external_id',
                condition=models.Q(external_id__isnull=False) & ~models.Q(external_id=''),
            )
        ]

        indexes = [
            # Filter by account and date
            models.Index(fields=['account', 'date'], name='idx_activity_account_date'),
            models.Index(fields=['account', 'created_at'], name='idx_activity_account_created'),
            # Filter by activity and date
            models.Index(fields=['date'], name='idx_activity_date'),
            # Filter by date and created_at
            models.Index(fields=['-date', '-created_at'], name='idx_activity_date_created_desc'),
        ]

    def save(self, *args, **kwargs):
        # Treat blank external_id as no ID (NULL) so it doesn't trigger the unique constraint
        if self.external_id is not None and self.external_id.strip() == '':
            self.external_id = None
        super().save(*args, **kwargs)

    def __str__(self):
        provider = self.account.provider if self.account_id else 'unknown'
        return f"{self.activity_type} - {self.date} ({provider})"
