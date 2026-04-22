from django.contrib.auth import get_user_model

from core.data import BaseRepository
from activities.models import Activity, ConnectedAccount

User = get_user_model()

VALID_PROVIDERS = {choice[0] for choice in ConnectedAccount.PROVIDER_CHOICES}

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)
 
    def create_user(self, **user_data):
        return self.model.objects.create_user(**user_data)
 
    def delete_provider_data(self, user, provider: str) -> dict:
        """
        Delete all imported activity data for a given user and provider.
 
        Only external (non-manual) providers are permitted. Raises ValueError
        for unknown or disallowed provider values so the caller can surface a
        meaningful error response without leaking ORM details.
 
        Returns a dict with the number of records deleted, e.g.:
            {"deleted_count": 42, "provider": "strava"}
        """
        if provider not in VALID_PROVIDERS:
            raise ValueError("Invalid provider")

        deleted_count, _ = Activity.objects.filter(
            account__user=user,
            account__provider=provider
        ).delete()

        return {
            "provider": provider,
            "deleted_count": deleted_count
        }
