from notifications.business.services import UserPreferencesService
from core.business import BaseService
from users.data import UserRepository


class UserRegistrationService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or UserRepository()
        self.user_preferences_service = UserPreferencesService()

    def register_user(self, validated_data):
        validated_data.pop("password2", None)
        created_user = self.repository.create_user(**validated_data)
        self.user_preferences_service.create_default_user_preferences(created_user.id)

class UserDeletionService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or UserRepository()

    def execute(self, user):
        return self.repository.delete_user(user.id)