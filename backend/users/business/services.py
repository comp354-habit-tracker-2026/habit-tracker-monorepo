import logging

from core.business import BaseService
from users.data import UserRepository

logger = logging.getLogger(__name__)


class UserRegistrationService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or UserRepository()

    def register_user(self, validated_data):
        validated_data.pop("password2", None)
        return self.repository.create_user(**validated_data)


class AccountDeletionService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or UserRepository()

    def delete_account(self, user, password):
        if not user.check_password(password):
            raise ValueError("Invalid password")
        logger.info(
            "Account deletion initiated: user_id=%s, username=%s",
            user.id,
            user.username,
        )
        self.repository.delete_user(user)
        logger.info(
            "Account deleted successfully: user_id=%s, username=%s",
            user.id,
            user.username,
        )