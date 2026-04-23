from core.business import BaseService
from users.data import UserRepository


class UserRegistrationService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or UserRepository()

    def register_user(self, validated_data):
        validated_data.pop("password2", None)
        return self.repository.create_user(**validated_data)

class UserDeletionService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or UserRepository()

    def execute(self, user):
        return self.repository.delete_user(user.id)