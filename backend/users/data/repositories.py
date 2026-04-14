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
        user.locked_until = timezone.now() + timezone.timedelta(minutes=30)
        user.save(update_fields=['failed_login_attempts', 'locked_until'])

    def reset_failed_attempts(self, user):
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save(update_fields=['failed_login_attempts', 'locked_until'])
