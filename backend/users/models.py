from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # OAuth provider fields
    oauth_provider = models.CharField(max_length=50, blank=True, null=True)
    oauth_provider_id = models.CharField(max_length=255, blank=True, null=True, unique=True)

    # Account lockout fields (Ticket #112)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['oauth_provider', 'oauth_provider_id']),
        ]
