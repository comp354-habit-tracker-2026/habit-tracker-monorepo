from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # oauth_provider and oauth_provider_id were removed from here.
    # Linking a user to an external fitness platform (Strava, MapMyRun, etc.)
    # is now handled by the ConnectedAccount model in the activities app,
    # which supports multiple providers per user.

    class Meta:
        db_table = 'users'
