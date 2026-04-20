from django.contrib.auth import get_user_model
from activities.models import ConnectedAccount, Activity
from core.data import BaseRepository

User = get_user_model()


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def create_user(self, **user_data):
        return self.model.objects.create_user(**user_data)
from django.contrib.auth import get_user_model

from core.data import BaseRepository

User = get_user_model()

VALID_PROVIDERS = {choice[0] for choice in ConnectedAccount.PROVIDER_CHOICES if choice[0] != "manual"}

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
            raise ValueError(
                f"Unknown or non-deletable provider '{provider}'. "
                f"Valid providers: {sorted(VALID_PROVIDERS)}"
            )
 
        deleted_count, _ = (
            Activity.objects.filter(user=user, provider=provider).delete()
        )
 
        return {"deleted_count": deleted_count, "provider": provider}
 