from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # OAuth provider fields
    oauth_provider = models.CharField(max_length=50, blank=True, null=True)
    oauth_provider_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['oauth_provider', 'oauth_provider_id']),
        ]



from django.utils import timezone

class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens"
    )
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_used(self):
        return self.used_at is not None
