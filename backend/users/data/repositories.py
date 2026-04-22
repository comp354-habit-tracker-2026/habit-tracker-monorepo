from django.contrib.auth import get_user_model
from django.utils import timezone
from core.data import BaseRepository

User = get_user_model()


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def create_user(self, **user_data):
        return self.model.objects.create_user(**user_data)
    
    def get_by_username(self, username):
        try:
            return self.model.objects.get(username=username)
        except self.model.DoesNotExist:
            return None

    def increment_failed_attempts(self, user):
        user.failed_login_attempts += 1
        user.save(update_fields=['failed_login_attempts'])

    def reset_failed_attempts(self, user):
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save(update_fields=['failed_login_attempts', 'locked_until'])
    
    def lock_account(self, user):
        user.locked_until = timezone.now() + timezone.timedelta(minutes=30)
        user.save(update_fields=['locked_until'])

    def get_or_create_oauth_user(self, provider, provider_id, email, first_name="", last_name=""):
        try:
            user = self.model.objects.get(
                oauth_provider=provider,
                oauth_provider_id=provider_id,
            )
            return user
        except self.model.DoesNotExist:
            pass

        try:
            user = self.model.objects.get(email=email)
            user.oauth_provider = provider
            user.oauth_provider_id = provider_id
            user.save(update_fields=["oauth_provider", "oauth_provider_id"])
            return user
        except self.model.DoesNotExist:
            pass

        username = email.split("@")[0]
        base_username = username
        counter = 1
        while self.model.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = self.model.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            oauth_provider=provider,
            oauth_provider_id=provider_id,
        )
        user.set_unusable_password()
        user.save()
        return user
